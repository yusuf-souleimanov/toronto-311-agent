"""Evaluate the system and write a report to eval/reports/.

    python -m eval.run_eval                  # free parts only: baselines + retrieval
    python -m eval.run_eval --llm            # also classify with Claude models (costs a few cents)
    python -m eval.run_eval --llm --agent    # also run full agent conversations (costs more)
    python -m eval.run_eval --only gas --repeat 5   # just one scenario, several times

Three parts:
  1. Classification: majority baseline vs TF-IDF vs Claude, on the 96 test messages.
  2. Retrieval: does the knowledge base search find the right article?
  3. Agent scenarios: does the full agent call (and avoid) the right tools?
"""

import argparse
import json
import re
import time
from collections import Counter
from datetime import datetime

import anthropic

from agent311 import classifier, config, llm
from agent311.knowledge import KnowledgeBase

from . import metrics


# ---- Part 1: classification ------------------------------------------------

def predict_majority(train_labels, test_texts):
    """The 'dumbest possible' baseline: always guess the most common training label."""
    most_common = Counter(train_labels).most_common(1)[0][0]
    return [most_common] * len(test_texts), [1.0] * len(test_texts), 0.0, 0.0


def predict_tfidf(train_texts, train_labels, test_texts):
    model = classifier.train(train_texts, train_labels)
    predictions, confidences = [], []
    start = time.perf_counter()
    for text in test_texts:
        label, confidence = classifier.predict_top(model, text, k=1)[0]
        predictions.append(label)
        confidences.append(confidence)
    seconds_per_message = (time.perf_counter() - start) / len(test_texts)
    return predictions, confidences, 0.0, seconds_per_message


def predict_claude(model_name, test_texts):
    predictions, confidences, total_cost = [], [], 0.0
    start = time.perf_counter()
    for i, text in enumerate(test_texts, start=1):
        result = llm.classify_with_claude(text, model_name)
        predictions.append(result["request_type"])
        confidences.append(result["confidence"])
        total_cost += result["cost_usd"]
        print(f"  {model_name}: {i}/{len(test_texts)}", end="\r")
    print()
    seconds_per_message = (time.perf_counter() - start) / len(test_texts)
    return predictions, confidences, total_cost / len(test_texts), seconds_per_message


def score_classifier(name, test_labels, test_styles, predictions, confidences, cost, seconds):
    return {
        "name": name,
        "accuracy": metrics.accuracy(test_labels, predictions),
        "macro_f1": metrics.macro_f1(test_labels, predictions),
        "by_style": metrics.accuracy_by_group(test_labels, predictions, test_styles),
        "top_confusions": metrics.top_confusions(test_labels, predictions),
        "thresholds": [metrics.threshold_tradeoff(test_labels, predictions, confidences, t)
                       for t in (0.2, 0.25, 0.3, 0.4, 0.5)],
        "cost_per_message_usd": cost,
        "seconds_per_message": seconds,
    }


def run_classification(use_llm):
    train_texts, train_labels, _ = classifier.load_messages(config.MESSAGES_DIR / "train.csv")
    test_texts, test_labels, test_styles = classifier.load_messages(config.MESSAGES_DIR / "test.csv")

    results = []
    preds, confs, cost, secs = predict_majority(train_labels, test_texts)
    results.append(score_classifier("majority baseline", test_labels, test_styles, preds, confs, cost, secs))

    preds, confs, cost, secs = predict_tfidf(train_texts, train_labels, test_texts)
    results.append(score_classifier("tf-idf + logistic regression", test_labels, test_styles,
                                    preds, confs, cost, secs))

    if use_llm:
        for model_name in config.EVAL_MODELS:
            preds, confs, cost, secs = predict_claude(model_name, test_texts)
            results.append(score_classifier(model_name, test_labels, test_styles, preds, confs, cost, secs))
    return results


# ---- Part 2: retrieval -----------------------------------------------------

def run_retrieval():
    import csv
    knowledge_base = KnowledgeBase()
    expected, ranked = [], []
    with open(config.ROOT / "eval" / "retrieval_questions.csv", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            expected.append(row["expected_file"])
            ranked.append([r["file"] for r in knowledge_base.search(row["question"], k=3)])
    misses = [(q_expected, q_ranked[0]) for q_expected, q_ranked in zip(expected, ranked)
              if q_ranked[0] != q_expected]
    return {
        "questions": len(expected),
        "hit_at_1": metrics.hit_at_k(expected, ranked, 1),
        "hit_at_3": metrics.hit_at_k(expected, ranked, 3),
        "misses_at_1": misses,
    }


# ---- Part 3: agent scenarios -----------------------------------------------

# Matches North American phone numbers like 1-866-555-1234, (416) 555-1234, 416.555.1234
PHONE_PATTERN = re.compile(r"(?:\b1[-\s.]?)?\(?\b\d{3}\)?[-\s.]\d{3}[-\s.]\d{4}\b")


def unverified_phone_numbers(text, knowledge_base):
    """Phone numbers in the agent's reply that don't appear in any knowledge base article.
    (911 and 311 are too short to match the pattern, so they're always allowed.)"""
    allowed = set()
    for article in knowledge_base.articles:
        for number in PHONE_PATTERN.findall(article["text"]):
            allowed.add(re.sub(r"\D", "", number))   # compare digits only
    found = []
    for number in PHONE_PATTERN.findall(text):
        if re.sub(r"\D", "", number) not in allowed:
            found.append(number)
    return found


def run_scenarios(only=None, repeat=1):
    from agent311 import data
    from agent311.agent import create_agent

    with open(config.ROOT / "eval" / "scenarios.json", encoding="utf-8") as f:
        scenarios = json.load(f)

    # Load the heavy things once and share them across scenarios.
    rows = data.load_requests()
    model = classifier.load()
    knowledge_base = KnowledgeBase()

    if only:
        scenarios = [s for s in scenarios if only.lower() in s["name"].lower()]
    # The model's replies vary between runs, so a scenario can be repeated.
    scenarios = [s for s in scenarios for _ in range(repeat)]

    results = []
    for scenario in scenarios:
        agent = create_agent(rows=rows, model=model, knowledge_base=knowledge_base)
        replies = [agent.send(turn) for turn in scenario["turns"]]
        called = agent.audit.tools_called()
        submitted = any(e["event"] == "request_submitted" for e in agent.audit.events)

        problems = []
        for tool in scenario.get("must_call", []):
            if tool not in called:
                problems.append(f"did not call {tool}")
        for tool in scenario.get("must_not_call", []):
            if tool in called:
                problems.append(f"called {tool}")
        for text in scenario.get("reply_must_contain", []):
            if text not in replies[-1]:
                problems.append(f"reply missing '{text}'")
        # Checked for every scenario: no phone numbers from the model's memory.
        for number in unverified_phone_numbers(" ".join(replies), knowledge_base):
            problems.append(f"gave unverified phone number {number}")
        if scenario.get("must_submit") and not submitted:
            problems.append("request was not submitted")
        if scenario.get("must_not_submit") and submitted:
            problems.append("request was submitted without confirmation")

        results.append({
            "name": scenario["name"],
            "passed": not problems,
            "problems": problems,
            "tools_called": called,
            "last_reply": replies[-1],
            "cost_usd": agent.total_cost_usd,
        })
        print(f"  {'PASS' if not problems else 'FAIL'}  {scenario['name']}")
    return results


# ---- Report ----------------------------------------------------------------

def percent(x):
    return f"{x:.0%}"


def build_report(classification, retrieval, scenarios):
    lines = [f"# Evaluation report ({datetime.now():%Y-%m-%d %H:%M})", ""]

    lines += ["## 1. Classification (96 test messages, 16 classes)", "",
              "| System | Accuracy | Macro F1 | Cost / message | Time / message |",
              "|---|---|---|---|---|"]
    for r in classification:
        lines.append(f"| {r['name']} | {percent(r['accuracy'])} | {r['macro_f1']:.2f} "
                     f"| ${r['cost_per_message_usd']:.5f} | {r['seconds_per_message']:.3f}s |")

    styles = list(classification[0]["by_style"].keys())
    lines += ["", "### Accuracy by writing style (fairness check)", "",
              "| System | " + " | ".join(styles) + " |",
              "|---|" + "---|" * len(styles)]
    for r in classification:
        lines.append(f"| {r['name']} | " + " | ".join(percent(r["by_style"][s]) for s in styles) + " |")

    lines += ["", "### Clarifying-question threshold (TF-IDF)", "",
              "If the agent asks a question whenever confidence is below the threshold:", "",
              "| Threshold | Asks a question | Accuracy when it doesn't ask |", "|---|---|---|"]
    tfidf = next(r for r in classification if r["name"].startswith("tf-idf"))
    for t in tfidf["thresholds"]:
        lines.append(f"| {t['threshold']} | {percent(t['ask_rate'])} | {percent(t['accuracy_on_rest'])} |")

    lines += ["", "### Most common mistakes", ""]
    for r in classification[1:]:
        lines.append(f"**{r['name']}**")
        for (true, predicted), count in r["top_confusions"]:
            lines.append(f"- {count}x  true: {true}  ->  predicted: {predicted}")
        lines.append("")

    lines += ["## 2. Knowledge base retrieval", "",
              f"- Questions: {retrieval['questions']}",
              f"- Right article ranked first: {percent(retrieval['hit_at_1'])}",
              f"- Right article in top 3: {percent(retrieval['hit_at_3'])}", ""]
    for expected, got in retrieval["misses_at_1"]:
        lines.append(f"- Miss: expected {expected}, got {got}")
    lines.append("")

    lines += ["## 3. Agent scenarios", ""]
    if scenarios is None:
        lines.append("Not run (use --llm --agent).")
    else:
        passed = sum(1 for s in scenarios if s["passed"])
        total_cost = sum(s["cost_usd"] for s in scenarios)
        lines.append(f"Passed {passed}/{len(scenarios)}. Total cost ${total_cost:.4f}.")
        lines.append("")
        for s in scenarios:
            status = "PASS" if s["passed"] else "FAIL: " + "; ".join(s["problems"])
            lines.append(f"- **{s['name']}**: {status}. Tools: {', '.join(s['tools_called']) or 'none'}")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", action="store_true", help="include Claude classification (costs money)")
    parser.add_argument("--agent", action="store_true", help="run agent scenarios (costs money)")
    parser.add_argument("--only", help="run only scenarios whose name contains this text (skips parts 1-2)")
    parser.add_argument("--repeat", type=int, default=1, help="run each scenario this many times")
    args = parser.parse_args()

    if args.only:
        # Quick check of specific scenarios, e.g.  --only gas --repeat 5
        if not config.has_api_key():
            print("ANTHROPIC_API_KEY not set.")
            return
        results = run_scenarios(args.only, args.repeat)
        passed = sum(1 for r in results if r["passed"])
        print(f"\nPassed {passed}/{len(results)}. Cost ${sum(r['cost_usd'] for r in results):.4f}")
        for r in results:
            if not r["passed"]:
                print(f"  FAIL {r['name']}: {'; '.join(r['problems'])}")
        return

    if (args.llm or args.agent) and not config.has_api_key():
        print("ANTHROPIC_API_KEY not set: running free parts only.")
        args.llm = args.agent = False

    print("Classification...")
    try:
        classification = run_classification(args.llm)
    except anthropic.AuthenticationError:
        print("The API key was rejected (401). Check ANTHROPIC_API_KEY in this project's .env.")
        return
    print("Retrieval...")
    retrieval = run_retrieval()
    scenarios = None
    if args.agent:
        print("Agent scenarios...")
        scenarios = run_scenarios()

    report = build_report(classification, retrieval, scenarios)
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (config.REPORTS_DIR / f"report-{stamp}.md").write_text(report, encoding="utf-8")
    raw = {"classification": classification, "retrieval": retrieval, "scenarios": scenarios}
    (config.REPORTS_DIR / f"report-{stamp}.json").write_text(json.dumps(raw, indent=2, default=str),
                                                            encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
