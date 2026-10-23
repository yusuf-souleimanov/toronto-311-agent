"""Append-only audit log: every tool call and decision the agent makes, one JSON line each.

This file is governance evidence. A reviewer should be able to rebuild why any
document was flagged from the log alone.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import LOG_DIR


class AuditLog:
    def __init__(self, run_id: str, log_dir: Path = LOG_DIR):
        log_dir.mkdir(parents=True, exist_ok=True)
        self.path = log_dir / f"audit-{run_id}.jsonl"
        self.run_id = run_id

    def record(self, event: str, **data) -> None:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "event": event,
            **data,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
