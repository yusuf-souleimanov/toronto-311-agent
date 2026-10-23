import unittest
from datetime import date

from compliance_agent.rules import is_compliant
from compliance_agent.schema import Extraction, Label, Prediction
from eval.metrics import field_accuracy, flag_scores, latency_cost


def label(doc_id, compliant, vendor=None, issued=None):
    return Label(doc_id, Extraction(vendor_name=vendor, issue_date=issued), compliant)


def pred(doc_id, compliant, vendor=None, issued=None, latency=0.0, cost=0.0):
    return Prediction(doc_id, Extraction(vendor_name=vendor, issue_date=issued), compliant,
                      latency_s=latency, cost_usd=cost)


class FieldAccuracyTest(unittest.TestCase):
    def test_vendor_match_ignores_case_and_punctuation(self):
        labels = [label("a", True, vendor="Acme Corp.")]
        preds = {"a": pred("a", True, vendor="ACME corp")}
        self.assertEqual(field_accuracy(labels, preds, "vendor_name"), 1.0)

    def test_both_blank_counts_as_correct(self):
        labels = [label("a", True)]
        preds = {"a": pred("a", True)}
        self.assertEqual(field_accuracy(labels, preds, "issue_date"), 1.0)

    def test_missing_prediction_is_wrong(self):
        labels = [label("a", True, issued=date(2024, 1, 1))]
        self.assertEqual(field_accuracy(labels, {}, "issue_date"), 0.0)


class FlagScoresTest(unittest.TestCase):
    def test_confusion_counts(self):
        labels = [label("tp", False), label("fp", True), label("fn", False), label("tn", True)]
        preds = {
            "tp": pred("tp", False),
            "fp": pred("fp", False),
            "fn": pred("fn", True),
            "tn": pred("tn", True),
        }
        s = flag_scores(labels, preds)
        self.assertEqual((s.tp, s.fp, s.fn, s.tn), (1, 1, 1, 1))
        self.assertAlmostEqual(s.precision, 0.5)
        self.assertAlmostEqual(s.recall, 0.5)

    def test_abstention_counts_as_flag_and_review(self):
        labels = [label("a", False), label("b", True)]
        preds = {"a": pred("a", None), "b": pred("b", None)}
        s = flag_scores(labels, preds)
        self.assertEqual(s.recall, 1.0)
        self.assertEqual(s.review_rate, 1.0)
        self.assertEqual(s.fp, 1)


class LatencyCostTest(unittest.TestCase):
    def test_cost_per_doc(self):
        preds = {"a": pred("a", True, latency=1.0, cost=0.02), "b": pred("b", True, latency=3.0, cost=0.04)}
        out = latency_cost(preds)
        self.assertAlmostEqual(out["cost_per_doc_usd"], 0.03)
        self.assertEqual(out["p95_latency_s"], 3.0)


class RuleTest(unittest.TestCase):
    as_of = date(2026, 10, 1)

    def test_recent_doc_is_compliant(self):
        self.assertTrue(is_compliant(date(2025, 1, 1), self.as_of, 3))

    def test_old_doc_is_flagged(self):
        self.assertFalse(is_compliant(date(2021, 1, 1), self.as_of, 3))

    def test_undated_or_future_doc_needs_review(self):
        self.assertIsNone(is_compliant(None, self.as_of, 3))
        self.assertIsNone(is_compliant(date(2027, 1, 1), self.as_of, 3))


if __name__ == "__main__":
    unittest.main()
