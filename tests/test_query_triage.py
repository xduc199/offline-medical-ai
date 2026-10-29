import unittest

from app.query_triage import QueryClass, classify_query


class QueryTriageTests(unittest.TestCase):
    def test_possible_emergency_is_flagged(self):
        result = classify_query("Người nhà tôi đang khó thở")
        self.assertEqual(result.classification, QueryClass.POSSIBLE_EMERGENCY)
        self.assertIn("đừng chờ câu trả lời", result.message)

    def test_personal_medication_question_is_not_answered(self):
        result = classify_query("Tôi có nên uống thêm thuốc không?")
        self.assertEqual(result.classification, QueryClass.PERSONAL_MEDICAL_ADVICE)

    def test_in_scope_first_aid_question(self):
        result = classify_query("Tài liệu nêu các bước sơ cứu rắn cắn nào?")
        self.assertEqual(result.classification, QueryClass.DOCUMENT_LOOKUP)

    def test_general_health_topic_is_not_assumed_supported(self):
        result = classify_query("Giải thích bệnh tiểu đường")
        self.assertEqual(result.classification, QueryClass.OUT_OF_SCOPE)

    def test_greeting(self):
        result = classify_query("Xin chào")
        self.assertEqual(result.classification, QueryClass.GREETING)

    def test_empty_query_is_ambiguous(self):
        result = classify_query("   ")
        self.assertEqual(result.classification, QueryClass.AMBIGUOUS)

    def test_emergency_phrase_without_accents(self):
        result = classify_query("Toi bi dau nguc")
        self.assertEqual(result.classification, QueryClass.POSSIBLE_EMERGENCY)


if __name__ == "__main__":
    unittest.main()
