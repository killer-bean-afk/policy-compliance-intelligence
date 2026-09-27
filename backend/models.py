"""
Pydantic Data Models for Policy Compliance Intelligence Platform.
Defines schemas for Policy Clauses, Compliance Scenarios, Agent Messages, Risk Assessments,
Validation Proofs, Remediation Actions, and Benchmark Evaluations.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MandatoryLevel(str, Enum):
    MUST = "MUST"
    SHOULD = "SHOULD"
    MAY = "MAY"


class ComplianceStatus(str, Enum):
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non-Compliant"
    PARTIALLY_COMPLIANT = "Partially Compliant"
    NEEDS_INFORMATION = "Needs Information"
    NOT_APPLICABLE = "Not Applicable"


class RiskSeverity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"


class PolicyClause(BaseModel):
    clause_id: str = Field(..., description="Unique Clause ID (e.g. KYC-1.1)")
    policy_id: str = Field(..., description="Parent Policy Document ID")
    policy_name: str = Field(..., description="Name of the Policy Document")
    policy_category: str = Field(..., description="Category (KYC/AML, Data Privacy, InfoSec, Governance, Financial Ops)")
    applicable_business_area: str = Field(..., description="Target business function or department")
    section_title: str = Field(..., description="Section heading")
    section_number: str = Field(..., description="Section number e.g. 2.1")
    mandatory_level: MandatoryLevel = Field(default=MandatoryLevel.MUST)
    clause_text: str = Field(..., description="Exact textual content of the policy requirement")
    key_keywords: List[str] = Field(default_factory=list, description="Extracted domain keywords for indexing")
    effective_date: str = Field(default="2025-01-01", description="Policy effective date")
    source_document: str = Field(..., description="Source document file name")


class ScenarioRequest(BaseModel):
    scenario_id: Optional[str] = None
    scenario_text: str = Field(..., description="Natural language business activity or compliance query")
    business_area: Optional[str] = Field(None, description="Optional filter by business area")
    policy_category: Optional[str] = Field(None, description="Optional filter by policy category")
    user_role: Optional[str] = Field("Compliance Officer", description="Role of the user submitting query")
    include_agent_trace: bool = Field(True, description="Whether to include step-by-step A2A agent logs")


class AgentMessageType(str, Enum):
    RETRIEVAL_QUERY = "RETRIEVAL_QUERY"
    RETRIEVAL_RESULT = "RETRIEVAL_RESULT"
    ANALYSIS_HANDOFF = "ANALYSIS_HANDOFF"
    RISK_EVALUATION = "RISK_EVALUATION"
    VALIDATION_REQUEST = "VALIDATION_REQUEST"
    VALIDATION_FEEDBACK = "VALIDATION_FEEDBACK"
    RECOMMENDATION_OUTPUT = "RECOMMENDATION_OUTPUT"
    SYSTEM_NOTIFICATION = "SYSTEM_NOTIFICATION"


class AgentMessage(BaseModel):
    message_id: str
    sender_agent: str
    receiver_agent: str
    message_type: AgentMessageType
    timestamp: str
    content: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class RetrievalResultItem(BaseModel):
    clause: PolicyClause
    relevance_score: float = Field(..., description="Hybrid relevance score [0.0 - 1.0]")
    match_reasons: List[str] = Field(default_factory=list, description="Reasons for matching (e.g. TF-IDF vector, BM25 keyword)")


class ClauseAnalysis(BaseModel):
    clause_id: str
    policy_name: str
    section_number: str
    requirement_summary: str
    status: ComplianceStatus
    findings: str
    evidence_quote: str = Field(..., description="Direct snippet quote from policy text grounding this finding")
    compliance_score: float = Field(..., description="Score 0.0 to 1.0 indicating degree of compliance")


class RiskItem(BaseModel):
    risk_id: str
    severity: RiskSeverity
    risk_category: str
    title: str
    description: str
    potential_penalty: str = Field(..., description="Potential regulatory fine, legal liability, or reputational damage")
    affected_clause_ids: List[str] = Field(default_factory=list)


class ValidationProof(BaseModel):
    is_grounded: bool
    grounding_confidence_score: float = Field(..., description="Confidence score [0.0 - 1.0] that findings are backed by policy evidence")
    hallucination_detected: bool
    explanation: str
    verified_clauses: List[str] = Field(default_factory=list)
    unbacked_claims: List[str] = Field(default_factory=list)


class RemediationAction(BaseModel):
    action_id: str
    priority: str = Field(..., description="Immediate, High, Medium, Low")
    title: str
    description: str
    responsible_party: str
    required_approvals: List[str] = Field(default_factory=list)
    prerequisite_documents: List[str] = Field(default_factory=list)
    workflow_handoff: Optional[str] = Field(None, description="System or team handoff recommendation")


class EvidenceTraceability(BaseModel):
    clause_id: str
    policy_name: str
    section: str
    clause_text: str
    finding: str
    compliance_status: ComplianceStatus
    linked_risk_id: Optional[str] = None


class ComplianceResponse(BaseModel):
    scenario_id: str
    scenario_text: str
    overall_compliance_status: ComplianceStatus
    overall_risk_level: RiskSeverity
    executive_summary: str
    retrieved_clauses: List[RetrievalResultItem]
    clause_analyses: List[ClauseAnalysis]
    risk_assessment: List[RiskItem]
    validation_proof: ValidationProof
    remediation_actions: List[RemediationAction]
    evidence_matrix: List[EvidenceTraceability]
    agent_execution_trace: List[AgentMessage]
    execution_time_ms: float


class EvaluationBenchmarkScenario(BaseModel):
    benchmark_id: str
    title: str
    category: str
    scenario_text: str
    expected_status: ComplianceStatus
    expected_risk: RiskSeverity
    relevant_clause_ids: List[str]


class EvaluationResult(BaseModel):
    total_scenarios_evaluated: int
    precision_at_k: float
    recall_at_k: float
    evidence_grounding_score: float
    risk_classification_precision: float
    status_classification_accuracy: float
    average_latency_ms: float
    details: List[Dict[str, Any]]
