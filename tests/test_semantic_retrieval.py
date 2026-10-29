import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import semantic_retrieval as sr


class SemanticRetrievalTests(unittest.TestCase):
    def test_embed_texts_batches_and_preserves_order(self):
        responses = [
            {"embeddings": [[1.0, 0.0], [0.0, 1.0]]},
            {"embeddings": [[0.5, 0.5]]},
        ]
        with patch("app.semantic_retrieval._post_json", side_effect=responses) as post:
            result = sr.embed_texts(
                ["one", "two", "three"],
                model="unit-test-model",
                ollama_url="http://127.0.0.1:11434",
                batch_size=2,
            )
        self.assertEqual(result, [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]])
        self.assertEqual(post.call_count, 2)
        self.assertTrue(post.call_args_list[0].args[0].endswith("/api/embed"))

    def test_embed_texts_rejects_wrong_embedding_count(self):
        with patch(
            "app.semantic_retrieval._post_json",
            return_value={"embeddings": [[1.0, 0.0]]},
        ):
            with self.assertRaises(sr.EmbeddingError):
                sr.embed_texts(["one", "two"], model="unit-test-model")

    def test_semantic_search_ranks_by_cosine_similarity(self):
        index_data = {
            "embedding_model": "unit-test-model",
            "entries": [
                {"index": 1, "vector": [0.0, 1.0], "text": "orthogonal"},
                {"index": 2, "vector": [1.0, 0.0], "text": "matches"},
                {"index": 3, "vector": [-1.0, 0.0], "text": "opposite"},
            ],
        }
        with patch(
            "app.semantic_retrieval.embed_texts",
            return_value=[[1.0, 0.0]],
        ):
            results = sr.semantic_search("query", index_data, limit=3)
        self.assertEqual([item[0]["index"] for item in results], [2, 1, 3])
        self.assertAlmostEqual(results[0][1], 1.0)
        self.assertAlmostEqual(results[-1][1], -1.0)

    def test_build_and_load_index_and_reject_stale_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.txt"
            source.write_text("medical source v1", encoding="utf-8")
            index_path = root / "vector_db" / "index.json"
            records = [
                {"index": 1, "page": "1", "start_line": 1, "end_line": 2, "text": "first passage"},
                {"index": 2, "page": "2", "start_line": 3, "end_line": 4, "text": "second passage"},
            ]
            with patch(
                "app.semantic_retrieval.embed_texts",
                return_value=[[3.0, 4.0], [0.0, 2.0]],
            ):
                summary = sr.build_index(
                    records,
                    source_path=source,
                    model="unit-test-model",
                    index_path=index_path,
                )
            self.assertEqual(summary["chunk_count"], 2)
            self.assertTrue(index_path.is_file())
            loaded = sr.load_index(
                source_path=source,
                index_path=index_path,
                model="unit-test-model",
            )
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["dimensions"], 2)
            self.assertAlmostEqual(sum(v * v for v in loaded["entries"][0]["vector"]), 1.0)

            source.write_text("medical source v2", encoding="utf-8")
            stale = sr.load_index(
                source_path=source,
                index_path=index_path,
                model="unit-test-model",
            )
            self.assertIsNone(stale)

    def test_load_index_rejects_mismatched_model(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.txt"
            source.write_text("source", encoding="utf-8")
            index_path = root / "index.json"
            with patch("app.semantic_retrieval.embed_texts", return_value=[[1.0, 0.0]]):
                sr.build_index(
                    [{"index": 1, "text": "one passage"}],
                    source_path=source,
                    model="model-a",
                    index_path=index_path,
                )
            self.assertIsNone(
                sr.load_index(source_path=source, index_path=index_path, model="model-b")
            )

    def test_load_index_rejects_malformed_entries(self):
        import json

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.txt"
            source.write_text("source", encoding="utf-8")
            index_path = root / "index.json"
            invalid_index = {
                "schema_version": 1,
                "embedding_model": "unit-test-model",
                "source_sha256": sr.sha256_file(source),
                "dimensions": 2,
                "entries": [None],
            }
            index_path.write_text(json.dumps(invalid_index), encoding="utf-8")
            self.assertIsNone(
                sr.load_index(source_path=source, index_path=index_path, model="unit-test-model")
            )

    def test_load_index_rejects_nonnumeric_and_nonfinite_values(self):
        import json

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.txt"
            source.write_text("source", encoding="utf-8")
            index_path = root / "index.json"
            for vector in (["1.0", 0.0], [float("nan"), 0.0]):
                invalid_index = {
                    "schema_version": 1,
                    "embedding_model": "unit-test-model",
                    "source_sha256": sr.sha256_file(source),
                    "dimensions": 2,
                    "entries": [{"index": 1, "page": "1", "vector": vector}],
                }
                index_path.write_text(json.dumps(invalid_index), encoding="utf-8")
                self.assertIsNone(
                    sr.load_index(source_path=source, index_path=index_path, model="unit-test-model")
                )

    def test_reciprocal_rank_fusion_rewards_agreement(self):
        from types import SimpleNamespace

        keyword = [(SimpleNamespace(index=1), 0.99), (SimpleNamespace(index=2), 0.98)]
        semantic = [
            ({"index": 2, "vector": [1.0]}, 0.9),
            ({"index": 3, "vector": [1.0]}, 0.8),
        ]
        fused = sr.reciprocal_rank_fusion(keyword, semantic, limit=3, rrf_k=10)
        self.assertEqual(fused[0][0], 2)
        score_by_index = dict(fused)
        self.assertGreater(score_by_index[2], score_by_index[1])
        self.assertGreater(score_by_index[2], score_by_index[3])


if __name__ == "__main__":
    unittest.main()
