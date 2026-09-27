"""
Knowledge Base Engine for Policy Search & Evidence Retrieval.
Implements Task 1 & Task 2:
- Hybrid Search (TF-IDF Vector Cosine Similarity + BM25 Keyword Search + Category Boost)
- Full evidence metadata traceability back to source policy document and section.
"""

import math
import re
from typing import List, Optional, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from models import PolicyClause, RetrievalResultItem
from policy_corpus import get_all_policy_clauses


class BM25Okapi:
    """Lightweight pure-python BM25 ranking algorithm."""

    def __init__(self, corpus: List[List[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.avgdl = sum(len(doc) for doc in corpus) / self.corpus_size if self.corpus_size > 0 else 1.0
        self.corpus = corpus
        self.doc_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}
        self.doc_len: List[int] = []

        self._initialize()

    def _initialize(self):
        df: Dict[str, int] = {}
        for doc in self.corpus:
            self.doc_len.append(len(doc))
            frequencies: Dict[str, int] = {}
            for word in doc:
                frequencies[word] = frequencies.get(word, 0) + 1
            self.doc_freqs.append(frequencies)
            for word in frequencies:
                df[word] = df.get(word, 0) + 1

        for word, freq in df.items():
            # BM25 IDF formula with smoothing
            idf_val = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1)
            self.idf[word] = max(idf_val, 0.01)

    def get_scores(self, query_tokens: List[str]) -> List[float]:
        scores = [0.0] * self.corpus_size
        for token in query_tokens:
            if token not in self.idf:
                continue
            idf = self.idf[token]
            for i, doc_freq in enumerate(self.doc_freqs):
                tf = doc_freq.get(token, 0)
                if tf == 0:
                    continue
                doc_len = self.doc_len[i]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
                scores[i] += idf * (numerator / denominator)
        return scores


def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text."""
    text_clean = re.sub(r"[^\w\s]", " ", text.lower())
    return [word for word in text_clean.split() if len(word) > 1]


class PolicyKnowledgeBase:
    """Searchable Knowledge Base containing policy clauses, requirements, and metadata."""

    def __init__(self):
        self.clauses: List[PolicyClause] = get_all_policy_clauses()
        self.corpus_texts: List[str] = []
        self.tokenized_corpus: List[List[str]] = []

        # Prepare text representations for vector & keyword indexing
        for c in self.clauses:
            full_text = f"{c.clause_id} {c.policy_name} {c.policy_category} {c.applicable_business_area} {c.section_title} {c.clause_text} {' '.join(c.key_keywords)}"
            self.corpus_texts.append(full_text)
            self.tokenized_corpus.append(tokenize(full_text))

        # Build TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words="english"
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus_texts)

        # Build BM25 Index
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None,
        business_area_filter: Optional[str] = None,
        min_score: float = 0.1
    ) -> List[RetrievalResultItem]:
        """
        Executes hybrid semantic search (TF-IDF Cosine Similarity + BM25 Keyword Search + Category Boost).
        Returns top matching PolicyClause objects with relevance score and match reasons.
        """
        if not query.strip():
            return []

        # 1. TF-IDF Cosine Similarity calculation
        query_vec = self.vectorizer.transform([query])
        tfidf_scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        # Normalize TF-IDF scores to [0, 1]
        max_tfidf = np.max(tfidf_scores) if np.max(tfidf_scores) > 0 else 1.0
        norm_tfidf = tfidf_scores / max_tfidf

        # 2. BM25 Score calculation
        query_tokens = tokenize(query)
        bm25_raw_scores = np.array(self.bm25.get_scores(query_tokens))
        max_bm25 = np.max(bm25_raw_scores) if np.max(bm25_raw_scores) > 0 else 1.0
        norm_bm25 = bm25_raw_scores / max_bm25

        # 3. Hybrid Combination & Boosts
        results: List[RetrievalResultItem] = []
        for i, clause in enumerate(self.clauses):
            # Apply Category / Business Area filters
            if category_filter and category_filter.lower() not in clause.policy_category.lower():
                continue
            if business_area_filter and business_area_filter.lower() not in clause.applicable_business_area.lower():
                continue

            v_score = float(norm_tfidf[i])
            k_score = float(norm_bm25[i])

            # Weighted Hybrid Score: 60% Vector Semantic + 40% Keyword Match
            hybrid_score = 0.60 * v_score + 0.40 * k_score

            # Category / Domain exact keyword boost
            category_boost = 0.0
            query_lower = query.lower()
            if clause.policy_category.lower() in query_lower:
                category_boost += 0.15
            if clause.clause_id.lower() in query_lower:
                category_boost += 0.25
            for kw in clause.key_keywords:
                if kw in query_lower:
                    category_boost += 0.05
                    break

            final_score = min(1.0, hybrid_score + category_boost)

            if final_score >= min_score:
                reasons = []
                if v_score > 0.3:
                    reasons.append(f"Semantic similarity match ({v_score:.2f})")
                if k_score > 0.3:
                    reasons.append(f"BM25 Keyword match ({k_score:.2f})")
                if category_boost > 0:
                    reasons.append("Exact policy domain or keyword match boost")
                if not reasons:
                    reasons.append("General textual relevance match")

                results.append(
                    RetrievalResultItem(
                        clause=clause,
                        relevance_score=round(final_score, 4),
                        match_reasons=reasons
                    )
                )

        # Sort descending by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]

    def get_clause_by_id(self, clause_id: str) -> Optional[PolicyClause]:
        """Find a single policy clause by its unique ID."""
        for c in self.clauses:
            if c.clause_id.lower() == clause_id.lower():
                return c
        return None

    def get_all_clauses() -> List[PolicyClause]:
        """Return all clauses in knowledge base."""
        return self.clauses
