"""Conservative topic-aware filtering for retrieved source passages.

This is a retrieval-quality heuristic, not a clinical relevance or entailment
classifier. If no candidate has a recognized topic anchor, it preserves the
original candidates. When an anchored candidate also matches an explicit
off-topic pattern, the filter can remove it and return no candidates.
"""
from __future__ import annotations

import unicodedata
from typing import Sequence, TypeVar

T = TypeVar("T")


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", (text or "").casefold()).replace("đ", "d")
    return "".join(char for char in text if not unicodedata.combining(char))


# Explicit source-text anchors are used; generic words such as "patient",
# "child", or "management" are not enough to establish topical relevance.
_PROFILES = (
    {
        "query": ("co giat", "seizure", "convulsion"),
        "anchors": ("seizure", "convulsion", "seizing", "postictal", "antiepileptic"),
        "off_topic": (
            "silent chest", "stridor", "salbutamol", "wheeze", "respiratory distress",
            "pediatric exposure conditions", "difficulty maintaining temperature",
            "hypothermic", "hyperthermic", "remove wet clothing", "skin-to-skin",
            "cover infants' heads",
        ),
    },
    {
        "query": ("ran can", "snake bite", "snakebite"),
        "anchors": ("snake bite", "snakebite", "venom", "bite marks"),
        "off_topic": (),
    },
    {
        "query": ("chan thuong", "trauma"),
        "anchors": ("primary survey", "injured person", "injured patients", "trauma care", "trauma-specific", "trauma primary survey"),
        "off_topic": (),
    },
    {
        "query": ("danh gia ban dau", "initial assessment", "abcde"),
        "anchors": ("initial assessment", "primary survey", "abcde", "sample history", "airway conditions"),
        "off_topic": (),
    },
    {
        "query": ("bong", "burn", "burns"),
        "anchors": ("burn", "burns", "escharotomy", "inhalational injury", "circumferential burn"),
        # Some cleaned table chunks merge the burn row with the following
        # general shock/trauma row. Exclude those mixed chunks rather than
        # presenting adjacent bleeding-control or fracture-splinting actions
        # as burn-specific care. A separate burn passage can still be retained.
        "off_topic": (
            "control external bleeding, splint femur/pelvis as indicated",
            "splint femur/pelvis as indicated",
        ),
    },
    {
        "query": ("kho tho", "difficulty breathing", "shortness of breath", "dyspnea", "dyspnoea"),
        "anchors": ("difficulty in breathing", "difficulty breathing", "respiratory distress", "airway", "breathing not adequate", "shortness of breath"),
        "off_topic": ("snake bite", "seizure", "convulsion"),
    },
    {
        "query": ("chay mau", "bleeding", "hemorrhage", "haemorrhage"),
        "anchors": ("bleeding", "hemorrhage", "haemorrhage", "blood loss", "control bleeding"),
        "off_topic": (
            "silent chest", "stridor", "salbutamol",
            "perineal or vaginal tear", "postpartum hemorrhage", "uterine massage",
            "advanced obstetric provider",
        ),
    },
    {
        "query": ("soc", "shock", "poor perfusion"),
        "anchors": ("shock", "perfusion", "hypovolaemic", "hypovolemic", "capillary refill"),
        "off_topic": ("silent chest", "stridor", "salbutamol"),
    },
)

_OBSTETRIC_BLEEDING_QUERY = (
    "sau sinh", "postpartum", "obstetric", "san khoa", "am dao", "vaginal", "pregnancy-related",
)
_OBSTETRIC_BLEEDING_SOURCE = (
    "postpartum hemorrhage", "postpartum haemorrhage", "uterine massage",
    "vaginal bleeding", "perineal or vaginal tear", "obstetric provider",
)
_GENERIC_SEIZURE_MENTIONS = (
    "assess for and manage seizures/convulsions",
    "always check for seizure/convulsions",
)
_SPECIFIC_SEIZURE_EVIDENCE = (
    "goal in managing seizures", "protect the seizing person", "active seizure",
    "benzodiazepine", "pregnant and seizing", "pregnant, or recently gave birth",
    "seizures/convulsions stop", "recovery position",
)


def _has_phrase(text: str, phrases: Sequence[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def filter_topic_candidates(query: str, candidates: Sequence[tuple[T, float]]) -> list[tuple[T, float]]:
    """Filter clear off-topic candidates while preserving order and scores.

    Candidate items are pairs whose first element has a text attribute. If the
    small explicit anchor list cannot recognize any candidate, fail open and
    preserve the original list.
    """
    original = list(candidates)
    if not original:
        return []

    normalized_query = _fold(query)
    profile = next(
        (item for item in _PROFILES if _has_phrase(normalized_query, item["query"])),
        None,
    )
    if profile is None:
        return original

    texts = [_fold(str(getattr(candidate, "text", ""))) for candidate, _ in original]
    is_bleeding_profile = profile["query"] == ("chay mau", "bleeding", "hemorrhage", "haemorrhage")
    if is_bleeding_profile and _has_phrase(normalized_query, _OBSTETRIC_BLEEDING_QUERY):
        # A specific obstetric bleeding question needs an obstetric passage.
        # Generic shock or wound-management text alone cannot support it.
        return [
            item for item, text in zip(original, texts)
            if _has_phrase(text, _OBSTETRIC_BLEEDING_SOURCE)
        ]

    relevant = [_has_phrase(text, profile["anchors"]) for text in texts]
    seizure_profile = profile["query"] == ("co giat", "seizure", "convulsion")
    weak_seizure_mentions = [
        seizure_profile
        and _has_phrase(text, _GENERIC_SEIZURE_MENTIONS)
        and not _has_phrase(text, _SPECIFIC_SEIZURE_EVIDENCE)
        for text in texts
    ]
    if seizure_profile:
        # Generic assessment reminders can occur inside broad pediatric tables.
        # They do not make every adjacent row seizure-treatment evidence.
        relevant = [is_relevant and not weak for is_relevant, weak in zip(relevant, weak_seizure_mentions)]
    if not any(relevant):
        if any(weak_seizure_mentions):
            return []
        return original

    kept: list[tuple[T, float]] = []
    for item, text, is_relevant in zip(original, texts, relevant):
        # Exclude clearly mismatched sections before accepting a topical anchor.
        # A single chunk may contain both a relevant phrase and an unrelated
        # neighboring section (for example, pediatric seizures plus temperature
        # management, or general bleeding plus postpartum hemorrhage).
        if _has_phrase(text, profile["off_topic"]):
            continue
        if is_relevant:
            kept.append(item)
            continue
        navigation_markers = ("glossary", "quick cards", "participant workbook", "refs & quick cards")
        if sum(marker in text for marker in navigation_markers) >= 2:
            continue
        # Precision-first: if another passage has an explicit topical anchor,
        # do not include passages that lack one in the model context.
    # Once at least one candidate has a topical anchor, candidates that were
    # explicitly rejected above must stay rejected. Falling back to the full
    # original list here would reintroduce a mixed burn/shock table when every
    # retrieved candidate happened to contain the same adjacent trauma row.
    return kept
