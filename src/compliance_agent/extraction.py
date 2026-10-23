"""PDF -> text, and text -> fields with deterministic heuristics.

Port your externship techniques here, rewritten from scratch against public docs:
PyMuPDF / pdfplumber text, OCR fallback for scans, regex + anchor phrases for dates.
"""

from datetime import date
from pathlib import Path

from .config import PROCESSED_DIR, RAW_DIR
from .schema import Extraction


def pdf_to_text(pdf_path: Path) -> str:
    """Extract text from a PDF. TODO (Week 1): PyMuPDF first, pdfplumber for tables,
    OCR (Tesseract or PaddleOCR) when a page has almost no text layer."""
    raise NotImplementedError


def extract_all(raw_dir: Path = RAW_DIR, out_dir: Path = PROCESSED_DIR) -> None:
    """Write data/processed/<doc_id>.txt for every PDF in data/raw/. Skips ones already done."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for pdf in sorted(raw_dir.glob("*.pdf")):
        out = out_dir / f"{pdf.stem}.txt"
        if not out.exists():
            out.write_text(pdf_to_text(pdf), encoding="utf-8")


def find_dates(text: str) -> list[date]:
    """All dates in the text. TODO (Week 1): handle '12 March 2023', '2023-03-12',
    '03/12/2023' (ambiguous: write down which convention you pick and why)."""
    raise NotImplementedError


def heuristic_extract(text: str) -> Extraction:
    """Rule-based extraction: anchor phrases ('Date of issue', 'Issued on') first,
    then fall back to the most recent plausible date. TODO (Week 1)."""
    raise NotImplementedError


if __name__ == "__main__":
    extract_all()
