import unittest
from unittest.mock import patch

from app import internal_pilot as pilot
from app.semantic_retrieval import EmbeddingError


class HybridRetrievalWrapperTests(unittest.TestCase):
    @staticmethod
    def distinct_chunks(count):
        selected = []
        seen = set()
        for chunk in pilot.CHUNKS:
            region = (chunk.page, chunk.start_line // 12)
            if region in seen:
                continue
            selected.append(chunk)
            seen.add(region)
            if len(selected) == count:
                return selected
        return selected

    def test_without_vector_index_uses_keyword_retrieval(self):
        chunk_a, chunk_b = self.distinct_chunks(2)
        keyword_results = [(chunk_a, 0.8), (chunk_b, 0.7)]
        with patch.object(pilot, "SEMANTIC_INDEX", None), patch.object(
            pilot, "keyword_retrieve", return_value=keyword_results
        ) as keyword:
            result = pilot.retrieve("test query", limit=1)
        self.assertEqual([item[0].index for item in result], [chunk_a.index])
        self.assertEqual(pilot.get_retrieval_diagnostics()["mode"], "keyword")
        keyword.assert_called_once_with("test query", limit=8)

    def test_valid_vector_index_uses_reciprocal_rank_fusion(self):
        chunk_a, chunk_b, chunk_c = self.distinct_chunks(3)
        keyword_results = [(chunk_a, 0.85), (chunk_b, 0.75)]
        semantic_results = [
            ({"index": chunk_a.index, "vector": [1.0, 0.0]}, 0.72),
            ({"index": chunk_c.index, "vector": [0.8, 0.2]}, 0.65),
        ]
        with patch.object(pilot, "SEMANTIC_INDEX", {"embedding_model": "fake", "entries": []}), patch.object(
            pilot, "keyword_retrieve", return_value=keyword_results
        ), patch.object(pilot, "semantic_search", return_value=semantic_results):
            result = pilot.retrieve("test query", limit=2)
        self.assertEqual(result[0][0].index, chunk_a.index)
        self.assertEqual(len(result), 2)
        self.assertEqual(pilot.get_retrieval_diagnostics()["mode"], "hybrid_rrf")
        self.assertIsNone(pilot.get_retrieval_diagnostics()["warning"])

    def test_embedding_failure_falls_back_to_keyword_and_exposes_warning(self):
        chunk_a, chunk_b = self.distinct_chunks(2)
        keyword_results = [(chunk_a, 0.8), (chunk_b, 0.7)]
        with patch.object(pilot, "SEMANTIC_INDEX", {"embedding_model": "fake", "entries": []}), patch.object(
            pilot, "keyword_retrieve", return_value=keyword_results
        ), patch.object(pilot, "semantic_search", side_effect=EmbeddingError("model unavailable")):
            result = pilot.retrieve("test query", limit=2)
        diagnostics = pilot.get_retrieval_diagnostics()
        self.assertEqual([item[0].index for item in result], [chunk_a.index, chunk_b.index])
        self.assertEqual(diagnostics["mode"], "keyword_fallback")
        self.assertIn("Embedding cục bộ không khả dụng", diagnostics["warning"])

    def test_low_semantic_score_falls_back_to_keyword(self):
        chunk_a, chunk_b = self.distinct_chunks(2)
        keyword_results = [(chunk_a, 0.8), (chunk_b, 0.7)]
        with patch.object(pilot, "SEMANTIC_INDEX", {"embedding_model": "fake", "entries": []}), patch.object(
            pilot, "keyword_retrieve", return_value=keyword_results
        ), patch.object(
            pilot, "semantic_search",
            return_value=[({"index": chunk_a.index, "vector": [1.0]}, 0.1)],
        ):
            result = pilot.retrieve("test query", limit=2)
        self.assertEqual([item[0].index for item in result], [chunk_a.index, chunk_b.index])
        self.assertEqual(pilot.get_retrieval_diagnostics()["mode"], "keyword_fallback")


if __name__ == "__main__":
    unittest.main()
