"""
Policy Retrieval Agent.
Retrieves applicable policy clauses from Knowledge Base based on natural language query,
business area, and policy category filters.
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent, A2AMessageBus
from knowledge_base import PolicyKnowledgeBase
from models import AgentMessageType, RetrievalResultItem


class PolicyRetrievalAgent(BaseAgent):

    def __init__(self, kb: PolicyKnowledgeBase):
        super().__init__(
            name="Policy Retrieval Agent",
            role="Knowledge Retrieval Specialist",
            description="Searches Knowledge Base for applicable policy clauses and grounds evidence."
        )
        self.kb = kb

    def process(self, context: Dict[str, Any], bus: A2AMessageBus) -> Dict[str, Any]:
        scenario_text = context.get("scenario_text", "")
        category_filter = context.get("policy_category")
        business_area_filter = context.get("business_area")

        bus.publish(
            sender=self.name,
            receiver="Compliance Analysis Agent",
            msg_type=AgentMessageType.RETRIEVAL_QUERY,
            content=f"Searching policy knowledge base for scenario: '{scenario_text[:80]}...'",
            payload={"category": category_filter, "business_area": business_area_filter}
        )

        # Retrieve top 5 matching policy clauses
        retrieved_items: List[RetrievalResultItem] = self.kb.search(
            query=scenario_text,
            top_k=5,
            category_filter=category_filter,
            business_area_filter=business_area_filter,
            min_score=0.05
        )

        # Fallback broad search if filters returned 0 results
        if not retrieved_items and (category_filter or business_area_filter):
            retrieved_items = self.kb.search(
                query=scenario_text,
                top_k=5,
                min_score=0.03
            )

        # Filter low relevance noise if top match is strong (> 0.5)
        if retrieved_items and retrieved_items[0].relevance_score > 0.4:
            top_score = retrieved_items[0].relevance_score
            retrieved_items = [r for r in retrieved_items if r.relevance_score >= 0.3 * top_score]

        context["retrieved_clauses"] = retrieved_items

        clauses_summary = ", ".join([item.clause.clause_id for item in retrieved_items]) if retrieved_items else "None"
        bus.publish(
            sender=self.name,
            receiver="Compliance Analysis Agent",
            msg_type=AgentMessageType.RETRIEVAL_RESULT,
            content=f"Retrieved {len(retrieved_items)} relevant policy clauses ({clauses_summary}) with metadata evidence.",
            payload={"count": len(retrieved_items), "clause_ids": [item.clause.clause_id for item in retrieved_items]}
        )

        return context
