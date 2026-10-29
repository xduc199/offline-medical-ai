"""Page-level retrieval metrics for the offline BEC research prototype.

Gold labels currently identify relevant PDF pages, not every relevant passage.
These metrics are a first diagnostic and must not be interpreted as clinical safety.
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any


def _page_text(value: Any) -> str:
    text = str(value).strip()
    return text if text.isdigit() else text


def page_from_result(item: Any) -> str:
    """Accept a Chunk, semantic-index entry, or (item, score) retrieval pair."""
    value = item[0] if isinstance(item, tuple) and len(item) == 2 else item
    if isinstance(value, dict):
        return _page_text(value.get("page", ""))
    return _page_text(getattr(value, "page", ""))


def retrieval_metrics(
    retrieved: Sequence[Any],
    expected_pages: Iterable[int | str],
    *,
    k: int = 5,
) -> dict[str, float | int | None]:
    """Compute page-level Recall@k, MRR and hit rate for ranked results."""
    if k < 1:
        raise ValueError("k must be >= 1")
    gold = {_page_text(page) for page in expected_pages if str(page).strip()}
    if not gold:
        return {
            "k": k,
            "relevant_pages": 0,
            "recall_at_k": None,
            "mrr": None,
            "hit_at_k": None,
        }

    ranked = [page_from_result(item) for item in retrieved[:k]]
    found_pages = {page for page in ranked if page}
    hits = len(gold & found_pages)
    reciprocal_rank = 0.0
    for rank, page in enumerate(ranked, start=1):
        if page in gold:
            reciprocal_rank = 1.0 / rank
            break
    return {
        "k": k,
        "relevant_pages": len(gold),
        "recall_at_k": hits / len(gold),
        "mrr": reciprocal_rank,
        "hit_at_k": 1 if hits else 0,
    }


def aggregate_metrics(
    rows: Sequence[dict[str, float | int | None]],
) -> dict[str, float | int]:
    """Average only labelled rows; return labelled case count for transparency."""
    labelled = [row for row in rows if row.get("recall_at_k") is not None]
    if not labelled:
        return {"labelled_cases": 0, "recall_at_k": 0.0, "mrr": 0.0, "hit_rate_at_k": 0.0}
    count = len(labelled)
    return {
        "labelled_cases": count,
        "recall_at_k": sum(float(row["recall_at_k"]) for row in labelled) / count,
        "mrr": sum(float(row["mrr"]) for row in labelled) / count,
        "hit_rate_at_k": sum(float(row["hit_at_k"]) for row in labelled) / count,
    }
