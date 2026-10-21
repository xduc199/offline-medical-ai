"""Run broad Vietnamese questions against the local BEC pilot for manual review.

Usage (PowerShell):
  python .\tests\run_broad_questions.py
  python .\tests\run_broad_questions.py --url http://127.0.0.1:8765 --limit 3

This is a smoke-test helper, not a clinical-quality or safety certification.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests" / "broad_questions_vi.json"


def request_json(url: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"} if data else {},
        method="POST" if data else "GET",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8765", help="Local pilot base URL")
    parser.add_argument("--limit", type=int, default=0, help="Run only the first N cases (0 = all)")
    args = parser.parse_args()

    try:
        health = request_json(args.url.rstrip("/") + "/api/health")
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        print(f"Không kết nối được ứng dụng tại {args.url}: {exc}")
        print("Khởi chạy bằng: python .\\app\\internal_pilot.py")
        return 2

    cases = json.loads(CASES.read_text(encoding="utf-8"))
    if args.limit > 0:
        cases = cases[: args.limit]

    print(f"Pilot: {health.get('mode')} | model: {health.get('model')} | cases: {len(cases)}")
    print("=" * 88)
    failures = 0
    for case in cases:
        started = time.perf_counter()
        try:
            result = request_json(
                args.url.rstrip("/") + "/api/ask",
                {"question": case["question"]},
            )
            elapsed = time.perf_counter() - started
            sources = result.get("sources") or []
            citations = "; ".join(source.get("citation", "") for source in sources) or "không có nguồn"
            actual_pages = {
                int(match.group(1))
                for source in sources
                if (match := re.search(r"PDF p\.\s*(\d+)", source.get("citation", "")))
            }
            expected_pages = set(case.get("expected_pdf_pages", []))
            page_check = "N/A"
            if expected_pages:
                page_check = "PASS" if expected_pages & actual_pages else "MISS"
            print(f"\n{case['id']} | {elapsed:.2f}s | nguồn: {citations}")
            if expected_pages:
                print(f"Trang nguồn mục tiêu: {sorted(expected_pages)} | truy xuất: {page_check}")
            print(f"Hỏi: {case['question']}")
            print(f"Đáp: {result.get('answer', '').strip()}")
            if result.get("warning"):
                print(f"Cảnh báo: {result['warning']}")
            print(f"Rà soát: {case['review_for']}")
        except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            failures += 1
            print(f"\n{case['id']} | REQUEST_ERROR | {exc}")

    print("\n" + "=" * 88)
    print(f"Hoàn tất: {len(cases) - failures}/{len(cases)} câu gọi thành công; lỗi kết nối: {failures}.")
    print("Đánh giá thủ công chất lượng, độ đầy đủ và độ khớp nguồn; script không tự chấm độ an toàn lâm sàng.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
