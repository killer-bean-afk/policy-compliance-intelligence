import os
import json
import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from src.config import KB_PATH, KB_DB_PATH, VECTOR_CACHE_PATH, EMBEDDING_MODEL_NAME
from src.models.schemas import PolicyDocument, PolicyClause, RequirementType, RiskLevel

class ComplianceKnowledgeStore:
    """Enterprise Knowledge Base Store combining SQLite, Dense Vectors, and BM25 Sparse Index."""

    _instance = None

    def __init__(self):
        self.db_path = KB_DB_PATH
        self.kb_json_path = KB_PATH
        self.embedding_model = None
        self.clauses: List[PolicyClause] = []
        self.clause_map: Dict[str, PolicyClause] = {}
        self.dense_embeddings: Optional[np.ndarray] = None
        self.bm25_vectorizer: Optional[TfidfVectorizer] = None
        self.bm25_matrix = None
        self.initialized = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ComplianceKnowledgeStore()
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        """Loads or builds the knowledge base, SQLite tables, dense embeddings, and BM25 index."""
        if self.initialized:
            return

        print("Initializing Compliance Knowledge Base...")
        self._init_sqlite()
        self._load_clauses()
        self._init_dense_embeddings()
        self._init_sparse_bm25()
        self.initialized = True
        print(f"Compliance Knowledge Base initialized successfully with {len(self.clauses)} clauses.")

    def _init_sqlite(self):
        """Creates SQLite tables for policies and clauses."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                policy_id TEXT PRIMARY KEY,
                policy_name TEXT NOT NULL,
                category TEXT NOT NULL,
                business_area TEXT NOT NULL,
                version TEXT NOT NULL,
                effective_date TEXT NOT NULL,
                owner TEXT NOT NULL,
                description TEXT,
                pdf_filename TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS clauses (
                clause_id TEXT PRIMARY KEY,
                policy_id TEXT NOT NULL,
                policy_name TEXT NOT NULL,
                section_number TEXT NOT NULL,
                section_title TEXT NOT NULL,
                category TEXT NOT NULL,
                business_area TEXT NOT NULL,
                requirement_type TEXT NOT NULL,
                clause_text TEXT NOT NULL,
                penalty_severity TEXT NOT NULL,
                regulatory_framework TEXT NOT NULL,
                source_file TEXT,
                version TEXT,
                effective_date TEXT,
                FOREIGN KEY (policy_id) REFERENCES policies(policy_id)
            )
        """)

        conn.commit()
        conn.close()

    def _load_clauses(self):
        """Loads policies and clauses from knowledge_base.json into SQLite and memory."""
        if not self.kb_json_path.exists():
            raise FileNotFoundError(f"Knowledge base file not found at {self.kb_json_path}. Run generator first.")

        with open(self.kb_json_path, "r", encoding="utf-8") as f:
            raw_docs = json.load(f)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        self.clauses = []
        self.clause_map = {}

        for doc in raw_docs:
            cur.execute("""
                INSERT OR REPLACE INTO policies 
                (policy_id, policy_name, category, business_area, version, effective_date, owner, description, pdf_filename)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc["policy_id"], doc["policy_name"], doc["category"], doc["business_area"],
                doc["version"], doc["effective_date"], doc["owner"], doc["description"], doc.get("pdf_filename")
            ))

            for c in doc["clauses"]:
                req_val = c["requirement_type"].value if hasattr(c["requirement_type"], "value") else str(c["requirement_type"])
                pen_val = c["penalty_severity"].value if hasattr(c["penalty_severity"], "value") else str(c["penalty_severity"])
                
                cur.execute("""
                    INSERT OR REPLACE INTO clauses
                    (clause_id, policy_id, policy_name, section_number, section_title, category, business_area,
                     requirement_type, clause_text, penalty_severity, regulatory_framework, source_file, version, effective_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    c["clause_id"], c["policy_id"], c["policy_name"], c["section_number"], c["section_title"],
                    c["category"], c["business_area"], req_val, c["clause_text"], pen_val,
                    c["regulatory_framework"], c.get("source_file", ""), c.get("version", "1.0"), c.get("effective_date", "2025-01-01")
                ))

                clause_obj = PolicyClause(
                    clause_id=c["clause_id"],
                    policy_id=c["policy_id"],
                    policy_name=c["policy_name"],
                    section_number=c["section_number"],
                    section_title=c["section_title"],
                    category=c["category"],
                    business_area=c["business_area"],
                    requirement_type=RequirementType(req_val),
                    clause_text=c["clause_text"],
                    key_terms=c.get("key_terms", []),
                    penalty_severity=RiskLevel(pen_val),
                    regulatory_framework=c["regulatory_framework"],
                    source_file=c.get("source_file", ""),
                    version=c.get("version", "1.0"),
                    effective_date=c.get("effective_date", "2025-01-01")
                )
                self.clauses.append(clause_obj)
                self.clause_map[clause_obj.clause_id] = clause_obj

        conn.commit()
        conn.close()

    def _init_dense_embeddings(self):
        """Generates or loads dense vector representations using sentence-transformers."""
        if self.embedding_model is None:
            print(f"Loading SentenceTransformer: {EMBEDDING_MODEL_NAME}...")
            os.environ["HF_HUB_OFFLINE"] = "1"
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

        # Check if vector cache exists and has matching clause count
        if VECTOR_CACHE_PATH.exists():
            try:
                cached_data = np.load(VECTOR_CACHE_PATH)
                if len(cached_data["embeddings"]) == len(self.clauses):
                    self.dense_embeddings = cached_data["embeddings"]
                    print(f"Loaded {len(self.dense_embeddings)} dense embeddings from cache.")
                    return
            except Exception as e:
                print(f"Cache load failed: {e}. Recomputing...")

        # Compute embeddings for rich text representation
        rich_texts = [
            f"Policy: {c.policy_name} | Section {c.section_number}: {c.section_title} | Category: {c.category} | "
            f"Requirement: {c.clause_text} | Regulatory Standard: {c.regulatory_framework}"
            for c in self.clauses
        ]

        print(f"Encoding {len(rich_texts)} clauses with {EMBEDDING_MODEL_NAME}...")
        embeddings = self.embedding_model.encode(rich_texts, show_progress_bar=False, normalize_embeddings=True)
        self.dense_embeddings = np.array(embeddings, dtype=np.float32)

        # Save cache
        np.savez_compressed(VECTOR_CACHE_PATH, embeddings=self.dense_embeddings)
        print("Dense embeddings computed and cached successfully.")

    def _init_sparse_bm25(self):
        """Initializes a tuned sub-linear TF-IDF / BM25 sparse index."""
        corpus = [
            f"{c.policy_name} {c.section_title} {c.category} {c.business_area} {c.regulatory_framework} {c.clause_text} " + " ".join(c.key_terms)
            for c in self.clauses
        ]
        self.bm25_vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            sublinear_tf=True,
            ngram_range=(1, 2)
        )
        self.bm25_matrix = self.bm25_vectorizer.fit_transform(corpus)

    def get_all_clauses(self) -> List[PolicyClause]:
        return self.clauses

    def get_clause_by_id(self, clause_id: str) -> Optional[PolicyClause]:
        return self.clause_map.get(clause_id)

    def get_all_policies(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT policy_id, policy_name, category, business_area, version, effective_date, owner, description, pdf_filename FROM policies")
        rows = cur.fetchall()
        conn.close()

        policies = []
        for r in rows:
            policies.append({
                "policy_id": r[0],
                "policy_name": r[1],
                "category": r[2],
                "business_area": r[3],
                "version": r[4],
                "effective_date": r[5],
                "owner": r[6],
                "description": r[7],
                "pdf_filename": r[8],
                "clause_count": len([c for c in self.clauses if c.policy_id == r[0]])
            })
        return policies

    def get_categories(self) -> List[str]:
        return sorted(list(set(c.category for c in self.clauses)))

    def get_business_areas(self) -> List[str]:
        return sorted(list(set(c.business_area for c in self.clauses)))
