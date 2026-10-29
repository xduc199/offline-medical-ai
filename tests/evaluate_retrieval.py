"""Compare keyword, dense-semantic, and production hybrid retrieval on labelled page queries.

Current gold labels identify relevant PDF pages, not every relevant passage. This is
a retrieval diagnostic only; it does not assess answer correctness or clinical safety.

Usage:
    python -m tests.evaluate_retrieval --method keyword
    python -m tests.evaluate_retrieval --method all --require-semantic --top-k 5
    python -m tests.evaluate_retrieval --method all --output reports/retrieval_metrics.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app import internal_pilot as pilot
from app.retrieval_metrics import aggregate_metrics, retrieval_metrics
from app.semantic_retrieval import EmbeddingError, semantic_search


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "tests" / "broad_questions_vi.json"


def _expected_pages(case: dict[str, Any]) -> list[int | str]:
    return case.get("expected_pdf_pages", case.get("pdf_pages", [])) or []


def _result_dict(item: Any) -> dict[str, Any]:
    value, score = item if isinstance(item, tuple) and len(item) == 2 else (item, None)
    if isinstance(value, dict):
        return {
            "chunk_index": value.get("index"),
            "page": str(value.get("page", "")),
            "start_line": value.get("start_line"),
            "end_line": value.get("end_line"),
            "score": float(score) if score is not None else None,
        }
    return {
        "chunk_index": getattr(value, "index", None),
        "page": str(getattr(value, "page", "")),
        "start_line": getattr(value, "start_line", None),
        "end_line": getattr(value, "end_line", None),
        "score": float(score) if score is not None else None,
    }


def run_benchmark(
    cases: list[dict[str, Any]],
    *,
    top_k: int = 5,
    methods: str = "all",
    require_semantic: bool = False,
) -> dict[str, Any]:
    if top_k < 1:
        raise ValueError("top_k must be >= 1")
    if methods not in {"all", "keyword", "semantic", "hybrid"}:
        raise ValueError(f"Unsupported method: {methods}")
    if methods in {"all", "semantic", "hybrid"} and pilot.SEMANTIC_INDEX is None:
        if require_semantic:
            raise EmbeddingError(
                "No compatible embedding index is loaded. Run python -m app.build_vector_index first."
            )
        if methods in {"semantic", "hybrid"}:
            raise EmbeddingError(
                f"Method {methods} requires a compatible embedding index. Build it first."
            )
        methods = "keyword"

    if methods == "all":
        selected_methods = ["keyword", "semantic", "hybrid"]
    elif methods == "keyword":
        selected_methods = ["keyword"]
    else:
        selected_methods = [methods]

    method_rows: dict[str, list[dict[str, Any]]] = {name: [] for name in selected_methods}
    for case in cases:
        question = str(case["question"])
        expected = _expected_pages(case)
        result_sets: dict[str, list[tuple[Any, float]]] = {}
        elapsed_by_method: dict[str, float] = {}

        if "keyword" in selected_methods:
            started = time.perf_counter()
            result_sets["keyword"] = pilot.keyword_retrieve(question, limit=top_k)
            elapsed_by_method["keyword"] = time.perf_counter() - started

        if "semantic" in selected_methods:
            started = time.perf_counter()
            result_sets["semantic"] = semantic_search(
                question,
                pilot.SEMANTIC_INDEX,
                ollama_url=pilot.OLLAMA_URL,
                limit=top_k,
            )
            elapsed_by_method["semantic"] = time.perf_counter() - started

        hybrid_diagnostics = None
        if "hybrid" in selected_methods:
            started = time.perf_counter()
            pilot._set_retrieval_diagnostics("keyword")
            result_sets["hybrid"] = pilot.retrieve(question, limit=top_k)
            elapsed_by_method["hybrid"] = time.perf_counter() - started
            hybrid_diagnostics = pilot.get_retrieval_diagnostics()

        for method, results in result_sets.items():
            metrics = retrieval_metrics(results, expected, k=top_k)
            row = {
                "id": case.get("id"),
                "question": question,
                "expected_pdf_pages": expected,
                "retrieved": [_result_dict(item) for item in results[:top_k]],
                "metrics": metrics,
                "latency_seconds": round(elapsed_by_method[method], 4),
            }
            if method == "hybrid":
                row["retrieval_diagnostics"] = hybrid_diagnostics
            method_rows[method].append(row)

    summary: dict[str, Any] = {}
    for method, rows in method_rows.items():
        summaries = [row["metrics"] for row in rows]
        summary[method] = {
            "k": top_k,
            **aggregate_metrics(summaries),
            "cases_total": len(rows),
            "unlabelled_cases": sum(1 for row in summaries if row["recall_at_k"] is None),
            "mean_latency_seconds": (
                sum(row["latency_seconds"] for row in rows) / len(rows) if rows else 0.0
            ),
        }

    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "page-level retrieval metrics; not answer-quality or clinical-safety evaluation",
        "embedding_model": (
            pilot.SEMANTIC_INDEX.get("embedding_model") if pilot.SEMANTIC_INDEX is not None else None
        ),
        "semantic_index_loaded": pilot.SEMANTIC_INDEX is not None,
        "top_k": top_k,
        "case_count": len(cases),
        "labelled_case_count": sum(bool(_expected_pages(case)) for case in cases),
        "summary": summary,
        "details": method_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES,
        help="JSON with question and expected_pdf_pages/pdf_pages labels",
    )
    parser.add_argument("--top-k", type=int, default=5, help="Ranked passages to evaluate")
    parser.add_argument("--method", choices=["all", "keyword", "semantic", "hybrid"], default="all")
    parser.add_argument(
        "--require-semantic",
        action="store_true",
        help="Fail if no compatible vector index is loaded; do not silently run keyword only",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()

    try:
        cases = json.loads(args.cases.read_text(encoding="utf-8"))
        if not isinstance(cases, list) or not all(
            isinstance(case, dict) and case.get("question") for case in cases
        ):
            raise ValueError("Evaluation file must be a list of objects with a question field.")
        report = run_benchmark(
            cases,
            top_k=args.top_k,
            methods=args.method,
            require_semantic=args.require_semantic,
        )
    except (OSError, json.JSONDecodeError, ValueError, EmbeddingError) as exc:
        print(f"Benchmark error: {exc}", file=sys.stderr)
        return 2

    print(f"Benchmark file: {args.cases}")
    print(
        f"Questions: {report['case_count']} | labelled pages: {report['labelled_case_count']} "
        f"| k={report['top_k']}"
    )
    print("Metrics use manually labelled PDF pages; they do not evaluate generated answers or clinical safety.")
    print("-" * 98)
    for method, item in report["summary"].items():
        print(
            f"{method:>8} | Recall@{report['top_k']}={item['recall_at_k']:.3f}"
            f" | MRR={item['mrr']:.3f} | HitRate@{report['top_k']}={item['hit_rate_at_k']:.3f}"
            f" | mean latency={item['mean_latency_seconds']:.3f}s"
            f" | labelled={item['labelled_cases']}/{item['cases_total']}"
        )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON report saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
