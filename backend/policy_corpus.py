"""
Policy Corpus Module.
Contains pre-loaded enterprise policies across multiple compliance domains:
- Banking / KYC & AML (POL-KYC-001)
- Data Privacy & HIPAA / GDPR (POL-HIPAA-002)
- Information Security & Vendor Risk (POL-SEC-003)
- Corporate Governance & FCPA Anti-Bribery (POL-GOV-004)
- Financial Operations & OFAC Sanctions (POL-FIN-005)
"""

from typing import List
from models import PolicyClause, MandatoryLevel

POLICY_DOCUMENTS = [
    {
        "policy_id": "POL-KYC-001",
        "policy_name": "Global Anti-Money Laundering & Know Your Customer (KYC) Policy",
        "policy_category": "KYC / AML",
        "applicable_business_area": "Customer Onboarding & Banking Operations",
        "effective_date": "2025-01-15",
        "source_document": "POL-KYC-001_AML_KYC_Policy_v4.pdf"
    },
    {
        "policy_id": "POL-HIPAA-002",
        "policy_name": "Healthcare Information Privacy & Business Associate Policy",
        "policy_category": "Data Privacy & Healthcare",
        "applicable_business_area": "Health Operations & IT Infrastructure",
        "effective_date": "2025-02-01",
        "source_document": "POL-HIPAA-002_Data_Privacy_Policy_v3.pdf"
    },
    {
        "policy_id": "POL-SEC-003",
        "policy_name": "Enterprise Information Security & Third-Party Vendor Risk Policy",
        "policy_category": "Information Security",
        "applicable_business_area": "IT, Vendor Management & Cloud Infrastructure",
        "effective_date": "2025-03-01",
        "source_document": "POL-SEC-003_InfoSec_Vendor_Risk_v5.pdf"
    },
    {
        "policy_id": "POL-GOV-004",
        "policy_name": "Code of Business Conduct, FCPA Anti-Bribery & Gifts Policy",
        "policy_category": "Corporate Governance",
        "applicable_business_area": "Sales, Executive Management & Procurement",
        "effective_date": "2025-01-01",
        "source_document": "POL-GOV-004_Code_of_Conduct_v2.pdf"
    },
    {
        "policy_id": "POL-FIN-005",
        "policy_name": "International Financial Transfers & OFAC Sanctions Screening Policy",
        "policy_category": "Financial Operations",
        "applicable_business_area": "Treasury, International Banking & Wire Operations",
        "effective_date": "2025-02-15",
        "source_document": "POL-FIN-005_OFAC_Sanctions_Policy_v4.pdf"
    }
]

RAW_POLICY_CLAUSES = [
    # --- POL-KYC-001 ---
    {
        "clause_id": "KYC-1.1",
        "policy_id": "POL-KYC-001",
        "policy_name": "Global Anti-Money Laundering & Know Your Customer (KYC) Policy",
        "policy_category": "KYC / AML",
        "applicable_business_area": "Customer Onboarding & Banking Operations",
        "section_title": "Customer Identification Program (CIP) Baseline Verification",
        "section_number": "1.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "All new institutional and individual customer accounts MUST undergo Customer Identification Program (CIP) verification prior to account activation. CIP verification requires validating government-issued photo identification, proof of legal address (utility bill or bank statement within 90 days), and tax identification number (SSN/EIN). Accounts missing any required verification document MUST NOT be opened or permitted to execute financial transactions.",
        "key_keywords": ["cip", "customer identification", "photo id", "proof of address", "ein", "ssn", "onboarding"],
        "effective_date": "2025-01-15",
        "source_document": "POL-KYC-001_AML_KYC_Policy_v4.pdf"
    },
    {
        "clause_id": "KYC-1.2",
        "policy_id": "POL-KYC-001",
        "policy_name": "Global Anti-Money Laundering & Know Your Customer (KYC) Policy",
        "policy_category": "KYC / AML",
        "applicable_business_area": "Customer Onboarding & Banking Operations",
        "section_title": "Enhanced Due Diligence (EDD) for Politically Exposed Persons (PEPs)",
        "section_number": "1.2",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Enhanced Due Diligence (EDD) MUST be performed for all high-risk accounts, including Politically Exposed Persons (PEPs), foreign senior political figures, and entities headquartered in FATF non-cooperative jurisdictions. EDD requires establishing the documented Source of Funds (SOF) and Source of Wealth (SOW), along with mandatory formal written approval from the Money Laundering Reporting Officer (MLRO) before establishing a business relationship.",
        "key_keywords": ["edd", "pep", "politically exposed person", "mlro approval", "source of funds", "source of wealth", "fatf"],
        "effective_date": "2025-01-15",
        "source_document": "POL-KYC-001_AML_KYC_Policy_v4.pdf"
    },
    {
        "clause_id": "KYC-2.1",
        "policy_id": "POL-KYC-001",
        "policy_name": "Global Anti-Money Laundering & Know Your Customer (KYC) Policy",
        "policy_category": "KYC / AML",
        "applicable_business_area": "Customer Onboarding & Banking Operations",
        "section_title": "Beneficial Ownership Disclosure Thresholds",
        "section_number": "2.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "For corporate customer onboarding, the organization MUST identify and verify all Ultimate Beneficial Owners (UBOs) who directly or indirectly hold 25% or more equity interest or voting rights in the legal entity. For high-risk corporate structures, the compliance team MAY lower the beneficial ownership disclosure threshold to 10%. Failure to identify all required UBOs prevents account opening.",
        "key_keywords": ["ubo", "beneficial owner", "ultimate beneficial ownership", "25 percent threshold", "corporate entity"],
        "effective_date": "2025-01-15",
        "source_document": "POL-KYC-001_AML_KYC_Policy_v4.pdf"
    },
    {
        "clause_id": "KYC-3.1",
        "policy_id": "POL-KYC-001",
        "policy_name": "Global Anti-Money Laundering & Know Your Customer (KYC) Policy",
        "policy_category": "KYC / AML",
        "applicable_business_area": "Customer Onboarding & Banking Operations",
        "section_title": "Suspicious Activity Reporting (SAR) Filing Timelines",
        "section_number": "3.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Any transaction or pattern of activity exceeding $10,000 USD that lacks a clear economic rationale or triggers automated AML monitoring flags MUST be referred to the Compliance Investigations Unit within 24 hours. If confirmed suspicious, a Suspicious Activity Report (SAR) MUST be filed with FinCEN within 30 calendar days. Disclosing SAR filing details to the customer is strictly prohibited by law.",
        "key_keywords": ["sar", "suspicious activity report", "fincen", "10000 threshold", "investigations unit", "anti tipping off"],
        "effective_date": "2025-01-15",
        "source_document": "POL-KYC-001_AML_KYC_Policy_v4.pdf"
    },

    # --- POL-HIPAA-002 ---
    {
        "clause_id": "HIPAA-1.1",
        "policy_id": "POL-HIPAA-002",
        "policy_name": "Healthcare Information Privacy & Business Associate Policy",
        "policy_category": "Data Privacy & Healthcare",
        "applicable_business_area": "Health Operations & IT Infrastructure",
        "section_title": "Protected Health Information (PHI) Access Restrictions",
        "section_number": "1.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Access to Protected Health Information (PHI) and Electronic Protected Health Information (ePHI) MUST be restricted strictly according to the 'Minimum Necessary' principle. Employees and systems MAY only access the specific PHI fields required to perform their explicit job function. Role-Based Access Controls (RBAC) MUST be enforced and audited quarterly.",
        "key_keywords": ["phi", "ephi", "minimum necessary", "rbac", "role based access control", "hipaa", "privacy"],
        "effective_date": "2025-02-01",
        "source_document": "POL-HIPAA-002_Data_Privacy_Policy_v3.pdf"
    },
    {
        "clause_id": "HIPAA-2.1",
        "policy_id": "POL-HIPAA-002",
        "policy_name": "Healthcare Information Privacy & Business Associate Policy",
        "policy_category": "Data Privacy & Healthcare",
        "applicable_business_area": "Health Operations & IT Infrastructure",
        "section_title": "Business Associate Agreements (BAA) for Third-Party Vendors",
        "section_number": "2.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Prior to transferring, sharing, or allowing third-party vendors, SaaS tools, AI models, or contractors access to PHI or ePHI, a formal executed Business Associate Agreement (BAA) MUST be in place. The BAA MUST mandate HIPAA compliance, prompt breach notification (within 72 hours), and explicit restrictions prohibiting third parties from training public AI models on ingested PHI.",
        "key_keywords": ["baa", "business associate agreement", "third party vendor", "phi disclosure", "ai training restriction", "72 hour breach notification"],
        "effective_date": "2025-02-01",
        "source_document": "POL-HIPAA-002_Data_Privacy_Policy_v3.pdf"
    },
    {
        "clause_id": "HIPAA-3.1",
        "policy_id": "POL-HIPAA-002",
        "policy_name": "Healthcare Information Privacy & Business Associate Policy",
        "policy_category": "Data Privacy & Healthcare",
        "applicable_business_area": "Health Operations & IT Infrastructure",
        "section_title": "PHI Encryption Standards in Transit & At Rest",
        "section_number": "3.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "All electronic PHI MUST be encrypted at rest using AES-256 bit encryption algorithms and in transit across external or internal networks using TLS 1.3. Storing unencrypted PHI on endpoints, mobile devices, local drives, or unapproved cloud storage services is strictly prohibited and constitutes a major compliance violation.",
        "key_keywords": ["encryption", "aes-256", "tls 1.3", "phi at rest", "phi in transit", "unencrypted data"],
        "effective_date": "2025-02-01",
        "source_document": "POL-HIPAA-002_Data_Privacy_Policy_v3.pdf"
    },
    {
        "clause_id": "HIPAA-4.1",
        "policy_id": "POL-HIPAA-002",
        "policy_name": "Healthcare Information Privacy & Business Associate Policy",
        "policy_category": "Data Privacy & Healthcare",
        "applicable_business_area": "Health Operations & IT Infrastructure",
        "section_title": "Patient Consent & Secondary Data Usage Controls",
        "section_number": "4.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Using patient data for non-treatment operational research, commercial monetization, or secondary analytics MUST require explicit opt-in written consent from the individual patient or full Expert Determination De-identification in accordance with 45 CFR 164.514(b). De-identified datasets MUST remove 18 HIPAA identifiers.",
        "key_keywords": ["patient consent", "secondary use", "de-identification", "18 identifiers", "opt-in", "commercial monetization"],
        "effective_date": "2025-02-01",
        "source_document": "POL-HIPAA-002_Data_Privacy_Policy_v3.pdf"
    },

    # --- POL-SEC-003 ---
    {
        "clause_id": "SEC-1.1",
        "policy_id": "POL-SEC-003",
        "policy_name": "Enterprise Information Security & Third-Party Vendor Risk Policy",
        "policy_category": "Information Security",
        "applicable_business_area": "IT, Vendor Management & Cloud Infrastructure",
        "section_title": "Vendor Security Assessment & SOC 2 Audits",
        "section_number": "1.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Every third-party software, cloud service, or external vendor processing company data classified as 'Restricted' or 'Confidential' MUST undergo a comprehensive Information Security Risk Assessment before contract execution. Vendors MUST provide an active SOC 2 Type II report (covering Security, Availability, and Confidentiality) or ISO 27001 certification dated within the past 12 months.",
        "key_keywords": ["vendor risk assessment", "soc 2 type ii", "iso 27001", "third party review", "confidential data"],
        "effective_date": "2025-03-01",
        "source_document": "POL-SEC-003_InfoSec_Vendor_Risk_v5.pdf"
    },
    {
        "clause_id": "SEC-2.1",
        "policy_id": "POL-SEC-003",
        "policy_name": "Enterprise Information Security & Third-Party Vendor Risk Policy",
        "policy_category": "Information Security",
        "applicable_business_area": "IT, Vendor Management & Cloud Infrastructure",
        "section_title": "Cross-Border Data Transfer & Geographic Cloud Hosting Constraints",
        "section_number": "2.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Customer and operational datasets classified as 'Confidential' MUST NOT be transferred to or hosted in servers located outside designated compliant jurisdictions (EU, US, UK) without prior written authorization from the Chief Information Security Officer (CISO) and Legal Counsel. Data transfers to jurisdictions without adequacy decisions require Standard Contractual Clauses (SCCs).",
        "key_keywords": ["cross border transfer", "ciso approval", "cloud hosting", "scc", "standard contractual clauses", "data sovereignty"],
        "effective_date": "2025-03-01",
        "source_document": "POL-SEC-003_InfoSec_Vendor_Risk_v5.pdf"
    },
    {
        "clause_id": "SEC-3.1",
        "policy_id": "POL-SEC-003",
        "policy_name": "Enterprise Information Security & Third-Party Vendor Risk Policy",
        "policy_category": "Information Security",
        "applicable_business_area": "IT, Vendor Management & Cloud Infrastructure",
        "section_title": "Multi-Factor Authentication (MFA) & Privileged Access Management",
        "section_number": "3.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Multi-Factor Authentication (MFA) using FIDO2 or hardware token/authenticator app MUST be enforced across all corporate accounts, VPNs, and administrative consoles. SMS-based MFA is prohibited for administrative accounts. Privileged sessions MUST be logged and monitored via Privileged Access Management (PAM).",
        "key_keywords": ["mfa", "multi factor authentication", "fido2", "pam", "privileged access", "admin account"],
        "effective_date": "2025-03-01",
        "source_document": "POL-SEC-003_InfoSec_Vendor_Risk_v5.pdf"
    },
    {
        "clause_id": "SEC-4.1",
        "policy_id": "POL-SEC-003",
        "policy_name": "Enterprise Information Security & Third-Party Vendor Risk Policy",
        "policy_category": "Information Security",
        "applicable_business_area": "IT, Vendor Management & Cloud Infrastructure",
        "section_title": "Data Loss Prevention (DLP) & Source Code Protection",
        "section_number": "4.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Proprietary source code, customer records, and credentials MUST NOT be pasted or uploaded into unvetted public generative AI models, code assistants, or web tools. Employees SHOULD use approved enterprise-managed AI environments with dedicated tenant isolation and non-retention agreements.",
        "key_keywords": ["generative ai", "source code leak", "public ai tools", "dlp", "data loss prevention", "tenant isolation"],
        "effective_date": "2025-03-01",
        "source_document": "POL-SEC-003_InfoSec_Vendor_Risk_v5.pdf"
    },

    # --- POL-GOV-004 ---
    {
        "clause_id": "GOV-1.1",
        "policy_id": "POL-GOV-004",
        "policy_name": "Code of Business Conduct, FCPA Anti-Bribery & Gifts Policy",
        "policy_category": "Corporate Governance",
        "applicable_business_area": "Sales, Executive Management & Procurement",
        "section_title": "Gifts, Hospitality & Entertainment Limits",
        "section_number": "1.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Employees MUST NOT offer, give, or accept gifts, meals, or entertainment exceeding $150 USD per instance (or cumulative $500 USD per year per counterparty) without prior written pre-clearance from the Ethics & Compliance Officer. Giving any gift, meal, or item of value to a foreign government official is strictly prohibited regardless of monetary value under the Foreign Corrupt Practices Act (FCPA).",
        "key_keywords": ["fcpa", "gift policy", "150 limit", "government official", "anti-bribery", "ethics approval"],
        "effective_date": "2025-01-01",
        "source_document": "POL-GOV-004_Code_of_Conduct_v2.pdf"
    },
    {
        "clause_id": "GOV-2.1",
        "policy_id": "POL-GOV-004",
        "policy_name": "Code of Business Conduct, FCPA Anti-Bribery & Gifts Policy",
        "policy_category": "Corporate Governance",
        "applicable_business_area": "Sales, Executive Management & Procurement",
        "section_title": "Conflict of Interest Disclosure & Outside Engagements",
        "section_number": "2.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Employees MUST formally disclose any actual, potential, or perceived conflict of interest to HR and Compliance within 5 business days. Engaging in outside employment, advisory roles, or holding financial interests in competitors, vendors, or business partners requires advance written approval from the Conflict of Interest Committee.",
        "key_keywords": ["conflict of interest", "outside employment", "advisory board", "compliance disclosure", "vendor relationship"],
        "effective_date": "2025-01-01",
        "source_document": "POL-GOV-004_Code_of_Conduct_v2.pdf"
    },
    {
        "clause_id": "GOV-3.1",
        "policy_id": "POL-GOV-004",
        "policy_name": "Code of Business Conduct, FCPA Anti-Bribery & Gifts Policy",
        "policy_category": "Corporate Governance",
        "applicable_business_area": "Sales, Executive Management & Procurement",
        "section_title": "Insider Trading & Material Non-Public Information (MNPI)",
        "section_number": "3.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Trading in company securities or the securities of partner entities while in possession of Material Non-Public Information (MNPI) is strictly illegal and violates corporate policy. Designated insiders MUST adhere to pre-scheduled trading windows and obtain pre-clearance from the General Counsel before executing trades.",
        "key_keywords": ["insider trading", "mnpi", "pre-clearance", "general counsel", "trading window"],
        "effective_date": "2025-01-01",
        "source_document": "POL-GOV-004_Code_of_Conduct_v2.pdf"
    },

    # --- POL-FIN-005 ---
    {
        "clause_id": "FIN-1.1",
        "policy_id": "POL-FIN-005",
        "policy_name": "International Financial Transfers & OFAC Sanctions Screening Policy",
        "policy_category": "Financial Operations",
        "applicable_business_area": "Treasury, International Banking & Wire Operations",
        "section_title": "OFAC Sanctions & SDN List Real-Time Screening",
        "section_number": "1.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "All outbound and inbound international wire transfers, beneficiary accounts, intermediary banks, and trade counterparties MUST be screened in real-time against the US OFAC Specially Designated Nationals (SDN) list, EU Consolidated Sanctions, and UN Sanctions lists prior to payment execution. Any transaction returning a potential match MUST be blocked immediately and referred to Sanctions Compliance.",
        "key_keywords": ["ofac", "sdn list", "sanctions screening", "wire transfer", "blocked transaction", "international payment"],
        "effective_date": "2025-02-15",
        "source_document": "POL-FIN-005_OFAC_Sanctions_Policy_v4.pdf"
    },
    {
        "clause_id": "FIN-2.1",
        "policy_id": "POL-FIN-005",
        "policy_name": "International Financial Transfers & OFAC Sanctions Screening Policy",
        "policy_category": "Financial Operations",
        "applicable_business_area": "Treasury, International Banking & Wire Operations",
        "section_title": "Dual Approval Thresholds for High-Value Wire Transfers",
        "section_number": "2.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Wire transfers exceeding $100,000 USD require dual authorization from two designated Treasury Officers. Wire transfers exceeding $1,000,000 USD MUST additionally obtain written authorization from the Chief Financial Officer (CFO). Splitting transactions to evade authorization thresholds (structuring) is strictly prohibited.",
        "key_keywords": ["wire transfer threshold", "100k dual approval", "cfo authorization", "structuring prohibition", "treasury"],
        "effective_date": "2025-02-15",
        "source_document": "POL-FIN-005_OFAC_Sanctions_Policy_v4.pdf"
    },
    {
        "clause_id": "FIN-3.1",
        "policy_id": "POL-FIN-005",
        "policy_name": "International Financial Transfers & OFAC Sanctions Screening Policy",
        "policy_category": "Financial Operations",
        "applicable_business_area": "Treasury, International Banking & Wire Operations",
        "section_title": "Cryptocurrency & Virtual Asset Payment Restrictions",
        "section_number": "3.1",
        "mandatory_level": MandatoryLevel.MUST,
        "clause_text": "Executing vendor payments or customer transactions using unhosted cryptocurrency wallets, decentralized protocols, or privacy coins (e.g. Monero, Tornado Cash) is strictly prohibited. Virtual asset transfers MAY only occur via regulated Vasps registered with FinCEN with Travel Rule compliance enabled.",
        "key_keywords": ["cryptocurrency", "virtual assets", "unhosted wallet", "fincen travel rule", "privacy coins", "vasp"],
        "effective_date": "2025-02-15",
        "source_document": "POL-FIN-005_OFAC_Sanctions_Policy_v4.pdf"
    }
]


def get_all_policy_clauses() -> List[PolicyClause]:
    """Returns all structured policy clauses as PolicyClause objects."""
    return [PolicyClause(**item) for item in RAW_POLICY_CLAUSES]
