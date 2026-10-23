"""The tools the agent can use, and their descriptions for Claude.

How tool use works:
  1. We send Claude a list of tools (TOOL_SCHEMAS): a name, a description,
     and what inputs each tool takes.
  2. When Claude wants one, it replies with a "tool_use" block such as
     {"name": "get_area_stats", "input": {"area": "M6H"}}.
  3. Our code runs the real Python function (Toolbox.run) and sends back the result.
Claude never runs code itself. It only asks, and we decide what actually happens.
"""

import json
import re
from datetime import datetime

from . import classifier, config, data, stats

TOOL_SCHEMAS = [
    {
        "name": "classify_request",
        "description": (
            "Guess which 311 request type a resident's problem belongs to, using a trained "
            "classifier. Returns the top 3 guesses with confidence scores and the responsible "
            "City division. Call this once you understand the problem."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "The problem in the resident's words."}
            },
            "required": ["description"],
        },
    },
    {
        "name": "get_area_stats",
        "description": (
            "Look up real 2025 City of Toronto 311 data for an area: total requests, the most "
            "common request types, and optionally how often one request type was reported there. "
            "Area can be a postal code prefix like M6H, or a ward name or number."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "area": {"type": "string"},
                "request_type": {"type": "string", "description": "Optional exact request type name."},
            },
            "required": ["area"],
        },
    },
    {
        "name": "search_city_info",
        "description": (
            "Search the 311 knowledge base for guidance: what to check before reporting, safety "
            "advice, what information to include. Use it before giving the resident advice."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "draft_service_request",
        "description": (
            "Prepare a service request for the resident to review. This does NOT submit it: "
            "the resident must reply 'yes' to submit. Only call this when you know the request "
            "type and a specific location."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "request_type": {"type": "string", "enum": config.REQUEST_TYPES},
                "location": {"type": "string", "description": "Street address, intersection, or postal code."},
                "description": {"type": "string", "description": "One or two sentence summary of the problem."},
            },
            "required": ["request_type", "location", "description"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": (
            "Hand the conversation to a human 311 agent. Use when the request doesn't fit any "
            "request type, the resident is upset or asks for a person, or you are unsure."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string"},
                "summary": {"type": "string", "description": "What the resident needs, for the human agent."},
            },
            "required": ["reason", "summary"],
        },
    },
]


def looks_like_location(text):
    """Very simple check that a location is specific enough for a crew to find."""
    text = text.strip()
    if stats.FSA_PATTERN.match(text.upper()[:3]):               # postal code like M6H or M6H 2B4
        return True
    if re.search(r"\d+\s+\w+", text):                          # address like "123 Main St"
        return True
    lowered = f" {text.lower()} "
    if "&" in text or " and " in lowered or " at " in lowered:  # intersection
        return True
    return False


class Toolbox:
    """Holds what the tools need (data, classifier, knowledge base) and runs them."""

    def __init__(self, rows, model, knowledge_base, audit):
        self.rows = rows
        self.model = model
        self.knowledge_base = knowledge_base
        self.audit = audit
        self.pending_draft = None   # a drafted request waiting for the resident's "yes"

        # Work out each request type's division once, instead of on every call.
        self.divisions = {}
        for request_type in config.REQUEST_TYPES:
            self.divisions[request_type] = data.division_for_type(rows, request_type)

    def run(self, name, tool_input):
        """Run one tool by name. Always returns a JSON string for Claude to read."""
        self.audit.record("tool_call", tool=name, input=tool_input)
        try:
            if name == "classify_request":
                result = self.classify_request(tool_input["description"])
            elif name == "get_area_stats":
                result = self.get_area_stats(tool_input["area"], tool_input.get("request_type"))
            elif name == "search_city_info":
                result = self.search_city_info(tool_input["query"])
            elif name == "draft_service_request":
                result = self.draft_service_request(
                    tool_input["request_type"], tool_input["location"], tool_input["description"])
            elif name == "escalate_to_human":
                result = self.escalate_to_human(tool_input["reason"], tool_input["summary"])
            else:
                result = {"error": f"Unknown tool {name}"}
        except KeyError as missing:
            result = {"error": f"Missing input: {missing}"}

        self.audit.record("tool_result", tool=name, result=result)
        return json.dumps(result, default=str)

    # ---- the tools ---------------------------------------------------------

    def classify_request(self, description):
        guesses = classifier.predict_top(self.model, description, k=3)
        best_type, best_confidence = guesses[0]
        result = {
            "top_guesses": [{"request_type": t, "confidence": c} for t, c in guesses],
            "confident": best_confidence >= config.CONFIDENCE_THRESHOLD and best_type != "OTHER",
        }
        if best_type in self.divisions:
            result["division"] = self.divisions[best_type]
        if not result["confident"]:
            result["instruction"] = (
                "Not confident. Ask the resident a clarifying question that tells the top "
                "options apart, or escalate if none fit. Do not assume a type."
            )
        return result

    def get_area_stats(self, area, request_type=None):
        result = stats.area_summary(self.rows, area, request_type)
        result["note"] = "Counts of 311 reports in 2025, not counts of actual problems."
        return result

    def search_city_info(self, query):
        results = self.knowledge_base.search(query, k=2)
        return {
            "articles": [{"title": r["title"], "score": r["score"], "text": r["text"]} for r in results],
            "note": "Demo knowledge base, not official City policy.",
        }

    def draft_service_request(self, request_type, location, description):
        if request_type not in config.REQUEST_TYPES:
            return {"error": f"'{request_type}' is not a request type this assistant can file."}
        if not looks_like_location(location):
            return {"error": "Location too vague. Ask for a street address, intersection, or postal code."}

        self.pending_draft = {
            "request_type": request_type,
            "division": self.divisions[request_type],
            "location": location.strip(),
            "description": description.strip(),
            "drafted_at": datetime.now().isoformat(timespec="seconds"),
        }
        return {
            "draft": self.pending_draft,
            "instruction": "Show this draft to the resident and ask them to reply 'yes' to submit it.",
        }

    def submit_pending_draft(self):
        """Called by the AGENT CODE (never by Claude) after the resident types yes."""
        request = dict(self.pending_draft)
        request["reference"] = "DEMO-" + datetime.now().strftime("%Y%m%d-%H%M%S")
        save_jsonl(config.OUTBOX_DIR / "submitted_requests.jsonl", request)
        self.audit.record("request_submitted", request=request)
        self.pending_draft = None
        return request

    def escalate_to_human(self, reason, summary):
        ticket = {
            "reason": reason,
            "summary": summary,
            "time": datetime.now().isoformat(timespec="seconds"),
        }
        save_jsonl(config.OUTBOX_DIR / "escalations.jsonl", ticket)
        return {
            "status": "escalated",
            "message_for_resident": "A 311 agent will follow up. For anything urgent, call 311 directly.",
        }


def save_jsonl(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
