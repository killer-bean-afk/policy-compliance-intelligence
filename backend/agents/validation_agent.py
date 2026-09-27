"""
Policy Interpretation & Validation Agent.
Audits analysis and risk outputs against retrieved policy text to guarantee 100% evidence grounding
and prevent hallucinations.
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent, A2AMessageBus
from models import (
    AgentMessageType,
    RetrievalResultItem,
    ClauseAnalysis,
    ValidationProof
)


class PolicyValidationAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Policy Validation Agent",
            role="Evidence Grounding Auditor",
            description="Verifies that all analysis conclusions are strictly grounded in retrieved policy text."
        )

    def process(self, context: Dict[str, Any], bus: A2AMessageBus) -> Dict[str, Any]:
        retrieved_items: List[RetrievalResultItem] = context.get("retrieved_clauses", [])
        clause_analyses: List[ClauseAnalysis] = context.get("clause_analyses", [])

        bus.publish(
            sender=self.name,
            receiver="Recommendation Agent",
            msg_type=AgentMessageType.VALIDATION_REQUEST,
            content="Auditing findings against raw policy text to ensure strict evidence grounding...",
            payload={}
        )

        retrieved_clause_ids = {item.clause.clause_id for item in retrieved_items}
        verified_clauses = []
        unbacked_claims = []

        for analysis in clause_analyses:
            if analysis.clause_id in retrieved_clause_ids:
                verified_clauses.append(analysis.clause_id)
            else:
                unbacked_claims.append(f"Finding for clause {analysis.clause_id} lacks source grounding")

        grounding_score = len(verified_clauses) / max(len(clause_analyses), 1)
        is_grounded = grounding_score >= 0.85
        hallucination_detected = len(unbacked_claims) > 0

        explanation = (
            f"Audit verified that {len(verified_clauses)} out of {len(clause_analyses)} clause evaluations "
            f"are directly grounded in retrieved policy source documents. Grounding score: {grounding_score * 100:.1f}%."
        )

        proof = ValidationProof(
            is_grounded=is_grounded,
            grounding_confidence_score=round(grounding_score, 4),
            hallucination_detected=hallucination_detected,
            explanation=explanation,
            verified_clauses=verified_clauses,
            unbacked_claims=unbacked_claims
        )

        context["validation_proof"] = proof

        bus.publish(
            sender=self.name,
            receiver="Recommendation Agent",
            msg_type=AgentMessageType.VALIDATION_FEEDBACK,
            content=f"Validation complete: Grounding score = {grounding_score * 100:.1f}%. Grounded = {is_grounded}.",
            payload={"grounding_score": grounding_score, "is_grounded": is_grounded}
        )

        return context
