import time
from typing import Dict, Any, List
from src.agents.base import BaseComplianceAgent, AgentMessageBus
from src.models.schemas import (
    ClauseAssessment,
    RiskFactor,
    RiskLevel,
    ComplianceVerdict
)

class RiskAssessmentAgent(BaseComplianceAgent):
    """Specialist Agent responsible for quantitative risk scoring, impact-likelihood matrix, and regulatory liability evaluation."""

    def __init__(self):
        super().__init__(
            agent_id="AGENT-RISK-03",
            name="Risk Assessment Agent",
            role="Risk Exposure & Regulatory Penalty Quantification",
            description="Evaluates probability, impact, statutory fines, and operational consequences of compliance gaps."
        )

    def execute(self, state: Dict[str, Any], bus: AgentMessageBus) -> Dict[str, Any]:
        t0 = time.time()
        clause_assessments: List[ClauseAssessment] = state.get("clause_assessments", [])
        identified_gaps: List[str] = state.get("identified_gaps", [])
        preliminary_verdict: ComplianceVerdict = state.get("preliminary_verdict", ComplianceVerdict.COMPLIANT)

        thought = (
            f"Evaluating compliance risk matrix for {len(clause_assessments)} assessed clauses and {len(identified_gaps)} identified gaps. "
            "Calculating quantitative risk score, regulatory penalty ceilings (GDPR, FinCEN, SEC, HIPAA, EU AI Act), and operational liability index."
        )

        risk_factors: List[RiskFactor] = []
        raw_risk_score = 10.0  # baseline operational friction

        for assessment in clause_assessments:
            cid = assessment.clause_id

            if assessment.verdict == ComplianceVerdict.NON_COMPLIANT:
                # Severity weight
                if assessment.severity == RiskLevel.CRITICAL:
                    clause_points = 35.0
                    impact = RiskLevel.CRITICAL
                    likelihood = RiskLevel.HIGH
                elif assessment.severity == RiskLevel.HIGH:
                    clause_points = 24.0
                    impact = RiskLevel.HIGH
                    likelihood = RiskLevel.HIGH
                else:
                    clause_points = 14.0
                    impact = RiskLevel.MEDIUM
                    likelihood = RiskLevel.MEDIUM

                raw_risk_score += clause_points

                # Build targeted regulatory penalty descriptions
                penalties = "Regulatory enforcement inquiry, operational suspension, and corrective mandatory audit."
                regs = ["Enterprise Compliance Standards"]

                if "POL-PRV" in cid:
                    regs = ["GDPR Art. 83", "CCPA/CPRA § 1798.155", "EU Data Protection Authorities"]
                    penalties = "Statutory administrative fines up to €20M or 4% of total worldwide annual turnover; mandatory public breach disclosure."
                elif "POL-KYC" in cid:
                    regs = ["FinCEN Bank Secrecy Act (BSA)", "OFAC Sanctions Enforcement", "FATF Guidelines"]
                    penalties = "Civil money penalties exceeding $1,000,000 per violation; personal liability for compliance officers; license revocation."
                elif "POL-SEC" in cid:
                    regs = ["ISO 27001", "SOC 2 Type II Compliance", "PCI-DSS v4.0", "CISA Zero Trust"]
                    penalties = "Loss of SOC 2 / ISO 27001 certification; contractual customer indemnification claims; immediate infrastructure shutdown."
                elif "POL-GOV" in cid:
                    regs = ["EU Artificial Intelligence Act (Regulation 2024/1689)", "FTC Section 5 Algorithmic Enforcement"]
                    penalties = "Administrative fines up to €35M or 7% of global turnover; mandatory withdrawal of algorithmic models from market."
                elif "POL-FIN" in cid:
                    regs = ["SEC Rule 10b-5", "Securities Exchange Act Sec. 10(b)", "FINRA Rule 2241"]
                    penalties = "Treble damages (3x illicit profits or avoided losses); SEC civil enforcement; federal criminal wire fraud referral."
                elif "POL-ETH" in cid:
                    regs = ["Foreign Corrupt Practices Act (FCPA)", "UK Bribery Act 2010"]
                    penalties = "Disgorgement of all commercial contract revenues; unlimited statutory fines; debarment from public contracting."
                elif "POL-BIO" in cid:
                    regs = ["HIPAA Privacy & Security Rule", "HITECH Act", "FDA 21 CFR Part 11"]
                    penalties = "HHS Office for Civil Rights (OCR) fines up to $1,900,000 per calendar year; suspension of clinical trials."

                risk_factors.append(RiskFactor(
                    risk_title=f"Non-Compliance with {assessment.section}",
                    category=assessment.policy_name,
                    severity=assessment.severity,
                    likelihood=likelihood,
                    impact=impact,
                    score=min(round(clause_points * 2.8, 1), 98.0),
                    regulatory_frameworks=regs,
                    potential_penalties=penalties,
                    mitigation_priority="URGENT" if assessment.severity in (RiskLevel.CRITICAL, RiskLevel.HIGH) else "HIGH",
                    clause_reference=assessment.citation
                ))

            elif assessment.verdict == ComplianceVerdict.CONDITIONAL:
                raw_risk_score += 6.0
                risk_factors.append(RiskFactor(
                    risk_title=f"Conditional Approval Dependency: {assessment.section}",
                    category=assessment.policy_name,
                    severity=RiskLevel.MEDIUM,
                    likelihood=RiskLevel.MEDIUM,
                    impact=RiskLevel.MEDIUM,
                    score=38.0,
                    regulatory_frameworks=["Internal Governance Protocol"],
                    potential_penalties="Internal audit deficiency finding and temporary activity freeze pending complete documentation.",
                    mitigation_priority="MEDIUM",
                    clause_reference=assessment.citation
                ))

        # Clamp composite risk score
        if preliminary_verdict == ComplianceVerdict.COMPLIANT and len(identified_gaps) == 0:
            final_risk_score = 12.0
            overall_risk_level = RiskLevel.LOW
            risk_factors = []
        else:
            final_risk_score = round(min(max(raw_risk_score, 8.0), 99.0), 1)
            # Categorize Overall Risk Level
            if final_risk_score >= 70.0:
                overall_risk_level = RiskLevel.CRITICAL
            elif final_risk_score >= 45.0:
                overall_risk_level = RiskLevel.HIGH
            elif final_risk_score >= 25.0:
                overall_risk_level = RiskLevel.MEDIUM
            else:
                overall_risk_level = RiskLevel.LOW

        elapsed_ms = (time.time() - t0) * 1000
        output_summary = f"Assigned composite risk score {final_risk_score}/100 ({overall_risk_level.value}). Generated {len(risk_factors)} targeted risk exposure factors."

        # Record Step Trace
        bus.record_trace(
            agent_name=self.name,
            stage="RISK_ASSESSMENT",
            action="Quantitative Risk Scoring & Penalty Calibration",
            thought=thought,
            output_summary=output_summary,
            execution_time_ms=elapsed_ms,
            confidence=0.93,
            data={
                "risk_score": final_risk_score,
                "risk_level": overall_risk_level.value,
                "risk_factors_count": len(risk_factors)
            }
        )

        # Handoff to Policy Interpretation/Validation Agent
        escalation_note = "CRITICAL ESCALATION: Severe regulatory exposures detected." if overall_risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH) else "Standard risk profile."
        handoff_reason = f"Routing findings to Policy Interpretation & Validation Agent for evidentiary grounding verification. {escalation_note}"

        bus.send_message(
            sender=self.name,
            receiver="Policy Interpretation/Validation Agent",
            stage="RISK_ASSESSMENT_COMPLETE",
            content=f"Risk assessment finalized: Score={final_risk_score}, Level={overall_risk_level.value}.",
            payload={
                "risk_score": final_risk_score,
                "risk_level": overall_risk_level.value,
                "risk_factor_titles": [r.risk_title for r in risk_factors]
            },
            handoff_reason=handoff_reason
        )

        state["risk_score"] = final_risk_score
        state["risk_level"] = overall_risk_level
        state["risk_factors"] = risk_factors
        return state
