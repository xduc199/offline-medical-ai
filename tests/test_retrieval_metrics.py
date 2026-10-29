import unittest
from types import SimpleNamespace

from app.retrieval_metrics import aggregate_metrics, page_from_result, retrieval_metrics


class RetrievalMetricsTests(unittest.TestCase):
    def test_recall_at_k_counts_relevant_pages(self):
        results = [
            (SimpleNamespace(page="32"), 0.9),
            (SimpleNamespace(page="33"), 0.8),
            (SimpleNamespace(page="70"), 0.7),
        ]
        metrics = retrieval_metrics(results, [32, 33, 34], k=2)
        self.assertAlmostEqual(metrics["recall_at_k"], 2 / 3)
        self.assertEqual(metrics["mrr"], 1.0)
        self.assertEqual(metrics["hit_at_k"], 1)

    def test_mrr_uses_first_relevant_rank(self):
        results = [
            {"page": "10", "index": 1},
            {"page": "20", "index": 2},
            {"page": "30", "index": 3},
        ]
        metrics = retrieval_metrics(results, [20, 30], k=3)
        self.assertEqual(metrics["recall_at_k"], 1.0)
        self.assertAlmostEqual(metrics["mrr"], 0.5)

    def test_unlabelled_case_is_explicitly_unscored(self):
        metrics = retrieval_metrics([{"page": "10"}], [], k=5)
        self.assertIsNone(metrics["recall_at_k"])
        self.assertIsNone(metrics["mrr"])
        self.assertIsNone(metrics["hit_at_k"])

    def test_page_extraction_accepts_chunk_tuple(self):
        item = (SimpleNamespace(page="73"), 0.6)
        self.assertEqual(page_from_result(item), "73")

    def test_aggregate_ignores_unlabelled_cases(self):
        rows = [
            {"recall_at_k": 1.0, "mrr": 1.0, "hit_at_k": 1},
            {"recall_at_k": 0.5, "mrr": 0.25, "hit_at_k": 1},
            {"recall_at_k": None, "mrr": None, "hit_at_k": None},
        ]
        summary = aggregate_metrics(rows)
        self.assertEqual(summary["labelled_cases"], 2)
        self.assertEqual(summary["recall_at_k"], 0.75)
        self.assertEqual(summary["mrr"], 0.625)
        self.assertEqual(summary["hit_rate_at_k"], 1.0)

    def test_invalid_k_is_rejected(self):
        with self.assertRaises(ValueError):
            retrieval_metrics([], [1], k=0)


if __name__ == "__main__":
    unittest.main()
