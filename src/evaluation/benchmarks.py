from typing import List
from src.models.schemas import BenchmarkScenario, ComplianceVerdict, RiskLevel

BENCHMARK_SCENARIOS: List[BenchmarkScenario] = [
    BenchmarkScenario(
        scenario_id="SCN-KYC-01",
        title="Customer Onboarding with Single ID & No Address Proof",
        domain="Anti-Money Laundering",
        scenario_text="A new retail client is attempting to open an investment account. The onboarding representative collected a single state driver's license but omitted residential address proof because the customer claims they recently relocated.",
        expected_policies=["POL-KYC-001"],
        expected_verdict=ComplianceVerdict.NON_COMPLIANT,
        expected_risk_level=RiskLevel.HIGH,
        key_compliance_questions=["Does this customer onboarding process comply with our KYC policy?"],
        description="Tests mandatory Customer Identification Program (CIP) requirements requiring dual government identification and 90-day address proof."
    ),
    BenchmarkScenario(
        scenario_id="SCN-KYC-02",
        title="Corporate Onboarding with Verified Dual IDs and Utility Bill",
        domain="Anti-Money Laundering",
        scenario_text="The operations team verified customer identity using two government IDs (valid passport and driver's license) along with a utility bill dated 25 days ago. Full beneficial ownership registers were verified.",
        expected_policies=["POL-KYC-001"],
        expected_verdict=ComplianceVerdict.COMPLIANT,
        expected_risk_level=RiskLevel.LOW,
        key_compliance_questions=["Is this verified onboarding process fully compliant with AML standards?"],
        description="Standard fully compliant customer onboarding flow."
    ),
    BenchmarkScenario(
        scenario_id="SCN-PRV-01",
        title="Third-Party Vendor Analytics Transfer Without DPA Over Plaintext HTTP",
        domain="Data Privacy & Protection",
        scenario_text="The growth engineering team wants to transmit EU customer personal profiles and purchase histories to a US cloud analytics vendor before signing a Data Processing Agreement (DPA). The transfer will use plaintext HTTP to accelerate deployment.",
        expected_policies=["POL-PRV-002"],
        expected_verdict=ComplianceVerdict.NON_COMPLIANT,
        expected_risk_level=RiskLevel.CRITICAL,
        key_compliance_questions=["What approvals are required before sharing customer information with a third party?"],
        description="Tests prohibition of unencrypted data transmission and mandatory requirement for bilateral Data Processing Agreement."
    ),
    BenchmarkScenario(
        scenario_id="SCN-PRV-02",
        title="Vendor Data Processing with Executed DPA & TLS 1.3 Encryption",
        domain="Data Privacy & Protection",
        scenario_text="Customer support records are synced to an EU SaaS vendor. A bilateral DPA containing Standard Contractual Clauses has been executed, customer consent was captured, and transmission is secured via TLS 1.3 with AES-256 at-rest encryption.",
        expected_policies=["POL-PRV-002"],
        expected_verdict=ComplianceVerdict.COMPLIANT,
        expected_risk_level=RiskLevel.LOW,
        key_compliance_questions=["Does this vendor data sharing workflow satisfy GDPR Article 28?"],
        description="Fully compliant third-party data sharing workflow."
    ),
    BenchmarkScenario(
        scenario_id="SCN-SEC-01",
        title="Direct Root SSH Production Access Without PAM Bastion",
        domain="Information Security",
        scenario_text="An infrastructure engineer requests permanent standing root administrator access and direct SSH login to live production database clusters, bypassing the PAM bastion and dual-manager approval.",
        expected_policies=["POL-SEC-003"],
        expected_verdict=ComplianceVerdict.NON_COMPLIANT,
        expected_risk_level=RiskLevel.CRITICAL,
        key_compliance_questions=["Does this proposed transaction violate any internal compliance requirements?"],
        description="Tests prohibition on standing root privileges and mandatory JIT PAM bastion controls."
    ),
    BenchmarkScenario(
        scenario_id="SCN-SEC-02",
        title="Just-In-Time (JIT) Bastion Access with Dual Approval",
        domain="Information Security",
        scenario_text="A DevOps lead requests 2-hour emergency database access via the Privileged Access Management (PAM) bastion with dual engineering manager sign-off, FIDO2 MFA verification, and automatic session recording.",
        expected_policies=["POL-SEC-003"],
        expected_verdict=ComplianceVerdict.COMPLIANT,
        expected_risk_level=RiskLevel.LOW,
        key_compliance_questions=["Does this emergency access workflow meet ISO 27001 access control directives?"],
        description="Compliant emergency access workflow adhering to Least Privilege."
    ),
    BenchmarkScenario(
        scenario_id="SCN-GOV-01",
        title="Autonomous AI Loan Rejection with Disparate Impact 0.68 & No Human Review",
        domain="AI Governance & Ethics",
        scenario_text="The credit division deployed a machine learning model that automatically rejects consumer mortgage applications without Human-in-the-Loop oversight. Preliminary testing shows a disparate impact ratio of 0.68 against protected demographic groups.",
        expected_policies=["POL-GOV-004"],
        expected_verdict=ComplianceVerdict.NON_COMPLIANT,
        expected_risk_level=RiskLevel.CRITICAL,
        key_compliance_questions=["Does this automated AI decision system comply with enterprise AI governance?"],
        description="Tests EU AI Act and ECOA requirements for Human-in-the-Loop and 0.80 four-fifths bias ratio."
    ),
    BenchmarkScenario(
        scenario_id="SCN-FIN-01",
        title="Executive Securities Trading During Quarterly Earnings Blackout Window",
        domain="Securities & Financial Conduct",
        scenario_text="A corporate Vice President plans to sell 10,000 company shares two days prior to the public quarterly earnings announcement without submitting a written pre-clearance request to Legal.",
        expected_policies=["POL-FIN-005"],
        expected_verdict=ComplianceVerdict.NON_COMPLIANT,
        expected_risk_level=RiskLevel.CRITICAL,
        key_compliance_questions=["Does this proposed transaction violate insider trading and market conduct policies?"],
        description="Tests mandatory blackout period and SEC Rule 10b-5 pre-clearance mandates."
    ),
    BenchmarkScenario(
        scenario_id="SCN-ETH-01",
        title="Providing $1,500 Luxury Dinner to Foreign State Enterprise Official",
        domain="Anti-Bribery & Corruption",
        scenario_text="A sales executive wishes to host a foreign state-owned energy company director for a $1,500 luxury dinner and golf outing to influence an upcoming sovereign procurement contract without compliance pre-approval.",
        expected_policies=["POL-ETH-006"],
        expected_verdict=ComplianceVerdict.NON_COMPLIANT,
        expected_risk_level=RiskLevel.CRITICAL,
        key_compliance_questions=["Does this hospitality expenditure violate our Anti-Bribery and FCPA policy?"],
        description="Tests FCPA foreign government official pre-approval and $100 hospitality limit."
    ),
    BenchmarkScenario(
        scenario_id="SCN-BIO-01",
        title="Biomedical Secondary AI Research on Raw PHI Without BAA or De-Identification",
        domain="Healthcare & Life Sciences Compliance",
        scenario_text="A bioinformatics team is uploading 5,000 raw patient clinical abstracts containing medical record numbers, full names, and exact admission dates to a commercial public cloud service without a Business Associate Agreement (BAA) or HIPAA Safe Harbor de-identification.",
        expected_policies=["POL-BIO-007"],
        expected_verdict=ComplianceVerdict.NON_COMPLIANT,
        expected_risk_level=RiskLevel.CRITICAL,
        key_compliance_questions=["What evidence supports this compliance decision regarding clinical health records?"],
        description="Tests HIPAA Safe Harbor 18 identifiers removal and mandatory Cloud BAA requirements."
    )
]
