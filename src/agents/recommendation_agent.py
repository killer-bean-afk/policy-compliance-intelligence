import time
import uuid
from typing import Dict, Any, List
from datetime import datetime
from src.agents.base import BaseComplianceAgent, AgentMessageBus
from src.models.schemas import (
    RemediationAction,
    ClauseAssessment,
    RiskFactor,
    RiskLevel,
    ComplianceVerdict,
    ComplianceDossier
)

class RecommendationAgent(BaseComplianceAgent):
    """Specialist Agent responsible for synthesizing remediation actions, approval workflows, and executive compliance reports."""

    def __init__(self):
        super().__init__(
            agent_id="AGENT-RECOMMEND-05",
            name="Recommendation Agent",
            role="Policy-Based Remediation & Workflow Synthesis",
            description="Transforms identified compliance gaps and risk factors into actionable operational steps, sign-off checklists, and audit dossiers."
        )

    def execute(self, state: Dict[str, Any], bus: AgentMessageBus) -> Dict[str, Any]:
        t0 = time.time()
        scenario_text = state.get("scenario", "")
        clause_assessments: List[ClauseAssessment] = state.get("clause_assessments", [])
        risk_factors: List[RiskFactor] = state.get("risk_factors", [])
        identified_gaps: List[str] = state.get("identified_gaps", [])
        risk_score: float = state.get("risk_score", 15.0)
        risk_level: RiskLevel = state.get("risk_level", RiskLevel.LOW)
        preliminary_verdict: ComplianceVerdict = state.get("preliminary_verdict", ComplianceVerdict.COMPLIANT)
        validation = state.get("validation")

        thought = (
            f"Synthesizing structured remediation plan based on {len(identified_gaps)} compliance gaps and certified evidentiary validation. "
            "Formulating approval matrices, operational checklists, stakeholder responsibilities, and executive compliance summary."
        )

        recommendations: List[RemediationAction] = []
        action_idx = 1

        for assessment in clause_assessments:
            cid = assessment.clause_id

            if assessment.verdict == ComplianceVerdict.NON_COMPLIANT:
                if "POL-PRV-002-C02" in cid or "POL-PRV" in cid:
                    recommendations.append(RemediationAction(
                        action_id=f"REM-{action_idx:02d}",
                        title="Execute Bilateral Data Processing Agreement (DPA)",
                        description="Halt personal data transmissions until a counter-signed DPA incorporating EU Standard Contractual Clauses (SCCs) and audit rights is finalized.",
                        responsible_party="Data Protection Officer (DPO) & Legal Counsel",
                        approval_required="DPO and Head of Procurement",
                        priority=RiskLevel.CRITICAL,
                        deadline_days=3,
                        policy_reference=assessment.citation
                    ))
                    action_idx += 1

                elif "POL-PRV-002-C04" in cid:
                    recommendations.append(RemediationAction(
                        action_id=f"REM-{action_idx:02d}",
                        title="Enforce Strong Cryptography (TLS 1.3 & AES-256)",
                        description="Mandate TLS 1.3 encryption on all public API endpoints and verify that backend database volumes enforce AES-256 at-rest encryption.",
                        responsible_party="Lead Security Architect & Infrastructure DevOps",
                        approval_required="Chief Information Security Officer (CISO)",
                        priority=RiskLevel.HIGH,
                        deadline_days=5,
                        policy_reference=assessment.citation
                    ))
                    action_idx += 1

                elif "POL-KYC-001-C01" in cid:
                    recommendations.append(RemediationAction(
                        action_id=f"REM-{action_idx:02d}",
                        title="Obtain Secondary Verified Identity & Address Proof",
                        description="Require the customer to provide a secondary unexpired government photo ID and utility bill dated within 90 days before unlocking account services.",
                        responsible_party="Onboarding Operations Lead",
                        approval_required="AML Compliance Supervisor",
                        priority=RiskLevel.HIGH,
                        deadline_days=2,
                        policy_reference=assessment.citation
                    ))
                    action_idx += 1

                elif "POL-KYC-001-C02" in cid:
                    recommendations.append(RemediationAction(
                        action_id=f"REM-{action_idx:02d}",
                        title="Escalate PEP Match to Head of Financial Crime",
                        description="Place immediate operational freeze on the account and submit full customer profile dossier for executive PEP sign-off.",
                        responsible_party="Financial Crime Compliance Analyst",
                        approval_required="Head of Financial Crime & Chief Compliance Officer",
                        priority=RiskLevel.CRITICAL,
                        deadline_days=1,
                        policy_reference=assessment.citation
                    ))
                    action_idx += 1

                elif "POL-KYC-001-C04" in cid:
                    recommendations.append(RemediationAction(
                        action_id=f"REM-{action_idx:02d}",
                        title="Conduct Ultimate Beneficial Ownership (25% UBO) Audit",
                        description="Issue formal demand for corporate capitalization table and notarized register of members to confirm natural persons with >=25% equity.",
                        responsible_party="Senior KYC Corporate Analyst",
                        approval_required="Compliance Operations Manager",
                        priority=RiskLevel.HIGH,
                        deadline_days=5,
                        policy_reference=assessment.citation
                    ))
                    action_idx += 1

                elif "POL-SEC-003-C01" in cid or "POL-SEC-003-C03" in cid:
                    recommendations.append(RemediationAction(
                        action_id=f"REM-{action_idx:02d}",
                        title="Revoke Standing Root Access & Implement JIT Bastion Elevation",
                        description="Deprovision permanent administrator credentials. Route all production operations through Privileged Access Management bastion with dual-manager approval.",
                        responsible_party="Cloud Infrastructure Security Team",
                        approval_required="Chief Information Security Officer (CISO)",
                        priority=RiskLevel.CRITICAL,
                        deadline_days=1,
                        policy_reference=assessment.citation
                    ))
                    action_idx += 1

                elif "POL-GOV-004" in cid:
                    recommendations.append(RemediationAction(
                        action_id=f"REM-{action_idx:02d}",
                        title="Suspend Model Deployment & Retrain for Algorithmic Fairness",
                        description="Suspend production inference until disparate impact ratio is remediated to >= 0.80 and Human-in-the-Loop review protocols are documented.",
                        responsible_party="Head of AI Research & Lead Data Scientist",
                        approval_required="Model Risk Committee (MRC) Chair",
                        priority=RiskLevel.CRITICAL,
                        deadline_days=7,
                        policy_reference=assessment.citation
                    ))
                    action_idx += 1

                elif "POL-FIN-005" in cid:
                    recommendations.append(RemediationAction(
                        action_id=f"REM-{action_idx:02d}",
                        title="Enforce Securities Trading Blackout & Cancel Pending Orders",
                        description="Instruct brokerage desk to reject trade order immediately. File formal incident record regarding blackout period inquiry with General Counsel.",
                        responsible_party="Associate General Counsel for Securities",
                        approval_required="General Counsel",
                        priority=RiskLevel.CRITICAL,
                        deadline_days=1,
                        policy_reference=assessment.citation
                    ))
                    action_idx += 1

                elif "POL-BIO-007" in cid:
                    recommendations.append(RemediationAction(
                        action_id=f"REM-{action_idx:02d}",
                        title="Execute HIPAA Safe Harbor De-Identification & Cloud BAA",
                        description="Scrub 18 HIPAA identifiers from clinical abstract dataset and execute standard Business Associate Agreement prior to cloud processing.",
                        responsible_party="Clinical Data Steward & Health Privacy Officer",
                        approval_required="Institutional Review Board (IRB) Chair & Health Privacy Officer",
                        priority=RiskLevel.CRITICAL,
                        deadline_days=3,
                        policy_reference=assessment.citation
                    ))
                    action_idx += 1

                else:
                    recommendations.append(RemediationAction(
                        action_id=f"REM-{action_idx:02d}",
                        title=f"Rectify Policy Deficiency in {assessment.section}",
                        description=f"Align operational procedure with mandatory clause criteria: {assessment.clause_text[:120]}...",
                        responsible_party="Operational Process Owner",
                        approval_required="Department Compliance Lead",
                        priority=RiskLevel.MEDIUM,
                        deadline_days=10,
                        policy_reference=assessment.citation
                    ))
                    action_idx += 1

            elif assessment.verdict == ComplianceVerdict.CONDITIONAL:
                recommendations.append(RemediationAction(
                    action_id=f"REM-{action_idx:02d}",
                    title=f"Complete Procedural Prerequisite: {assessment.section}",
                    description=f"Obtain formal sign-off and log documentation according to {assessment.citation} before finalizing transaction.",
                    responsible_party="Initiating Business Unit Lead",
                    approval_required="Designated Compliance Officer",
                    priority=RiskLevel.LOW,
                    deadline_days=14,
                    policy_reference=assessment.citation
                ))
                action_idx += 1

        # Fallback if scenario was already compliant
        if not recommendations:
            recommendations.append(RemediationAction(
                action_id="REM-01",
                title="Maintain Ongoing Compliance Monitoring & Audit Logging",
                description="Scenario satisfies primary policy criteria. Ensure standard operational audit logging and periodic review are maintained.",
                responsible_party="Business Unit Lead",
                approval_required="Standard Line Manager",
                priority=RiskLevel.LOW,
                deadline_days=30,
                policy_reference="[POL-SEC-003 §4.2]"
            ))

        # Executive Summary Generation
        policies_involved = list(set(a.policy_name for a in clause_assessments))
        if preliminary_verdict == ComplianceVerdict.NON_COMPLIANT:
            summary = (
                f"NON-COMPLIANT: The proposed business activity or scenario violates {len([a for a in clause_assessments if a.verdict == ComplianceVerdict.NON_COMPLIANT])} "
                f"binding requirements across {len(policies_involved)} organizational policies. "
                f"Overall Compliance Risk Score is calibrated at {risk_score}/100 ({risk_level.value}). "
                f"Key deficiencies include: {'; '.join(identified_gaps[:2])}. "
                f"Remediation requires immediate execution of {len(recommendations)} mandatory corrective actions prior to proceeding."
            )
        elif preliminary_verdict == ComplianceVerdict.CONDITIONAL:
            summary = (
                f"CONDITIONAL APPROVAL: The proposed activity does not explicitly violate policy prohibitions but requires completion of "
                f"{len(recommendations)} procedural prerequisites and approvals across {len(policies_involved)} policies. "
                f"Risk score is estimated at {risk_score}/100 ({risk_level.value}). Formal approval must be logged before full execution."
            )
        else:
            summary = (
                f"COMPLIANT: The submitted scenario complies with the applicable policy requirements across {len(policies_involved)} evaluated directives. "
                f"Residual operational risk score is {risk_score}/100 ({risk_level.value}). Standard procedural safeguards apply."
            )

        elapsed_ms = (time.time() - t0) * 1000
        output_summary = f"Synthesized executive compliance report with verdict '{preliminary_verdict.value}' and {len(recommendations)} actionable recommendations."

        bus.record_trace(
            agent_name=self.name,
            stage="RECOMMENDATION",
            action="Remediation Synthesis & Report Finalization",
            thought=thought,
            output_summary=output_summary,
            execution_time_ms=elapsed_ms,
            confidence=0.96,
            data={
                "verdict": preliminary_verdict.value,
                "recommendation_count": len(recommendations),
                "summary": summary
            }
        )

        bus.send_message(
            sender=self.name,
            receiver="Compliance Workflow Orchestrator",
            stage="WORKFLOW_COMPLETE",
            content="Final compliance dossier generated with traceable recommendations and executive summary.",
            payload={"recommendation_count": len(recommendations), "verdict": preliminary_verdict.value},
            handoff_reason="Finalizing compliance assessment and returning complete dossier to requesting user."
        )

        # Assemble full dossier
        dossier = ComplianceDossier(
            analysis_id=f"CMP-{uuid.uuid4().hex[:8].upper()}",
            scenario=scenario_text,
            verdict=preliminary_verdict,
            overall_confidence=0.94 if validation and validation.is_valid else 0.78,
            risk_score=risk_score,
            risk_level=risk_level,
            executive_summary=summary,
            applicable_policies=policies_involved,
            clause_assessments=clause_assessments,
            identified_gaps=identified_gaps,
            risk_factors=risk_factors,
            recommendations=recommendations,
            agent_trace=bus.get_traces(),
            a2a_messages=bus.get_messages(),
            validation=validation,
            created_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"),
            processing_time_ms=round(sum(t.execution_time_ms for t in bus.get_traces()), 2)
        )

        state["dossier"] = dossier
        return state
