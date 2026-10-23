"""The traditional ML model: TF-IDF + logistic regression.

It turns a resident's message into a request type, with a confidence score.
It's fast, free and runs offline, so the agent calls it first; the eval
compares it against Claude to see whether the LLM is worth its cost.

Train and save it:   python -m agent311.classifier
"""

import csv
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from . import config

MODEL_PATH = config.MODELS_DIR / "classifier.pkl"


def load_messages(path):
    """Read a messages CSV. Returns three lists: texts, labels, styles."""
    texts, labels, styles = [], [], []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            texts.append(row["text"])
            labels.append(row["request_type"])
            styles.append(row.get("style", ""))   # only the test file has styles
    return texts, labels, styles


def build_model():
    """
    TfidfVectorizer turns text into numbers. analyzer="char_wb" looks at
    3-5 letter chunks instead of whole words, so "garbige" still looks a lot
    like "garbage". That makes the model much more forgiving of typos.

    LogisticRegression then learns which chunks point to which request type.
    """
    return make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True),
        LogisticRegression(max_iter=2000, C=10),
    )


def train(texts, labels):
    model = build_model()
    model.fit(texts, labels)
    return model


def save(model, path=MODEL_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(model, f)


def load(path=MODEL_PATH):
    """Load the saved model, training a fresh one first if none exists yet."""
    if not path.exists():
        texts, labels, _ = load_messages(config.MESSAGES_DIR / "train.csv")
        save(train(texts, labels), path)
    with open(path, "rb") as f:
        return pickle.load(f)


def predict_top(model, text, k=3):
    """Top k guesses as a list of (request_type, probability), best first."""
    probabilities = model.predict_proba([text])[0]
    pairs = list(zip(model.classes_, probabilities))
    pairs.sort(key=lambda pair: pair[1], reverse=True)
    # str() and float() turn numpy types into plain Python ones (cleaner JSON and printing)
    return [(str(label), round(float(prob), 3)) for label, prob in pairs[:k]]


if __name__ == "__main__":
    texts, labels, _ = load_messages(config.MESSAGES_DIR / "train.csv")
    model = train(texts, labels)
    save(model)
    print(f"Trained on {len(texts)} messages, saved to {MODEL_PATH}")

    test_texts, test_labels, _ = load_messages(config.MESSAGES_DIR / "test.csv")
    correct = sum(1 for t, y in zip(test_texts, test_labels) if model.predict([t])[0] == y)
    print(f"Test accuracy: {correct}/{len(test_texts)} = {correct / len(test_texts):.0%}")
