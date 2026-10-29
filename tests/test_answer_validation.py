import unittest

from app.answer_validation import citations_are_in_range, validate_grounded_answer


class GroundedAnswerValidationTests(unittest.TestCase):
    def test_accepts_answer_with_valid_citation(self):
        result = validate_grounded_answer("Theo tài liệu, dấu hiệu được nêu là X. [S1]", 1)
        self.assertTrue(result.accepted)
        self.assertIsNone(result.warning)

    def test_rejects_empty_answer(self):
        result = validate_grounded_answer("", 1)
        self.assertFalse(result.accepted)
        self.assertIn("empty_answer", result.issues)

    def test_rejects_missing_sources(self):
        result = validate_grounded_answer("Một câu trả lời. [S1]", 0)
        self.assertFalse(result.accepted)
        self.assertIn("missing_sources", result.issues)

    def test_rejects_missing_citation(self):
        result = validate_grounded_answer("Một câu trả lời không có nguồn.", 1)
        self.assertFalse(result.accepted)
        self.assertIn("missing_citation", result.issues)

    def test_rejects_invalid_citation_index(self):
        result = validate_grounded_answer("Một câu trả lời. [S2]", 1)
        self.assertFalse(result.accepted)
        self.assertIn("invalid_citation", result.issues)

    def test_rejects_uncited_list_item(self):
        result = validate_grounded_answer("- Ý thứ nhất. [S1]\n- Ý thứ hai.", 1)
        self.assertFalse(result.accepted)
        self.assertIn("uncited_bullet", result.issues)

    def test_rejects_overlong_output(self):
        result = validate_grounded_answer("x" * 50, 1, max_chars=20)
        self.assertFalse(result.accepted)
        self.assertIn("answer_too_long", result.issues)

    def test_explicit_source_ids(self):
        self.assertTrue(citations_are_in_range("Có nguồn [S1] và [S2].", ["S1", "S2"]))
        self.assertFalse(citations_are_in_range("Có nguồn [S3].", ["S1", "S2"]))

    def test_accepts_grouped_citations(self):
        result = validate_grounded_answer("Theo tài liệu, nội dung A và B. [S1, S2]", 2)
        self.assertTrue(result.accepted)
        self.assertTrue(citations_are_in_range("Nội dung [S1, S2].", ["S1", "S2"]))

    def test_rejects_invalid_id_inside_grouped_citations(self):
        result = validate_grounded_answer("Theo tài liệu, nội dung A. [S1, S2]", 1)
        self.assertFalse(result.accepted)
        self.assertIn("invalid_citation", result.issues)

    def test_grouped_citation_satisfies_bullet_citation_check(self):
        result = validate_grounded_answer("- Ý thứ nhất. [S1, S2]", 2)
        self.assertTrue(result.accepted)

    def test_grouped_citation_with_unknown_id_fails_explicit_source_check(self):
        self.assertFalse(citations_are_in_range("Nội dung [S1, S3].", ["S1", "S2"]))


if __name__ == "__main__":
    unittest.main()
