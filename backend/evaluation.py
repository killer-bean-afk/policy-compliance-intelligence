"""
Evaluation & Benchmark Engine for Policy Compliance Intelligence.
Implements Task 4: Evaluates retrieval quality, evidence grounding, status accuracy,
and risk precision against 10 ground-truth compliance scenarios.
"""

from typing import List, Dict, Any
from models import (
    EvaluationBenchmarkScenario,
    EvaluationResult,
    ComplianceStatus,
    RiskSeverity,
    ScenarioRequest
)
from knowledge_base import PolicyKnowledgeBase
from agent_workflow import MultiAgentComplianceWorkflow

BENCHMARK_SCENARIOS: List[EvaluationBenchmarkScenario] = [
    EvaluationBenchmarkScenario(
        benchmark_id="BENCH-001",
        title="PEP Customer Onboarding without EDD Dossier",
        category="KYC / AML",
        scenario_text="A new institutional client account is being onboarded for a senior foreign government minister (Politically Exposed Person). The account executive wants to activate the account immediately without completing an Enhanced Due Diligence (EDD) report or securing formal written sign-off from the Money Laundering Reporting Officer (MLRO).",
        expected_status=ComplianceStatus.NON_COMPLIANT,
        expected_risk=RiskSeverity.CRITICAL,
        relevant_clause_ids=["KYC-1.2", "KYC-1.1"]
    ),
    EvaluationBenchmarkScenario(
        benchmark_id="BENCH-002",
        title="Sharing Patient EHR Data with SaaS Vendor without BAA",
        category="Data Privacy & Healthcare",
        scenario_text="The health operations team plans to upload 5,000 patient electronic health records (ePHI) to a third-party cloud analytics SaaS vendor to optimize clinical workflow scheduling. No Business Associate Agreement (BAA) has been executed with the vendor.",
        expected_status=ComplianceStatus.NON_COMPLIANT,
        expected_risk=RiskSeverity.CRITICAL,
        relevant_clause_ids=["HIPAA-2.1", "HIPAA-1.1"]
    ),
    EvaluationBenchmarkScenario(
        benchmark_id="BENCH-003",
        title="Uploading Core Source Code to Public AI Chatbot",
        category="Information Security",
        scenario_text="A software engineer pasted 1,500 lines of proprietary payment processing source code into a public web-based generative AI tool to debug an algorithm error.",
        expected_status=ComplianceStatus.NON_COMPLIANT,
        expected_risk=RiskSeverity.HIGH,
        relevant_clause_ids=["SEC-4.1", "SEC-1.1"]
    ),
    EvaluationBenchmarkScenario(
        benchmark_id="BENCH-004",
        title="High-Value International Transfer Without Sanctions Screening",
        category="Financial Operations",
        scenario_text="Treasury initiated an outbound wire transfer of $250,000 USD to a corporate supplier in Eastern Europe without running real-time OFAC SDN sanctions screening or obtaining dual Treasury authorization.",
        expected_status=ComplianceStatus.NON_COMPLIANT,
        expected_risk=RiskSeverity.CRITICAL,
        relevant_clause_ids=["FIN-1.1", "FIN-2.1"]
    ),
    EvaluationBenchmarkScenario(
        benchmark_id="BENCH-005",
        title="Hosting $500 Dinner for Foreign Regulatory Official",
        category="Corporate Governance",
        scenario_text="A sales executive hosted a $500 luxury dinner for a foreign government regulatory inspector to discuss upcoming license approvals, without obtaining prior compliance pre-clearance.",
        expected_status=ComplianceStatus.NON_COMPLIANT,
        expected_risk=RiskSeverity.HIGH,
        relevant_clause_ids=["GOV-1.1"]
    ),
    EvaluationBenchmarkScenario(
        benchmark_id="BENCH-006",
        title="Cross-Border Data Hosting on Foreign Server Without CISO Sign-Off",
        category="Information Security",
        scenario_text="The engineering team migrated confidential customer databases to cloud servers located in a foreign jurisdiction without standard contractual clauses or CISO approval.",
        expected_status=ComplianceStatus.NON_COMPLIANT,
        expected_risk=RiskSeverity.HIGH,
        relevant_clause_ids=["SEC-2.1"]
    ),
    EvaluationBenchmarkScenario(
        benchmark_id="BENCH-007",
        title="Unhosted Cryptocurrency Monero Wire Transfer",
        category="Financial Operations",
        scenario_text="A business unit attempted to pay an overseas contractor using an unhosted Monero cryptocurrency wallet via an anonymous decentralized privacy protocol.",
        expected_status=ComplianceStatus.NON_COMPLIANT,
        expected_risk=RiskSeverity.CRITICAL,
        relevant_clause_ids=["FIN-3.1"]
    ),
    EvaluationBenchmarkScenario(
        benchmark_id="BENCH-008",
        title="Compliant Baseline Institutional Customer Onboarding",
        category="KYC / AML",
        scenario_text="Onboarding a corporate entity after verifying valid government registration, tax EIN, 90-day utility proof of address, and beneficial ownership disclosure for all 25%+ shareholders.",
        expected_status=ComplianceStatus.COMPLIANT,
        expected_risk=RiskSeverity.LOW,
        relevant_clause_ids=["KYC-1.1", "KYC-2.1"]
    ),
    EvaluationBenchmarkScenario(
        benchmark_id="BENCH-009",
        title="Compliant Encrypted PHI Cloud Storage with Executed BAA",
        category="Data Privacy & Healthcare",
        scenario_text="Storing patient health records on a secure cloud provider with AES-256 encryption at rest, TLS 1.3 in transit, and an active executed Business Associate Agreement (BAA).",
        expected_status=ComplianceStatus.COMPLIANT,
        expected_risk=RiskSeverity.LOW,
        relevant_clause_ids=["HIPAA-3.1", "HIPAA-2.1"]
    ),
    EvaluationBenchmarkScenario(
        benchmark_id="BENCH-010",
        title="Compliant Treasury Wire Transfer under Dual Approval Threshold",
        category="Financial Operations",
        scenario_text="Executing a $45,000 domestic wire transfer with verified OFAC real-time green check and standard Treasury officer sign-off.",
        expected_status=ComplianceStatus.COMPLIANT,
        expected_risk=RiskSeverity.LOW,
        relevant_clause_ids=["FIN-1.1", "FIN-2.1"]
    )
]


class ComplianceEvaluator:
    """Evaluates the Policy Compliance Intelligence platform against benchmark ground truth."""

    def __init__(self, workflow: MultiAgentComplianceWorkflow):
        self.workflow = workflow

    def evaluate_all(self) -> EvaluationResult:
        total = len(BENCHMARK_SCENARIOS)
        retrieval_precisions = []
        retrieval_recalls = []
        grounding_scores = []
        status_matches = 0
        risk_matches = 0
        latencies = []
        details = []

        for bench in BENCHMARK_SCENARIOS:
            req = ScenarioRequest(
                scenario_text=bench.scenario_text,
                policy_category=bench.category,
                include_agent_trace=False
            )

            res = self.workflow.run_workflow(req)
            latencies.append(res.execution_time_ms)

            # Evaluate Retrieval Quality (Precision@K and Recall@K)
            retrieved_ids = {item.clause.clause_id for item in res.retrieved_clauses}
            expected_ids = set(bench.relevant_clause_ids)

            intersection = retrieved_ids.intersection(expected_ids)
            precision = len(intersection) / max(len(retrieved_ids), 1)
            recall = len(intersection) / max(len(expected_ids), 1)

            retrieval_precisions.append(precision)
            retrieval_recalls.append(recall)

            # Evaluate Grounding Score
            grounding_scores.append(res.validation_proof.grounding_confidence_score)

            # Evaluate Status Match
            status_matched = res.overall_compliance_status == bench.expected_status
            if status_matched:
                status_matches += 1

            # Evaluate Risk Match
            risk_matched = res.overall_risk_level == bench.expected_risk
            if risk_matched:
                risk_matches += 1

            details.append({
                "benchmark_id": bench.benchmark_id,
                "title": bench.title,
                "category": bench.category,
                "expected_status": bench.expected_status.value,
                "predicted_status": res.overall_compliance_status.value,
                "status_correct": status_matched,
                "expected_risk": bench.expected_risk.value,
                "predicted_risk": res.overall_risk_level.value,
                "risk_correct": risk_matched,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "grounding_score": res.validation_proof.grounding_confidence_score,
                "latency_ms": res.execution_time_ms
            })

        avg_precision = sum(retrieval_precisions) / total
        avg_recall = sum(retrieval_recalls) / total
        avg_grounding = sum(grounding_scores) / total
        status_acc = status_matches / total
        risk_prec = risk_matches / total
        avg_latency = sum(latencies) / total

        return EvaluationResult(
            total_scenarios_evaluated=total,
            precision_at_k=round(avg_precision, 4),
            recall_at_k=round(avg_recall, 4),
            evidence_grounding_score=round(avg_grounding, 4),
            risk_classification_precision=round(risk_prec, 4),
            status_classification_accuracy=round(status_acc, 4),
            average_latency_ms=round(avg_latency, 2),
            details=details
        )
