import unittest
from types import SimpleNamespace

from app.topic_relevance import filter_topic_candidates


def candidate(text, score=1.0):
    return SimpleNamespace(text=text), score


class TopicRelevanceTests(unittest.TestCase):
    def test_seizure_question_drops_unrelated_pediatric_breathing_passage(self):
        seizure = candidate(
            "The goal in managing seizures is to prevent hypoxia and injury. "
            "Protect the seizing person from falls."
        )
        breathing = candidate(
            "A SILENT CHEST is a sign of severe respiratory distress in a child. "
            "Give salbutamol and oxygen."
        )

        result = filter_topic_candidates(
            "Tổng hợp cách xử trí co giật ở người lớn và trẻ em",
            [seizure, breathing],
        )

        self.assertEqual(result, [seizure])

    def test_trauma_question_drops_navigation_or_glossary_chunk(self):
        glossary = candidate(
            "SKILLS AMS SHOCK BREATHING TRAUMA INTRO ABCDE GLOSSARY "
            "REFS & QUICK CARDS PARTICIPANT WORKBOOK"
        )
        primary_survey = candidate(
            "ABCDE: TRAUMA PRIMARY SURVEY. This trauma-specific approach "
            "includes initial assessment and management for injured patients."
        )

        result = filter_topic_candidates(
            "Tóm tắt các bước đánh giá người bệnh chấn thương",
            [glossary, primary_survey],
        )

        self.assertEqual(result, [primary_survey])

    def test_bleeding_question_drops_unrelated_respiratory_passage(self):
        bleeding = candidate(
            "External bleeding and internal bleeding can cause rapid blood loss."
        )
        respiratory = candidate(
            "STRIDOR signals severe airway compromise in children."
        )

        result = filter_topic_candidates(
            "Theo tài liệu, cần đánh giá và xử trí người bệnh bị chảy máu như thế nào?",
            [bleeding, respiratory],
        )

        self.assertEqual(result, [bleeding])

    def test_seizure_question_drops_mixed_chunk_with_unrelated_pediatric_exposure_section(self):
        seizure = candidate(
            "The goal in managing seizures is to prevent hypoxia and injury."
        )
        mixed_pediatric = candidate(
            "Pediatric disability conditions: Always check for seizure/convulsions. "
            "Pediatric exposure conditions: children can quickly become hypothermic. "
            "Remove wet clothing and place infants skin-to-skin."
        )

        result = filter_topic_candidates(
            "Tổng hợp cách xử trí co giật ở người lớn và trẻ em",
            [seizure, mixed_pediatric],
        )

        self.assertEqual(result, [seizure])

    def test_bleeding_question_drops_obstetric_specific_chunk_for_general_prompt(self):
        general_bleeding = candidate(
            "Shock signs include tachycardia and control bleeding."
        )
        obstetric = candidate(
            "Visually check for a perineal or vaginal tear. "
            "Uterine massage for postpartum hemorrhage."
        )

        result = filter_topic_candidates(
            "Theo tài liệu, cần đánh giá và xử trí người bệnh bị chảy máu như thế nào?",
            [general_bleeding, obstetric],
        )

        self.assertEqual(result, [general_bleeding])

    def test_preserves_candidates_when_no_explicit_anchor_is_recognized(self):
        first = candidate("A passage with unfamiliar wording.", 0.8)
        second = candidate("Another passage with unfamiliar wording.", 0.7)

        result = filter_topic_candidates("Tổng hợp cách xử trí co giật", [first, second])

        self.assertEqual(result, [first, second])

    def test_unrecognized_query_is_unchanged(self):
        first = candidate("A source passage about an unrelated topic.", 0.8)
        second = candidate("Another passage.", 0.7)

        result = filter_topic_candidates("Câu hỏi không thuộc hồ sơ chủ đề", [first, second])

        self.assertEqual(result, [first, second])


if __name__ == "__main__":
    unittest.main()
