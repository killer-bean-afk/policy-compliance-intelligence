import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_POLICIES_DIR = DATA_DIR / "raw_policies"
KB_PATH = DATA_DIR / "knowledge_base.json"
KB_DB_PATH = DATA_DIR / "compliance_kb.db"
VECTOR_CACHE_PATH = DATA_DIR / "embeddings_cache.npz"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure data directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_POLICIES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Retrieval Configuration
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
EMBEDDING_DIM = 384
TOP_K_RETRIEVAL = 5
DENSE_WEIGHT = 0.65
SPARSE_WEIGHT = 0.35
RRF_K = 60
SIMILARITY_THRESHOLD = 0.32

# Multi-Agent Workflow Parameters
CONFIDENCE_THRESHOLD_HIGH = 0.85
CONFIDENCE_THRESHOLD_MEDIUM = 0.65
RISK_THRESHOLD_CRITICAL = 80.0
RISK_THRESHOLD_HIGH = 60.0
RISK_THRESHOLD_MEDIUM = 35.0

# Server Configuration
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# Ensure Hugging Face operates reliably offline if cached
os.environ.setdefault("HF_HUB_OFFLINE", "1")
