import unittest
from types import SimpleNamespace

from app.internal_pilot import CHUNKS
from app.topic_relevance import filter_topic_candidates


def candidate(text, score=1.0):
    return SimpleNamespace(text=text), score


class TopicRelevanceTests(unittest.TestCase):
    def test_actual_pediatric_seizure_mention_does_not_promote_mixed_chunk(self):
        query = "Tổng hợp cách xử trí co giật ở người lớn và trẻ em theo tài liệu."
        generic_pediatric_table = next(
            chunk for chunk in CHUNKS
            if chunk.page == "76" and "Assess for and manage seizures/convulsions" in chunk.text
        )
        dedicated_seizure_passage = next(
            chunk for chunk in CHUNKS
            if chunk.page == "33" and "The goal in managing seizures/convulsions" in chunk.text
        )
        seizure_management_passage = next(
            chunk for chunk in CHUNKS
            if chunk.page == "142" and "benzodiazepine" in chunk.text.lower() and "seizure" in chunk.text.lower()
        )

        filtered = filter_topic_candidates(
            query,
            [
                (generic_pediatric_table, 0.9),
                (dedicated_seizure_passage, 0.8),
                (seizure_management_passage, 0.7),
            ],
        )

        self.assertEqual(
            [chunk.index for chunk, _ in filtered],
            [dedicated_seizure_passage.index, seizure_management_passage.index],
        )
        self.assertEqual(filter_topic_candidates(query, [(generic_pediatric_table, 0.9)]), [])

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

    def test_specific_postpartum_bleeding_keeps_only_obstetric_evidence(self):
        general_bleeding = candidate("Shock signs include tachycardia and control bleeding.")
        postpartum = candidate(
            "Postpartum hemorrhage: visually check for a perineal or vaginal tear. "
            "Uterine massage for postpartum haemorrhage."
        )

        result = filter_topic_candidates(
            "Theo tài liệu, xử trí chảy máu sau sinh như thế nào?",
            [general_bleeding, postpartum],
        )

        self.assertEqual(result, [postpartum])

    def test_specific_postpartum_bleeding_without_obstetric_source_fails_closed(self):
        general_bleeding = candidate("Shock signs include tachycardia and control bleeding.")

        result = filter_topic_candidates(
            "Theo tài liệu, xử trí chảy máu sau sinh như thế nào?",
            [general_bleeding],
        )

        self.assertEqual(result, [])


    def test_burn_question_drops_mixed_chunk_with_adjacent_shock_trauma_actions(self):
        inhalational_burn = candidate(
            "Inhalational injuries due to burns can cause swelling of the airway."
        )
        mixed_burn_trauma_table = candidate(
            "Large burns of chest or abdomen: give IV fluids per burn size and oxygen. "
            "Signs of shock: give oxygen, IV fluids, control external bleeding, "
            "splint femur/pelvis as indicated."
        )

        result = filter_topic_candidates(
            "Tóm tắt các nội dung chính về bỏng trong tài liệu",
            [inhalational_burn, mixed_burn_trauma_table],
        )

        self.assertEqual(result, [inhalational_burn])

    def test_burn_question_drops_mixed_table_when_it_is_the_only_candidate(self):
        mixed_burn_shock_table = candidate(
            "Large burns of chest or abdomen: give IV fluids per burn size and oxygen. "
            "Signs of shock: give oxygen, IV fluids, control external bleeding, "
            "splint femur/pelvis as indicated."
        )

        result = filter_topic_candidates(
            "Tóm tắt các nội dung chính về bỏng trong tài liệu",
            [mixed_burn_shock_table],
        )

        self.assertEqual(result, [])

    def test_actual_cleaned_burn_shock_chunks_are_excluded_for_burn_query(self):
        mixed_chunks = [
            ((chunk, 1.0), chunk.page)
            for chunk in CHUNKS
            if "splint femur/pelvis as indicated" in chunk.text
        ]

        self.assertTrue(mixed_chunks, "expected the cleaned source to contain the mixed table rows")
        self.assertEqual({page for _, page in mixed_chunks}, {"226", "227"})
        self.assertEqual(
            filter_topic_candidates(
                "Summarize burn management",
                [candidate_pair for candidate_pair, _ in mixed_chunks],
            ),
            [],
        )

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
