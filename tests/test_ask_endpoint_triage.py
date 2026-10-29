"""Integration tests for the local /api/ask request-triage gate."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

from app.internal_pilot import AnswerOutcome, CHUNKS, Chunk, Handler


class AskEndpointTriageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def post_question(self, question):
        return self.post_raw(json.dumps({"question": question}, ensure_ascii=False).encode("utf-8"))[1]

    def post_raw(self, body):
        request = Request(
            self.base_url + "/api/ask",
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except HTTPError as response:
            return response.code, json.loads(response.read().decode("utf-8"))

    def test_non_object_json_is_rejected_as_bad_request(self):
        status, payload = self.post_raw(b"[]")
        self.assertEqual(status, 400)
        self.assertIn("object", payload["error"])

    def test_unexpected_api_error_is_logged_without_exposing_exception_text(self):
        secret = "api-key=top-secret"
        with patch("app.internal_pilot.retrieve", side_effect=RuntimeError(secret)):
            with self.assertLogs("app.internal_pilot", level="ERROR") as logs:
                status, payload = self.post_raw(
                    json.dumps({"question": "What does the source say?"}).encode("utf-8")
                )
        self.assertEqual(status, 500)
        self.assertNotIn(secret, payload["error"])
        self.assertTrue(all(secret not in record for record in logs.output))

    def test_possible_emergency_short_circuits_retrieval(self):
        with patch("app.internal_pilot.retrieve", side_effect=AssertionError("retrieval must not run")):
            payload = self.post_question("Người nhà tôi đang khó thở")
        self.assertEqual(payload["classification"], "possible_emergency")
        self.assertEqual(payload["sources"], [])
        self.assertIn("đừng chờ câu trả lời", payload["answer"])

    def test_personal_medication_question_short_circuits_retrieval(self):
        with patch("app.internal_pilot.retrieve", side_effect=AssertionError("retrieval must not run")):
            payload = self.post_question("Tôi có nên uống thêm thuốc không?")
        self.assertEqual(payload["classification"], "personal_medical_advice")
        self.assertEqual(payload["sources"], [])

    def test_greeting_short_circuits_retrieval(self):
        with patch("app.internal_pilot.retrieve", side_effect=AssertionError("retrieval must not run")):
            payload = self.post_question("Xin chào")
        self.assertEqual(payload["classification"], "greeting")
        self.assertEqual(payload["sources"], [])


    def test_ambiguous_query_short_circuits_retrieval(self):
        with patch("app.internal_pilot.retrieve", side_effect=AssertionError("retrieval must not run")):
            payload = self.post_question("??")
        self.assertEqual(payload["classification"], "ambiguous")
        self.assertEqual(payload["sources"], [])

    def test_no_source_response_keeps_classification(self):
        with patch("app.internal_pilot.retrieve", return_value=[]):
            payload = self.post_question("Tài liệu nêu các bước sơ cứu rắn cắn nào?")
        self.assertEqual(payload["classification"], "document_lookup")
        self.assertEqual(payload["sources"], [])
        self.assertIn("Chưa tìm thấy", payload["answer"])

    def test_unanswered_pediatric_workbook_query_returns_limited_api_answer(self):
        page_33 = next(
            chunk for chunk in CHUNKS
            if chunk.page == "33" and "The goal in managing seizures/convulsions" in chunk.text
        )
        page_142 = next(
            chunk for chunk in CHUNKS
            if chunk.page == "142" and "Workbook question 4" in chunk.text
        )
        question = "Theo tài liệu, trong mục co giật, phần bài tập có đáp án nào cho trẻ 3 tuổi có glucose 2 mmol/L?"

        with patch("app.internal_pilot.retrieve", return_value=[(page_33, 0.9), (page_142, 0.8)]), patch(
            "app.internal_pilot.source_list_answer", return_value=None
        ), patch("app.internal_pilot.ollama_chat") as chat:
            payload = self.post_question(question)

        self.assertEqual(payload["classification"], "document_lookup")
        self.assertIn("chưa cung cấp đáp án cụ thể", payload["answer"])
        self.assertIn("[S2]", payload["answer"])
        self.assertNotIn("co giật", payload["answer"].lower())
        self.assertEqual([source["id"] for source in payload["sources"]], ["S1", "S2"])
        chat.assert_not_called()

    def test_ask_response_contains_classification_for_document_query(self):
        fake_chunk = type(
            "FakeChunk",
            (),
            {
                "citation": "PDF p. 32; cleaned lines 10-15",
                "text": "Shock • tachycardia and tachypnoea",
                "index": 1,
                "page": "32",
                "start_line": 10,
                "end_line": 15,
                "source_id": "TEST_SOURCE",
                "source_title": "Test source",
                "publishers": ("Test publisher",),
                "publication_year": 2026,
                "topics": ("test",),
                "language": "en",
                "source_path": "tests/fixture.txt",
            },
        )()
        with patch("app.internal_pilot.retrieve", return_value=[(fake_chunk, 0.9)]), patch(
            "app.internal_pilot.source_list_answer",
            return_value=("Nội dung tham chiếu [S1].", None),
        ):
            payload = self.post_question("Tài liệu liệt kê những dấu hiệu nào của sốc?")
        self.assertEqual(payload["classification"], "document_lookup")
        self.assertEqual(len(payload["sources"]), 1)
        self.assertEqual(payload["sources"][0]["id"], "S1")
        self.assertEqual(payload["answer"], "Nội dung tham chiếu [S1].")
        self.assertIsNone(payload["warning"])

    def test_hidden_model_output_keeps_safe_warning_without_revalidating_refusal(self):
        fake_chunk = type(
            "FakeChunk",
            (),
            {
                "citation": "PDF p. 32; cleaned lines 10-15",
                "text": "A source passage about the requested topic.",
                "index": 1,
                "page": "32",
                "start_line": 10,
                "end_line": 15,
                "source_id": "TEST_SOURCE",
                "source_title": "Test source",
                "publishers": ("Test publisher",),
                "publication_year": 2026,
                "topics": ("test",),
                "language": "en",
                "source_path": "tests/fixture.txt",
            },
        )()
        hidden_answer = "Chưa thể hiển thị câu trả lời đạt kiểm tra. Hãy đối chiếu trực tiếp các đoạn nguồn bên dưới."
        model_warning = "Mô hình không tạo được mã trích dẫn hợp lệ sau một lần yêu cầu sửa; câu trả lời đã bị ẩn."
        with patch("app.internal_pilot.retrieve", return_value=[(fake_chunk, 0.8)]), patch(
            "app.internal_pilot.source_list_answer", return_value=None
        ), patch(
            "app.internal_pilot.call_model",
            return_value=AnswerOutcome(hidden_answer, model_warning, should_validate=False),
        ):
            payload = self.post_question("Tài liệu nêu điều gì về sơ cứu rắn cắn?")

        self.assertEqual(payload["answer"], hidden_answer)
        self.assertEqual(payload["warning"], model_warning)
        self.assertNotIn("Câu trả lời không có mã trích dẫn", payload["warning"])
        self.assertEqual(payload["sources"][0]["id"], "S1")
        self.assertIn("retrieval", payload)

    def test_specific_postpartum_query_does_not_send_general_bleeding_chunk_to_model(self):
        general_bleeding = Chunk(
            index=1,
            page="32",
            start_line=1,
            end_line=5,
            text="Shock signs include tachycardia and control bleeding.",
        )
        with patch("app.internal_pilot.SEMANTIC_INDEX", None), patch(
            "app.internal_pilot.keyword_retrieve",
            return_value=[(general_bleeding, 0.8)],
        ), patch("app.internal_pilot.call_model", side_effect=AssertionError("must not call model")):
            payload = self.post_question("Theo tài liệu, xử trí chảy máu sau sinh như thế nào?")

        self.assertEqual(payload["sources"], [])
        self.assertIn("Chưa tìm thấy đoạn đủ liên quan", payload["answer"])

    def test_abcde_endpoint_uses_source_list_and_does_not_relabel_stages(self):
        glossary = Chunk(
            index=1,
            page="221",
            start_line=10,
            end_line=14,
            text=(
                "The primary survey consists of the ABCDE: Airway, Breathing, "
                "Circulation, Disability and Exposure."
            ),
        )
        partial_survey = Chunk(
            index=2,
            page="49",
            start_line=10,
            end_line=14,
            text="ABCDE: TRAUMA PRIMARY SURVEY. Airway with cervical spine immobilization. Look for blood.",
        )
        with patch("app.internal_pilot.retrieve", return_value=[(glossary, 1.0), (partial_survey, 0.9)]), patch(
            "app.internal_pilot.call_model", side_effect=AssertionError("source list should answer this query")
        ):
            payload = self.post_question("Tóm tắt các bước đánh giá người bệnh chấn thương.")

        self.assertIn("A – Airway, B – Breathing, C – Circulation, D – Disability và E – Exposure", payload["answer"])
        self.assertIn("các phần B, C, D, E", payload["answer"])
        self.assertNotIn("C: Các dấu hiệu", payload["answer"])
        self.assertEqual([source["id"] for source in payload["sources"]], ["S1", "S2"])
        self.assertIn("chưa đủ", payload["warning"])

    def test_abcde_query_retrieves_the_complete_definition_instead_of_partial_pages(self):
        with patch(
            "app.internal_pilot.call_model",
            side_effect=AssertionError("the explicit source list should answer this query"),
        ):
            payload = self.post_question("Tóm tắt các bước đánh giá người bệnh chấn thương.")

        self.assertEqual(payload["retrieval"]["mode"], "keyword_abcde_definition")
        self.assertEqual(len(payload["sources"]), 1)
        self.assertIn("PDF p. 221", payload["sources"][0]["citation"])
        self.assertIn(
            "A – Airway, B – Breathing, C – Circulation, D – Disability và E – Exposure",
            payload["answer"],
        )
        self.assertIn("chưa mô tả đủ thao tác", payload["answer"])
        self.assertIn("chưa đủ", payload["warning"])


if __name__ == "__main__":
    unittest.main()
