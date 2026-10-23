"""Shared data shapes. Labels, predictions and agent tool outputs all use these."""

from dataclasses import dataclass, field
from datetime import date

DOC_TYPES = ("certificate", "letter", "attestation", "audit_report", "other")


@dataclass
class Document:
    doc_id: str
    text: str


@dataclass
class Extraction:
    """The fields we pull out of one document. Blank means 'not found'."""

    doc_type: str | None = None
    vendor_name: str | None = None
    issue_date: date | None = None


@dataclass
class Prediction:
    """What a predictor (baseline, LLM, or the full agent) says about one document."""

    doc_id: str
    extraction: Extraction
    is_compliant: bool | None
    confidence: float = 1.0
    # Filled by the harness, not the predictor
    latency_s: float = 0.0
    cost_usd: float = 0.0
    meta: dict = field(default_factory=dict)


@dataclass
class Label:
    doc_id: str
    extraction: Extraction
    is_compliant: bool
