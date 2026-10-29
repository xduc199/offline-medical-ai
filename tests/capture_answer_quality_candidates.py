"""Capture real responses from the locally running medical RAG pilot for later human review.

Usage from the repository root while app/internal_pilot.py is running:
    python -m tests.capture_answer_quality_candidates

This captures raw model outputs and retrieved sources. It does NOT assign ratings,
decide clinical correctness, or create human-reviewed evaluation results.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "tests" / "broad_questions_vi.json"
DEFAULT_OUTPUT = ROOT / "reports" / "answer_quality_candidates.json"


def request_json(url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"} if data else {},
        method="POST" if data is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not isinstance(result, dict):
        raise ValueError(f"Expected JSON object from {url}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8765", help="Local pilot URL")
    parser.add_argument("--limit", type=int, default=0, help="Capture first N cases; 0 captures all")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSON path")
    args = parser.parse_args()

    try:
        health = request_json(args.url.rstrip("/") + "/api/health")
        cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
        if not isinstance(cases, list):
            raise ValueError(f"{CASES_PATH} must contain a JSON list.")
        if args.limit < 0:
            raise ValueError("--limit must be zero or a positive integer.")
        if args.limit:
            cases = cases[: args.limit]
    except (OSError, json.JSONDecodeError, ValueError, urllib.error.URLError, TimeoutError) as exc:
        print(f"Không thể khởi tạo thu thập: {exc}", file=sys.stderr)
        print("Hãy khởi chạy ứng dụng cục bộ trước: python .\\app\\internal_pilot.py", file=sys.stderr)
        return 2

    output_records: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    print(f"Pilot mode: {health.get('mode')} | model: {health.get('model')} | cases: {len(cases)}")

    for case in cases:
        case_id = str(case.get("id", "")).strip()
        question = str(case.get("question", "")).strip()
        if not case_id or not question:
            failures.append({"id": case_id or "(missing id)", "error": "Missing id or question"})
            continue

        started = time.perf_counter()
        try:
            response = request_json(
                args.url.rstrip("/") + "/api/ask",
                {"question": question},
            )
            elapsed = round(time.perf_counter() - started, 4)
            sources = response.get("sources")
            if not isinstance(sources, list):
                sources = []
            output_records.append({
                "id": case_id,
                "question": question,
                "answer": str(response.get("answer", "")).strip(),
                "sources": sources,
                "warning": response.get("warning"),
                "expected_pdf_pages": case.get("expected_pdf_pages", []),
                "review_for": case.get("review_for", ""),
                "latency_seconds": elapsed,
                "capture_status": "success",
            })
            print(f"{case_id}: captured in {elapsed:.2f}s; sources={len(sources)}")
        except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            failures.append({"id": case_id, "error": str(exc)})
            print(f"{case_id}: FAILED: {exc}", file=sys.stderr)

    payload = {
        "schema_version": 1,
        "capture_type": "raw_local_pilot_outputs_for_human_review",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_url": args.url,
        "pilot_mode": health.get("mode"),
        "model": health.get("model"),
        "records_captured": len(output_records),
        "failures": failures,
        "records": output_records,
        "notice": (
            "Raw application outputs only. These records have not been human-reviewed, "
            "rated, or clinically validated. Do not pass this file directly to "
            "tests.evaluate_answer_quality; review and annotate each record first."
        ),
    }
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"Không ghi được file kết quả: {exc}", file=sys.stderr)
        return 2

    print(f"\nĐã lưu đầu ra thực tế: {args.output}")
    print(f"Thành công: {len(output_records)}/{len(cases)} | lỗi: {len(failures)}")
    print("Đây mới là dữ liệu thô; cần người đánh giá gán nhãn trước khi tổng hợp chất lượng.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
