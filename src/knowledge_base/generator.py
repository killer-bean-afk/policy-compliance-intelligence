import os
import json
from pathlib import Path
from typing import List, Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from src.config import RAW_POLICIES_DIR, KB_PATH
from src.models.schemas import PolicyDocument, PolicyClause, RequirementType, RiskLevel

POLICIES_DATA: List[Dict] = [
    {
        "policy_id": "POL-KYC-001",
        "policy_name": "Global Anti-Money Laundering (AML) & Customer Due Diligence (KYC) Policy",
        "category": "Anti-Money Laundering",
        "business_area": "Operations & Compliance",
        "version": "3.2",
        "effective_date": "2025-01-15",
        "owner": "Chief Compliance Officer (CCO)",
        "pdf_filename": "POL-KYC-001_Anti_Money_Laundering.pdf",
        "description": "Establishes mandatory protocols for customer onboarding, Customer Identification Program (CIP), Politically Exposed Persons (PEP) screening, Beneficial Ownership verification, and Suspicious Activity Reporting.",
        "clauses": [
            {
                "clause_id": "POL-KYC-001-C01",
                "section_number": "2.1",
                "section_title": "Customer Identification Program (CIP) Verification",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Prior to establishing any business relationship or executing non-custodial transactions, the onboarding team must verify customer identity using at least two independent, unexpired government-issued photographic identification documents and validated residential address proofs dated within the last 90 days.",
                "key_terms": ["CIP", "customer onboarding", "government ID", "identity verification", "address proof"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "FinCEN Customer Due Diligence Rule 31 CFR 1010.230; USA PATRIOT Act Sec. 326",
            },
            {
                "clause_id": "POL-KYC-001-C02",
                "section_number": "3.1",
                "section_title": "Politically Exposed Persons (PEPs) & Sanctions Screening",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "All new and existing customers must be screened in real-time against current OFAC SDN lists, UN Sanctions, and global PEP databases prior to account activation. Any positive match for a foreign or domestic PEP requires mandatory escalation to the Head of Financial Crime and senior executive sign-off prior to account opening.",
                "key_terms": ["PEP", "OFAC", "sanctions screening", "politically exposed persons", "escalation"],
                "penalty_severity": RiskLevel.CRITICAL,
                "regulatory_framework": "OFAC Sanctions Regulations; FATF Recommendation 12",
            },
            {
                "clause_id": "POL-KYC-001-C03",
                "section_number": "4.1",
                "section_title": "Enhanced Due Diligence (EDD) for High-Risk Accounts",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Enhanced Due Diligence (EDD) is strictly required for entities domiciled in FATF-monitored high-risk jurisdictions, non-bank financial institutions, and accounts with anticipated annual turnover exceeding $5,000,000. EDD must establish verified Source of Wealth (SoW) and Source of Funds (SoF) with certified audited financial statements.",
                "key_terms": ["EDD", "enhanced due diligence", "high-risk", "source of wealth", "source of funds", "FATF"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "FATF High-Risk Jurisdictions Guidance; FinCEN EDD Guidelines",
            },
            {
                "clause_id": "POL-KYC-001-C04",
                "section_number": "5.2",
                "section_title": "Beneficial Ownership Transparency (25% Rule)",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "For all corporate clients, the compliance analyst must identify and independently verify every natural person who directly or indirectly owns or controls 25% or more of the equity interests of the legal entity, or who exercises significant management control. No account may be opened if any ultimate beneficial owner (UBO) remains undisclosed.",
                "key_terms": ["beneficial ownership", "UBO", "25% rule", "equity interest", "corporate onboarding"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "FinCEN CDD Rule 31 CFR 1010.230(d); Corporate Transparency Act",
            },
            {
                "clause_id": "POL-KYC-001-C05",
                "section_number": "6.3",
                "section_title": "Suspicious Activity Reporting (SAR) & Cash Thresholds",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Any single transaction or aggregated series of transactions exceeding $10,000 in currency must trigger a Currency Transaction Report (CTR) within 15 calendar days. Any transaction exhibiting indicators of structuring, lack of apparent economic rationale, or fund layering must be submitted to the AML Officer for filing a Suspicious Activity Report (SAR) with FinCEN within 30 days.",
                "key_terms": ["SAR", "CTR", "suspicious activity", "cash threshold", "$10,000", "structuring"],
                "penalty_severity": RiskLevel.CRITICAL,
                "regulatory_framework": "Bank Secrecy Act (BSA) 31 U.S.C. 5318(g); FinCEN 31 CFR 1020.320",
            },
            {
                "clause_id": "POL-KYC-001-C06",
                "section_number": "7.1",
                "section_title": "Periodic KYC Refresh Cycle",
                "requirement_type": RequirementType.CONDITIONAL,
                "clause_text": "High-risk customer files must undergo full re-certification annually. Medium-risk customers must be refreshed every two years, and low-risk customers every three years. If an account experiences a material change in ownership, leadership, or business activity, an immediate ad-hoc KYC review must be executed.",
                "key_terms": ["periodic review", "KYC refresh", "recertification", "material change"],
                "penalty_severity": RiskLevel.MEDIUM,
                "regulatory_framework": "FinCEN Risk-Based AML Procedures",
            }
        ]
    },
    {
        "policy_id": "POL-PRV-002",
        "policy_name": "Enterprise Data Protection, Privacy & Third-Party Sharing Policy",
        "category": "Data Privacy & Protection",
        "business_area": "Legal, Information Security & Engineering",
        "version": "4.1",
        "effective_date": "2025-02-01",
        "owner": "Data Protection Officer (DPO)",
        "pdf_filename": "POL-PRV-002_Data_Protection_Privacy.pdf",
        "description": "Defines binding rules governing personal data processing, lawful basis, third-party vendor transfers, cross-border data transfer mechanisms, data subject rights, and statutory breach notifications.",
        "clauses": [
            {
                "clause_id": "POL-PRV-002-C01",
                "section_number": "1.2",
                "section_title": "Lawful Basis & Explicit Customer Consent",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Customer personal data, including contact records, financial data, and behavioral profiles, must only be processed where a documented lawful basis exists under GDPR Art. 6 or CCPA. Where consent serves as the legal basis, consent must be freely given, specific, informed, and unambiguous. Pre-ticked opt-in checkboxes or bundled terms of service are strictly prohibited.",
                "key_terms": ["consent", "lawful basis", "GDPR", "CCPA", "opt-in", "personal data"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "GDPR Article 6 & 7; California Consumer Privacy Act (CCPA) § 1798.120",
            },
            {
                "clause_id": "POL-PRV-002-C02",
                "section_number": "2.1",
                "section_title": "Third-Party Data Sharing & Data Processing Agreements (DPA)",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Before disclosing, transmitting, or granting API access to customer personal information with any third-party vendor, partner, or cloud service provider, the business unit must execute a legally binding Data Processing Agreement (DPA) containing standard contractual clauses, purpose limitation restrictions, mandatory sub-processor notification, and right-to-audit provisions. Sharing customer data without a counter-signed DPA is a tier-1 compliance breach.",
                "key_terms": ["third party", "data sharing", "DPA", "vendor risk", "sub-processor", "audit"],
                "penalty_severity": RiskLevel.CRITICAL,
                "regulatory_framework": "GDPR Article 28; CPRA § 1798.140",
            },
            {
                "clause_id": "POL-PRV-002-C03",
                "section_number": "3.2",
                "section_title": "Cross-Border Data Transfers & Adequacy Safeguards",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Transferring personal data originating in the European Economic Area (EEA), United Kingdom, or Switzerland to jurisdictions outside these territories without an official European Commission Adequacy Decision requires the implementation of EU Standard Contractual Clauses (SCCs) and a completed Transfer Impact Assessment (TIA) signed by the Data Protection Officer.",
                "key_terms": ["cross-border", "international transfer", "SCC", "standard contractual clauses", "TIA", "EEA"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "GDPR Chapter V (Articles 44-49); Schrems II Ruling",
            },
            {
                "clause_id": "POL-PRV-002-C04",
                "section_number": "4.1",
                "section_title": "Cryptographic Protection & In-Transit / At-Rest Encryption",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "All customer confidential information, personally identifiable information (PII), and authentication credentials must be encrypted in transit using TLS 1.3 (or minimum TLS 1.2 with forward secrecy) and encrypted at rest using AES-256 or equivalent quantum-resistant cipher suites. Unencrypted transmission via plaintext email or HTTP is grounds for immediate credential revocation.",
                "key_terms": ["encryption", "TLS 1.3", "AES-256", "PII", "in-transit", "at-rest"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "GDPR Article 32; PCI-DSS Requirement 3 & 4; NIST SP 800-52",
            },
            {
                "clause_id": "POL-PRV-002-C05",
                "section_number": "5.3",
                "section_title": "Data Subject Access Rights & 30-Day Erasure Mandate",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Upon receiving a verified Data Subject Request (DSR) or Right to Be Forgotten request, the Privacy Operations team must delete or pseudonymize all non-mandatory personal data across primary systems and replica databases within 30 calendar days, unless retention is statutorily required under tax, anti-money laundering, or litigation hold rules.",
                "key_terms": ["right to erasure", "DSR", "right to be forgotten", "deletion", "retention schedule"],
                "penalty_severity": RiskLevel.MEDIUM,
                "regulatory_framework": "GDPR Article 17; CCPA § 1798.105",
            },
            {
                "clause_id": "POL-PRV-002-C06",
                "section_number": "6.1",
                "section_title": "Statutory 72-Hour Personal Data Breach Notification",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "In the event of a confirmed or suspected security incident resulting in unlawful destruction, loss, alteration, or unauthorized disclosure of personal data, the Incident Response Commander must notify the Data Protection Officer within 4 hours. The DPO must report the breach to the relevant Supervisory Authority within 72 hours of becoming aware of it.",
                "key_terms": ["breach notification", "72 hours", "supervisory authority", "data incident", "DPO"],
                "penalty_severity": RiskLevel.CRITICAL,
                "regulatory_framework": "GDPR Article 33 & 34; CCPA § 1798.82",
            }
        ]
    },
    {
        "policy_id": "POL-SEC-003",
        "policy_name": "Information Security, Access Control & Cloud Infrastructure Policy",
        "category": "Information Security",
        "business_area": "IT, DevOps & Engineering",
        "version": "5.0",
        "effective_date": "2025-01-01",
        "owner": "Chief Information Security Officer (CISO)",
        "pdf_filename": "POL-SEC-003_Information_Security.pdf",
        "description": "Mandates strict technical and organizational measures including Zero Trust architecture, privileged access management, multi-factor authentication, cloud security guardrails, and audit logging.",
        "clauses": [
            {
                "clause_id": "POL-SEC-003-C01",
                "section_number": "1.1",
                "section_title": "Principle of Least Privilege and Role-Based Access Control",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Access to corporate information systems, source code repositories, databases, and customer environments must be granted strictly on the Principle of Least Privilege and implemented via Role-Based Access Control (RBAC). Standing administrator rights on employee endpoints or production infrastructure are strictly prohibited.",
                "key_terms": ["least privilege", "RBAC", "standing admin", "access control", "zero trust"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "ISO/IEC 27001:2022 Control A.5.15, A.8.2; SOC 2 CC6.1, CC6.3",
            },
            {
                "clause_id": "POL-SEC-003-C02",
                "section_number": "2.2",
                "section_title": "Universal Multi-Factor Authentication (MFA) Requirement",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Phishing-resistant Multi-Factor Authentication (MFA)—utilizing FIDO2/WebAuthn hardware security keys or managed authenticator applications—is universally mandatory for all employee accounts, VPN connections, cloud management consoles (AWS, Azure, GCP), and sensitive SaaS services. SMS-based OTP is prohibited for privileged administrators.",
                "key_terms": ["MFA", "multi-factor authentication", "FIDO2", "hardware token", "cloud console"],
                "penalty_severity": RiskLevel.CRITICAL,
                "regulatory_framework": "NIST SP 800-63B AAL2/AAL3; CISA Zero Trust Guidance",
            },
            {
                "clause_id": "POL-SEC-003-C03",
                "section_number": "3.3",
                "section_title": "Production Environment Access & Just-In-Time (JIT) Elevation",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Direct SSH, RDP, or root console access to live production environments is prohibited. Emergency access must be obtained through a Privileged Access Management (PAM) bastion using Just-In-Time (JIT) access requests requiring dual-person engineering manager approval, automatic session screen recording, and automated credential expiration within a maximum of 4 hours.",
                "key_terms": ["production access", "root access", "PAM", "bastion", "JIT", "dual approval"],
                "penalty_severity": RiskLevel.CRITICAL,
                "regulatory_framework": "SOC 2 Type II CC6.6; ISO 27001 A.8.18",
            },
            {
                "clause_id": "POL-SEC-003-C04",
                "section_number": "4.2",
                "section_title": "Audit Logging, SIEM Integration & 365-Day Retention",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "All authentication attempts, privilege elevations, database queries against customer tables, firewall modifications, and administrative actions must be forwarded in real time to the centralized SIEM platform. Audit logs must be cryptographically signed, stored in immutable write-once-read-many (WORM) storage, and retained for not less than 365 calendar days.",
                "key_terms": ["audit logging", "SIEM", "log retention", "immutable storage", "WORM", "365 days"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "PCI-DSS v4.0 Req 10; SOC 2 CC7.2; NIST SP 800-92",
            },
            {
                "clause_id": "POL-SEC-003-C05",
                "section_number": "5.4",
                "section_title": "Critical Vulnerability Remediation SLA",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Any vulnerability identified in production systems or public-facing applications with a Common Vulnerability Scoring System (CVSS v3) score of 9.0 or higher must be remediated or mitigated within 72 hours of discovery. High-severity vulnerabilities (CVSS 7.0-8.9) must be patched within 14 calendar days.",
                "key_terms": ["vulnerability management", "patching SLA", "CVSS 9.0", "72 hours", "remediation"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "FedRAMP Incident & Vulnerability Standards; CISA BOD 22-01",
            }
        ]
    },
    {
        "policy_id": "POL-GOV-004",
        "policy_name": "Enterprise Artificial Intelligence Governance & Algorithmic Ethics Policy",
        "category": "AI Governance & Ethics",
        "business_area": "Product, Data Science & AI Engineering",
        "version": "2.0",
        "effective_date": "2025-01-20",
        "owner": "Chief AI Ethics Officer & Model Risk Committee",
        "pdf_filename": "POL-GOV-004_AI_Governance_Risk.pdf",
        "description": "Establishes compliance frameworks for AI systems, generative AI adoption, algorithmic bias prevention, human-in-the-loop controls for high-risk applications, and data lineage tracking.",
        "clauses": [
            {
                "clause_id": "POL-GOV-004-C01",
                "section_number": "1.1",
                "section_title": "High-Risk AI System Classification & Risk Register",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Any artificial intelligence, machine learning, or automated scoring system used to make or substantially influence decisions concerning creditworthiness, employment screening, customer identity verification, healthcare recommendations, or insurance pricing is classified as a High-Risk AI System. Such systems must be registered in the Corporate AI Registry and undergo formal Model Risk Committee (MRC) approval prior to deployment.",
                "key_terms": ["high-risk AI", "algorithmic scoring", "creditworthiness", "model registry", "EU AI Act"],
                "penalty_severity": RiskLevel.CRITICAL,
                "regulatory_framework": "EU Artificial Intelligence Act (Regulation 2024/1689) Annex III; NIST AI RMF 1.0",
            },
            {
                "clause_id": "POL-GOV-004-C02",
                "section_number": "2.3",
                "section_title": "Human-in-the-Loop (HITL) for Automated Customer Decisions",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Fully autonomous decisions that produce legal effects or significantly affect individuals (such as loan rejections, account terminations, or hiring disqualifications) are strictly prohibited without meaningful Human-in-the-Loop (HITL) oversight. A qualified human reviewer must possess the operational authority, capability, and time to understand the algorithmic rationale and override the recommendation.",
                "key_terms": ["human-in-the-loop", "HITL", "autonomous decisions", "override", "human oversight"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "GDPR Article 22 (Automated Decision Making); EU AI Act Article 14",
            },
            {
                "clause_id": "POL-GOV-004-C03",
                "section_number": "3.2",
                "section_title": "Algorithmic Bias Testing & Disparate Impact Disparity Ratio",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Prior to release and quarterly thereafter, all predictive models affecting end-users must undergo demographic parity and disparate impact testing across protected characteristics (race, gender, age, religion). The disparate impact ratio between any protected group and the baseline group must not fall below 0.80 (four-fifths rule). Any model breaching this threshold must be suspended immediately.",
                "key_terms": ["algorithmic bias", "disparate impact", "four-fifths rule", "0.80", "fairness audit"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "EEOC Uniform Guidelines on Employee Selection Procedures; FTC Fair Lending AI Guidance",
            },
            {
                "clause_id": "POL-GOV-004-C04",
                "section_number": "4.1",
                "section_title": "Generative AI & LLM Input Data Confidentiality",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Employees and engineering systems are prohibited from entering non-public corporate intellectual property, source code, customer personal data (PII), or confidential contract terms into external public generative AI platforms (e.g., public consumer web chatbots) unless an enterprise agreement with strict zero-data-retention and zero-model-training clauses is officially executed.",
                "key_terms": ["generative AI", "LLM", "confidentiality", "zero data retention", "prompt data leakage"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "Enterprise Trade Secret Protection; GDPR Art. 5; ISO 42001",
            },
            {
                "clause_id": "POL-GOV-004-C05",
                "section_number": "5.2",
                "section_title": "Model Explainability & Adverse Action Notices",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "When an AI model produces an adverse outcome against a consumer, the system must generate a human-readable explanation specifying the top 4 contributing feature factors (e.g., using SHAP or LIME attributions). The affected individual must be provided with an Adverse Action Notice within 30 days clearly stating the key reasons for the outcome.",
                "key_terms": ["explainability", "SHAP", "adverse action notice", "interpretability", "consumer disclosure"],
                "penalty_severity": RiskLevel.MEDIUM,
                "regulatory_framework": "Equal Credit Opportunity Act (ECOA) 12 CFR 1002.9; FCRA § 615(a)",
            }
        ]
    },
    {
        "policy_id": "POL-FIN-005",
        "policy_name": "Insider Trading, Securities Transactions & Market Conduct Policy",
        "category": "Securities & Financial Conduct",
        "business_area": "Finance, Executive Leadership & Legal",
        "version": "3.0",
        "effective_date": "2025-01-01",
        "owner": "General Counsel & Chief Financial Officer",
        "pdf_filename": "POL-FIN-005_Insider_Trading_Securities.pdf",
        "description": "Prohibits trading on or disseminating Material Non-Public Information (MNPI), institutes trading blackout windows, and mandates transaction pre-clearance for designated insiders.",
        "clauses": [
            {
                "clause_id": "POL-FIN-005-C01",
                "section_number": "1.2",
                "section_title": "Prohibition on Trading on Material Non-Public Information (MNPI)",
                "requirement_type": RequirementType.PROHIBITED,
                "clause_text": "No director, officer, employee, or contractor who possesses Material Non-Public Information (MNPI) concerning the company, business partners, prospective acquisition targets, or public clients may buy or sell securities of such entities, nor communicate such information ('tipping') to any other person. MNPI includes non-public quarterly financial results, major contract wins/losses, merger discussions, or executive departures.",
                "key_terms": ["insider trading", "MNPI", "tipping", "material non-public information", "securities"],
                "penalty_severity": RiskLevel.CRITICAL,
                "regulatory_framework": "Securities Exchange Act of 1934 Section 10(b) & Rule 10b-5; Market Abuse Regulation (MAR)",
            },
            {
                "clause_id": "POL-FIN-005-C02",
                "section_number": "2.1",
                "section_title": "Mandatory Pre-Clearance for Covered Insiders",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "All Designated Insiders (including all Vice Presidents and above, finance personnel, and legal team members) must submit a written Pre-Clearance Request to the Legal Department at least two full business days before executing any purchase, sale, gift, or option exercise of company securities. Pre-clearance is valid for five trading days.",
                "key_terms": ["pre-clearance", "designated insider", "legal approval", "securities trade"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "SEC Regulation S-K Item 408; Corporate Governance Guidelines",
            },
            {
                "clause_id": "POL-FIN-005-C03",
                "section_number": "3.1",
                "section_title": "Mandatory Quarterly Blackout Periods",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Quarterly Trading Blackout Periods commence on the 15th calendar day of the final month of each fiscal quarter and conclude at the end of the second full trading day following the public dissemination of the company quarterly financial results. During blackout windows, all trading in company securities by covered personnel is strictly prohibited.",
                "key_terms": ["blackout period", "trading window", "earnings release", "covered personnel"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "Sarbanes-Oxley Act Sec. 306(a); SEC Insider Trading Regulations",
            },
            {
                "clause_id": "POL-FIN-005-C04",
                "section_number": "4.2",
                "section_title": "Information Barriers & Ethical Walls",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Business units engaged in confidential transactional advisory, investment banking, or M&A diligence must maintain physical and logical Ethical Walls. Personnel behind the wall may not share document access, shared drive folders, or discuss project specifics with employees on public trading desks or retail advisory teams.",
                "key_terms": ["ethical wall", "information barrier", "Chinese wall", "M&A", "data segregation"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "FINRA Rule 2241; SEC Section 15(g) of the Exchange Act",
            }
        ]
    },
    {
        "policy_id": "POL-ETH-006",
        "policy_name": "Anti-Bribery, Anti-Corruption & Corporate Hospitality Policy",
        "category": "Anti-Bribery & Corruption",
        "business_area": "Sales, Business Development & Procurement",
        "version": "3.1",
        "effective_date": "2025-01-10",
        "owner": "Chief Ethics & Compliance Officer",
        "pdf_filename": "POL-ETH-006_Anti_Bribery_Hospitality.pdf",
        "description": "Establishes zero tolerance for bribery, strict caps and approvals for corporate gifts and hospitality, mandatory third-party due diligence, and rules governing public official interactions.",
        "clauses": [
            {
                "clause_id": "POL-ETH-006-C01",
                "section_number": "1.1",
                "section_title": "Zero Tolerance for Bribes, Kickbacks & Facilitation Payments",
                "requirement_type": RequirementType.PROHIBITED,
                "clause_text": "Employees, agents, and representatives are unconditionally prohibited from offering, promising, giving, requesting, or receiving any bribe, kickback, improper payment, or item of value to or from any person, whether in the private or public sector, to secure an improper commercial advantage. Facilitation or 'grease' payments to expedite routine administrative services are strictly prohibited regardless of local custom.",
                "key_terms": ["bribery", "kickbacks", "facilitation payments", "improper advantage", "FCPA"],
                "penalty_severity": RiskLevel.CRITICAL,
                "regulatory_framework": "Foreign Corrupt Practices Act (FCPA) 15 U.S.C. § 78dd; UK Bribery Act 2010 Section 1 & 6",
            },
            {
                "clause_id": "POL-ETH-006-C02",
                "section_number": "2.2",
                "section_title": "Corporate Gifts & Hospitality Expenditure Limits ($100 Threshold)",
                "requirement_type": RequirementType.CONDITIONAL,
                "clause_text": "Gifts, meals, entertainment, or corporate hospitality offered to or received from non-government business contacts must not exceed $100 per person per occasion, and may not exceed an aggregate of $250 per individual per calendar year. Any gift or meal exceeding $100 requires prior written approval from the Department Vice President and compliance log registration.",
                "key_terms": ["gifts", "hospitality", "meals", "$100 limit", "entertainment", "approval"],
                "penalty_severity": RiskLevel.MEDIUM,
                "regulatory_framework": "DOJ Evaluation of Corporate Compliance Programs; ISO 37001",
            },
            {
                "clause_id": "POL-ETH-006-C03",
                "section_number": "3.1",
                "section_title": "Mandatory Pre-Approval for Interactions with Government Officials",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Providing any gift, meal, travel reimbursement, conference fee, or entertainment to any foreign or domestic Government Official, state-owned enterprise (SOE) employee, or candidate for public office, regardless of value, requires advance written pre-clearance from the Legal & Compliance Department. Unapproved hospitality to officials is a severe policy breach.",
                "key_terms": ["government official", "public official", "state-owned enterprise", "pre-approval", "travel"],
                "penalty_severity": RiskLevel.CRITICAL,
                "regulatory_framework": "FCPA Provisions on Foreign Officials; UK Bribery Act Sec. 6",
            },
            {
                "clause_id": "POL-ETH-006-C04",
                "section_number": "4.3",
                "section_title": "Third-Party Intermediary Due Diligence & Anti-Corruption Clauses",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Before retaining any sales agent, distributor, lobbyist, customs broker, or joint venture partner operating in international jurisdictions, the business unit must conduct an anti-corruption background check, verify ultimate ownership, and ensure the contract includes standard anti-bribery representations, audit rights, and immediate termination provisions for corruption violations.",
                "key_terms": ["intermediaries", "sales agents", "distributor due diligence", "anti-corruption clause", "audit rights"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "DOJ FCPA Resource Guide 2nd Ed; OECD Anti-Bribery Convention",
            }
        ]
    },
    {
        "policy_id": "POL-BIO-007",
        "policy_name": "Biomedical Research, Clinical Data Sharing & Patient Privacy Policy",
        "category": "Healthcare & Life Sciences Compliance",
        "business_area": "Clinical Research, R&D & Health Informatics",
        "version": "2.2",
        "effective_date": "2025-02-15",
        "owner": "Chief Medical Officer & Institutional Review Board (IRB)",
        "pdf_filename": "POL-BIO-007_Biomedical_HIPAA_Clinical.pdf",
        "description": "Governs the ethical collection, de-identification, secure processing, and publication of human health data, clinical trial records, and biomedical abstracts adhering to HIPAA and FDA regulations.",
        "clauses": [
            {
                "clause_id": "POL-BIO-007-C01",
                "section_number": "1.2",
                "section_title": "Protected Health Information (PHI) De-Identification Standards",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Patient clinical abstracts, diagnostic records, or genomic data used for secondary research, machine learning training, or academic publication must undergo complete de-identification in accordance with the HIPAA Privacy Rule Safe Harbor standard by removing all 18 specified direct and indirect identifiers (names, dates, geographic data below state level, medical record numbers, biometric IDs), or through statistical certification by a qualified expert.",
                "key_terms": ["PHI", "HIPAA", "Safe Harbor", "de-identification", "18 identifiers", "clinical abstracts"],
                "penalty_severity": RiskLevel.CRITICAL,
                "regulatory_framework": "HIPAA Privacy Rule 45 CFR § 164.514(b); HITECH Act",
            },
            {
                "clause_id": "POL-BIO-007-C02",
                "section_number": "2.1",
                "section_title": "Institutional Review Board (IRB) Protocol & Informed Consent",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Any research study, biobanking initiative, or secondary analysis involving human subjects or identifiable private health information must receive formal Institutional Review Board (IRB) approval prior to data ingestion. Participants must execute an Informed Consent Form that explicitly enumerates prospective secondary use, algorithmic analysis, and potential third-party research collaboration.",
                "key_terms": ["IRB", "informed consent", "clinical trial", "human subjects", "secondary use"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "Common Rule 45 CFR 46; FDA 21 CFR Parts 50 & 56",
            },
            {
                "clause_id": "POL-BIO-007-C03",
                "section_number": "3.3",
                "section_title": "Business Associate Agreements (BAA) for Health Data Clouds",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Cloud service providers, high-performance computing clusters, or AI infrastructure vendors storing or processing Protected Health Information (PHI) or identifiable clinical datasets must enter into a formal Business Associate Agreement (BAA) with the organization prior to any data transmission. Storing PHI on non-BAA covered commercial cloud tiers is strictly prohibited.",
                "key_terms": ["BAA", "business associate agreement", "health cloud", "HIPAA security", "PHI storage"],
                "penalty_severity": RiskLevel.CRITICAL,
                "regulatory_framework": "HIPAA Security Rule 45 CFR Part 160 & Part 164 Subparts A & C",
            },
            {
                "clause_id": "POL-BIO-007-C04",
                "section_number": "4.2",
                "section_title": "Electronic Records Audit Trail & FDA 21 CFR Part 11 Compliance",
                "requirement_type": RequirementType.MANDATORY,
                "clause_text": "Electronic systems used to manage clinical trial data, electronic case report forms (eCRF), or bio-sample tracking must maintain computer-generated, time-stamped audit trails that independently record the date, time, and operator of any entry, modification, or deletion. System access requires unique electronic signatures meeting FDA 21 CFR Part 11 criteria.",
                "key_terms": ["audit trail", "FDA 21 CFR Part 11", "clinical trials", "electronic signatures", "eCRF"],
                "penalty_severity": RiskLevel.HIGH,
                "regulatory_framework": "FDA 21 CFR Part 11; Good Clinical Practice (GCP) ICH E6(R2)",
            }
        ]
    }
]

def generate_pdf_for_policy(policy_data: Dict, output_path: Path):
    """Generates an official enterprise PDF document for the policy."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=4,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    badge_style = ParagraphStyle(
        'BadgeText',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0369A1'),
        fontName='Helvetica-Bold'
    )

    elements = []

    # Header / Meta Table
    header_data = [
        [
            Paragraph(f"<b>ORGANIZATIONAL POLICY MANUAL</b>", styles['Normal']),
            Paragraph(f"<b>Policy Code:</b> {policy_data['policy_id']}", styles['Normal'])
        ],
        [
            Paragraph(f"<b>Document:</b> {policy_data['policy_name']}", styles['Normal']),
            Paragraph(f"<b>Version:</b> {policy_data['version']} | <b>Effective:</b> {policy_data['effective_date']}", styles['Normal'])
        ],
        [
            Paragraph(f"<b>Category:</b> {policy_data['category']}", styles['Normal']),
            Paragraph(f"<b>Business Area:</b> {policy_data['business_area']}", styles['Normal'])
        ],
        [
            Paragraph(f"<b>Compliance Owner:</b> {policy_data['owner']}", styles['Normal']),
            Paragraph(f"<b>Classification:</b> Confidential - Internal Corporate Use", styles['Normal'])
        ]
    ]

    header_table = Table(header_data, colWidths=[330, 190])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))

    elements.append(Paragraph(policy_data['policy_name'], title_style))
    elements.append(Paragraph(f"Enterprise Compliance Directive • Ref: {policy_data['policy_id']}", subtitle_style))
    elements.append(header_table)
    elements.append(Spacer(1, 14))

    # Overview
    elements.append(Paragraph("<b>1. Policy Purpose & Executive Scope</b>", h2_style))
    elements.append(Paragraph(policy_data['description'], body_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E2E8F0'), spaceBefore=8, spaceAfter=12))

    # Clauses
    elements.append(Paragraph("<b>2. Binding Regulatory Clauses & Compliance Requirements</b>", h2_style))

    for clause in policy_data['clauses']:
        cid = clause['clause_id']
        s_num = clause['section_number']
        s_title = clause['section_title']
        req_type = clause['requirement_type'].value if hasattr(clause['requirement_type'], 'value') else clause['requirement_type']
        text = clause['clause_text']
        framework = clause['regulatory_framework']
        severity = clause['penalty_severity'].value if hasattr(clause['penalty_severity'], 'value') else clause['penalty_severity']

        clause_header = f"<b>Section {s_num}: {s_title}</b> &nbsp;&nbsp; [<font color='#2563EB'>{cid}</font>]"
        elements.append(Paragraph(clause_header, h2_style))

        # Meta tags
        meta_html = f"<b>Requirement:</b> {req_type} &nbsp;|&nbsp; <b>Risk Impact:</b> {severity} &nbsp;|&nbsp; <b>Regulatory Base:</b> {framework}"
        elements.append(Paragraph(meta_html, badge_style))
        elements.append(Spacer(1, 3))
        elements.append(Paragraph(text, body_style))
        elements.append(Spacer(1, 6))

    doc.build(elements)

def generate_policy_corpus():
    """Generates all PDF files and builds the canonical knowledge base JSON."""
    RAW_POLICIES_DIR.mkdir(parents=True, exist_ok=True)
    all_policies = []
    total_clauses = 0

    print("Building Policy Corpus & Generating Official PDF Documents...")
    for p_data in POLICIES_DATA:
        pdf_path = RAW_POLICIES_DIR / p_data["pdf_filename"]
        generate_pdf_for_policy(p_data, pdf_path)
        print(f"Generated PDF: {pdf_path.name}")

        # Construct PolicyDocument schema
        clauses_obj = []
        for c in p_data["clauses"]:
            c_copy = dict(c)
            c_copy["policy_id"] = p_data["policy_id"]
            c_copy["policy_name"] = p_data["policy_name"]
            c_copy["category"] = p_data["category"]
            c_copy["business_area"] = p_data["business_area"]
            c_copy["source_file"] = p_data["pdf_filename"]
            c_copy["version"] = p_data["version"]
            c_copy["effective_date"] = p_data["effective_date"]
            clauses_obj.append(c_copy)
            total_clauses += 1

        doc_dict = dict(p_data)
        doc_dict["clauses"] = clauses_obj
        all_policies.append(doc_dict)

    # Save to knowledge_base.json
    with open(KB_PATH, "w", encoding="utf-8") as f:
        json.dump(all_policies, f, indent=2)

    print(f"Successfully generated {len(all_policies)} policies with {total_clauses} clauses.")
    print(f"Knowledge base saved to: {KB_PATH}")
    return all_policies

if __name__ == "__main__":
    generate_policy_corpus()
