"""
Recommendation Agent.
Formulates actionable remediation steps, required sign-offs, mandatory documentation,
and system workflow handoffs.
"""

import uuid
from typing import Dict, Any, List
from agents.base_agent import BaseAgent, A2AMessageBus
from models import (
    AgentMessageType,
    ClauseAnalysis,
    RiskItem,
    RemediationAction,
    ComplianceStatus,
    RiskSeverity
)


class RecommendationAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Recommendation Agent",
            role="Remediation & Action Advisor",
            description="Generates step-by-step remediation plans, required approvals, and workflow handoffs."
        )

    def process(self, context: Dict[str, Any], bus: A2AMessageBus) -> Dict[str, Any]:
        clause_analyses: List[ClauseAnalysis] = context.get("clause_analyses", [])
        risk_items: List[RiskItem] = context.get("risk_assessment", [])
        overall_risk: RiskSeverity = context.get("overall_risk_level", RiskSeverity.LOW)

        bus.publish(
            sender=self.name,
            receiver="User Application",
            msg_type=AgentMessageType.RECOMMENDATION_OUTPUT,
            content="Synthesizing actionable remediation recommendations and required approval workflows...",
            payload={}
        )

        remediations: List[RemediationAction] = []

        # Analyze clauses to generate specific remediation steps
        for analysis in clause_analyses:
            cid = analysis.clause_id

            if analysis.status in [ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT]:

                if "KYC" in cid:
                    remediations.append(
                        RemediationAction(
                            action_id=f"ACT-{uuid.uuid4().hex[:6].upper()}",
                            priority="Immediate" if overall_risk == RiskSeverity.CRITICAL else "High",
                            title="Execute Enhanced Due Diligence (EDD) & Obtain MLRO Sign-Off",
                            description="Immediately halt account activation or transaction processing. Collect documented Source of Wealth (SOW), Source of Funds (SOF), and submit formal EDD dossier to MLRO for written approval.",
                            responsible_party="KYC / Onboarding Operations Team",
                            required_approvals=["Money Laundering Reporting Officer (MLRO)", "Head of Financial Crime"],
                            prerequisite_documents=["Government Photo ID", "Proof of Address (<90 days)", "Documented Source of Wealth", "EDD Risk Assessment Form"],
                            workflow_handoff="Handoff to FinCrime EDD Workflow Queue (#AML-EDD-802)"
                        )
                    )

                elif "HIPAA" in cid:
                    remediations.append(
                        RemediationAction(
                            action_id=f"ACT-{uuid.uuid4().hex[:6].upper()}",
                            priority="Immediate",
                            title="Execute Business Associate Agreement (BAA) & Enable PHI Encryption",
                            description="Suspend all PHI data transmission to vendor/SaaS platform immediately. Execute standard corporate BAA containing 72-hour breach notice clause and AI model training prohibition. Verify AES-256 / TLS 1.3 encryption.",
                            responsible_party="Healthcare Privacy Officer & Legal Counsel",
                            required_approvals=["Chief Privacy Officer", "Corporate Legal Counsel"],
                            prerequisite_documents=["Standard Corporate Business Associate Agreement (BAA)", "SOC 2 Type II Security Certification"],
                            workflow_handoff="Handoff to Vendor Legal & Privacy Risk Queue (#PRIV-BAA-404)"
                        )
                    )

                elif "SEC" in cid:
                    remediations.append(
                        RemediationAction(
                            action_id=f"ACT-{uuid.uuid4().hex[:6].upper()}",
                            priority="High",
                            title="Conduct Third-Party InfoSec Risk Review & Implement Enterprise AI Isolation",
                            description="Perform mandatory InfoSec vendor risk assessment. Verify SOC 2 Type II compliance. For AI integrations, migrate usage from public models to enterprise-managed isolated tenant with DLP controls.",
                            responsible_party="Information Security & IT Governance Team",
                            required_approvals=["Chief Information Security Officer (CISO)", "Head of IT Risk"],
                            prerequisite_documents=["Vendor SOC 2 Type II Report", "ISO 27001 Certificate", "InfoSec Assessment Questionnaire"],
                            workflow_handoff="Handoff to CISO Security Governance Queue (#SEC-REV-109)"
                        )
                    )

                elif "GOV" in cid:
                    remediations.append(
                        RemediationAction(
                            action_id=f"ACT-{uuid.uuid4().hex[:6].upper()}",
                            priority="High",
                            title="Submit Ethics & FCPA Compliance Pre-Clearance Request",
                            description="Cancel unapproved hospitality/gift or submit formal pre-clearance request with justification. Confirm zero value provided to foreign government officials.",
                            responsible_party="Business Relationship Manager",
                            required_approvals=["Ethics & Compliance Officer", "General Counsel"],
                            prerequisite_documents=["Ethics Pre-Clearance Request Form", "Itemized Expenditure Receipt"],
                            workflow_handoff="Handoff to Ethics & Compliance Board Queue (#ETHICS-FCPA-301)"
                        )
                    )

                elif "FIN" in cid:
                    remediations.append(
                        RemediationAction(
                            action_id=f"ACT-{uuid.uuid4().hex[:6].upper()}",
                            priority="Immediate",
                            title="Perform Real-Time OFAC Screening & Obtain Dual Treasury Approval",
                            description="Pass beneficiary details through OFAC SDN real-time screening engine. For transfers >$100k, obtain dual Treasury Officer authorization; for >$1M, secure CFO sign-off before wire release.",
                            responsible_party="Treasury & Payment Operations",
                            required_approvals=["Treasury Director", "Chief Financial Officer (CFO)"],
                            prerequisite_documents=["OFAC Screening Audit Log", "Dual Authorization Transfer Ticket"],
                            workflow_handoff="Handoff to Treasury Wire Approval Queue (#WIRE-TREAS-505)"
                        )
                    )

        # Fallback if compliant
        if not remediations:
            remediations.append(
                RemediationAction(
                    action_id=f"ACT-{uuid.uuid4().hex[:6].upper()}",
                    priority="Low",
                    title="Proceed with Operational Standard Operating Procedure",
                    description="Proposed activity complies with all evaluated policy requirements. Maintain standard audit logging.",
                    responsible_party="Business Unit Lead",
                    required_approvals=["Standard Business Unit Supervisor"],
                    prerequisite_documents=["Standard Operating Audit Log"],
                    workflow_handoff="Standard Operational Workflow"
                )
            )

        context["remediation_actions"] = remediations

        bus.publish(
            sender=self.name,
            receiver="User Application",
            msg_type=AgentMessageType.RECOMMENDATION_OUTPUT,
            content=f"Generated {len(remediations)} targeted remediation action steps with approval workflows.",
            payload={"remediation_count": len(remediations)}
        )

        return context
