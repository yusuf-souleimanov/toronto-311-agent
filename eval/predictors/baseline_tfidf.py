"""Traditional ML baseline: TF-IDF + logistic regression for doc_type, regex heuristics for
the date, and the same deterministic rule for compliance.

This is the "is the LLM worth it?" comparison. Report it honestly even if it wins.
"""

from compliance_agent.schema import Document, Label, Prediction


class TfidfBaseline:
    name = "tfidf"

    def fit(self, docs: list[Document], labels: list[Label]) -> None:
        """TODO (Week 3):
        - sklearn Pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2), LogisticRegression(max_iter=1000))
        - IMPORTANT: train on a split the harness never scores on. Use cross_val_predict
          or a fixed train/test split, and write down which one in the eval report.
        """
        raise NotImplementedError

    def predict(self, doc: Document) -> Prediction:
        """TODO (Week 3): doc_type from the classifier, issue_date from
        extraction.heuristic_extract, is_compliant from tools.check_compliance.
        confidence = classifier predict_proba max."""
        raise NotImplementedError
