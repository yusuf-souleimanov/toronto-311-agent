"""LLM extraction predictor. Same prompt and schema for every provider, so the
comparison is about the model, not the prompt."""

from compliance_agent.schema import Document, Label, Prediction


class LLMPredictor:
    def __init__(self, provider: str):
        self.provider = provider
        self.name = provider

    def fit(self, docs: list[Document], labels: list[Label]) -> None:
        pass  # zero-shot; if you add few-shot examples, take them from the train split only

    def predict(self, doc: Document) -> Prediction:
        """TODO (Week 3):
        - structured output against a Pydantic model mirroring schema.Extraction
        - record input/output tokens in meta and compute cost_usd from the provider's price sheet
        - is_compliant comes from tools.check_compliance(issue_date), NOT from the model
        - confidence: ask the model for it, or use agreement across 2 samples (write down which)
        """
        raise NotImplementedError
