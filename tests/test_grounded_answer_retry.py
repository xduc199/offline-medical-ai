"""Regression tests for citation repair and optional CPU-only Ollama inference."""

import unittest
from unittest.mock import patch

from app.internal_pilot import Chunk, _ollama_options, call_model_uncached


class GroundedAnswerRetryTests(unittest.TestCase):
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
            answer, warning = call_model_uncached("Tài liệu nêu gì về co giật?", [(chunk, 1.0)])

        self.assertIsNone(warning)
        self.assertIn("[S1]", answer)
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
            answer, warning = call_model_uncached("Tài liệu nêu gì về co giật?", [(chunk, 1.0)])

        self.assertIsNone(warning)
        self.assertIn("[S1]", answer)
        self.assertEqual(chat.call_count, 1)


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
