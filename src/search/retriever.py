import time
import numpy as np
from typing import List, Optional, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from src.config import (
    TOP_K_RETRIEVAL,
    DENSE_WEIGHT,
    SPARSE_WEIGHT,
    RRF_K,
    SIMILARITY_THRESHOLD
)
from src.knowledge_base.store import ComplianceKnowledgeStore
from src.models.schemas import (
    SearchQuery,
    SearchResult,
    RetrievedEvidence,
    PolicyClause
)
from src.search.citation import EvidenceCitationEngine

class PolicyEvidenceRetriever:
    """Hybrid Dense + Sparse BM25 Policy Retriever with Reciprocal Rank Fusion and Evidence Grounding."""

    def __init__(self, store: Optional[ComplianceKnowledgeStore] = None):
        self.store = store or ComplianceKnowledgeStore.get_instance()

    def search(self, query_obj: Any) -> SearchResult:
        """Executes hybrid retrieval, applying dense semantic search, sparse lexical matching, and RRF."""
        start_time = time.time()
        if isinstance(query_obj, str):
            query_obj = SearchQuery(query=query_obj)
        query_text = query_obj.query.strip()
        top_k = query_obj.top_k or TOP_K_RETRIEVAL

        if not query_text:
            return SearchResult(query=query_text, total_found=0, results=[], retrieval_time_ms=0.0)

        clauses = self.store.get_all_clauses()
        if not clauses:
            return SearchResult(query=query_text, total_found=0, results=[], retrieval_time_ms=0.0)

        # 1. Dense Semantic Scoring
        query_dense_vec = self.store.embedding_model.encode([query_text], normalize_embeddings=True)
        dense_sims = cosine_similarity(query_dense_vec, self.store.dense_embeddings)[0]

        # 2. Sparse Lexical Scoring (BM25 / TF-IDF)
        query_sparse_vec = self.store.bm25_vectorizer.transform([query_text])
        sparse_sims = cosine_similarity(query_sparse_vec, self.store.bm25_matrix)[0]

        # 3. Dense & Sparse Ranking for RRF
        dense_ranking = np.argsort(-dense_sims)
        sparse_ranking = np.argsort(-sparse_sims)

        dense_rank_dict = {idx: rank for rank, idx in enumerate(dense_ranking)}
        sparse_rank_dict = {idx: rank for rank, idx in enumerate(sparse_ranking)}

        # 4. Score Fusion & Metadata Filtering
        scored_candidates = []
        for idx, clause in enumerate(clauses):
            # Metadata filter
            if query_obj.category and clause.category.lower() != query_obj.category.lower():
                continue
            if query_obj.business_area and clause.business_area.lower() != query_obj.business_area.lower():
                continue

            d_score = float(dense_sims[idx])
            s_score = float(sparse_sims[idx])

            # Reciprocal Rank Fusion component
            rrf_score = (
                (DENSE_WEIGHT / (RRF_K + dense_rank_dict[idx])) +
                (SPARSE_WEIGHT / (RRF_K + sparse_rank_dict[idx]))
            )

            # Combined normalized score
            hybrid_score = (DENSE_WEIGHT * d_score) + (SPARSE_WEIGHT * s_score)
            blended_score = 0.5 * hybrid_score + 0.5 * (rrf_score * 50.0)  # scale RRF to ~0-1 range

            scored_candidates.append({
                "clause": clause,
                "score": blended_score,
                "dense_score": d_score,
                "sparse_score": s_score
            })

        # 5. Sort by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        # 6. Apply threshold and top_k
        filtered_results = [
            c for c in scored_candidates
            if c["dense_score"] >= SIMILARITY_THRESHOLD or c["score"] >= 0.28
        ][:top_k]

        # Fallback if strict threshold filters everything
        if not filtered_results and scored_candidates:
            filtered_results = scored_candidates[:min(3, len(scored_candidates))]

        # 7. Ground Evidence with Citations and Highlight Spans
        evidence_list: List[RetrievedEvidence] = []
        for cand in filtered_results:
            evidence = EvidenceCitationEngine.ground_evidence(
                query=query_text,
                clause=cand["clause"],
                score=cand["score"],
                dense_score=cand["dense_score"],
                sparse_score=cand["sparse_score"]
            )
            evidence_list.append(evidence)

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        return SearchResult(
            query=query_text,
            total_found=len(evidence_list),
            results=evidence_list,
            retrieval_time_ms=elapsed_ms
        )

    def retrieve_clauses_for_scenario(self, scenario_text: str, top_k: int = 5) -> List[RetrievedEvidence]:
        """Convenience method for multi-agent workflows."""
        query_obj = SearchQuery(query=scenario_text, top_k=top_k)
        search_res = self.search(query_obj)
        return search_res.results
