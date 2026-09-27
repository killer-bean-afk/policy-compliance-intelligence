from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class RequirementType(str, Enum):
    MANDATORY = "MANDATORY"
    PROHIBITED = "PROHIBITED"
    CONDITIONAL = "CONDITIONAL"
    RECOMMENDED = "RECOMMENDED"

class ComplianceVerdict(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    CONDITIONAL = "CONDITIONAL"
    INSUFFICIENT_INFO = "INSUFFICIENT_INFO"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class PolicyClause(BaseModel):
    clause_id: str = Field(..., description="Unique clause identifier e.g. POL-KYC-001-C01")
    policy_id: str = Field(..., description="Parent policy identifier e.g. POL-KYC-001")
    policy_name: str = Field(..., description="Full human-readable policy title")
    section_number: str = Field(..., description="Section number e.g. 3.2")
    section_title: str = Field(..., description="Section title e.g. Enhanced Due Diligence (EDD)")
    category: str = Field(..., description="Policy category e.g. Anti-Money Laundering, Data Privacy")
    business_area: str = Field(..., description="Applicable business area e.g. Operations, Compliance, Engineering")
    requirement_type: RequirementType = Field(default=RequirementType.MANDATORY)
    clause_text: str = Field(..., description="Verbatim requirement text")
    key_terms: List[str] = Field(default_factory=list)
    penalty_severity: RiskLevel = Field(default=RiskLevel.MEDIUM)
    regulatory_framework: str = Field(..., description="Associated standard e.g. FinCEN BSA, GDPR Art. 28, HIPAA, ISO 27001")
    source_file: str = Field(default="")
    version: str = Field(default="2.4")
    effective_date: str = Field(default="2025-01-01")

class PolicyDocument(BaseModel):
    policy_id: str
    policy_name: str
    category: str
    business_area: str
    version: str
    effective_date: str
    owner: str
    description: str
    clauses: List[PolicyClause] = Field(default_factory=list)
    pdf_filename: Optional[str] = None

class SearchQuery(BaseModel):
    query: str = Field(..., description="Natural language compliance question or business scenario")
    category: Optional[str] = None
    business_area: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
    include_full_clauses: bool = True

class RetrievedEvidence(BaseModel):
    clause: PolicyClause
    score: float = Field(..., description="Combined hybrid relevance score (0-1)")
    dense_score: float = 0.0
    sparse_score: float = 0.0
    matched_terms: List[str] = Field(default_factory=list)
    highlight_span: Optional[str] = None
    citation_tag: str = Field(..., description="Traceable citation tag e.g. [POL-KYC-001 §3.2]")

class SearchResult(BaseModel):
    query: str
    total_found: int
    results: List[RetrievedEvidence]
    retrieval_time_ms: float

# Multi-Agent Models
class AgentMessage(BaseModel):
    sender: str
    receiver: str
    timestamp: str
    stage: str
    content: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    handoff_reason: Optional[str] = None

class AgentStepTrace(BaseModel):
    agent_name: str
    stage: str
    action: str
    thought: str
    output_summary: str
    execution_time_ms: float
    confidence: float
    data: Optional[Dict[str, Any]] = None

class ClauseAssessment(BaseModel):
    clause_id: str
    policy_name: str
    section: str
    citation: str
    requirement_type: RequirementType
    clause_text: str
    verdict: ComplianceVerdict
    reasoning: str
    evidence_quote: str
    gap_identified: Optional[str] = None
    severity: RiskLevel = RiskLevel.LOW

class RiskFactor(BaseModel):
    risk_title: str
    category: str
    severity: RiskLevel
    likelihood: RiskLevel
    impact: RiskLevel
    score: float = Field(..., ge=0.0, le=100.0)
    regulatory_frameworks: List[str]
    potential_penalties: str
    mitigation_priority: str
    clause_reference: str

class RemediationAction(BaseModel):
    action_id: str
    title: str
    description: str
    responsible_party: str
    approval_required: str
    priority: RiskLevel
    deadline_days: int
    policy_reference: str
    completed: bool = False

class ValidationCertificate(BaseModel):
    is_valid: bool
    grounding_faithfulness_score: float = Field(..., ge=0.0, le=1.0)
    unsupported_claims: List[str] = Field(default_factory=list)
    hallucination_detected: bool = False
    evidence_coverage_ratio: float = Field(..., ge=0.0, le=1.0)
    validator_notes: str

class ComplianceDossier(BaseModel):
    analysis_id: str
    scenario: str
    verdict: ComplianceVerdict
    overall_confidence: float
    risk_score: float
    risk_level: RiskLevel
    executive_summary: str
    applicable_policies: List[str]
    clause_assessments: List[ClauseAssessment]
    identified_gaps: List[str]
    risk_factors: List[RiskFactor]
    recommendations: List[RemediationAction]
    agent_trace: List[AgentStepTrace]
    a2a_messages: List[AgentMessage]
    validation: ValidationCertificate
    created_at: str
    processing_time_ms: float

class ComplianceRequest(BaseModel):
    scenario: str = Field(..., description="Business scenario or proposed action to analyze")
    category_hint: Optional[str] = None
    business_area_hint: Optional[str] = None
    strict_validation: bool = True

class BenchmarkScenario(BaseModel):
    scenario_id: str
    title: str
    domain: str
    scenario_text: str
    expected_policies: List[str]
    expected_verdict: ComplianceVerdict
    expected_risk_level: RiskLevel
    key_compliance_questions: List[str]
    description: str

class EvaluationSummary(BaseModel):
    total_scenarios_evaluated: int
    retrieval_mrr: float
    retrieval_recall_at_5: float
    retrieval_precision_at_5: float
    verdict_accuracy: float
    risk_calibration_score: float
    average_faithfulness_score: float
    average_latency_ms: float
    scenario_results: List[Dict[str, Any]]
