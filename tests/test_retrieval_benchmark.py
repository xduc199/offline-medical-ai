import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.semantic_retrieval import EmbeddingError
from tests.evaluate_retrieval import run_benchmark


class RetrievalBenchmarkTests(unittest.TestCase):
    def test_keyword_benchmark_uses_page_labels(self):
        fake_chunk = SimpleNamespace(index=7, page="32", start_line=10, end_line=15, text="passage")
        cases = [
            {"id": "T1", "question": "sample question", "expected_pdf_pages": [32]},
            {"id": "T2", "question": "unlabelled question", "expected_pdf_pages": []},
        ]
        with patch("app.internal_pilot.SEMANTIC_INDEX", None), patch(
            "app.internal_pilot.keyword_retrieve", return_value=[(fake_chunk, 0.8)]
        ):
            report = run_benchmark(cases, top_k=3, methods="keyword")
        summary = report["summary"]["keyword"]
        self.assertEqual(summary["labelled_cases"], 1)
        self.assertEqual(summary["unlabelled_cases"], 1)
        self.assertEqual(summary["recall_at_k"], 1.0)
        self.assertEqual(summary["mrr"], 1.0)

    def test_all_method_falls_back_to_keyword_if_index_absent(self):
        fake_chunk = SimpleNamespace(index=4, page="49", start_line=1, end_line=2, text="passage")
        cases = [{"id": "T1", "question": "question", "expected_pdf_pages": [49]}]
        with patch("app.internal_pilot.SEMANTIC_INDEX", None), patch(
            "app.internal_pilot.keyword_retrieve", return_value=[(fake_chunk, 0.7)]
        ):
            report = run_benchmark(cases, methods="all", require_semantic=False)
        self.assertEqual(list(report["summary"]), ["keyword"])

    def test_require_semantic_fails_when_no_index_is_loaded(self):
        with patch("app.internal_pilot.SEMANTIC_INDEX", None):
            with self.assertRaises(EmbeddingError):
                run_benchmark(
                    [{"id": "T1", "question": "question", "expected_pdf_pages": [49]}],
                    methods="all",
                    require_semantic=True,
                )


if __name__ == "__main__":
    unittest.main()
