import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from pypdf import PdfReader
from src.models.schemas import PolicyDocument, PolicyClause, RequirementType, RiskLevel

class PolicyDocumentParser:
    """Parses compliance policy PDFs and documents into structured clauses."""

    @staticmethod
    def extract_text_from_pdf(pdf_path: Path) -> str:
        """Extracts full raw text from a PDF file using pypdf."""
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        reader = PdfReader(str(pdf_path))
        text_parts = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)

    @classmethod
    def parse_policy_pdf(cls, pdf_path: Path, fallback_meta: Optional[Dict[str, Any]] = None) -> PolicyDocument:
        """Parses a policy PDF into a structured PolicyDocument object."""
        raw_text = cls.extract_text_from_pdf(pdf_path)
        filename = pdf_path.name
        
        # Policy ID detection
        policy_id_match = re.search(r"(POL-[A-Z]+-\d{3})", raw_text) or re.search(r"(POL-[A-Z]+-\d{3})", filename)
        policy_id = policy_id_match.group(1) if policy_id_match else (fallback_meta.get("policy_id") if fallback_meta else "POL-GEN-001")

        # Category and metadata
        category = fallback_meta.get("category", "General Corporate Compliance") if fallback_meta else "General Corporate Compliance"
        business_area = fallback_meta.get("business_area", "Enterprise") if fallback_meta else "Enterprise"
        version = fallback_meta.get("version", "1.0") if fallback_meta else "1.0"
        effective_date = fallback_meta.get("effective_date", "2025-01-01") if fallback_meta else "2025-01-01"
        owner = fallback_meta.get("owner", "Compliance Department") if fallback_meta else "Compliance Department"
        policy_name = fallback_meta.get("policy_name", filename.replace(".pdf", "").replace("_", " ")) if fallback_meta else filename

        clauses: List[PolicyClause] = []
        if fallback_meta and "clauses" in fallback_meta:
            for c in fallback_meta["clauses"]:
                if isinstance(c, dict):
                    clauses.append(PolicyClause(**c))
                else:
                    clauses.append(c)

        return PolicyDocument(
            policy_id=policy_id,
            policy_name=policy_name,
            category=category,
            business_area=business_area,
            version=version,
            effective_date=effective_date,
            owner=owner,
            description=fallback_meta.get("description", "Enterprise operational compliance standard") if fallback_meta else "Enterprise operational compliance standard",
            clauses=clauses,
            pdf_filename=filename
        )
