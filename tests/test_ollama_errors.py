"""Regression tests for local Ollama error handling in the internal pilot."""

import io
import json
import unittest
import urllib.error
from unittest.mock import patch

from app.internal_pilot import ollama_chat


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def _http_error(code: int, body: str) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        "http://127.0.0.1:11434/api/chat",
        code,
        "Internal Server Error",
        hdrs=None,
        fp=io.BytesIO(body.encode("utf-8")),
    )


class OllamaChatErrorTests(unittest.TestCase):
    def test_retries_transient_http_500_once(self):
        success = _FakeResponse({"message": {"content": "Đã tạo câu trả lời."}})
        with patch(
            "app.internal_pilot.urllib.request.urlopen",
            side_effect=[_http_error(500, "temporary runner error"), success],
        ) as urlopen, patch("app.internal_pilot.time.sleep"):
            result = ollama_chat("system", "user")

        self.assertEqual(result, "Đã tạo câu trả lời.")
        self.assertEqual(urlopen.call_count, 2)

    def test_persistent_http_500_includes_server_diagnostic(self):
        with patch(
            "app.internal_pilot.urllib.request.urlopen",
            side_effect=[
                _http_error(500, "runner process exited"),
                _http_error(500, "model load failed: out of memory"),
            ],
        ), patch("app.internal_pilot.time.sleep"):
            with self.assertRaisesRegex(RuntimeError, "model load failed: out of memory"):
                ollama_chat("system", "user")

    def test_empty_model_content_is_reported(self):
        with patch(
            "app.internal_pilot.urllib.request.urlopen",
            return_value=_FakeResponse({"message": {"content": ""}}),
        ):
            with self.assertRaisesRegex(RuntimeError, "message.content rỗng"):
                ollama_chat("system", "user")


if __name__ == "__main__":
    unittest.main()
