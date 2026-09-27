"""
Compliance Analysis Agent.
Compares business scenario against retrieved policy clauses, checks requirement fulfillment,
determines compliance status, and extracts direct policy evidence quotes.
Supports Negation & Pre-condition Analysis (e.g. "without EDD", "lacks BAA", "missing approval").
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent, A2AMessageBus
from models import (
    AgentMessageType,
    RetrievalResultItem,
    ClauseAnalysis,
    ComplianceStatus
)


def is_negated(text: str, keyword: str) -> bool:
    """Detects if a keyword is preceded by a negation indicator (e.g. 'without', 'lacks', 'missing')."""
    idx = text.find(keyword)
    if idx == -1:
        return False
    window = text[max(0, idx - 40):idx]
    negations = ["without", "lacks", "missing", "no ", "not ", "unapproved", "failed to", "bypassed", "non-"]
    return any(neg in window for neg in negations)


class ComplianceAnalysisAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Compliance Analysis Agent",
            role="Policy Assessment Specialist",
            description="Compares scenario details against mandatory policy clauses line-by-line."
        )

    def process(self, context: Dict[str, Any], bus: A2AMessageBus) -> Dict[str, Any]:
        scenario_text = context.get("scenario_text", "").lower()
        retrieved_items: List[RetrievalResultItem] = context.get("retrieved_clauses", [])

        clause_analyses: List[ClauseAnalysis] = []

        bus.publish(
            sender=self.name,
            receiver="Risk Assessment Agent",
            msg_type=AgentMessageType.ANALYSIS_HANDOFF,
            content=f"Analyzing {len(retrieved_items)} retrieved policy clauses against scenario facts...",
            payload={}
        )

        for item in retrieved_items:
            clause = item.clause

            status = ComplianceStatus.COMPLIANT
            findings_parts = []
            score = 1.0

            # 1. KYC / PEP / EDD Checks
            if clause.clause_id in ["KYC-1.2", "KYC-1.1"]:
                has_pep = any(kw in scenario_text for kw in ["pep", "politically exposed", "politician", "minister", "foreign official", "senator", "governor", "head of state"])
                
                edd_present = ("edd" in scenario_text or "enhanced due diligence" in scenario_text or "source of wealth" in scenario_text) and not is_negated(scenario_text, "edd") and not is_negated(scenario_text, "enhanced due diligence")
                mlro_present = ("mlro" in scenario_text or "money laundering officer" in scenario_text) and not is_negated(scenario_text, "mlro") and not is_negated(scenario_text, "sign-off")

                if has_pep:
                    if not edd_present or not mlro_present:
                        status = ComplianceStatus.NON_COMPLIANT
                        score = 0.15
                        findings_parts.append("Scenario involves a Politically Exposed Person (PEP) / foreign politician but lacks mandatory Enhanced Due Diligence (EDD) or formal written MLRO sign-off.")
                    else:
                        findings_parts.append("PEP customer onboarding satisfied mandatory EDD dossier and written MLRO approval.")
                elif any(kw in scenario_text for kw in ["no photo id", "missing id", "without verification", "unverified"]):
                    status = ComplianceStatus.NON_COMPLIANT
                    score = 0.10
                    findings_parts.append("CIP baseline requirements violated due to missing mandatory government photo identification or address verification.")
                else:
                    findings_parts.append("Customer onboarding baseline verification requirements satisfied.")

            # 2. HIPAA / Data Privacy / BAA Checks
            elif clause.clause_id in ["HIPAA-2.1", "HIPAA-1.1", "HIPAA-3.1"]:
                has_phi = any(kw in scenario_text for kw in ["phi", "patient", "health record", "medical data", "ephi", "diagnosis", "ehr"])
                has_third_party = any(kw in scenario_text for kw in ["third party", "vendor", "cloud", "saas", "external", "ai model", "chatgpt"])
                
                baa_present = ("baa" in scenario_text or "business associate agreement" in scenario_text) and not is_negated(scenario_text, "baa") and not is_negated(scenario_text, "agreement")
                is_unencrypted = any(kw in scenario_text for kw in ["unencrypted", "plain text", "without encryption"])

                if has_phi and has_third_party and not baa_present:
                    status = ComplianceStatus.NON_COMPLIANT
                    score = 0.05
                    findings_parts.append("Sharing Protected Health Information (PHI) with a third-party vendor without an executed Business Associate Agreement (BAA) violates HIPAA Clause 2.1.")
                elif is_unencrypted:
                    status = ComplianceStatus.NON_COMPLIANT
                    score = 0.10
                    findings_parts.append("Transmission or storage of unencrypted PHI violates mandatory AES-256 / TLS 1.3 encryption requirements.")
                else:
                    findings_parts.append("Data privacy access controls and executed agreements align with HIPAA policy guidelines.")

            # 3. InfoSec & Vendor Risk Checks
            elif clause.clause_id in ["SEC-1.1", "SEC-2.1", "SEC-4.1"]:
                has_ai_paste = any(kw in scenario_text for kw in ["pasted code", "public ai", "chatgpt", "public llm", "uploaded code", "public web-based"])
                soc2_present = ("soc 2" in scenario_text or "soc2" in scenario_text or "iso 27001" in scenario_text) and not is_negated(scenario_text, "soc 2")
                has_cross_border = any(kw in scenario_text for kw in ["offshore", "outside us", "china", "russia", "foreign server", "foreign jurisdiction"])
                ciso_present = ("ciso" in scenario_text) and not is_negated(scenario_text, "ciso") and not is_negated(scenario_text, "approval")

                if has_ai_paste:
                    status = ComplianceStatus.NON_COMPLIANT
                    score = 0.10
                    findings_parts.append("Uploading proprietary source code or confidential assets to unvetted public generative AI tools violates DLP Policy SEC-4.1.")
                elif has_cross_border and not ciso_present:
                    status = ComplianceStatus.NON_COMPLIANT
                    score = 0.20
                    findings_parts.append("Cross-border transfer of confidential data without prior CISO authorization violates Clause SEC-2.1.")
                elif "vendor" in scenario_text and not soc2_present:
                    status = ComplianceStatus.PARTIALLY_COMPLIANT
                    score = 0.50
                    findings_parts.append("Vendor risk assessment initiated, but SOC 2 Type II audit report verification is missing.")
                else:
                    findings_parts.append("Vendor security controls and data protection requirements are satisfied.")

            # 4. Corporate Governance & FCPA Gifts Checks
            elif clause.clause_id in ["GOV-1.1", "GOV-2.1"]:
                has_gift = any(kw in scenario_text for kw in ["gift", "dinner", "entertainment", "ticket", "hospitality"])
                has_govt = any(kw in scenario_text for kw in ["government official", "foreign minister", "regulator", "inspector", "regulatory official"])
                has_high_value = any(kw in scenario_text for kw in ["$200", "$300", "$400", "$500", "$1000", "200 usd", "500 usd", "expensive"])
                preclearance_present = ("pre-clearance" in scenario_text or "preclearance" in scenario_text) and not is_negated(scenario_text, "pre-clearance")

                if has_gift and has_govt:
                    status = ComplianceStatus.NON_COMPLIANT
                    score = 0.0
                    findings_parts.append("Offering gifts, meals, or entertainment to a foreign government/regulatory official is strictly prohibited under FCPA and Clause GOV-1.1.")
                elif has_gift and has_high_value and not preclearance_present:
                    status = ComplianceStatus.NON_COMPLIANT
                    score = 0.25
                    findings_parts.append("Gift/entertainment exceeds the $150 USD limit and lacks mandatory written compliance pre-clearance.")
                else:
                    findings_parts.append("Gift/hospitality expenditure complies with governance limits.")

            # 5. Financial Operations & OFAC Checks
            elif clause.clause_id in ["FIN-1.1", "FIN-2.1", "FIN-3.1"]:
                has_sanctions_mention = any(kw in scenario_text for kw in ["sanction", "ofac", "sdn list", "iran", "russia", "cuba", "high risk country", "eastern europe"])
                ofac_screened = ("screened" in scenario_text or "screening" in scenario_text or "green check" in scenario_text or "verified ofac" in scenario_text) and not is_negated(scenario_text, "screening") and not is_negated(scenario_text, "screened")
                has_high_val = any(kw in scenario_text for kw in ["$100,000", "$150,000", "$200,000", "$250,000", "$500,000", "$1,000,000", "150k", "200k", "250k", "1m"])
                dual_appr = ("dual authorization" in scenario_text or "dual approval" in scenario_text or "dual treasury" in scenario_text or "cfo approval" in scenario_text) and not is_negated(scenario_text, "approval") and not is_negated(scenario_text, "authorization")
                has_crypto = any(kw in scenario_text for kw in ["monero", "tornado cash", "unhosted wallet", "crypto", "virtual asset"])

                if has_sanctions_mention and not ofac_screened:
                    status = ComplianceStatus.NON_COMPLIANT
                    score = 0.0
                    findings_parts.append("Executing international wire transfer without real-time OFAC SDN screening violates Clause FIN-1.1.")
                elif has_crypto and any(kw in scenario_text for kw in ["unhosted", "monero", "tornado"]):
                    status = ComplianceStatus.NON_COMPLIANT
                    score = 0.05
                    findings_parts.append("Using unhosted crypto wallets or privacy-focused mixing services is strictly prohibited under Clause FIN-3.1.")
                elif has_high_val and not dual_appr:
                    status = ComplianceStatus.NON_COMPLIANT
                    score = 0.30
                    findings_parts.append("High-value wire transfer (> $100k) executed without required dual Treasury authorization or CFO sign-off.")
                else:
                    findings_parts.append("Financial transfer procedures align with treasury approval and sanctions screening rules.")

            else:
                if any(kw in scenario_text for kw in ["without approval", "unauthorized", "bypassed"]):
                    status = ComplianceStatus.NON_COMPLIANT
                    score = 0.3
                    findings_parts.append(f"Scenario indicates missing procedural approval required by Clause {clause.clause_id}.")
                else:
                    findings_parts.append(f"Scenario appears consistent with requirement in Section {clause.section_number}.")

            quote_snippet = clause.clause_text[:160] + "..." if len(clause.clause_text) > 160 else clause.clause_text

            clause_analyses.append(
                ClauseAnalysis(
                    clause_id=clause.clause_id,
                    policy_name=clause.policy_name,
                    section_number=clause.section_number,
                    requirement_summary=f"Section {clause.section_number} - {clause.section_title} [{clause.mandatory_level}]",
                    status=status,
                    findings=" ".join(findings_parts),
                    evidence_quote=quote_snippet,
                    compliance_score=score
                )
            )

        context["clause_analyses"] = clause_analyses

        non_compliant_count = sum(1 for a in clause_analyses if a.status == ComplianceStatus.NON_COMPLIANT)
        bus.publish(
            sender=self.name,
            receiver="Risk Assessment Agent",
            msg_type=AgentMessageType.ANALYSIS_HANDOFF,
            content=f"Completed clause analysis: {non_compliant_count} non-compliant clause(s) detected out of {len(clause_analyses)} evaluated.",
            payload={"non_compliant_count": non_compliant_count}
        )

        return context
