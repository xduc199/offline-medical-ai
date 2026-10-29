import unittest

from app.answer_validation import (
    abcde_source_coverage,
    citations_are_in_range,
    missing_abcde_answer_stages,
    validate_grounded_answer,
)


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

    def test_rejects_parenthetical_source_marker_and_explains_required_syntax(self):
        result = validate_grounded_answer("Một ý có nguồn. (S1)", 1)
        self.assertFalse(result.accepted)
        self.assertIn("invalid_citation_format", result.issues)
        self.assertIn("[S1]", result.details[0])

    def test_markdown_heading_is_not_treated_as_an_uncited_claim(self):
        result = validate_grounded_answer(
            "## Đánh giá ban đầu\n\nNội dung có căn cứ từ nguồn. [S1]",
            1,
        )
        self.assertTrue(result.accepted)

    def test_nonfactual_introduction_is_not_treated_as_a_claim(self):
        result = validate_grounded_answer(
            "Dưới đây là các ý chính:\n\nNội dung có căn cứ từ nguồn. [S1]",
            1,
        )
        self.assertTrue(result.accepted)

    def test_b07_burn_summary_intro_is_not_a_claim_but_each_item_still_needs_citation(self):
        lead = "Các nội dung chính về bỏng trong tài liệu bao gồm:\n"
        accepted = validate_grounded_answer(lead + "- Nguồn nêu một nội dung. [S1]", 1)
        rejected = validate_grounded_answer(
            lead + "- Nội dung có nguồn. [S1]\n- Một nội dung không có trích dẫn.",
            1,
        )

        self.assertTrue(accepted.accepted)
        self.assertIn("uncited_bullet", rejected.issues)

    def test_b07_uncited_explanatory_note_still_fails_after_ignoring_intro(self):
        answer = (
            "Các nội dung chính về bỏng trong tài liệu bao gồm:\n\n"
            "- Nội dung được nguồn hỗ trợ. [S1]\n\n"
            "Lưu ý: đoạn dịch được giữ nguyên vì thuật ngữ chưa rõ."
        )
        result = validate_grounded_answer(answer, 1)

        self.assertIn("uncited_claim", result.issues)
        self.assertIn("dòng 5", result.details[0])

    def test_valid_citation_does_not_establish_that_a_claim_is_supported(self):
        # This syntax-only function has no source text to compare. Acceptance
        # here is not an entailment verdict and must not be reported as one.
        result = validate_grounded_answer(
            "Chấn thương do cháy nổ gây sưng đường thở. [S1]",
            1,
        )
        self.assertTrue(result.accepted)

    def test_nested_list_label_is_allowed_but_each_child_needs_its_own_citation(self):
        accepted = validate_grounded_answer(
            "- Khám ban đầu (ABCDE):\n  - Đánh giá đường thở. [S1]\n  - Đánh giá hô hấp. [S1]",
            1,
        )
        rejected = validate_grounded_answer(
            "- Khám ban đầu (ABCDE):\n  - Đánh giá đường thở. [S1]\n  - Đánh giá hô hấp.",
            1,
        )
        self.assertTrue(accepted.accepted)
        self.assertIn("uncited_bullet", rejected.issues)

    def test_unrelated_citation_in_a_later_list_item_does_not_cover_prose_before_it(self):
        result = validate_grounded_answer(
            "Một nhận định chưa trích dẫn.\n- Một ý có nguồn. [S1]",
            1,
        )
        self.assertIn("uncited_claim", result.issues)

    def test_each_sentence_needs_its_own_citation(self):
        result = validate_grounded_answer(
            "Ý thứ nhất có nguồn. [S1] Ý thứ hai không có nguồn.",
            1,
        )
        self.assertIn("uncited_claim", result.issues)

    def test_citation_before_its_claim_is_misplaced(self):
        result = validate_grounded_answer("[S1] Nội dung được nêu sau mã nguồn.", 1)
        self.assertIn("citation_misplaced", result.issues)

    def test_soft_wrapped_list_item_can_carry_a_trailing_citation(self):
        result = validate_grounded_answer(
            "- Một ý được xuống dòng trong Markdown\n  và có trích dẫn ở cuối. [S1]",
            1,
        )
        self.assertTrue(result.accepted)

    def test_rejects_invalid_citation_index(self):
        result = validate_grounded_answer("Một câu trả lời. [S2]", 1)
        self.assertFalse(result.accepted)
        self.assertIn("invalid_citation", result.issues)

    def test_rejects_uncited_list_item(self):
        result = validate_grounded_answer("- Ý thứ nhất. [S1]\n- Ý thứ hai.", 1)
        self.assertFalse(result.accepted)
        self.assertIn("uncited_bullet", result.issues)

    def test_rejects_uncited_factual_paragraph_after_cited_paragraph(self):
        result = validate_grounded_answer(
            "Ý thứ nhất có nguồn. [S1]\n\nÝ thực tế thứ hai chưa có nguồn.",
            1,
        )
        self.assertFalse(result.accepted)
        self.assertIn("uncited_claim", result.issues)

    def test_rejects_overlong_output(self):
        result = validate_grounded_answer("x" * 50, 1, max_chars=20)
        self.assertFalse(result.accepted)
        self.assertIn("answer_too_long", result.issues)

    def test_explicit_source_ids(self):
        self.assertTrue(citations_are_in_range("Có nguồn [S1] và [S2].", ["S1", "S2"]))
        self.assertFalse(citations_are_in_range("Có nguồn [S3].", ["S1", "S2"]))

    def test_selected_nonconsecutive_source_id_is_valid_only_when_allowed(self):
        valid = validate_grounded_answer(
            "Nội dung được hỗ trợ. [S2]",
            1,
            allowed_source_ids=["S2"],
        )
        invalid = validate_grounded_answer(
            "Nội dung được hỗ trợ. [S1]",
            1,
            allowed_source_ids=["S2"],
        )
        self.assertTrue(valid.accepted)
        self.assertIn("invalid_citation", invalid.issues)

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

    def test_abcde_source_coverage_detects_missing_steps(self):
        question = "Tài liệu trình bày những bước đánh giá ban đầu người bệnh cấp cứu nào?"
        source = "ABCDE: trauma primary survey. Airway assessment starts here."
        self.assertFalse(abcde_source_coverage(question, [source]))

    def test_abcde_source_coverage_accepts_all_five_source_labels(self):
        question = "Tóm tắt các bước đánh giá người bệnh chấn thương."
        source = "ABCDE: Airway, Breathing, Circulation, Disability and Exposure."
        self.assertTrue(abcde_source_coverage(question, [source]))

    def test_abcde_answer_with_only_airway_is_incomplete(self):
        question = "Tóm tắt các bước đánh giá người bệnh chấn thương."
        answer = "- A: Đường thở và cột sống cổ. [S1]"
        self.assertEqual(
            missing_abcde_answer_stages(question, answer),
            ("B", "C", "D", "E"),
        )

    def test_abcde_completeness_does_not_apply_to_other_queries(self):
        self.assertIsNone(abcde_source_coverage("Tài liệu nêu gì về co giật?", ["seizure"]))
        self.assertEqual(missing_abcde_answer_stages("Tài liệu nêu gì về co giật?", "Một câu."), ())


if __name__ == "__main__":
    unittest.main()
