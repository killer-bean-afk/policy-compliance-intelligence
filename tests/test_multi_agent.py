import pytest
from src.agents.orchestrator import ComplianceWorkflowOrchestrator
from src.models.schemas import ComplianceRequest, ComplianceVerdict, RiskLevel

def test_multi_agent_workflow_non_compliant():
    orchestrator = ComplianceWorkflowOrchestrator()
    req = ComplianceRequest(
        scenario="Our product team plans to share European customer personal data with a US third party vendor without a Data Processing Agreement (DPA) over unencrypted HTTP."
    )
    dossier = orchestrator.run_workflow(req)

    assert dossier.verdict == ComplianceVerdict.NON_COMPLIANT
    assert dossier.risk_score >= 60.0
    assert dossier.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
    assert len(dossier.identified_gaps) > 0
    assert len(dossier.recommendations) > 0
    assert len(dossier.agent_trace) == 5
    assert len(dossier.a2a_messages) >= 4
    assert dossier.validation.is_valid is True
    assert dossier.validation.grounding_faithfulness_score >= 0.90

def test_multi_agent_workflow_compliant():
    orchestrator = ComplianceWorkflowOrchestrator()
    req = ComplianceRequest(
        scenario="The customer support team verified two government photographic IDs and a utility bill dated 25 days ago. Full beneficial ownership registers were verified."
    )
    dossier = orchestrator.run_workflow(req)

    assert dossier.verdict == ComplianceVerdict.COMPLIANT
    assert dossier.risk_score < 40.0
    assert dossier.risk_level == RiskLevel.LOW
