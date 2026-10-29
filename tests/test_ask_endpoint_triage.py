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

    def test_emergency_warning_short_circuits_retrieval(self):
        with patch("app.internal_pilot.retrieve", side_effect=AssertionError("retrieval should not run")):
            payload = self.post_question("Người nhà tôi đang khó thở")
        self.assertEqual(payload["classification"], "possible_emergency")
        self.assertEqual(payload["sources"], [])
        self.assertIn("đừng chờ câu trả lời", payload["answer"])

    def test_personal_medication_question_short_circuits_model(self):
        with patch("app.internal_pilot.retrieve", side_effect=AssertionError("retrieval should not run")):
            payload = self.post_question("Tôi có nên uống thêm thuốc không?")
        self.assertEqual(payload["classification"], "personal_medical_advice")
        self.assertEqual(payload["sources"], [])

    def test_greeting_does_not_call_retrieval(self):
        with patch("app.internal_pilot.retrieve", side_effect=AssertionError("retrieval should not run")):
            payload = self.post_question("Xin chào")
        self.assertEqual(payload["classification"], "greeting")
        self.assertEqual(payload["sources"], [])


if __name__ == "__main__":
    unittest.main()
