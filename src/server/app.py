import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from src.config import (
    RAW_POLICIES_DIR,
    REPORTS_DIR,
    EMBEDDING_MODEL_NAME,
    SERVER_HOST,
    SERVER_PORT
)
from src.knowledge_base.store import ComplianceKnowledgeStore
from src.search.retriever import PolicyEvidenceRetriever
from src.agents.orchestrator import ComplianceWorkflowOrchestrator
from src.reporting.pdf_exporter import ComplianceReportExporter
from src.evaluation.evaluator import ComplianceEvaluator
from src.evaluation.benchmarks import BENCHMARK_SCENARIOS
from contextlib import asynccontextmanager
from src.models.schemas import (
    SearchQuery,
    SearchResult,
    ComplianceRequest,
    ComplianceDossier,
    EvaluationSummary
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Pre-warming knowledge base and embedding models...")
    get_store()
    get_retriever()
    get_orchestrator()
    print("Microservice is warm and ready.")
    yield

# Initialize FastAPI application
app = FastAPI(
    title="Policy Compliance Intelligence API",
    description="AI-Powered Policy Retrieval, Evidentiary Compliance Search & Multi-Agent Risk Assessment Microservice",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local or browser interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy singletons
_store = None
_retriever = None
_orchestrator = None
_evaluator = None

def get_store() -> ComplianceKnowledgeStore:
    global _store
    if _store is None:
        _store = ComplianceKnowledgeStore.get_instance()
    return _store

def get_retriever() -> PolicyEvidenceRetriever:
    global _retriever
    if _retriever is None:
        _retriever = PolicyEvidenceRetriever(get_store())
    return _retriever

def get_orchestrator() -> ComplianceWorkflowOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ComplianceWorkflowOrchestrator(get_retriever())
    return _orchestrator

def get_evaluator() -> ComplianceEvaluator:
    global _evaluator
    if _evaluator is None:
        _evaluator = ComplianceEvaluator(get_orchestrator())
    return _evaluator

# --- Endpoints ---

@app.get("/api/health")
def health_check():
    store = get_store()
    return {
        "status": "HEALTHY",
        "service": "Policy Compliance Intelligence Microservice",
        "version": "1.0.0",
        "embedding_model": EMBEDDING_MODEL_NAME,
        "policies_indexed": len(store.get_all_policies()),
        "clauses_indexed": len(store.get_all_clauses()),
        "categories": store.get_categories(),
        "timestamp": time.time()
    }

@app.get("/api/policies")
def list_policies():
    store = get_store()
    return {
        "total": len(store.get_all_policies()),
        "policies": store.get_all_policies()
    }

@app.get("/api/policies/{policy_id}")
def get_policy(policy_id: str):
    store = get_store()
    policies = store.get_all_policies()
    matched_meta = next((p for p in policies if p["policy_id"].lower() == policy_id.lower()), None)
    if not matched_meta:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found.")

    clauses = [c for c in store.get_all_clauses() if c.policy_id.lower() == policy_id.lower()]
    return {
        **matched_meta,
        "clauses": clauses
    }

@app.get("/api/policies/{policy_id}/pdf")
def download_policy_pdf(policy_id: str):
    store = get_store()
    policies = store.get_all_policies()
    matched = next((p for p in policies if p["policy_id"].lower() == policy_id.lower()), None)
    if not matched or not matched.get("pdf_filename"):
        raise HTTPException(status_code=404, detail=f"PDF for {policy_id} not found.")

    pdf_path = RAW_POLICIES_DIR / matched["pdf_filename"]
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"File {matched['pdf_filename']} does not exist on disk.")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=matched["pdf_filename"]
    )

@app.post("/api/search", response_model=SearchResult)
def search_policies(query: SearchQuery):
    """Evidence-based semantic and lexical search for policy requirements (Task 2)."""
    retriever = get_retriever()
    return retriever.search(query)

@app.post("/api/compliance/analyze", response_model=ComplianceDossier)
def analyze_compliance(request: ComplianceRequest):
    """Executes the full multi-agent compliance workflow (Task 3)."""
    orchestrator = get_orchestrator()
    dossier = orchestrator.run_workflow(request)
    return dossier

@app.get("/api/compliance/stream")
def stream_compliance_analysis(scenario: str = Query(...)):
    """Server-Sent Events (SSE) streaming endpoint for live multi-agent execution."""
    orchestrator = get_orchestrator()
    request = ComplianceRequest(scenario=scenario)

    def event_generator():
        for event in orchestrator.stream_workflow(request):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/scenarios")
def get_preset_scenarios():
    """Returns benchmark and demonstration scenarios for quick testing."""
    return [
        {
            "scenario_id": s.scenario_id,
            "title": s.title,
            "domain": s.domain,
            "text": s.scenario_text,
            "expected_verdict": s.expected_verdict.value,
            "expected_risk": s.expected_risk_level.value,
            "description": s.description
        }
        for s in BENCHMARK_SCENARIOS
    ]

@app.post("/api/evaluation/run", response_model=EvaluationSummary)
def run_evaluation_benchmark():
    """Executes the quantitative evaluation suite and returns metrics (Task 4)."""
    evaluator = get_evaluator()
    summary = evaluator.run_benchmark(verbose=False)
    return summary

@app.post("/api/reports/export")
def export_compliance_report(dossier: ComplianceDossier):
    """Generates an official PDF audit dossier report."""
    output_path = ComplianceReportExporter.export_pdf(dossier)
    return {
        "filename": output_path.name,
        "download_url": f"/api/reports/{output_path.name}",
        "size_bytes": output_path.stat().st_size
    }

@app.get("/api/reports/{filename}")
def download_compliance_report(filename: str):
    file_path = REPORTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audit report not found.")

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename
    )

# Static file serving for Frontend UI
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
