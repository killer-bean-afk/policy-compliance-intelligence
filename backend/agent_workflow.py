"""
Multi-Agent Compliance Workflow Supervisor.
Coordinates execution of Policy Retrieval -> Compliance Analysis -> Risk Assessment -> Validation -> Recommendation agents.
Builds Agent-to-Agent (A2A) execution trace and Evidence Traceability Matrix.
"""

import time
import uuid
from typing import Dict, Any, List

from models import (
    ScenarioRequest,
    ComplianceResponse,
    ComplianceStatus,
    RiskSeverity,
    EvidenceTraceability
)
from knowledge_base import PolicyKnowledgeBase
from agents import (
    A2AMessageBus,
    PolicyRetrievalAgent,
    ComplianceAnalysisAgent,
    RiskAssessmentAgent,
    PolicyValidationAgent,
    RecommendationAgent
)


class MultiAgentComplianceWorkflow:
    """Supervises end-to-end multi-agent policy compliance lifecycle."""

    def __init__(self, kb: PolicyKnowledgeBase):
        self.kb = kb
        self.retrieval_agent = PolicyRetrievalAgent(self.kb)
        self.analysis_agent = ComplianceAnalysisAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.validation_agent = PolicyValidationAgent()
        self.recommendation_agent = RecommendationAgent()

    def run_workflow(self, request: ScenarioRequest) -> ComplianceResponse:
        start_time = time.time()
        bus = A2AMessageBus()

        scenario_id = request.scenario_id or f"SCN-{uuid.uuid4().hex[:8].upper()}"

        # Initialize workflow context
        context: Dict[str, Any] = {
            "scenario_id": scenario_id,
            "scenario_text": request.scenario_text,
            "policy_category": request.policy_category,
            "business_area": request.business_area,
            "user_role": request.user_role
        }

        # Step 1: Policy Retrieval Agent
        context = self.retrieval_agent.process(context, bus)

        # Step 2: Compliance Analysis Agent
        context = self.analysis_agent.process(context, bus)

        # Step 3: Risk Assessment Agent (Agent Handoff based on analysis findings)
        context = self.risk_agent.process(context, bus)

        # Step 4: Policy Interpretation & Validation Agent
        context = self.validation_agent.process(context, bus)

        # Step 5: Recommendation Agent
        context = self.recommendation_agent.process(context, bus)

        # Determine Overall Compliance Status
        clause_analyses = context.get("clause_analyses", [])
        statuses = [a.status for a in clause_analyses]
        if ComplianceStatus.NON_COMPLIANT in statuses:
            overall_status = ComplianceStatus.NON_COMPLIANT
        elif ComplianceStatus.PARTIALLY_COMPLIANT in statuses:
            overall_status = ComplianceStatus.PARTIALLY_COMPLIANT
        elif ComplianceStatus.NEEDS_INFORMATION in statuses:
            overall_status = ComplianceStatus.NEEDS_INFORMATION
        else:
            overall_status = ComplianceStatus.COMPLIANT

        overall_risk = context.get("overall_risk_level", RiskSeverity.LOW)

        # Formulate Executive Summary
        non_comp_count = sum(1 for s in statuses if s == ComplianceStatus.NON_COMPLIANT)
        total_clauses = len(clause_analyses)

        exec_summary = (
            f"Evaluated scenario against {total_clauses} relevant policy clause(s). "
            f"Overall Status: {overall_status.value} (Risk Level: {overall_risk.value}). "
            f"Identified {non_comp_count} policy violation(s) and {len(context.get('risk_assessment', []))} risk item(s). "
            f"Evidence grounding audit confirmed {context.get('validation_proof').grounding_confidence_score * 100:.0f}% policy backing."
        )

        # Build Evidence Traceability Matrix
        evidence_matrix: List[EvidenceTraceability] = []
        risk_items = context.get("risk_assessment", [])
        for analysis in clause_analyses:
            linked_risk = None
            for r in risk_items:
                if analysis.clause_id in r.affected_clause_ids:
                    linked_risk = r.risk_id
                    break

            evidence_matrix.append(
                EvidenceTraceability(
                    clause_id=analysis.clause_id,
                    policy_name=analysis.policy_name,
                    section=analysis.section_number,
                    clause_text=analysis.evidence_quote,
                    finding=analysis.findings,
                    compliance_status=analysis.status,
                    linked_risk_id=linked_risk
                )
            )

        execution_time_ms = round((time.time() - start_time) * 1000, 2)

        return ComplianceResponse(
            scenario_id=scenario_id,
            scenario_text=request.scenario_text,
            overall_compliance_status=overall_status,
            overall_risk_level=overall_risk,
            executive_summary=exec_summary,
            retrieved_clauses=context.get("retrieved_clauses", []),
            clause_analyses=clause_analyses,
            risk_assessment=risk_items,
            validation_proof=context.get("validation_proof"),
            remediation_actions=context.get("remediation_actions", []),
            evidence_matrix=evidence_matrix,
            agent_execution_trace=bus.get_history() if request.include_agent_trace else [],
            execution_time_ms=execution_time_ms
        )
