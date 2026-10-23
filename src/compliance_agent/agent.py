"""LangGraph agent. Week 2 builds this out; the shape is fixed now so eval can target it.

Graph:
    route  ->  (single doc)  extract -> decide -> [review | done]
           ->  (question)    retrieve -> answer

`decide` applies rules.is_compliant to the extracted date. If the extraction
confidence is below REVIEW_CONFIDENCE_THRESHOLD, or the rule returns None, the
document goes to `review` (human-in-the-loop interrupt) instead of `done`.
"""

from typing import TypedDict

from .schema import Extraction


class AgentState(TypedDict, total=False):
    question: str
    doc_id: str
    extraction: Extraction
    confidence: float
    is_compliant: bool | None
    needs_review: bool
    answer: str


def build_graph():
    """TODO (Week 2):
    1. StateGraph(AgentState) with nodes route, extract, decide, review, retrieve, answer
    2. conditional edge after decide on state['needs_review']
    3. interrupt_before=['review'] with a checkpointer, so a human approves or overrides
    4. AuditLog.record(...) inside every node
    """
    raise NotImplementedError
