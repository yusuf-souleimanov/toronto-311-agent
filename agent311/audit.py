"""Audit log: every tool call and decision, one JSON line each.

Why: if the agent ever does something odd, you (or an auditor) can open the log
and see exactly what it was asked, which tools it used, and what came back.
"""

import json
from datetime import datetime

from . import config


class AuditLog:
    def __init__(self, session_id):
        config.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.path = config.LOG_DIR / f"session-{session_id}.jsonl"
        self.session_id = session_id
        self.events = []   # also kept in memory so tests and the eval can read them

    def record(self, event, **details):
        entry = {"time": datetime.now().isoformat(timespec="seconds"), "event": event}
        entry.update(details)
        self.events.append(entry)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    def tools_called(self):
        """Names of every tool the agent called, in order."""
        names = []
        for e in self.events:
            if e["event"] == "tool_call":
                names.append(e["tool"])
        return names
