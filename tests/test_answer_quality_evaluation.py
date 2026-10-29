import unittest

from tests.evaluate_answer_quality import aggregate_answer_quality, validate_review_data


def reviewed_record(
    record_id,
    *,
    expected="answer",
    observed="answer",
    ratings=None,
    unsupported=False,
    critical=False,
):
    return {
        "id": record_id,
        "question": "Câu hỏi kiểm thử về nội dung tài liệu.",
        "answer": "Câu trả lời đã được người đánh giá xem xét. [S1]",
        "expected_behavior": expected,
        "observed_behavior": observed,
        "ratings": ratings or {
            "groundedness": 4,
            "citation_fidelity": 5,
            "completeness": 3,
            "clarity": 4,
        },
        "unsupported_claims": unsupported,
        "critical_safety_error": critical,
        "reviewer_notes": "",
    }


class AnswerQualityEvaluationTests(unittest.TestCase):
    def test_aggregates_ratings_behavior_and_review_flags(self):
        records = [
            reviewed_record("Q01"),
            reviewed_record(
                "Q02",
                expected="caution",
                observed="answer",
                ratings={
                    "groundedness": 2,
                    "citation_fidelity": 3,
                    "completeness": 2,
                    "clarity": 4,
                },
                unsupported=True,
                critical=True,
            ),
        ]

        report = aggregate_answer_quality(records)

        self.assertEqual(report["cases_reviewed"], 2)
        self.assertEqual(report["mean_ratings_1_to_5"]["groundedness"], 3.0)
        self.assertEqual(report["mean_ratings_1_to_5"]["citation_fidelity"], 4.0)
        self.assertEqual(report["expected_behavior_match"], {
            "matches": 1,
            "cases": 2,
            "rate": 0.5,
        })
        self.assertEqual(report["unsupported_claims"]["cases_flagged"], 1)
        self.assertEqual(report["critical_safety_errors"]["cases_flagged"], 1)
        self.assertEqual(report["by_expected_behavior"]["caution"]["match_rate"], 0.0)

    def test_rejects_empty_review_set(self):
        with self.assertRaisesRegex(ValueError, "non-empty list"):
            validate_review_data({"schema_version": 1, "records": []})

    def test_rejects_duplicate_review_ids(self):
        record = reviewed_record("Q01")
        with self.assertRaisesRegex(ValueError, "Duplicate review id"):
            validate_review_data({"schema_version": 1, "records": [record, record.copy()]})

    def test_rejects_rating_outside_one_to_five(self):
        record = reviewed_record("Q01")
        record["ratings"]["groundedness"] = 6
        with self.assertRaisesRegex(ValueError, "integer from 1 to 5"):
            validate_review_data({"schema_version": 1, "records": [record]})

    def test_rejects_boolean_as_numeric_rating(self):
        record = reviewed_record("Q01")
        record["ratings"]["groundedness"] = True
        with self.assertRaisesRegex(ValueError, "integer from 1 to 5"):
            validate_review_data({"schema_version": 1, "records": [record]})

    def test_rejects_unknown_rating_dimension(self):
        record = reviewed_record("Q01")
        record["ratings"]["clinical_accuracy"] = 5
        with self.assertRaisesRegex(ValueError, "unknown: clinical_accuracy"):
            validate_review_data({"schema_version": 1, "records": [record]})

    def test_rejects_non_boolean_safety_flags(self):
        record = reviewed_record("Q01")
        record["critical_safety_error"] = "no"
        with self.assertRaisesRegex(ValueError, "must be true or false"):
            validate_review_data({"schema_version": 1, "records": [record]})


if __name__ == "__main__":
    unittest.main()
