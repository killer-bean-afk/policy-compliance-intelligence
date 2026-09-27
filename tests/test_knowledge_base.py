import pytest
from src.knowledge_base.store import ComplianceKnowledgeStore

def test_knowledge_base_initialization():
    kb = ComplianceKnowledgeStore.get_instance()
    assert kb.initialized is True
    assert len(kb.clauses) == 34
    assert len(kb.get_all_policies()) == 7

def test_categories_and_areas():
    kb = ComplianceKnowledgeStore.get_instance()
    categories = kb.get_categories()
    assert "Anti-Money Laundering" in categories
    assert "Data Privacy & Protection" in categories
    assert "Information Security" in categories
    assert "AI Governance & Ethics" in categories

def test_clause_lookup():
    kb = ComplianceKnowledgeStore.get_instance()
    clause = kb.get_clause_by_id("POL-KYC-001-C01")
    assert clause is not None
    assert clause.section_number == "2.1"
    assert "CIP" in clause.key_terms or "Customer Identification Program" in clause.section_title
