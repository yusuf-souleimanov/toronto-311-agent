"""Run predictors over the labelled set and write a comparison report.

    python -m eval.run_eval --predictors dummy tfidf claude
"""

import argparse
import json
import time
from dataclasses import asdict
from datetime import datetime

from compliance_agent.config import REPORTS_DIR, load_settings

from .dataset import load_documents, load_labels
from .metrics import field_accuracy, flag_scores, latency_cost
from .predictors import PREDICTORS

FIELDS = ("doc_type", "vendor_name", "issue_date")


def evaluate(predictor, docs, labels) -> dict:
    predictor.fit(docs, labels)
    preds = {}
    for doc in docs:
        start = time.perf_counter()
        pred = predictor.predict(doc)
        pred.latency_s = time.perf_counter() - start
        preds[doc.doc_id] = pred
    return {
        "predictor": predictor.name,
        "n_docs": len(labels),
        "field_accuracy": {f: field_accuracy(labels, preds, f) for f in FIELDS},
        "flags": asdict(flag_scores(labels, preds)),
        **latency_cost(preds),
    }


def to_markdown(results: list[dict], settings) -> str:
    lines = [
        f"# Eval report, {datetime.now():%Y-%m-%d %H:%M}",
        "",
        f"As-of date: {settings.as_of_date} · Max doc age: {settings.max_doc_age_years} years · "
        f"Docs: {results[0]['n_docs'] if results else 0}",
        "",
        "| Predictor | doc_type acc | vendor acc | date acc | Flag precision | Flag recall | F1 | Review rate | Cost/doc | p95 latency |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        fa, fl = r["field_accuracy"], r["flags"]
        lines.append(
            f"| {r['predictor']} | {fa['doc_type']:.0%} | {fa['vendor_name']:.0%} | {fa['issue_date']:.0%} "
            f"| {fl['precision']:.0%} | {fl['recall']:.0%} | {fl['f1']:.2f} | {fl['review_rate']:.0%} "
            f"| ${r['cost_per_doc_usd']:.4f} | {r['p95_latency_s']:.2f}s |"
        )
    lines += ["", "## What this means", "", "TODO: write 3–5 sentences a compliance manager could act on."]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictors", nargs="+", default=["dummy"], choices=sorted(PREDICTORS))
    args = parser.parse_args()

    labels = load_labels()
    if not labels:
        print("data/labels/labels.csv has no rows yet. Label some documents first.")
        return
    docs = load_documents(labels)
    settings = load_settings()

    results = [evaluate(PREDICTORS[name](), docs, labels) for name in args.predictors]

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (REPORTS_DIR / f"{stamp}.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    report = to_markdown(results, settings)
    (REPORTS_DIR / f"{stamp}.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
