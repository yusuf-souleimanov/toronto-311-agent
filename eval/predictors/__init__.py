"""Every system we compare implements the same interface, so the harness treats them alike.

    class MyPredictor:
        name = "my-predictor"
        def fit(self, docs, labels): ...        # optional; only the ML baseline trains
        def predict(self, doc) -> Prediction: ...

Register new predictors in PREDICTORS below.
"""

from .baseline_tfidf import TfidfBaseline
from .dummy import DummyPredictor
from .llm import LLMPredictor

PREDICTORS = {
    "dummy": DummyPredictor,
    "tfidf": TfidfBaseline,
    "claude": lambda: LLMPredictor(provider="anthropic"),
    "second-llm": lambda: LLMPredictor(provider="second"),
    # "agent": AgentPredictor,  # Week 3: wrap the full LangGraph agent
}
