"""Optional dense retrieval through the local Ollama embeddings API.

The index is a local generated artifact and must use the same embedding model as
query vectors. No external service is contacted: all requests target OLLAMA_URL.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Sequence


DEFAULT_MODEL = os.environ.get("BEC_EMBEDDING_MODEL", "bge-m3")
DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_INDEX_PATH = Path(os.environ.get(
    "BEC_VECTOR_INDEX_PATH",
    str(Path(__file__).resolve().parents[1] / "vector_db" / "who_icrc_bec_bge_m3.json"),
))
BATCH_SIZE = max(1, int(os.environ.get("BEC_EMBED_BATCH_SIZE", "16")))
EMBED_TIMEOUT = float(os.environ.get("BEC_EMBED_TIMEOUT", "180"))


class EmbeddingError(RuntimeError):
    """Raised when the configured local embedding model cannot be used."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _post_json(url: str, payload: dict[str, Any], timeout: float = EMBED_TIMEOUT) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise EmbeddingError(f"Không gọi được API embedding cục bộ tại {url}: {exc}") from exc
    if not isinstance(result, dict):
        raise EmbeddingError("Ollama trả về cấu trúc embedding không hợp lệ.")
    return result


def embed_texts(
    texts: Sequence[str],
    *,
    model: str = DEFAULT_MODEL,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    batch_size: int = BATCH_SIZE,
) -> list[list[float]]:
    """Embed text in batches with Ollama's current /api/embed endpoint."""
    if not texts:
        return []
    if not model.strip():
        raise ValueError("Tên embedding model không được để trống.")
    if batch_size < 1:
        raise ValueError("batch_size phải lớn hơn 0.")

    vectors: list[list[float]] = []
    endpoint = f"{ollama_url.rstrip('/')}/api/embed"
    for start in range(0, len(texts), batch_size):
        batch = list(texts[start:start + batch_size])
        response = _post_json(endpoint, {"model": model, "input": batch, "truncate": False})
        embeddings = response.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != len(batch):
            raise EmbeddingError(
                f"Ollama trả về số vector không khớp: mong đợi {len(batch)}, nhận {len(embeddings) if isinstance(embeddings, list) else 'không hợp lệ'}."
            )
        for vector in embeddings:
            if not isinstance(vector, list) or not vector:
                raise EmbeddingError("Ollama trả về vector rỗng hoặc sai định dạng.")
            try:
                normalized = [float(value) for value in vector]
            except (TypeError, ValueError) as exc:
                raise EmbeddingError("Vector embedding chứa phần tử không phải số.") from exc
            if any(not math.isfinite(value) for value in normalized):
                raise EmbeddingError("Vector embedding chứa giá trị không hữu hạn.")
            vectors.append(normalized)

    dimensions = len(vectors[0])
    if any(len(vector) != dimensions for vector in vectors):
        raise EmbeddingError("Các vector embedding có số chiều không đồng nhất.")
    return vectors


def _normalize(vector: Sequence[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    if not magnitude or not math.isfinite(magnitude):
        raise ValueError("Không thể chuẩn hóa vector rỗng hoặc không hữu hạn.")
    return [value / magnitude for value in vector]


def build_index(
    records: Sequence[dict[str, Any]],
    *,
    source_path: Path,
    model: str = DEFAULT_MODEL,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    index_path: Path = DEFAULT_INDEX_PATH,
    batch_size: int = BATCH_SIZE,
) -> dict[str, Any]:
    """Build a versioned JSON index; each record must include index and text."""
    if not source_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy tệp tri thức nguồn: {source_path}")
    if not records:
        raise ValueError("Không có đoạn văn bản để tạo chỉ mục.")

    clean_records: list[dict[str, Any]] = []
    texts: list[str] = []
    for record in records:
        text = str(record.get("text", "")).strip()
        if not text:
            continue
        clean_records.append({
            "index": int(record["index"]),
            "page": str(record.get("page", "")),
            "start_line": int(record.get("start_line", 0)),
            "end_line": int(record.get("end_line", 0)),
            "text": text,
        })
        texts.append(text)
    if not texts:
        raise ValueError("Không tìm thấy đoạn văn bản có nội dung.")

    raw_vectors = embed_texts(texts, model=model, ollama_url=ollama_url, batch_size=batch_size)
    entries = []
    for record, vector in zip(clean_records, raw_vectors):
        entries.append({**record, "vector": _normalize(vector)})

    source_sha = sha256_file(source_path)
    index_data = {
        "schema_version": 1,
        "embedding_provider": "ollama",
        "embedding_endpoint": "/api/embed",
        "embedding_model": model,
        "source_path": str(source_path),
        "source_sha256": source_sha,
        "chunk_count": len(entries),
        "dimensions": len(entries[0]["vector"]),
        "entries": entries,
    }
    index_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = index_path.with_suffix(index_path.suffix + ".tmp")
    try:
        tmp_path.write_text(json.dumps(index_data, ensure_ascii=False), encoding="utf-8")
        tmp_path.replace(index_path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    return {
        "index_path": str(index_path),
        "chunk_count": len(entries),
        "dimensions": index_data["dimensions"],
        "embedding_model": model,
        "source_sha256": source_sha,
    }


def load_index(
    *,
    source_path: Path,
    index_path: Path = DEFAULT_INDEX_PATH,
    model: str = DEFAULT_MODEL,
) -> dict[str, Any] | None:
    """Load only a compatible index; return None when absent, stale, or malformed."""
    if not index_path.is_file() or not source_path.is_file():
        return None
    try:
        index_data = json.loads(index_path.read_text(encoding="utf-8"))
        if not isinstance(index_data, dict) or index_data.get("schema_version") != 1:
            return None
        if index_data.get("embedding_model") != model:
            return None
        if index_data.get("source_sha256") != sha256_file(source_path):
            return None

        entries = index_data.get("entries")
        dimensions = index_data.get("dimensions")
        if (
            not isinstance(entries, list)
            or not entries
            or not isinstance(dimensions, int)
            or dimensions < 1
        ):
            return None
        for entry in entries:
            if not isinstance(entry, dict):
                return None
            vector = entry.get("vector")
            if not isinstance(vector, list) or len(vector) != dimensions:
                return None
            if not isinstance(entry.get("index"), int):
                return None
            if any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                for value in vector
            ):
                return None
        return index_data
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return None


def semantic_search(
    query: str,
    index_data: dict[str, Any],
    *,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    limit: int = 8,
) -> list[tuple[dict[str, Any], float]]:
    if limit < 1:
        return []
    question = query.strip()
    if not question:
        return []
    vectors = embed_texts([question], model=str(index_data["embedding_model"]), ollama_url=ollama_url)
    query_vector = _normalize(vectors[0])
    results: list[tuple[dict[str, Any], float]] = []
    for entry in index_data["entries"]:
        vector = entry.get("vector", [])
        if len(vector) != len(query_vector):
            continue
        score = sum(a * b for a, b in zip(query_vector, vector))
        results.append((entry, score))
    results.sort(key=lambda pair: pair[1], reverse=True)
    return results[:limit]


def reciprocal_rank_fusion(
    keyword_results: Sequence[tuple[Any, float]],
    semantic_results: Sequence[tuple[dict[str, Any], float]],
    *,
    limit: int = 2,
    rrf_k: int = 60,
) -> list[tuple[int, float]]:
    """Fuse two ranked lists by RRF, preserving keyword/semantic disagreements."""
    if limit < 1:
        return []
    rank_scores: dict[int, float] = {}
    for rank, (chunk, _score) in enumerate(keyword_results, start=1):
        idx = int(chunk.index)
        rank_scores[idx] = rank_scores.get(idx, 0.0) + 1.0 / (rrf_k + rank)
    for rank, (entry, _score) in enumerate(semantic_results, start=1):
        idx = int(entry["index"])
        rank_scores[idx] = rank_scores.get(idx, 0.0) + 1.0 / (rrf_k + rank)
    return sorted(rank_scores.items(), key=lambda item: item[1], reverse=True)[:limit]


def fuse_with_chunks(
    keyword_results: Sequence[tuple[Any, float]],
    semantic_results: Sequence[tuple[dict[str, Any], float]],
    chunks_by_index: dict[int, Any],
    *,
    limit: int = 2,
) -> list[tuple[Any, float]]:
    fused = reciprocal_rank_fusion(keyword_results, semantic_results, limit=limit)
    return [(chunks_by_index[index], score) for index, score in fused if index in chunks_by_index]
