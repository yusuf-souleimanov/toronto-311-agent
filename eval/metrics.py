"""Scoring functions, written by hand with plain Python so you can see exactly
what each number means. (scikit-learn has versions of these too.)

Vocabulary, for one request type, say "Construction Noise":
  precision = of the messages we LABELLED construction noise, how many really were?
  recall    = of the messages that REALLY were construction noise, how many did we catch?
  F1        = one number that balances the two (their harmonic mean)
"""

from collections import Counter, defaultdict


def accuracy(true_labels, predicted_labels):
    if not true_labels:
        return 0.0
    correct = 0
    for true, predicted in zip(true_labels, predicted_labels):
        if true == predicted:
            correct += 1
    return correct / len(true_labels)


def per_class_scores(true_labels, predicted_labels):
    """Precision, recall and F1 for every label. Returns {label: {...}}."""
    labels = sorted(set(true_labels) | set(predicted_labels))
    scores = {}
    for label in labels:
        true_positive = false_positive = false_negative = 0
        for true, predicted in zip(true_labels, predicted_labels):
            if predicted == label and true == label:
                true_positive += 1
            elif predicted == label and true != label:
                false_positive += 1
            elif predicted != label and true == label:
                false_negative += 1

        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        scores[label] = {"precision": precision, "recall": recall, "f1": f1,
                         "support": true_positive + false_negative}
    return scores


def macro_f1(true_labels, predicted_labels):
    """Average F1 across labels that appear in the true labels. Every type counts equally."""
    scores = per_class_scores(true_labels, predicted_labels)
    real_labels = set(true_labels)
    f1s = [scores[label]["f1"] for label in real_labels]
    return sum(f1s) / len(f1s) if f1s else 0.0


def accuracy_by_group(true_labels, predicted_labels, groups):
    """Accuracy separately for each group (here: writing style). The fairness check."""
    buckets = defaultdict(lambda: [0, 0])   # group -> [correct, total]
    for true, predicted, group in zip(true_labels, predicted_labels, groups):
        buckets[group][1] += 1
        if true == predicted:
            buckets[group][0] += 1
    return {group: correct / total for group, (correct, total) in buckets.items()}


def top_confusions(true_labels, predicted_labels, n=5):
    """The most common (true, predicted) mistakes."""
    mistakes = Counter()
    for true, predicted in zip(true_labels, predicted_labels):
        if true != predicted:
            mistakes[(true, predicted)] += 1
    return mistakes.most_common(n)


def threshold_tradeoff(true_labels, predicted_labels, confidences, threshold):
    """
    If the agent asks a clarifying question whenever confidence < threshold:
      ask_rate         = share of messages that trigger a question (costs resident effort)
      accuracy_on_rest = accuracy on messages where it didn't ask (what actually gets filed)
    """
    answered_true, answered_pred, asked = [], [], 0
    for true, predicted, confidence in zip(true_labels, predicted_labels, confidences):
        if confidence < threshold:
            asked += 1
        else:
            answered_true.append(true)
            answered_pred.append(predicted)
    return {
        "threshold": threshold,
        "ask_rate": asked / len(true_labels) if true_labels else 0.0,
        "accuracy_on_rest": accuracy(answered_true, answered_pred) if answered_true else 0.0,
    }


def hit_at_k(expected, ranked_results, k):
    """Share of queries where the expected item appears in the top k results."""
    if not expected:
        return 0.0
    hits = 0
    for wanted, results in zip(expected, ranked_results):
        if wanted in results[:k]:
            hits += 1
    return hits / len(expected)
