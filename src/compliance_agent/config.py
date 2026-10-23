"""Settings read from the environment (see .env.example)."""

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
LABELS_PATH = DATA_DIR / "labels" / "labels.csv"
REPORTS_DIR = ROOT / "eval" / "reports"
LOG_DIR = ROOT / "logs"


@dataclass(frozen=True)
class Settings:
    max_doc_age_years: int
    as_of_date: date
    review_confidence_threshold: float


def load_settings() -> Settings:
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    return Settings(
        max_doc_age_years=int(os.getenv("MAX_DOC_AGE_YEARS", "3")),
        as_of_date=date.fromisoformat(os.getenv("EVAL_AS_OF_DATE", date.today().isoformat())),
        review_confidence_threshold=float(os.getenv("REVIEW_CONFIDENCE_THRESHOLD", "0.8")),
    )
