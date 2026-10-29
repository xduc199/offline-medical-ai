"""Regression tests for citation repair and optional CPU-only Ollama inference."""

import io
import json
import os
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from app.internal_pilot import (
    AnswerOutcome,
    CHUNKS,
    Chunk,
    _ollama_options,
    call_model_uncached,
    localize_medical_terms,
    ollama_chat,
    source_list_answer,
    translation_quality_warning,
)
from app.answer_validation import validate_grounded_answer


class GroundedAnswerRetryTests(unittest.TestCase):
    def test_b07_retry_redacts_forbidden_script_and_logs_the_exact_prompts(self):
        chunk = Chunk(
            index=1,
            page="71",
            start_line=1,
            end_line=5,
            text="Do not forget to give tetanus vaccination and pain relief for burn injuries.",
        )
        first_draft = (
            "Các nội dung chính về bỏng trong tài liệu bao gồm:\n\n"
            "- Tiêm phòng破风 and giảm đau cho bỏng. [S1]"
        )
        repaired = "- Tiêm phòng uốn ván và giảm đau cho bỏng. [S1]"

        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "b07-trace.jsonl"
            with patch.dict(os.environ, {"BEC_PILOT_DIAGNOSTICS_PATH": str(trace_path)}), patch(
                "app.internal_pilot.ollama_chat",
                side_effect=[first_draft, repaired],
            ) as chat:
                outcome = call_model_uncached(
                    "Tóm tắt các nội dung chính về bỏng trong tài liệu.",
                    [(chunk, 1.0)],
                )
            records = [
                json.loads(line)
                for line in trace_path.read_text(encoding="utf-8").splitlines()
            ]

        self.assertTrue(outcome.should_validate)
        self.assertEqual(outcome.answer, repaired)
        self.assertEqual(chat.call_count, 2)
        repair_prompt = chat.call_args_list[1].args[1]
        self.assertIn("[ký tự chữ viết không được phép đã lược]", repair_prompt)
        self.assertNotIn("破风", repair_prompt)
        self.assertIn("tetanus vaccination", repair_prompt)
        self.assertIn("tiêm phòng uốn ván", repair_prompt)
        self.assertIn("Không viết lời dẫn, tiêu đề, chú thích", repair_prompt)
        self.assertEqual(records[1]["user_prompt"], repair_prompt)
        self.assertEqual(records[1]["system_prompt"], chat.call_args_list[1].args[0])
        self.assertEqual(records[1]["source_text"], chunk.text)
        self.assertEqual(records[0]["raw_model_output"], first_draft)
        self.assertTrue(records[0]["citation_accepted"])
        self.assertEqual(records[0]["final_issues"], ["translation"])
        self.assertNotIn("破风", records[1]["user_prompt"])

    def test_burn_terminology_localization_uses_only_terms_present_in_source(self):
        source = "Do not forget to give tetanus vaccination and pain relief for burn injuries."
        localized = localize_medical_terms(
            "Tetanus vaccination and pain relief. [S1]",
            source,
        )

        self.assertEqual(localized, "tiêm phòng uốn ván và giảm đau. [S1]")
        self.assertIsNone(translation_quality_warning(localized))

    def test_malformed_ollama_json_is_converted_to_a_safe_runtime_error(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b"secret response fragment: not-json"
        with patch("app.internal_pilot.urllib.request.urlopen", return_value=response):
            with self.assertRaises(RuntimeError) as caught:
                ollama_chat("system", "user")

        self.assertNotIn("secret response fragment", str(caught.exception))
        self.assertIn("JSON không hợp lệ", str(caught.exception))

    def test_wrapped_ollama_timeout_returns_a_safe_timeout_message(self):
        chunk = Chunk(
            index=1,
            page="71",
            start_line=1,
            end_line=5,
            text="Burn care includes tetanus vaccination and pain relief.",
        )
        with self.assertLogs("app.internal_pilot", level="ERROR"), patch(
            "app.internal_pilot.ollama_chat",
            side_effect=urllib.error.URLError(TimeoutError("sensitive transport detail")),
        ):
            outcome = call_model_uncached("What does the source say about burns?", [(chunk, 1.0)])

        self.assertFalse(outcome.should_validate)
        self.assertIn("hết thời gian chờ", outcome.warning)
        self.assertNotIn("sensitive transport detail", outcome.warning)

    def test_ollama_runtime_error_details_are_not_returned_to_the_user(self):
        chunk = Chunk(
            index=1,
            page="71",
            start_line=1,
            end_line=5,
            text="Burn care includes tetanus vaccination and pain relief.",
        )
        with self.assertLogs("app.internal_pilot", level="ERROR") as logs, patch(
            "app.internal_pilot.ollama_chat", side_effect=RuntimeError("api-key=top-secret")
        ):
            outcome = call_model_uncached("What does the source say?", [(chunk, 1.0)])

        self.assertFalse(outcome.should_validate)
        self.assertNotIn("top-secret", outcome.warning)
        self.assertNotIn("top-secret", logs.output[0])

    def test_opt_in_diagnostic_records_safe_ollama_failure_without_exception_text(self):
        chunk = Chunk(
            index=1,
            page="71",
            start_line=1,
            end_line=5,
            text="Burn care includes tetanus vaccination and pain relief.",
        )
        secret = "api-key=top-secret"
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "ollama-error.jsonl"
            with patch.dict(os.environ, {"BEC_PILOT_DIAGNOSTICS_PATH": str(trace_path)}), \
                    self.assertLogs("app.internal_pilot", level="ERROR") as logs, \
                    patch(
                        "app.internal_pilot.ollama_chat",
                        side_effect=RuntimeError(f"Ollama /api/chat trả HTTP 500: {secret}"),
                    ):
                outcome = call_model_uncached("Summarize burns.", [(chunk, 1.0)])
            trace_text = trace_path.read_text(encoding="utf-8")
            record = json.loads(trace_text.splitlines()[0])

        self.assertFalse(outcome.should_validate)
        self.assertEqual(record["failure"], {
            "stage": "ollama_chat",
            "type": "RuntimeError",
            "category": "http_500",
        })
        self.assertIn("Chỉ được dùng các đoạn nguồn", record["system_prompt"])
        self.assertIn("Summarize burns.", record["user_prompt"])
        self.assertEqual(record["source_text"], chunk.text)
        self.assertNotIn(secret, trace_text)
        self.assertTrue(all(secret not in line for line in logs.output))

    def test_postpartum_magnesium_claim_retries_with_the_source_that_supports_both_conditions(self):
        page_33 = next(
            chunk for chunk in CHUNKS
            if chunk.page == "33" and "recently gave birth" in chunk.text
        )
        page_142 = next(
            chunk for chunk in CHUNKS
            if chunk.page == "142" and "If pregnant and seizing" in chunk.text
        )
        unsupported_draft = "- Nếu người phụ nữ mang thai hoặc mới sinh con, cung cấp magnesium sulphate. [S2]"
        supported_draft = "- Nếu người phụ nữ mang thai hoặc mới sinh con, cung cấp magne sunfat. [S1]"

        with patch(
            "app.internal_pilot.ollama_chat",
            side_effect=[unsupported_draft, supported_draft],
        ) as chat:
            outcome = call_model_uncached(
                "Tổng hợp cách xử trí co giật ở người lớn và trẻ em theo tài liệu.",
                [(page_33, 0.9), (page_142, 0.8)],
            )

        self.assertTrue(outcome.should_validate)
        self.assertIsNone(outcome.warning)
        self.assertIn("[S1]", outcome.answer)
        retry_prompt = chat.call_args_list[1].args[1]
        self.assertIn("citation của chính dòng đó", retry_prompt)
        self.assertIn("hãy bỏ điều kiện đó", retry_prompt)
        self.assertEqual(chat.call_count, 2)

    def test_pregnancy_only_seizure_source_cannot_support_postpartum_magnesium_claim(self):
        page_142 = next(
            chunk for chunk in CHUNKS
            if chunk.page == "142" and "If pregnant and seizing" in chunk.text
        )
        draft = "- Nếu người phụ nữ mang thai hoặc mới sinh con, cung cấp magne sunfat. [S1]"

        with patch("app.internal_pilot.ollama_chat", return_value=draft) as chat:
            outcome = call_model_uncached(
                "Tóm tắt phần xử trí co giật.",
                [(page_142, 0.9)],
            )

        self.assertFalse(outcome.should_validate)
        self.assertIn("Citation không hỗ trợ trực tiếp điều kiện sau sinh", outcome.warning)
        self.assertNotIn("mới sinh con", outcome.answer)
        self.assertEqual(chat.call_count, 2)

    def test_postpartum_magnesium_claim_is_hidden_when_no_source_verifies_it(self):
        unrelated = Chunk(
            index=1,
            page="34",
            start_line=1,
            end_line=3,
            text="The source discusses an unrelated emergency topic.",
        )
        draft = "- Nếu người phụ nữ mang thai hoặc mới sinh con, cung cấp magne sulphat. [S1]"

        with patch("app.internal_pilot.ollama_chat", return_value=draft) as chat:
            outcome = call_model_uncached("Tóm tắt tài liệu.", [(unrelated, 1.0)])

        self.assertFalse(outcome.should_validate)
        self.assertIn("Citation không hỗ trợ trực tiếp điều kiện sau sinh", outcome.warning)
        self.assertNotIn("mới sinh con", outcome.answer)
        self.assertEqual(chat.call_count, 2)

    def test_generation_diagnostics_are_silent_and_write_nothing_by_default(self):
        chunk = Chunk(
            index=1,
            page="71",
            start_line=1,
            end_line=5,
            text="Burn care includes tetanus vaccination and pain relief.",
        )
        stdout = io.StringIO()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "should-not-exist.jsonl"
            with patch.dict(os.environ, {"BEC_PILOT_DIAGNOSTICS_PATH": ""}), \
                    redirect_stdout(stdout), redirect_stderr(stderr), \
                    patch(
                        "app.internal_pilot.ollama_chat",
                        side_effect=["Cần đối chiếu nguồn.", "Cần kiểm tra疫苗. [S1]"],
                    ):
                outcome = call_model_uncached("Tài liệu nêu gì về bỏng?", [(chunk, 1.0)])

            self.assertFalse(outcome.should_validate)
            self.assertFalse(trace_path.exists())
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), "")

    def test_generation_diagnostic_write_failure_does_not_fail_answer(self):
        chunk = Chunk(
            index=1,
            page="71",
            start_line=1,
            end_line=5,
            text="Burn care includes tetanus vaccination and pain relief.",
        )
        invalid_path = Mock()
        invalid_path.expanduser.return_value = invalid_path
        invalid_path.parent.mkdir.return_value = None
        invalid_path.open.side_effect = ValueError("embedded null character")

        with self.assertLogs("app.internal_pilot", level="WARNING") as logs:
            with patch.dict(os.environ, {"BEC_PILOT_DIAGNOSTICS_PATH": "invalid-trace.jsonl"}), \
                    patch("app.internal_pilot.Path", return_value=invalid_path), \
                    patch(
                        "app.internal_pilot.ollama_chat",
                        return_value="Tài liệu nêu nội dung được trích dẫn. [S1]",
                    ):
                outcome = call_model_uncached("Tài liệu nêu gì về bỏng?", [(chunk, 1.0)])

        self.assertTrue(outcome.should_validate)
        self.assertIsNone(outcome.warning)
        self.assertIn("[S1]", outcome.answer)
        self.assertIn("Optional generation diagnostics could not be written", logs.output[0])
        invalid_path.open.assert_called_once_with("a", encoding="utf-8", newline="\n")

    def test_opt_in_generation_diagnostic_identifies_cjk_in_raw_model_output(self):
        chunk = Chunk(
            index=1,
            page="71",
            start_line=1,
            end_line=5,
            text="Burn care includes tetanus vaccination and pain relief.",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "b07-trace.jsonl"
            with patch.dict(
                os.environ,
                {
                    "BEC_PILOT_DIAGNOSTICS_PATH": str(trace_path),
                },
            ), patch(
                "app.internal_pilot.ollama_chat",
                side_effect=["Cần đối chiếu nguồn.", "Cần kiểm tra疫苗. [S1]"],
            ):
                outcome = call_model_uncached("Tài liệu nêu gì về bỏng?", [(chunk, 1.0)])

            records = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]

        self.assertFalse(outcome.should_validate)
        self.assertEqual(len(records), 2)
        self.assertNotIn("label", records[1])
        self.assertIn("疫", records[1]["raw_model_output"])
        self.assertIn("疫", records[1]["post_localization_output"])
        self.assertEqual(records[1]["cjk_characters"]["raw_model_output"], ["疫", "苗"])
        self.assertEqual(records[1]["cjk_characters"]["post_localization_output"], ["疫", "苗"])
        self.assertEqual(records[1]["cjk_characters"]["source_text"], [])
        self.assertEqual(records[1]["cjk_characters"]["user_prompt"], [])
        self.assertIsNotNone(records[1]["translation_warning"])
        self.assertIn("translation", records[1]["final_issues"])

    def test_retry_requires_flat_individually_cited_bullets_and_still_hides_bad_output(self):
        first_source = Chunk(
            index=1,
            page="52",
            start_line=1,
            end_line=4,
            text="A source passage about burns.",
        )
        second_source = Chunk(
            index=2,
            page="71",
            start_line=5,
            end_line=9,
            text="Another source passage about burns.",
        )
        first_draft = (
            "Summary:\n"
            "- [S1] First heading:\n"
            "  - First factual item.\n"
            "  - Second factual item.\n"
            "- [S2] Second heading:\n"
            "  - Third factual item."
        )
        second_draft = (
            "Summary:\n"
            "- [S1] First heading:\n"
            "  - Still uncited factual item.\n"
            "- [S2] Annotation with 汉字."
        )

        with patch(
            "app.internal_pilot.ollama_chat",
            side_effect=[first_draft, second_draft],
        ) as chat:
            outcome = call_model_uncached(
                "Summarize burn management.",
                [(first_source, 0.9), (second_source, 0.8)],
            )

        retry_prompt = chat.call_args_list[1].args[1]
        self.assertIn("danh sách phẳng", retry_prompt)
        self.assertIn("không lồng bullet", retry_prompt)
        self.assertIn("Mỗi dòng chỉ nêu một ý thực tế", retry_prompt)
        self.assertIn("mã nguồn trực tiếp hỗ trợ", retry_prompt)
        self.assertIn("[S1], [S2]", retry_prompt)
        self.assertFalse(outcome.should_validate)
        self.assertIn("thiếu mã trích dẫn", outcome.warning)
        self.assertIn("ký tự ngoài tiếng Việt", outcome.warning)
        self.assertNotIn("Still uncited", outcome.answer)
        self.assertEqual(chat.call_count, 2)

    def test_missing_citations_trigger_one_repair_attempt(self):
        chunk = Chunk(
            index=1,
            page="33",
            start_line=10,
            end_line=14,
            text="Protect the person from falls and nearby hard or sharp objects.",
            source_id="WHO_ICRC_BEC_2018",
            source_title="Basic Emergency Care",
            publishers=("WHO", "ICRC"),
            publication_year=2018,
        )
        with patch(
            "app.internal_pilot.ollama_chat",
            side_effect=[
                "Bảo vệ người bệnh khỏi nguy cơ té ngã.",
                "Bảo vệ người bệnh khỏi nguy cơ té ngã. [S1]",
            ],
        ) as chat:
            outcome = call_model_uncached("Tài liệu nêu gì về co giật?", [(chunk, 1.0)])

        self.assertIsNone(outcome.warning)
        self.assertIn("[S1]", outcome.answer)
        self.assertTrue(outcome.should_validate)
        retry_prompt = chat.call_args_list[1].args[1]
        self.assertIn("hoàn toàn bằng tiếng Việt", retry_prompt)
        self.assertIn("Không sinh ký tự Han, Nhật hoặc Hàn", retry_prompt)
        self.assertIn("không sao chép nguyên văn câu tiếng Anh dài", retry_prompt)
        self.assertIn("Chỉ dùng các ID hợp lệ trong prompt: [S1]", retry_prompt)
        self.assertIn("BẢN NHÁP BỊ TỪ CHỐI", retry_prompt)
        self.assertIn("Bảo vệ người bệnh khỏi nguy cơ té ngã.", retry_prompt)
        self.assertIn("dòng 1", retry_prompt)
        self.assertIn("[S1] hoặc [S1, S2]", retry_prompt)
        self.assertEqual(chat.call_count, 2)

    def test_parenthetical_source_marker_gets_format_specific_repair_feedback(self):
        chunk = Chunk(
            index=1,
            page="49",
            start_line=1,
            end_line=4,
            text="A source passage about an initial assessment.",
        )
        with patch(
            "app.internal_pilot.ollama_chat",
            side_effect=[
                "- Đánh giá đường thở. (S1)",
                "- Đánh giá đường thở. [S1]",
            ],
        ) as chat:
            outcome = call_model_uncached("Tài liệu nói gì về đường thở?", [(chunk, 1.0)])

        self.assertTrue(outcome.should_validate)
        self.assertIn("[S1]", outcome.answer)
        retry_prompt = chat.call_args_list[1].args[1]
        self.assertIn("invalid_citation_format", retry_prompt)
        self.assertIn("(S1)", retry_prompt)
        self.assertIn("ngoặc vuông", retry_prompt)
        self.assertEqual(chat.call_count, 2)

    def test_pediatric_workbook_case_is_omitted_but_general_seizure_guidance_remains(self):
        page_33 = next(
            chunk for chunk in CHUNKS
            if chunk.page == "33" and "The goal in managing seizures/convulsions" in chunk.text
        )
        page_142 = next(
            chunk for chunk in CHUNKS
            if chunk.page == "142" and "Workbook question 4" in chunk.text
        )
        answer = (
            "- Bảo vệ người đang co giật khỏi ngã và vật cứng hoặc sắc ở gần. [S1]\n"
            "- Dùng benzodiazepine. [S2]"
        )

        with patch("app.internal_pilot.ollama_chat", return_value=answer) as chat:
            outcome = call_model_uncached(
                "Tổng hợp cách xử trí co giật ở người lớn và trẻ em theo tài liệu.",
                [(page_33, 0.9), (page_142, 0.8)],
            )

        self.assertTrue(outcome.should_validate)
        self.assertIsNone(outcome.warning)
        prompt = chat.call_args.args[1]
        self.assertIn("The goal in managing seizures/convulsions", prompt)
        self.assertIn("Give a benzodiazepine", prompt)
        self.assertIn("dòng trả lời để trống", prompt)
        self.assertNotIn("Workbook question 4", prompt)
        self.assertNotIn("3-year-old child", prompt)
        self.assertNotIn("2 mmol/L", prompt)

    def test_specific_query_for_blank_workbook_case_returns_source_limitation(self):
        page_33 = next(
            chunk for chunk in CHUNKS
            if chunk.page == "33" and "The goal in managing seizures/convulsions" in chunk.text
        )
        page_142 = next(
            chunk for chunk in CHUNKS
            if chunk.page == "142" and "Workbook question 4" in chunk.text
        )

        with patch("app.internal_pilot.ollama_chat") as chat:
            outcome = call_model_uncached(
                "Tài liệu nêu đáp án gì cho trẻ 3 tuổi có glucose 2 mmol/L?",
                [(page_33, 0.9), (page_142, 0.8)],
            )

        self.assertTrue(outcome.should_validate)
        self.assertIn("chưa cung cấp đáp án cụ thể", outcome.answer)
        self.assertIn("[S2]", outcome.answer)
        self.assertNotIn("co giật", outcome.answer.lower())
        chat.assert_not_called()

    def test_model_cannot_present_blank_workbook_case_as_supported_treatment(self):
        page_33 = next(
            chunk for chunk in CHUNKS
            if chunk.page == "33" and "The goal in managing seizures/convulsions" in chunk.text
        )
        page_142 = next(
            chunk for chunk in CHUNKS
            if chunk.page == "142" and "Workbook question 4" in chunk.text
        )
        unsupported_case_answer = (
            "- Với trẻ 3 tuổi có thay đổi trạng thái tinh thần và glucose 2 mmol/L, "
            "cung cấp oxy và kiểm tra đường huyết. [S1]"
        )
        structurally_valid = validate_grounded_answer(
            unsupported_case_answer,
            2,
            allowed_source_ids=["S1", "S2"],
        )
        self.assertTrue(structurally_valid.accepted)

        with patch(
            "app.internal_pilot.ollama_chat",
            side_effect=[unsupported_case_answer, unsupported_case_answer],
        ) as chat:
            outcome = call_model_uncached(
                "Tổng hợp cách xử trí co giật ở người lớn và trẻ em theo tài liệu.",
                [(page_33, 0.9), (page_142, 0.8)],
            )

        self.assertFalse(outcome.should_validate)
        self.assertIn("để trống đáp án", outcome.warning)
        self.assertNotIn("trẻ 3 tuổi", outcome.answer.lower())
        self.assertEqual(chat.call_count, 2)
        self.assertIn("Không nêu cách xử trí cho tình huống bài tập", chat.call_args_list[1].args[1])


    def test_translation_warning_catches_short_english_fragment(self):
        warning = translation_quality_warning(
            "Dấu hiệu gồm lú lẫn that gradually improves over minutes to hours. [S1]"
        )

        self.assertIsNotNone(warning)
        self.assertIn("tiếng Anh", warning)

    def test_translation_warning_accepts_acronyms_and_units(self):
        self.assertIsNone(translation_quality_warning("ABCDE, AVPU, WHO, 5 mmol/L [S1]"))
        self.assertIsNone(translation_quality_warning("Tên thuốc benzodiazepine, đơn vị 5 mmol/L. [S1]"))

    def test_translation_warning_accepts_short_medical_term_after_vietnamese_gloss(self):
        self.assertIsNone(
            translation_quality_warning(
                "Đánh giá hô hấp (Breathing) trong khảo sát ABCDE. [S1]"
            )
        )

    def test_translation_warning_rejects_untranslated_english_sentence(self):
        warning = translation_quality_warning("Assess airway and breathing immediately. [S1]")
        self.assertIsNotNone(warning)
        self.assertIn("tiếng Anh", warning)

    def test_valid_answer_with_medicine_abbreviation_and_unit_passes_all_checks(self):
        chunk = Chunk(
            index=1,
            page="33",
            start_line=1,
            end_line=5,
            text="The source mentions AVPU, benzodiazepine, and a value of 5 mmol/L.",
        )
        answer = "Theo tài liệu, có nhắc AVPU, benzodiazepine và đơn vị 5 mmol/L. [S1]"

        with patch("app.internal_pilot.ollama_chat", return_value=answer) as chat:
            outcome = call_model_uncached("Tài liệu nêu những thuật ngữ nào?", [(chunk, 1.0)])

        self.assertTrue(outcome.should_validate)
        self.assertIsNone(outcome.warning)
        self.assertEqual(outcome.answer, answer)
        self.assertEqual(chat.call_count, 1)

    def test_retry_with_valid_citation_but_cjk_is_still_hidden(self):
        chunk = Chunk(
            index=1,
            page="71",
            start_line=1,
            end_line=5,
            text="Burn care includes tetanus vaccination and pain relief.",
        )
        with patch(
            "app.internal_pilot.ollama_chat",
            side_effect=[
                "Cần đối chiếu nguồn để trả lời.",
                "Tiêm phòng破风疫苗和给予止痛药. [S1]",
            ],
        ) as chat:
            outcome = call_model_uncached("Tài liệu nêu gì về bỏng?", [(chunk, 1.0)])

        self.assertFalse(outcome.should_validate)
        self.assertIn("ký tự ngoài tiếng Việt", outcome.warning)
        self.assertNotIn("thiếu mã trích dẫn", outcome.warning)
        self.assertNotIn("破风疫苗", outcome.answer)
        self.assertEqual(chat.call_count, 2)
        retry_prompt = chat.call_args_list[1].args[1]
        self.assertIn("Không sinh ký tự Han, Nhật hoặc Hàn", retry_prompt)
        self.assertIn("không sao chép nguyên văn câu tiếng Anh dài", retry_prompt)
        self.assertIn("[S1]", retry_prompt)

    def test_translation_warning_accepts_source_abcde_stage_labels(self):
        answer = "\n".join(
            f"- {letter}: {term} [S1]"
            for letter, term in (
                ("A", "Airway"),
                ("B", "Breathing"),
                ("C", "Circulation"),
                ("D", "Disability"),
                ("E", "Exposure"),
            )
        )
        self.assertIsNone(translation_quality_warning(answer))

    def test_translation_warning_catches_mixed_vietnamese_and_english_medical_sentence(self):
        warning = translation_quality_warning(
            "A: Trauma primary survey, còn được gọi là ABCDE approach, được thực hiện trong 5 phút. [S1]"
        )
        self.assertIsNotNone(warning)
        self.assertIn("tiếng Anh", warning)

    def test_translation_retry_reuses_sources_and_repairs_english_fragment(self):
        chunk = Chunk(
            index=1,
            page="33",
            start_line=10,
            end_line=14,
            text="Confusion that gradually improves over minutes to hours.",
            source_id="WHO_ICRC_BEC_2018",
        )
        with patch(
            "app.internal_pilot.ollama_chat",
            side_effect=[
                "Lú lẫn that gradually improves over minutes to hours. [S1]",
                "Lú lẫn cải thiện dần trong vài phút đến vài giờ. [S1]",
            ],
        ) as chat:
            outcome = call_model_uncached("Tài liệu nêu dấu hiệu nào?", [(chunk, 1.0)])

        self.assertIsNone(outcome.warning)
        self.assertIn("cải thiện dần", outcome.answer)
        self.assertEqual(chat.call_count, 2)
        for call in chat.call_args_list:
            self.assertIn("[S1] WHO_ICRC_BEC_2018", call.args[1])
        self.assertIn("Dịch toàn bộ câu tiếng Anh", chat.call_args_list[1].args[1])

    def test_translation_retry_is_bounded_and_hides_persistent_english(self):
        chunk = Chunk(
            index=1,
            page="33",
            start_line=10,
            end_line=14,
            text="Confusion that gradually improves over minutes to hours.",
            source_id="WHO_ICRC_BEC_2018",
        )
        with patch(
            "app.internal_pilot.ollama_chat",
            return_value="Lú lẫn that gradually improves over minutes to hours. [S1]",
        ) as chat:
            outcome = call_model_uncached("Tài liệu nêu dấu hiệu nào?", [(chunk, 1.0)])

        self.assertFalse(outcome.should_validate)
        self.assertIn("tiếng Anh", outcome.warning)
        self.assertNotIn("gradually", outcome.answer)
        self.assertEqual(chat.call_count, 2)

    def test_valid_citations_do_not_trigger_repair(self):
        chunk = Chunk(
            index=1,
            page="33",
            start_line=10,
            end_line=14,
            text="Protect the person from falls and nearby hard or sharp objects.",
            source_id="WHO_ICRC_BEC_2018",
            source_title="Basic Emergency Care",
            publishers=("WHO", "ICRC"),
            publication_year=2018,
        )
        with patch(
            "app.internal_pilot.ollama_chat",
            return_value="Bảo vệ người bệnh khỏi nguy cơ té ngã. [S1]",
        ) as chat:
            outcome = call_model_uncached("Tài liệu nêu gì về co giật?", [(chunk, 1.0)])

        self.assertIsNone(outcome.warning)
        self.assertIn("[S1]", outcome.answer)
        self.assertEqual(chat.call_count, 1)

    def test_selected_second_source_keeps_its_api_citation_id(self):
        unrelated = Chunk(
            index=1,
            page="31",
            start_line=1,
            end_line=2,
            text="An unrelated passage.",
        )
        shock = Chunk(
            index=2,
            page="32",
            start_line=10,
            end_line=14,
            text="Shock • tachycardia and tachypnoea. Poor perfusion is reduced blood flow.",
        )
        with patch(
            "app.internal_pilot.ollama_chat",
            return_value="Nhịp tim nhanh. [S2]",
        ) as chat:
            outcome = call_model_uncached(
                "Tài liệu nêu dấu hiệu nào của sốc?",
                [(unrelated, 1.0), (shock, 0.9)],
            )

        self.assertIsNone(outcome.warning)
        self.assertIn("[S2]", chat.call_args.args[1])
        self.assertNotIn("[S1] Basic Emergency Care", chat.call_args.args[1])

    def test_incomplete_abcde_source_returns_limited_answer_without_llm(self):
        chunk = Chunk(
            index=1,
            page="49",
            start_line=10,
            end_line=14,
            text="ABCDE: TRAUMA PRIMARY SURVEY. Airway assessment begins here.",
        )
        question = "Tài liệu trình bày những bước đánh giá ban đầu người bệnh cấp cứu nào?"
        with patch("app.internal_pilot.ollama_chat") as chat:
            outcome = call_model_uncached(question, [(chunk, 1.0)])

        self.assertIn("chưa chứa mô tả đủ cả năm phần", outcome.answer)
        self.assertIn("[S1]", outcome.answer)
        self.assertIn("ABCDE", outcome.warning)
        self.assertTrue(outcome.should_validate)
        chat.assert_not_called()

    def test_abcde_answer_missing_steps_gets_one_repair_then_is_hidden(self):
        chunk = Chunk(
            index=1,
            page="221",
            start_line=10,
            end_line=14,
            text="The primary survey consists of the ABCDE: Airway, Breathing, Circulation, Disability and Exposure.",
        )
        question = "Tóm tắt các bước đánh giá người bệnh chấn thương."
        with patch(
            "app.internal_pilot.ollama_chat",
            return_value="- A: Đường thở. [S1]",
        ) as chat:
            outcome = call_model_uncached(question, [(chunk, 1.0)])

        self.assertFalse(outcome.should_validate)
        self.assertIn("chưa nêu đủ các bước ABCDE", outcome.warning)
        self.assertEqual(chat.call_count, 2)
        self.assertIn("B, C, D, E", chat.call_args.args[1])

    def test_abcde_list_uses_exact_source_definition_and_limits_detail_claims(self):
        glossary = Chunk(
            index=1,
            page="221",
            start_line=10,
            end_line=14,
            text=(
                "Trauma primary survey. The primary survey consists of the ABCDE: "
                "Airway, Breathing, Circulation, Disability and Exposure."
            ),
        )
        partial_survey = Chunk(
            index=2,
            page="49",
            start_line=10,
            end_line=14,
            text="ABCDE: TRAUMA PRIMARY SURVEY. Airway with cervical spine immobilization. Look for blood.",
        )
        result = source_list_answer(
            "Tóm tắt các bước đánh giá người bệnh chấn thương.",
            [(glossary, 1.0), (partial_survey, 0.9)],
        )

        self.assertIsNotNone(result)
        answer, warning = result
        self.assertIn("đánh giá ban đầu người bị chấn thương", answer)
        self.assertNotIn("trauma primary survey", answer)
        self.assertIn("A – Airway, B – Breathing, C – Circulation, D – Disability và E – Exposure", answer)
        self.assertIn("thao tác cho các phần B, C, D, E", answer)
        self.assertIn("[S1]", answer)
        self.assertIn("[S2]", answer)
        self.assertIsNotNone(warning)

    def test_general_bleeding_answer_uses_only_supported_source_principles(self):
        shock = Chunk(
            index=1,
            page="32",
            start_line=1,
            end_line=5,
            text="Shock management includes control bleeding.",
        )
        wound = Chunk(
            index=2,
            page="196",
            start_line=1,
            end_line=5,
            text=(
                "WOUND MANAGEMENT: GENERAL WOUND MANAGEMENT. "
                "Use a pressure dressing if the wound is still bleeding."
            ),
        )
        result = source_list_answer(
            "Theo tài liệu, cần đánh giá và xử trí người bệnh bị chảy máu như thế nào?",
            [(shock, 0.6), (wound, 0.5)],
        )

        self.assertIsNotNone(result)
        answer, warning = result
        self.assertIsNotNone(warning)
        self.assertIn("kiểm soát chảy máu", answer)
        self.assertIn("băng ép nếu vết thương vẫn chảy máu", answer)
        self.assertIn("chưa đủ để mô tả", answer)
        self.assertIn("[S1]", answer)
        self.assertIn("[S2]", answer)

    def test_specific_bleeding_question_is_not_answered_from_general_chunks(self):
        general = Chunk(
            index=1,
            page="32",
            start_line=1,
            end_line=5,
            text="Shock management includes control bleeding.",
        )
        result = source_list_answer(
            "Theo tài liệu, xử trí chảy máu sau sinh như thế nào?",
            [(general, 0.6)],
        )

        self.assertIsNone(result)


class OllamaCpuFallbackTests(unittest.TestCase):
    def test_num_gpu_zero_is_sent_when_cpu_fallback_is_configured(self):
        with patch("app.internal_pilot.OLLAMA_NUM_GPU", "0"):
            options = _ollama_options(450)

        self.assertEqual(options["num_gpu"], 0)
        self.assertEqual(options["num_predict"], 450)

    def test_invalid_num_gpu_configuration_is_reported(self):
        with patch("app.internal_pilot.OLLAMA_NUM_GPU", "cpu"):
            with self.assertRaisesRegex(RuntimeError, "BEC_OLLAMA_NUM_GPU"):
                _ollama_options(450)


if __name__ == "__main__":
    unittest.main()
