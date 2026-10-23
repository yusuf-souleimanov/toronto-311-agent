import unittest

from eval import metrics


class MetricsTest(unittest.TestCase):
    def test_accuracy(self):
        self.assertEqual(metrics.accuracy(["a", "b", "c", "d"], ["a", "b", "x", "d"]), 0.75)

    def test_precision_and_recall(self):
        true = ["noise", "noise", "pothole", "pothole"]
        pred = ["noise", "pothole", "pothole", "pothole"]
        scores = metrics.per_class_scores(true, pred)
        # We said "pothole" 3 times, 2 were right -> precision 2/3. Caught 2 of 2 real potholes -> recall 1.
        self.assertAlmostEqual(scores["pothole"]["precision"], 2 / 3)
        self.assertEqual(scores["pothole"]["recall"], 1.0)
        # Caught 1 of 2 real noise messages -> recall 0.5
        self.assertEqual(scores["noise"]["recall"], 0.5)

    def test_accuracy_by_group(self):
        result = metrics.accuracy_by_group(["a", "a", "b"], ["a", "x", "b"], ["plain", "typos", "plain"])
        self.assertEqual(result, {"plain": 1.0, "typos": 0.0})

    def test_threshold_tradeoff(self):
        result = metrics.threshold_tradeoff(["a", "b"], ["a", "x"], [0.9, 0.1], threshold=0.5)
        self.assertEqual(result["ask_rate"], 0.5)          # the low-confidence one triggers a question
        self.assertEqual(result["accuracy_on_rest"], 1.0)  # the one it answered was right

    def test_hit_at_k(self):
        self.assertEqual(metrics.hit_at_k(["x", "y"], [["x", "z"], ["z", "y"]], 1), 0.5)
        self.assertEqual(metrics.hit_at_k(["x", "y"], [["x", "z"], ["z", "y"]], 2), 1.0)


if __name__ == "__main__":
    unittest.main()
