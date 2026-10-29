import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app import build_vector_index as builder


class BuildVectorIndexTests(unittest.TestCase):
    def setUp(self):
        self.chunk = SimpleNamespace(
            index=7,
            page="12",
            start_line=101,
            end_line=105,
            text="A cleaned medical passage.",
            source_id="GUIDE_A",
            source_title="First Aid Guide",
            publishers=("Publisher A", "Publisher B"),
            publication_year=2024,
            language="en",
            topics=("first_aid", "bleeding"),
            source_path="knowledge_base/cleaned/guide_a.txt",
        )

    def test_records_preserve_source_provenance(self):
        records = builder.records_from_chunks([self.chunk])

        self.assertEqual(
            records,
            [
                {
                    "index": 7,
                    "page": "12",
                    "start_line": 101,
                    "end_line": 105,
                    "text": "A cleaned medical passage.",
                    "source_id": "GUIDE_A",
                    "source_title": "First Aid Guide",
                    "publishers": ["Publisher A", "Publisher B"],
                    "publication_year": 2024,
                    "language": "en",
                    "topics": ["first_aid", "bleeding"],
                    "source_path": "knowledge_base/cleaned/guide_a.txt",
                }
            ],
        )

    def test_build_passes_all_active_sources_to_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_a = root / "guide_a.txt"
            source_b = root / "guide_b.txt"
            with patch("app.build_vector_index.build_index", return_value={"chunk_count": 1}) as build:
                result = builder.build_index_from_chunks(
                    [self.chunk],
                    source_path=source_a,
                    source_paths=[source_a, source_b],
                    model="unit-test-model",
                    index_path=root / "index.json",
                    batch_size=3,
                )

        self.assertEqual(result, {"chunk_count": 1})
        args, kwargs = build.call_args
        self.assertEqual(len(args[0]), 1)
        self.assertEqual(kwargs["source_path"], source_a)
        self.assertEqual(kwargs["source_paths"], [source_a, source_b])
        self.assertEqual(kwargs["model"], "unit-test-model")
        self.assertEqual(kwargs["batch_size"], 3)
        self.assertEqual(args[0][0]["source_id"], "GUIDE_A")
        self.assertEqual(args[0][0]["source_path"], "knowledge_base/cleaned/guide_a.txt")


if __name__ == "__main__":
    unittest.main()
