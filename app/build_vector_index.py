"""Build a local dense-vector index for the active cleaned knowledge sources.

Run from repository root:
    python -m app.build_vector_index

Requires Ollama to be running and the configured embedding model to be available.
The generated index is ignored by Git and remains on the local machine.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Iterable

try:
    from app.internal_pilot import CHUNKS, SOURCE_PATH, SOURCE_PATHS
except ModuleNotFoundError as exc:
    if exc.name != "app":
        raise
    from internal_pilot import CHUNKS, SOURCE_PATH, SOURCE_PATHS

try:
    from app.semantic_retrieval import DEFAULT_INDEX_PATH, DEFAULT_MODEL, build_index
except ModuleNotFoundError as exc:
    if exc.name != "app":
        raise
    from semantic_retrieval import DEFAULT_INDEX_PATH, DEFAULT_MODEL, build_index


def records_from_chunks(chunks: Iterable[Any]) -> list[dict[str, Any]]:
    """Convert loaded corpus chunks to index records without dropping provenance."""
    return [
        {
            "index": chunk.index,
            "page": chunk.page,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "text": chunk.text,
            "source_id": chunk.source_id,
            "source_title": chunk.source_title,
            "publishers": list(chunk.publishers),
            "publication_year": chunk.publication_year,
            "language": chunk.language,
            "topics": list(chunk.topics),
            "source_path": chunk.source_path,
        }
        for chunk in chunks
    ]


def build_index_from_chunks(
    chunks: Iterable[Any],
    *,
    source_path: Path,
    source_paths: list[Path],
    model: str = DEFAULT_MODEL,
    index_path: Path = DEFAULT_INDEX_PATH,
    batch_size: int = 16,
) -> dict[str, Any]:
    """Build an index fingerprinted against every active source file."""
    return build_index(
        records_from_chunks(chunks),
        source_path=source_path,
        source_paths=source_paths,
        model=model,
        index_path=index_path,
        batch_size=batch_size,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Local Ollama embedding model")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH, help="Generated local index path")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("BEC_EMBED_BATCH_SIZE", "16")))
    args = parser.parse_args()

    result = build_index_from_chunks(
        CHUNKS,
        source_path=SOURCE_PATH,
        source_paths=list(SOURCE_PATHS),
        model=args.model,
        index_path=args.index,
        batch_size=args.batch_size,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("Chỉ mục đã tạo cục bộ. Nếu thay đổi tài liệu nguồn hoặc embedding model, hãy tạo lại chỉ mục.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
