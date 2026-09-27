import re
from typing import List, Tuple, Optional
from src.models.schemas import PolicyClause, RetrievedEvidence

class EvidenceCitationEngine:
    """Extracts evidence spans, highlights matching compliance conditions, and constructs formal citations."""

    @staticmethod
    def format_citation(clause: PolicyClause) -> str:
        """Constructs a canonical traceable citation e.g. [POL-KYC-001 §2.1]."""
        return f"[{clause.policy_id} §{clause.section_number}]"

    @classmethod
    def extract_relevant_span(cls, query: str, clause_text: str, max_chars: int = 240) -> Tuple[str, List[str]]:
        """Identifies key matching terms and returns an excerpt focused on the most relevant sentence."""
        # Clean query words
        query_words = set(re.findall(r"\b[A-Za-z]{4,}\b", query.lower()))
        sentences = re.split(r"(?<=[.!?])\s+", clause_text)

        best_sentence = sentences[0]
        max_overlap = -1
        matched_terms = []

        for sent in sentences:
            sent_words = set(re.findall(r"\b[A-Za-z]{4,}\b", sent.lower()))
            overlap = query_words.intersection(sent_words)
            if len(overlap) > max_overlap:
                max_overlap = len(overlap)
                best_sentence = sent
                matched_terms = list(overlap)

        # Fallback if no specific word overlap found
        if not matched_terms:
            matched_terms = [w for w in query_words if w in clause_text.lower()][:4]

        # Truncate if sentence is very long
        if len(best_sentence) > max_chars:
            best_sentence = best_sentence[:max_chars].rsplit(" ", 1)[0] + "..."

        return best_sentence, matched_terms

    @classmethod
    def ground_evidence(
        cls,
        query: str,
        clause: PolicyClause,
        score: float,
        dense_score: float = 0.0,
        sparse_score: float = 0.0
    ) -> RetrievedEvidence:
        """Enriches a retrieved clause with citation and span evidence."""
        citation_tag = cls.format_citation(clause)
        span, matched_terms = cls.extract_relevant_span(query, clause.clause_text)

        return RetrievedEvidence(
            clause=clause,
            score=round(float(score), 4),
            dense_score=round(float(dense_score), 4),
            sparse_score=round(float(sparse_score), 4),
            matched_terms=matched_terms,
            highlight_span=span,
            citation_tag=citation_tag
        )
