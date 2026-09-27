"""
Risk Assessment Agent.
Evaluates compliance severity, potential financial fines, regulatory penalties,
reputational damage, and identifies operational gaps.
"""

import uuid
from typing import Dict, Any, List
from agents.base_agent import BaseAgent, A2AMessageBus
from models import (
    AgentMessageType,
    ClauseAnalysis,
    RiskItem,
    RiskSeverity,
    ComplianceStatus
)


class RiskAssessmentAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Risk Assessment Agent",
            role="Risk & Gap Identification Specialist",
            description="Quantifies compliance risks, potential regulatory fines, and identifies policy gaps."
        )

    def process(self, context: Dict[str, Any], bus: A2AMessageBus) -> Dict[str, Any]:
        clause_analyses: List[ClauseAnalysis] = context.get("clause_analyses", [])
        risk_items: List[RiskItem] = []

        bus.publish(
            sender=self.name,
            receiver="Policy Validation Agent",
            msg_type=AgentMessageType.RISK_EVALUATION,
            content="Evaluating compliance risks and regulatory penalty exposure...",
            payload={}
        )

        critical_flags = 0
        high_flags = 0
        medium_flags = 0

        for analysis in clause_analyses:
            if analysis.status == ComplianceStatus.NON_COMPLIANT:
                cid = analysis.clause_id

                # Determine Risk Profile based on Clause Domain
                if "HIPAA" in cid:
                    critical_flags += 1
                    risk_items.append(
                        RiskItem(
                            risk_id=f"RISK-{uuid.uuid4().hex[:6].upper()}",
                            severity=RiskSeverity.CRITICAL,
                            risk_category="Regulatory & Privacy Law Violation",
                            title="HIPAA PHI Data Disclosure Risk",
                            description=f"Unlawful sharing or processing of Protected Health Information (PHI) without a BAA violates 45 CFR § 164.502. Finding: {analysis.findings}",
                            potential_penalty="HHS Civil Monetary Penalties up to $1,919,173 per calendar year; potential criminal prosecution under HIPAA Privacy Rule.",
                            affected_clause_ids=[cid]
                        )
                    )

                elif "KYC" in cid:
                    critical_flags += 1
                    risk_items.append(
                        RiskItem(
                            risk_id=f"RISK-{uuid.uuid4().hex[:6].upper()}",
                            severity=RiskSeverity.CRITICAL,
                            risk_category="Anti-Money Laundering (AML) Compliance Gap",
                            title="Unverified PEP / High-Risk Account Exposure",
                            description=f"Onboarding or processing transactions for PEPs without EDD and MLRO sign-off creates severe AML vulnerability. Finding: {analysis.findings}",
                            potential_penalty="FinCEN / OCC enforcement actions, deferred prosecution agreements, and multi-million dollar regulatory fines.",
                            affected_clause_ids=[cid]
                        )
                    )

                elif "FIN" in cid:
                    critical_flags += 1
                    risk_items.append(
                        RiskItem(
                            risk_id=f"RISK-{uuid.uuid4().hex[:6].upper()}",
                            severity=RiskSeverity.CRITICAL,
                            risk_category="OFAC Sanctions & Wire Transfer Violation",
                            title="Sanctions Non-Compliance & Unapproved Transfer Risk",
                            description=f"Bypassing OFAC SDN screening or dual Treasury authorization exposes organization to illicit funds transfer. Finding: {analysis.findings}",
                            potential_penalty="OFAC civil monetary penalties up to $356,579 per transaction; asset freezing orders.",
                            affected_clause_ids=[cid]
                        )
                    )

                elif "GOV" in cid:
                    high_flags += 1
                    risk_items.append(
                        RiskItem(
                            risk_id=f"RISK-{uuid.uuid4().hex[:6].upper()}",
                            severity=RiskSeverity.HIGH,
                            risk_category="Anti-Bribery & FCPA Risk",
                            title="FCPA Foreign Official / Excess Gift Violation",
                            description=f"Providing value to government officials or unapproved gifts breaks FCPA compliance rules. Finding: {analysis.findings}",
                            potential_penalty="DOJ / SEC FCPA enforcement, corporate disgorgement, and reputational blacklist.",
                            affected_clause_ids=[cid]
                        )
                    )

                elif "SEC" in cid:
                    high_flags += 1
                    risk_items.append(
                        RiskItem(
                            risk_id=f"RISK-{uuid.uuid4().hex[:6].upper()}",
                            severity=RiskSeverity.HIGH,
                            risk_category="Information Security & Vendor Risk",
                            title="Uncontrolled Data Leak / Public AI Exposure",
                            description=f"Exposing company code or confidential assets to public AI tools breaks InfoSec policy. Finding: {analysis.findings}",
                            potential_penalty="Trade secret invalidation, breach notification obligations, customer contract breach damages.",
                            affected_clause_ids=[cid]
                        )
                    )

                else:
                    medium_flags += 1
                    risk_items.append(
                        RiskItem(
                            risk_id=f"RISK-{uuid.uuid4().hex[:6].upper()}",
                            severity=RiskSeverity.MEDIUM,
                            risk_category="Operational Policy Gap",
                            title=f"Non-Compliance with Policy Clause {cid}",
                            description=f"General policy deviation detected. Finding: {analysis.findings}",
                            potential_penalty="Internal compliance corrective action, audit finding, operational delay.",
                            affected_clause_ids=[cid]
                        )
                    )

            elif analysis.status == ComplianceStatus.PARTIALLY_COMPLIANT:
                medium_flags += 1
                risk_items.append(
                    RiskItem(
                        risk_id=f"RISK-{uuid.uuid4().hex[:6].upper()}",
                        severity=RiskSeverity.MEDIUM,
                        risk_category="Procedural Documentation Gap",
                        title=f"Incomplete Approval / Documentation for Clause {analysis.clause_id}",
                        description=f"Partial requirement fulfillment. Finding: {analysis.findings}",
                        potential_penalty="Audit non-conformity notice; delay in business approval.",
                        affected_clause_ids=[analysis.clause_id]
                    )
                )

        # Calculate Overall Risk Level
        if critical_flags > 0:
            overall_risk = RiskSeverity.CRITICAL
        elif high_flags > 0:
            overall_risk = RiskSeverity.HIGH
        elif medium_flags > 0:
            overall_risk = RiskSeverity.MEDIUM
        else:
            overall_risk = RiskSeverity.LOW

        context["risk_assessment"] = risk_items
        context["overall_risk_level"] = overall_risk

        bus.publish(
            sender=self.name,
            receiver="Policy Validation Agent",
            msg_type=AgentMessageType.RISK_EVALUATION,
            content=f"Risk assessment finalized: Overall Risk = {overall_risk.value}. Total risks identified: {len(risk_items)}.",
            payload={"overall_risk": overall_risk.value, "risk_count": len(risk_items)}
        )

        return context
