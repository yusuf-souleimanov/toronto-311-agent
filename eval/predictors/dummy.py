"""Floor baseline: predicts the most common label for everything.

Any real system must beat this. It also lets you run the harness end to end
before anything else is built.
"""

from collections import Counter

from compliance_agent.schema import Document, Extraction, Label, Prediction


class DummyPredictor:
    name = "dummy"

    def __init__(self):
        self.doc_type = None
        self.is_compliant = True

    def fit(self, docs: list[Document], labels: list[Label]) -> None:
        if labels:
            self.doc_type = Counter(l.extraction.doc_type for l in labels).most_common(1)[0][0]
            self.is_compliant = Counter(l.is_compliant for l in labels).most_common(1)[0][0]

    def predict(self, doc: Document) -> Prediction:
        return Prediction(
            doc_id=doc.doc_id,
            extraction=Extraction(doc_type=self.doc_type),
            is_compliant=self.is_compliant,
        )
