import time
import re
from typing import Dict, Any, List
from src.agents.base import BaseComplianceAgent, AgentMessageBus
from src.search.retriever import PolicyEvidenceRetriever
from src.models.schemas import SearchQuery, RetrievedEvidence

class PolicyRetrievalAgent(BaseComplianceAgent):
    """Specialist Agent responsible for query intent decomposition and evidence retrieval."""

    def __init__(self, retriever: PolicyEvidenceRetriever):
        super().__init__(
            agent_id="AGENT-RETRIEVAL-01",
            name="Policy Retrieval Agent",
            role="Knowledge Base & Clause Evidence Discovery",
            description="Decomposes user scenarios into semantic compliance vectors and retrieves authoritative policy clauses."
        )
        self.retriever = retriever

    def execute(self, state: Dict[str, Any], bus: AgentMessageBus) -> Dict[str, Any]:
        t0 = time.time()
        scenario_text = state.get("scenario", "").strip()

        # Step 1: Semantic Intent Analysis
        thought = (
            f"Analyzing business scenario: '{scenario_text[:80]}...'. "
            "Decomposing scenario keywords to identify regulated domains (AML/KYC, Privacy, Security, AI Governance, Financial Conduct, Anti-Bribery, Biomedical). "
            "Formulating hybrid dense-vector and sparse BM25 queries with RRF re-ranking."
        )

        # Detect domain hints from keywords
        kw_lower = scenario_text.lower()
        domain_hints = []
        if any(w in kw_lower for w in ["kyc", "customer onboarding", "pep", "aml", "laundering", "beneficial owner", "sar", "passport", "id verification"]):
            domain_hints.append("Anti-Money Laundering")
        if any(w in kw_lower for w in ["share", "third party", "vendor", "privacy", "gdpr", "personal data", "consent", "dpa", "pii", "cloud provider"]):
            domain_hints.append("Data Privacy & Protection")
        if any(w in kw_lower for w in ["root", "ssh", "admin", "privilege", "mfa", "password", "production access", "bastion", "vulnerability"]):
            domain_hints.append("Information Security")
        if any(w in kw_lower for w in ["ai", "model", "algorithm", "credit scoring", "automated decision", "llm", "gpt", "disparate impact", "bias"]):
            domain_hints.append("AI Governance & Ethics")
        if any(w in kw_lower for w in ["trade", "stock", "shares", "insider", "earnings", "blackout", "securities", "mnpi", "financial results"]):
            domain_hints.append("Securities & Financial Conduct")
        if any(w in kw_lower for w in ["bribe", "gift", "hospitality", "official", "government", "entertainment", "dinner", "fcpa"]):
            domain_hints.append("Anti-Bribery & Corruption")
        if any(w in kw_lower for w in ["patient", "phi", "hipaa", "clinical", "health", "irb", "biomedical", "trial", "hospital"]):
            domain_hints.append("Healthcare & Life Sciences Compliance")

        # Step 2: Retrieve Authoritative Policy Clauses
        search_query = SearchQuery(
            query=scenario_text,
            top_k=state.get("top_k", 6)
        )
        search_result = self.retriever.search(search_query)
        evidence_items = search_result.results

        # Fallback if domain specific clauses weren't top ranked
        if domain_hints and len(evidence_items) < 3:
            for cat in domain_hints:
                cat_results = self.retriever.search(SearchQuery(query=scenario_text, category=cat, top_k=2))
                existing_ids = {e.clause.clause_id for e in evidence_items}
                for ce in cat_results.results:
                    if ce.clause.clause_id not in existing_ids:
                        evidence_items.append(ce)

        elapsed_ms = (time.time() - t0) * 1000
        confidence = 0.94 if len(evidence_items) >= 2 else 0.70

        # Output Summary
        clause_cites = [e.citation_tag for e in evidence_items]
        output_summary = f"Retrieved {len(evidence_items)} policy clauses across {len(set(e.clause.policy_name for e in evidence_items))} policies: {', '.join(clause_cites[:4])}"

        # Record Step Trace
        bus.record_trace(
            agent_name=self.name,
            stage="RETRIEVAL",
            action="Semantic & Lexical Policy Retrieval",
            thought=thought,
            output_summary=output_summary,
            execution_time_ms=elapsed_ms,
            confidence=confidence,
            data={
                "retrieved_count": len(evidence_items),
                "clauses": [
                    {
                        "clause_id": e.clause.clause_id,
                        "citation": e.citation_tag,
                        "policy": e.clause.policy_name,
                        "score": e.score,
                        "highlight": e.highlight_span
                    }
                    for e in evidence_items
                ]
            }
        )

        # Agent Handoff logic
        handoff_reason = (
            f"Routing {len(evidence_items)} retrieved policy clauses to Compliance Analysis Agent for requirement-by-requirement evaluation."
        )

        # Dispatch A2A Message
        bus.send_message(
            sender=self.name,
            receiver="Compliance Analysis Agent",
            stage="RETRIEVAL_COMPLETE",
            content=f"Successfully extracted {len(evidence_items)} candidate policy clauses relevant to scenario.",
            payload={"evidence_count": len(evidence_items), "citations": clause_cites},
            handoff_reason=handoff_reason
        )

        # Update State
        state["retrieved_evidence"] = evidence_items
        state["detected_domains"] = domain_hints
        return state
