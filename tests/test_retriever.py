import pytest
from src.search.retriever import PolicyEvidenceRetriever
from src.models.schemas import SearchQuery

def test_hybrid_retrieval_kyc():
    retriever = PolicyEvidenceRetriever()
    res = retriever.search(SearchQuery(query="Does this customer onboarding process comply with our KYC policy?"))
    assert res.total_found > 0
    top_hit = res.results[0]
    assert top_hit.clause.policy_id == "POL-KYC-001"
    assert top_hit.citation_tag.startswith("[POL-KYC-001")
    assert top_hit.score > 0.4

def test_hybrid_retrieval_dpa():
    retriever = PolicyEvidenceRetriever()
    res = retriever.search(SearchQuery(query="What approvals are required before sharing customer information with a third party?"))
    assert res.total_found > 0
    # Expected top policy is POL-PRV-002
    policy_ids = [e.clause.policy_id for e in res.results[:3]]
    assert "POL-PRV-002" in policy_ids

def test_category_filter():
    retriever = PolicyEvidenceRetriever()
    res = retriever.search(SearchQuery(
        query="data encryption standards",
        category="Information Security"
    ))
    for r in res.results:
        assert r.clause.category == "Information Security"
