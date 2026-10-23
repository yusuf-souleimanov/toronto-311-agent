"""Load the labelled set and the matching extracted text."""

import csv
from datetime import date
from pathlib import Path

from compliance_agent.config import LABELS_PATH, PROCESSED_DIR
from compliance_agent.schema import Document, Extraction, Label


def load_labels(path: Path = LABELS_PATH) -> list[Label]:
    labels = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            labels.append(
                Label(
                    doc_id=row["doc_id"],
                    extraction=Extraction(
                        doc_type=row["doc_type"] or None,
                        vendor_name=row["vendor_name"] or None,
                        issue_date=date.fromisoformat(row["issue_date"]) if row["issue_date"] else None,
                    ),
                    is_compliant=row["is_compliant"].strip().lower() == "true",
                )
            )
    return labels


def load_documents(labels: list[Label], processed_dir: Path = PROCESSED_DIR) -> list[Document]:
    """Text for every labelled doc. Missing text is an error: run extraction first."""
    docs = []
    missing = []
    for label in labels:
        path = processed_dir / f"{label.doc_id}.txt"
        if path.exists():
            docs.append(Document(label.doc_id, path.read_text(encoding="utf-8")))
        else:
            missing.append(label.doc_id)
    if missing:
        raise FileNotFoundError(
            f"No extracted text for {len(missing)} docs (e.g. {missing[:3]}). "
            "Run: python -m compliance_agent.extraction"
        )
    return docs
