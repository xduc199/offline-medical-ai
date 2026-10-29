"""Aggregate human-reviewed answer-quality records for the offline medical RAG prototype.

This tool does not generate answers or automatically determine medical correctness.
It summarizes reviewer annotations saved as JSON.

Usage:
    python -m tests.evaluate_answer_quality --input reports/answer_quality_review.json
    python -m tests.evaluate_answer_quality --input reports/answer_quality_review.json --output reports/answer_quality_metrics.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RATING_DIMENSIONS = ("groundedness", "citation_fidelity", "completeness", "clarity")
BEHAVIORS = {"answer", "caution", "refuse"}


def validate_review_data(data: Any) -> list[dict[str, Any]]:
    """Validate the review schema and return records in their original order."""
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data.get("schema_version") != 1:
        raise ValueError("Input must be an object with schema_version=1.")
    records = data.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a non-empty list of human-reviewed answers.")

    seen_ids: set[str] = set()
    for position, record in enumerate(records, start=1):
        label = f"records[{position - 1}]"
        if not isinstance(record, dict):
            raise ValueError(f"{label} must be an object.")
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError(f"{label}.id must be a non-empty string.")
        if record_id in seen_ids:
            raise ValueError(f"Duplicate review id: {record_id}")
        seen_ids.add(record_id)

        for field in ("question", "answer"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise ValueError(f"{label}.{field} must be a non-empty string.")

        for field in ("expected_behavior", "observed_behavior"):
            if not isinstance(record.get(field), str) or record.get(field) not in BEHAVIORS:
                raise ValueError(
                    f"{label}.{field} must be one of: {', '.join(sorted(BEHAVIORS))}."
                )

        ratings = record.get("ratings")
        if not isinstance(ratings, dict):
            raise ValueError(f"{label}.ratings must be an object.")
        missing = [name for name in RATING_DIMENSIONS if name not in ratings]
        extra = sorted(set(ratings) - set(RATING_DIMENSIONS))
        if missing or extra:
            details = []
            if missing:
                details.append("missing: " + ", ".join(missing))
            if extra:
                details.append("unknown: " + ", ".join(extra))
            raise ValueError(f"{label}.ratings has " + "; ".join(details) + ".")
        for name in RATING_DIMENSIONS:
            score = ratings[name]
            if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
                raise ValueError(f"{label}.ratings.{name} must be an integer from 1 to 5.")

        for field in ("unsupported_claims", "critical_safety_error"):
            if type(record.get(field)) is not bool:
                raise ValueError(f"{label}.{field} must be true or false.")

        notes = record.get("reviewer_notes", "")
        if not isinstance(notes, str):
            raise ValueError(f"{label}.reviewer_notes must be a string when provided.")

    return records


def aggregate_answer_quality(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize human ratings and explicit review flags without inferring safety."""
    records = validate_review_data({"schema_version": 1, "records": records})
    count = len(records)
    rating_means = {
        dimension: round(
            sum(record["ratings"][dimension] for record in records) / count,
            3,
        )
        for dimension in RATING_DIMENSIONS
    }

    correct_behavior = sum(
        record["expected_behavior"] == record["observed_behavior"]
        for record in records
    )
    unsupported_count = sum(record["unsupported_claims"] for record in records)
    critical_error_count = sum(record["critical_safety_error"] for record in records)

    behavior_breakdown: dict[str, dict[str, int | float]] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["expected_behavior"]].append(record)
    for behavior, items in sorted(grouped.items()):
        matches = sum(item["expected_behavior"] == item["observed_behavior"] for item in items)
        behavior_breakdown[behavior] = {
            "cases": len(items),
            "matches": matches,
            "match_rate": round(matches / len(items), 3),
        }

    return {
        "schema_version": 1,
        "evaluation_type": "human_reviewed_answer_quality",
        "scope_note": (
            "Reviewer ratings and flags are not an automated clinical correctness test, "
            "and do not establish medical safety or readiness for real-world use."
        ),
        "cases_reviewed": count,
        "mean_ratings_1_to_5": rating_means,
        "expected_behavior_match": {
            "matches": correct_behavior,
            "cases": count,
            "rate": round(correct_behavior / count, 3),
        },
        "unsupported_claims": {
            "cases_flagged": unsupported_count,
            "cases": count,
            "rate": round(unsupported_count / count, 3),
        },
        "critical_safety_errors": {
            "cases_flagged": critical_error_count,
            "cases": count,
            "rate": round(critical_error_count / count, 3),
        },
        "by_expected_behavior": behavior_breakdown,
        "reviewed_ids": [record["id"] for record in records],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="JSON file with human-reviewed answers")
    parser.add_argument("--output", type=Path, help="Optional path for the aggregate JSON report")
    args = parser.parse_args()

    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        records = validate_review_data(data)
        report = aggregate_answer_quality(records)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Answer-quality evaluation error: {exc}", file=sys.stderr)
        return 2

    print(f"Reviewed answers: {report['cases_reviewed']}")
    print(
        "Expected-behavior match: "
        f"{report['expected_behavior_match']['rate']:.3f} "
        f"({report['expected_behavior_match']['matches']}/{report['cases_reviewed']})"
    )
    print("Mean reviewer ratings (1-5):")
    for dimension, score in report["mean_ratings_1_to_5"].items():
        print(f"  {dimension}: {score:.3f}")
    print(
        "Unsupported-claim flags: "
        f"{report['unsupported_claims']['cases_flagged']}/{report['cases_reviewed']}"
    )
    print(
        "Critical-safety-error flags: "
        f"{report['critical_safety_errors']['cases_flagged']}/{report['cases_reviewed']}"
    )
    print("These are reviewer annotations, not a clinical-safety certification.")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON report saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
