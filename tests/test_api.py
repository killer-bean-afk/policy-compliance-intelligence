import pytest
from starlette.testclient import TestClient
from src.server.app import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["policies_indexed"] == 7
    assert data["clauses_indexed"] == 34

def test_api_policies():
    res = client.get("/api/policies")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 7
    assert len(data["policies"]) == 7

def test_api_search():
    res = client.post("/api/search", json={
        "query": "Does this customer onboarding process comply with our KYC policy?",
        "top_k": 5
    })
    assert res.status_code == 200
    data = res.json()
    assert data["total_found"] > 0
    assert len(data["results"]) <= 5

def test_api_scenarios():
    res = client.get("/api/scenarios")
    assert res.status_code == 200
    scenarios = res.json()
    assert len(scenarios) == 10

def test_api_compliance_analyze():
    res = client.post("/api/compliance/analyze", json={
        "scenario": "A sales representative wants to give a $1,500 luxury dinner and sports tickets to a foreign state-owned energy official without compliance pre-approval."
    })
    assert res.status_code == 200
    dossier = res.json()
    assert dossier["verdict"] == "NON_COMPLIANT"
    assert dossier["risk_level"] in ("HIGH", "CRITICAL")
    assert len(dossier["recommendations"]) > 0
