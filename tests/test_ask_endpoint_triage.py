"""Integration tests for the local /api/ask request-triage gate."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from unittest.mock import patch

from app.internal_pilot import Handler


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
        request = Request(
            self.base_url + "/api/ask",
            data=json.dumps({"question": question}, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

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


if __name__ == "__main__":
    unittest.main()
