"""Build a local dense-vector index for the cleaned WHO/ICRC BEC text.

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

try:
    from app.internal_pilot import CHUNKS, SOURCE_PATH
except ModuleNotFoundError as exc:
    if exc.name != "app":
        raise
    from internal_pilot import CHUNKS, SOURCE_PATH

try:
    from app.semantic_retrieval import DEFAULT_INDEX_PATH, DEFAULT_MODEL, build_index
except ModuleNotFoundError as exc:
    if exc.name != "app":
        raise
    from semantic_retrieval import DEFAULT_INDEX_PATH, DEFAULT_MODEL, build_index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Local Ollama embedding model")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH, help="Generated local index path")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("BEC_EMBED_BATCH_SIZE", "16")))
    args = parser.parse_args()

    records = [
        {
            "index": chunk.index,
            "page": chunk.page,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "text": chunk.text,
        }
        for chunk in CHUNKS
    ]
    result = build_index(
        records,
        source_path=SOURCE_PATH,
        model=args.model,
        index_path=args.index,
        batch_size=args.batch_size,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("Chỉ mục đã tạo cục bộ. Nếu thay đổi tài liệu nguồn hoặc embedding model, hãy tạo lại chỉ mục.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
