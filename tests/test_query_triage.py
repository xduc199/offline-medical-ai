import unittest

from app.query_triage import QueryClass, classify_query


class QueryTriageTests(unittest.TestCase):
    def test_possible_emergency_is_flagged(self):
        result = classify_query("Người nhà tôi đang khó thở")
        self.assertEqual(result.classification, QueryClass.POSSIBLE_EMERGENCY)
        self.assertIn("đừng chờ câu trả lời", result.message)

    def test_emergency_phrase_without_accents(self):
        result = classify_query("Toi bi dau nguc")
        self.assertEqual(result.classification, QueryClass.POSSIBLE_EMERGENCY)

    def test_personal_medication_question_is_not_answered(self):
        result = classify_query("Tôi có nên uống thêm thuốc không?")
        self.assertEqual(result.classification, QueryClass.PERSONAL_MEDICAL_ADVICE)

    def test_personal_symptom_question_is_not_treated_as_document_lookup(self):
        result = classify_query("Tôi đang bị đau bụng")
        self.assertEqual(result.classification, QueryClass.PERSONAL_MEDICAL_ADVICE)

    def test_family_member_symptom_is_personal_advice(self):
        result = classify_query("Con tôi đang bị sốt cao")
        self.assertEqual(result.classification, QueryClass.PERSONAL_MEDICAL_ADVICE)

    def test_in_scope_first_aid_question(self):
        result = classify_query("Tài liệu nêu các bước sơ cứu rắn cắn nào?")
        self.assertEqual(result.classification, QueryClass.DOCUMENT_LOOKUP)

    def test_document_question_about_difficulty_breathing_is_not_emergency_report(self):
        result = classify_query("Theo tài liệu, tổng quan về xử trí khó thở là gì?")
        self.assertEqual(result.classification, QueryClass.DOCUMENT_LOOKUP)

    def test_document_question_about_seizures_is_not_emergency_report(self):
        result = classify_query("Tổng hợp cách xử trí co giật ở người lớn và trẻ em theo tài liệu.")
        self.assertEqual(result.classification, QueryClass.DOCUMENT_LOOKUP)

    def test_document_wording_does_not_override_personal_emergency(self):
        result = classify_query("Theo tài liệu, người nhà tôi đang khó thở")
        self.assertEqual(result.classification, QueryClass.POSSIBLE_EMERGENCY)

    def test_general_health_topic_is_not_assumed_supported(self):
        result = classify_query("Giải thích bệnh tiểu đường")
        self.assertEqual(result.classification, QueryClass.OUT_OF_SCOPE)

    def test_greeting(self):
        result = classify_query("Xin chào")
        self.assertEqual(result.classification, QueryClass.GREETING)

    def test_empty_query_is_ambiguous(self):
        result = classify_query("   ")
        self.assertEqual(result.classification, QueryClass.AMBIGUOUS)


if __name__ == "__main__":
    unittest.main()
