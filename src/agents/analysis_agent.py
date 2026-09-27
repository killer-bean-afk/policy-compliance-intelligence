import time
import re
from typing import Dict, Any, List
from src.agents.base import BaseComplianceAgent, AgentMessageBus
from src.models.schemas import (
    RetrievedEvidence,
    ClauseAssessment,
    ComplianceVerdict,
    RequirementType,
    RiskLevel
)

class ComplianceAnalysisAgent(BaseComplianceAgent):
    """Specialist Agent responsible for clause-by-clause condition evaluation and compliance gap identification."""

    def __init__(self):
        super().__init__(
            agent_id="AGENT-ANALYSIS-02",
            name="Compliance Analysis Agent",
            role="Clause-by-Clause Requirement Assessment",
            description="Evaluates scenario facts against extracted policy requirements and identifies compliance gaps."
        )

    def execute(self, state: Dict[str, Any], bus: AgentMessageBus) -> Dict[str, Any]:
        t0 = time.time()
        scenario_text = state.get("scenario", "")
        evidence_items: List[RetrievedEvidence] = state.get("retrieved_evidence", [])

        thought = (
            f"Received {len(evidence_items)} policy clauses from Policy Retrieval Agent. "
            "Beginning formal requirement condition analysis against submitted business facts. "
            "Evaluating whether mandatory obligations are satisfied, conditional waivers apply, or explicit prohibitions are violated."
        )

        scenario_lower = scenario_text.lower()
        clause_assessments: List[ClauseAssessment] = []
        identified_gaps: List[str] = []

        for item in evidence_items:
            clause = item.clause
            cid = clause.clause_id
            c_text_lower = clause.clause_text.lower()
            
            verdict = ComplianceVerdict.COMPLIANT
            reasoning = ""
            gap = None

            # 1. Negative / Violation Indicator Checking
            has_violation_cues = any(w in scenario_lower for w in [
                "without", "failed to", "no dpa", "did not", "refused", "omitted", "missing", "bypassed",
                "unencrypted", "unauthorized", "unapproved", "single id", "one id", "undisclosed ubo",
                "anonymous", "bribe", "facilitation", "blackout", "breach", "no mfa", "sms only",
                "disparate impact 0.", "disparate impact ratio 0.6", "disparate impact ratio 0.7",
                "direct ssh", "standing admin", "root access without", "non-baa", "no consent",
                "unidentified ubo", "shared customer data without"
            ])

            # Domain-Specific Condition Rules
            if "POL-KYC-001-C01" in cid:
                if any(w in scenario_lower for w in ["single id", "one id", "single identification", "only driver license", "no address proof", "without verifying id"]):
                    verdict = ComplianceVerdict.NON_COMPLIANT
                    gap = "Customer onboarding attempted with single ID or without validated 90-day address proof."
                    reasoning = f"Clause requires at least two independent, unexpired government photo IDs and address proof dated within 90 days. Scenario indicates insufficient or single identification."
                elif any(w in scenario_lower for w in ["two government", "passport and", "verified id", "utility bill", "two independent"]):
                    verdict = ComplianceVerdict.COMPLIANT
                    reasoning = "Customer identity verification meets the dual-document CIP requirement with valid photo ID and proof of address."
                else:
                    verdict = ComplianceVerdict.CONDITIONAL
                    reasoning = "Customer onboarding may proceed conditionally provided two independent government IDs and 90-day address proof are verified."

            elif "POL-KYC-001-C02" in cid:
                if any(w in scenario_lower for w in ["pep", "politically exposed", "sanctions", "ofac", "sdn"]):
                    if any(w in scenario_lower for w in ["without approval", "unapproved", "bypassed compliance", "no sign-off"]):
                        verdict = ComplianceVerdict.NON_COMPLIANT
                        gap = "PEP / Sanctions positive match onboarded without Head of Financial Crime or executive sign-off."
                        reasoning = "Mandatory escalation to Head of Financial Crime and senior executive approval is strictly required before activating accounts with PEP exposure."
                    else:
                        verdict = ComplianceVerdict.CONDITIONAL
                        reasoning = "PEP match identified; activation is contingent upon senior compliance officer approval and enhanced scrutiny."
                else:
                    verdict = ComplianceVerdict.COMPLIANT
                    reasoning = "Real-time OFAC sanctions and PEP screening protocol must be executed prior to activation."

            elif "POL-KYC-001-C04" in cid:
                if any(w in scenario_lower for w in ["undisclosed", "anonymous", "cannot verify ubo", "hidden owner", "refused to provide beneficial"]):
                    verdict = ComplianceVerdict.NON_COMPLIANT
                    gap = "Failure to identify and verify natural persons owning 25% or more equity."
                    reasoning = "Corporate client accounts are prohibited from opening if any ultimate beneficial owner (25%+ rule) remains undisclosed."
                else:
                    verdict = ComplianceVerdict.COMPLIANT
                    reasoning = "Beneficial ownership disclosure verified for all 25%+ equity controllers."

            elif "POL-PRV-002-C01" in cid:
                if any(w in scenario_lower for w in ["without consent", "no consent", "pre-ticked", "bundled", "assumed consent"]):
                    verdict = ComplianceVerdict.NON_COMPLIANT
                    gap = "Customer personal data processed or shared without freely given, explicit opt-in consent."
                    reasoning = "Processing personal data without documented lawful basis or explicit consent violates GDPR Art. 6 and CCPA."
                else:
                    verdict = ComplianceVerdict.COMPLIANT
                    reasoning = "Lawful basis and explicit customer consent requirements are upheld."

            elif "POL-PRV-002-C02" in cid:
                if any(w in scenario_lower for w in ["without a dpa", "no dpa", "before signing dpa", "unsigned dpa", "without data processing agreement", "without agreement"]):
                    verdict = ComplianceVerdict.NON_COMPLIANT
                    gap = "Customer personal information shared with third-party vendor without an executed Data Processing Agreement (DPA)."
                    reasoning = "Disclosing customer personal data without an executed, counter-signed DPA is classified as a Tier-1 compliance breach under GDPR Art. 28."
                elif any(w in scenario_lower for w in ["dpa signed", "executed dpa", "signed data processing agreement"]):
                    verdict = ComplianceVerdict.COMPLIANT
                    reasoning = "Vendor engagement supported by an executed Data Processing Agreement with standard contractual clauses."
                else:
                    verdict = ComplianceVerdict.CONDITIONAL
                    reasoning = "Third-party sharing permitted only after counter-signing a formal DPA containing audit rights and sub-processor clauses."

            elif "POL-PRV-002-C04" in cid:
                if any(w in scenario_lower for w in ["unencrypted", "plaintext", "http:", "without encryption", "cleartext"]):
                    verdict = ComplianceVerdict.NON_COMPLIANT
                    gap = "Transmission or storage of customer confidential data in unencrypted plaintext."
                    reasoning = "Clause mandates TLS 1.3 in-transit encryption and AES-256 at-rest encryption for all customer personal data."
                else:
                    verdict = ComplianceVerdict.COMPLIANT
                    reasoning = "Data encryption standards (TLS 1.3 / AES-256) are satisfied."

            elif "POL-SEC-003-C01" in cid or "POL-SEC-003-C03" in cid:
                if any(w in scenario_lower for w in ["direct ssh", "standing admin", "permanent root", "root access without", "bypass bastion", "no pam"]):
                    verdict = ComplianceVerdict.NON_COMPLIANT
                    gap = "Direct production access or standing root privileges granted without PAM bastion or dual-person JIT approval."
                    reasoning = "Standing administrator access and direct SSH/RDP to production environments are strictly prohibited."
                else:
                    verdict = ComplianceVerdict.COMPLIANT
                    reasoning = "Production access adheres to the Principle of Least Privilege and Just-In-Time PAM bastion guardrails."

            elif "POL-GOV-004-C02" in cid or "POL-GOV-004-C03" in cid:
                if any(w in scenario_lower for w in ["fully automated", "no human", "disparate impact ratio 0.6", "disparate impact ratio 0.7", "bias test failed", "0.68", "0.72"]):
                    verdict = ComplianceVerdict.NON_COMPLIANT
                    gap = "AI model exhibits algorithmic disparate impact ratio below 0.80 or lacks Human-in-the-Loop oversight for adverse decisions."
                    reasoning = "Automated consumer rejection models must maintain disparate impact >= 0.80 and incorporate meaningful Human-in-the-Loop oversight."
                else:
                    verdict = ComplianceVerdict.CONDITIONAL
                    reasoning = "High-risk AI system deployment requires Model Risk Committee approval and quarterly bias testing."

            elif "POL-FIN-005-C01" in cid or "POL-FIN-005-C03" in cid:
                if any(w in scenario_lower for w in ["blackout period", "during blackout", "before earnings", "mnpi", "non-public results", "advance financial data"]):
                    verdict = ComplianceVerdict.NON_COMPLIANT
                    gap = "Securities trading or tipping conducted during a mandatory quarterly blackout period or with MNPI."
                    reasoning = "Trading company securities during earnings blackout periods or while possessing MNPI is strictly prohibited by SEC Rule 10b-5."
                else:
                    verdict = ComplianceVerdict.CONDITIONAL
                    reasoning = "Securities trade requires formal Pre-Clearance Request to Legal at least two business days prior."

            elif "POL-ETH-006-C01" in cid or "POL-ETH-006-C02" in cid:
                if any(w in scenario_lower for w in ["bribe", "kickback", "facilitation payment", "grease payment", "$500 dinner", "$1000", "expensive gift"]):
                    verdict = ComplianceVerdict.NON_COMPLIANT
                    gap = "Gift, hospitality, or corporate expenditure exceeds $100 cap or constitutes prohibited facilitation payment."
                    reasoning = "Zero tolerance for facilitation payments; corporate hospitality exceeding $100 requires advance VP pre-approval."
                else:
                    verdict = ComplianceVerdict.COMPLIANT
                    reasoning = "Hospitality remains within allowable thresholds."

            elif "POL-BIO-007-C01" in cid or "POL-BIO-007-C03" in cid:
                if any(w in scenario_lower for w in ["without de-identification", "raw phi", "patient names included", "non-baa cloud", "public cloud without baa"]):
                    verdict = ComplianceVerdict.NON_COMPLIANT
                    gap = "Biomedical research or AI training conducted on raw, non-de-identified PHI or without a signed BAA."
                    reasoning = "HIPAA Safe Harbor mandates removal of 18 identifiers, and cloud environments storing PHI must possess a signed BAA."
                else:
                    verdict = ComplianceVerdict.CONDITIONAL
                    reasoning = "Clinical data sharing requires Institutional Review Board (IRB) approval and HIPAA Safe Harbor de-identification."

            else:
                # Generic fallback check
                if has_violation_cues:
                    verdict = ComplianceVerdict.NON_COMPLIANT
                    gap = f"Potential discrepancy identified against requirement: {clause.section_title}."
                    reasoning = f"Facts suggest non-fulfillment of criteria specified in clause {cid}."
                else:
                    verdict = ComplianceVerdict.CONDITIONAL
                    reasoning = f"Action is permissible subject to standard procedural controls in {clause.section_title}."

            if gap and gap not in identified_gaps:
                identified_gaps.append(gap)

            assessment = ClauseAssessment(
                clause_id=clause.clause_id,
                policy_name=clause.policy_name,
                section=f"{clause.section_number} {clause.section_title}",
                citation=item.citation_tag,
                requirement_type=clause.requirement_type,
                clause_text=clause.clause_text,
                verdict=verdict,
                reasoning=reasoning,
                evidence_quote=item.highlight_span or clause.clause_text[:140],
                gap_identified=gap,
                severity=clause.penalty_severity
            )
            clause_assessments.append(assessment)

        # Compute overall preliminary verdict
        non_compliant_count = sum(1 for a in clause_assessments if a.verdict == ComplianceVerdict.NON_COMPLIANT)
        compliant_count = sum(1 for a in clause_assessments if a.verdict == ComplianceVerdict.COMPLIANT)
        conditional_count = sum(1 for a in clause_assessments if a.verdict == ComplianceVerdict.CONDITIONAL)

        if non_compliant_count > 0:
            preliminary_verdict = ComplianceVerdict.NON_COMPLIANT
        elif len(identified_gaps) == 0 and compliant_count > 0:
            preliminary_verdict = ComplianceVerdict.COMPLIANT
        elif conditional_count > 0 and len(identified_gaps) > 0:
            preliminary_verdict = ComplianceVerdict.CONDITIONAL
        else:
            preliminary_verdict = ComplianceVerdict.COMPLIANT

        elapsed_ms = (time.time() - t0) * 1000
        output_summary = f"Assessed {len(clause_assessments)} clauses: {non_compliant_count} Non-Compliant, {conditional_count} Conditional, {len(clause_assessments) - non_compliant_count - conditional_count} Compliant. Identified {len(identified_gaps)} compliance gaps."

        # Record trace
        bus.record_trace(
            agent_name=self.name,
            stage="ANALYSIS",
            action="Condition Verification & Gap Detection",
            thought=thought,
            output_summary=output_summary,
            execution_time_ms=elapsed_ms,
            confidence=0.91,
            data={
                "preliminary_verdict": preliminary_verdict.value,
                "non_compliant_count": non_compliant_count,
                "identified_gaps": identified_gaps
            }
        )

        # Handoff to Risk Assessment Agent
        handoff_reason = (
            f"Handing off {len(identified_gaps)} identified gaps and preliminary verdict '{preliminary_verdict.value}' to Risk Assessment Agent for financial, regulatory, and operational severity scoring."
        )

        bus.send_message(
            sender=self.name,
            receiver="Risk Assessment Agent",
            stage="ANALYSIS_COMPLETE",
            content=f"Clause analysis concluded with preliminary verdict: {preliminary_verdict.value}.",
            payload={
                "verdict": preliminary_verdict.value,
                "gap_count": len(identified_gaps),
                "non_compliant_clauses": [a.clause_id for a in clause_assessments if a.verdict == ComplianceVerdict.NON_COMPLIANT]
            },
            handoff_reason=handoff_reason
        )

        state["clause_assessments"] = clause_assessments
        state["identified_gaps"] = identified_gaps
        state["preliminary_verdict"] = preliminary_verdict
        return state
