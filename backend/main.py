"""
FastAPI Microservice for Policy Compliance Intelligence Platform.
Provides REST endpoints for Policy Data Management, Evidence Retrieval Search,
Multi-Agent Compliance Workflow Execution, and Benchmark Evaluation.
"""

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from models import (
    ScenarioRequest,
    ComplianceResponse,
    RetrievalResultItem,
    EvaluationResult,
    PolicyClause
)
from policy_corpus import POLICY_DOCUMENTS
from knowledge_base import PolicyKnowledgeBase
from agent_workflow import MultiAgentComplianceWorkflow
from evaluation import ComplianceEvaluator, BENCHMARK_SCENARIOS

app = FastAPI(
    title="Policy Compliance Intelligence Microservice",
    description="AI-powered Policy Compliance Intelligence & Evidence Retrieval System",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Knowledge Base and Multi-Agent Workflow
kb = PolicyKnowledgeBase()
workflow = MultiAgentComplianceWorkflow(kb)
evaluator = ComplianceEvaluator(workflow)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Policy Compliance Intelligence Microservice",
        "version": "1.0.0",
        "indexed_clauses_count": len(kb.clauses)
    }


@app.get("/api/policies")
def get_policies():
    """Task 1: Returns searchable knowledge base documents and metadata."""
    return {
        "policies": POLICY_DOCUMENTS,
        "total_documents": len(POLICY_DOCUMENTS),
        "total_clauses": len(kb.clauses),
        "clauses": kb.clauses
    }


@app.get("/api/policies/{policy_id}")
def get_policy_by_id(policy_id: str):
    """Returns policy document details and clauses for a specific policy ID."""
    doc = next((p for p in POLICY_DOCUMENTS if p["policy_id"].lower() == policy_id.lower()), None)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Policy with ID '{policy_id}' not found.")

    matching_clauses = [c for c in kb.clauses if c.policy_id.lower() == policy_id.lower()]
    return {
        "policy": doc,
        "clauses": matching_clauses
    }


@app.post("/api/search")
def search_policy_evidence(
    query: str = Query(..., description="Natural language compliance query or keyword"),
    category: str = Query(None, description="Optional category filter"),
    business_area: str = Query(None, description="Optional business area filter"),
    top_k: int = Query(5, ge=1, le=20)
):
    """Task 2: Grounded Evidence-Based Policy Retrieval."""
    results: list[RetrievalResultItem] = kb.search(
        query=query,
        top_k=top_k,
        category_filter=category,
        business_area_filter=business_area
    )
    return {
        "query": query,
        "total_results": len(results),
        "results": results
    }


@app.post("/api/analyze-compliance", response_model=ComplianceResponse)
def analyze_compliance_scenario(request: ScenarioRequest):
    """Task 3: Multi-Agent Compliance Analysis & Risk Assessment Workflow."""
    if not request.scenario_text.strip():
        raise HTTPException(status_code=400, detail="Scenario text cannot be empty.")

    try:
        response = workflow.run_workflow(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@app.get("/api/evaluate", response_model=EvaluationResult)
def run_evaluation_suite():
    """Task 4: Quality Evaluation Harness & Metric Calculation."""
    try:
        results = evaluator.evaluate_all()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@app.get("/api/benchmark-scenarios")
def get_benchmark_scenarios():
    """Task 4: Returns list of 10 ground-truth benchmark scenarios for UI testing."""
    return {"scenarios": BENCHMARK_SCENARIOS}


# Serve Frontend UI
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def serve_frontend_index():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse({"message": "Policy Compliance Intelligence Backend API Running. Frontend index.html not found."})
