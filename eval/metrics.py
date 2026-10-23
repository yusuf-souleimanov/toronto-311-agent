"""Scoring functions. Pure Python, no dependencies, fully unit-tested.

Convention: the positive class is "flagged" (non-compliant). Recall on flags is
the number that matters most to a compliance team: a missed stale document is
worse than an extra one sent to review.
"""

import re
import statistics
from dataclasses import dataclass

from compliance_agent.schema import Label, Prediction


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"[^\w\s]", " ", value.casefold())
    return " ".join(value.split())


def field_accuracy(labels: list[Label], preds: dict[str, Prediction], field: str) -> float:
    """Share of documents where the predicted field matches the label.
    Both blank counts as correct (the model rightly found nothing)."""
    if not labels:
        return 0.0
    correct = 0
    for label in labels:
        pred = preds.get(label.doc_id)
        expected = getattr(label.extraction, field)
        got = getattr(pred.extraction, field) if pred else None
        if isinstance(expected, str) or isinstance(got, str):
            correct += normalize_text(expected) == normalize_text(got)
        else:
            correct += expected == got
    return correct / len(labels)


@dataclass
class FlagScores:
    precision: float
    recall: float
    f1: float
    review_rate: float  # share of docs where the predictor abstained (is_compliant=None)
    tp: int
    fp: int
    fn: int
    tn: int


def flag_scores(labels: list[Label], preds: dict[str, Prediction]) -> FlagScores:
    """Precision/recall on the 'flagged' class.

    An abstention (None) goes to human review, so it counts as flagged: it catches
    the stale doc (no false negative) but costs reviewer time (shows in review_rate).
    """
    tp = fp = fn = tn = abstained = 0
    for label in labels:
        pred = preds.get(label.doc_id)
        verdict = pred.is_compliant if pred else None
        if verdict is None:
            abstained += 1
        predicted_flag = verdict is not True
        actual_flag = not label.is_compliant
        if predicted_flag and actual_flag:
            tp += 1
        elif predicted_flag:
            fp += 1
        elif actual_flag:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    review_rate = abstained / len(labels) if labels else 0.0
    return FlagScores(precision, recall, f1, review_rate, tp, fp, fn, tn)


def latency_cost(preds: dict[str, Prediction]) -> dict[str, float]:
    latencies = sorted(p.latency_s for p in preds.values())
    if not latencies:
        return {"mean_latency_s": 0.0, "p95_latency_s": 0.0, "total_cost_usd": 0.0, "cost_per_doc_usd": 0.0}
    p95_index = max(0, int(round(0.95 * len(latencies))) - 1)
    total_cost = sum(p.cost_usd for p in preds.values())
    return {
        "mean_latency_s": statistics.fmean(latencies),
        "p95_latency_s": latencies[p95_index],
        "total_cost_usd": total_cost,
        "cost_per_doc_usd": total_cost / len(latencies),
    }
