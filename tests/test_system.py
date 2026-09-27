"""
Comprehensive Integration Tests for Policy Compliance Intelligence Platform.
Validates Task 1 (Knowledge Base), Task 2 (Policy Retrieval), Task 3 (Multi-Agent Workflow),
and Task 4 (Benchmark Evaluation).
"""

import sys
import os
import unittest

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from models import (
    ScenarioRequest,
    ComplianceStatus,
    RiskSeverity
)
from knowledge_base import PolicyKnowledgeBase
from agent_workflow import MultiAgentComplianceWorkflow
from evaluation import ComplianceEvaluator


class TestPolicyComplianceIntelligence(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.kb = PolicyKnowledgeBase()
        cls.workflow = MultiAgentComplianceWorkflow(cls.kb)
        cls.evaluator = ComplianceEvaluator(cls.workflow)

    def test_task1_knowledge_base_indexing(self):
        """Task 1: Verify policy document and clause indexing."""
        self.assertGreater(len(self.kb.clauses), 10)
        clause = self.kb.get_clause_by_id("KYC-1.2")
        self.assertIsNotNone(clause)
        self.assertEqual(clause.policy_id, "POL-KYC-001")
        self.assertIn("PEP", clause.clause_text)

    def test_task2_hybrid_retrieval(self):
        """Task 2: Verify natural language policy evidence retrieval."""
        results = self.kb.search("Business Associate Agreement HIPAA patient data vendor", top_k=3)
        self.assertGreater(len(results), 0)
        top_clause_ids = [r.clause.clause_id for r in results]
        self.assertIn("HIPAA-2.1", top_clause_ids)
        self.assertGreater(results[0].relevance_score, 0.2)

    def test_task3_multi_agent_workflow_non_compliant(self):
        """Task 3: Test multi-agent workflow for non-compliant PEP scenario."""
        req = ScenarioRequest(
            scenario_text="Onboarding a foreign politician (PEP) without an EDD report or MLRO sign-off.",
            include_agent_trace=True
        )
        res = self.workflow.run_workflow(req)

        self.assertEqual(res.overall_compliance_status, ComplianceStatus.NON_COMPLIANT)
        self.assertIn(res.overall_risk_level, [RiskSeverity.CRITICAL, RiskSeverity.HIGH])
        self.assertGreater(len(res.retrieved_clauses), 0)
        self.assertGreater(len(res.risk_assessment), 0)
        self.assertGreater(len(res.remediation_actions), 0)
        self.assertGreater(len(res.agent_execution_trace), 5)
        self.assertGreaterEqual(res.validation_proof.grounding_confidence_score, 0.8)

    def test_task3_multi_agent_workflow_compliant(self):
        """Task 3: Test multi-agent workflow for fully compliant scenario."""
        req = ScenarioRequest(
            scenario_text="Executing a $45,000 domestic wire transfer with verified OFAC real-time green check and standard Treasury officer sign-off.",
            include_agent_trace=True
        )
        res = self.workflow.run_workflow(req)

        self.assertEqual(res.overall_compliance_status, ComplianceStatus.COMPLIANT)
        self.assertEqual(res.overall_risk_level, RiskSeverity.LOW)
        self.assertEqual(len(res.risk_assessment), 0)

    def test_task4_benchmark_evaluation(self):
        """Task 4: Test evaluation harness metrics."""
        eval_res = self.evaluator.evaluate_all()
        self.assertEqual(eval_res.total_scenarios_evaluated, 10)
        self.assertGreater(eval_res.precision_at_k, 0.7)
        self.assertGreater(eval_res.recall_at_k, 0.7)
        self.assertGreater(eval_res.status_classification_accuracy, 0.8)
        self.assertGreater(eval_res.evidence_grounding_score, 0.85)


if __name__ == "__main__":
    unittest.main()
