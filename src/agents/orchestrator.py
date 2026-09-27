import time
from typing import Dict, Any, Generator, Optional
from src.agents.base import AgentMessageBus
from src.agents.retrieval_agent import PolicyRetrievalAgent
from src.agents.analysis_agent import ComplianceAnalysisAgent
from src.agents.risk_agent import RiskAssessmentAgent
from src.agents.validation_agent import PolicyInterpretationValidationAgent
from src.agents.recommendation_agent import RecommendationAgent
from src.search.retriever import PolicyEvidenceRetriever
from src.models.schemas import ComplianceRequest, ComplianceDossier

class ComplianceWorkflowOrchestrator:
    """Coordinates the end-to-end Multi-Agent Compliance Workflow with dynamic handoffs and state persistence."""

    def __init__(self, retriever: Optional[PolicyEvidenceRetriever] = None):
        self.retriever = retriever or PolicyEvidenceRetriever()
        self.retrieval_agent = PolicyRetrievalAgent(self.retriever)
        self.analysis_agent = ComplianceAnalysisAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.validation_agent = PolicyInterpretationValidationAgent()
        self.recommendation_agent = RecommendationAgent()

    def run_workflow(self, request: ComplianceRequest) -> ComplianceDossier:
        """Executes the complete multi-agent pipeline synchronously."""
        bus = AgentMessageBus()
        state: Dict[str, Any] = {
            "scenario": request.scenario,
            "category_hint": request.category_hint,
            "business_area_hint": request.business_area_hint,
            "strict_validation": request.strict_validation
        }

        # Step 1: Retrieval Agent
        state = self.retrieval_agent.execute(state, bus)

        # Step 2: Compliance Analysis Agent
        state = self.analysis_agent.execute(state, bus)

        # Step 3: Risk Assessment Agent
        state = self.risk_agent.execute(state, bus)

        # Step 4: Policy Interpretation & Validation Agent
        state = self.validation_agent.execute(state, bus)

        # Step 5: Recommendation Agent
        state = self.recommendation_agent.execute(state, bus)

        dossier: ComplianceDossier = state["dossier"]
        return dossier

    def stream_workflow(self, request: ComplianceRequest) -> Generator[Dict[str, Any], None, ComplianceDossier]:
        """Generator that yields progress and step traces for real-time frontend streaming."""
        bus = AgentMessageBus()
        state: Dict[str, Any] = {
            "scenario": request.scenario,
            "category_hint": request.category_hint,
            "business_area_hint": request.business_area_hint,
            "strict_validation": request.strict_validation
        }

        agents = [
            ("RETRIEVAL", self.retrieval_agent),
            ("ANALYSIS", self.analysis_agent),
            ("RISK_ASSESSMENT", self.risk_agent),
            ("VALIDATION", self.validation_agent),
            ("RECOMMENDATION", self.recommendation_agent),
        ]

        for stage_name, agent in agents:
            yield {
                "event": "agent_start",
                "agent_name": agent.name,
                "stage": stage_name,
                "role": agent.role
            }

            state = agent.execute(state, bus)
            latest_trace = bus.get_traces()[-1]
            latest_msg = bus.get_messages()[-1]

            yield {
                "event": "agent_complete",
                "agent_name": agent.name,
                "stage": stage_name,
                "trace": latest_trace.model_dump(),
                "handoff": {
                    "sender": latest_msg.sender,
                    "receiver": latest_msg.receiver,
                    "reason": latest_msg.handoff_reason
                }
            }

        dossier: ComplianceDossier = state["dossier"]
        yield {
            "event": "workflow_finished",
            "dossier": dossier.model_dump()
        }
        return dossier
