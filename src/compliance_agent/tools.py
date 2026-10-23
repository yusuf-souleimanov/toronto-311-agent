"""Tools the agent can call. Each one is small, deterministic where possible, and logged.

TODO (Week 2): wrap these with LangChain's @tool decorator once the bodies work.
"""

from datetime import date

from .config import load_settings
from .rules import is_compliant
from .schema import Extraction


def read_document(doc_id: str) -> str:
    """Return the extracted text for a document from data/processed/."""
    raise NotImplementedError


def extract_fields(doc_id: str) -> Extraction:
    """LLM extraction with structured output (Pydantic schema), falling back to
    extraction.heuristic_extract when the model returns nothing usable."""
    raise NotImplementedError


def check_compliance(issue_date: date | None) -> bool | None:
    s = load_settings()
    return is_compliant(issue_date, s.as_of_date, s.max_doc_age_years)


def search_documents(query: str, k: int = 5) -> list[dict]:
    """Semantic search over document chunks in ChromaDB (reuse your action-item tracker
    pattern). Returns [{doc_id, chunk, score}]. TODO (Week 2)."""
    raise NotImplementedError


def flag_for_review(doc_id: str, reason: str) -> None:
    """Put a document in the human review queue. Never auto-decide on low confidence."""
    raise NotImplementedError
