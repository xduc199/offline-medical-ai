"""Conservative topic-aware filtering for retrieved source passages.

This is a retrieval-quality heuristic, not a clinical relevance or entailment
classifier. If no candidate clearly matches the detected topic, it preserves the
original candidates rather than hiding all evidence.
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
        "off_topic": ("silent chest", "stridor", "salbutamol", "wheeze", "respiratory distress"),
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
        "off_topic": (),
    },
    {
        "query": ("kho tho", "difficulty breathing", "shortness of breath", "dyspnea", "dyspnoea"),
        "anchors": ("difficulty in breathing", "difficulty breathing", "respiratory distress", "airway", "breathing not adequate", "shortness of breath"),
        "off_topic": ("snake bite", "seizure", "convulsion"),
    },
    {
        "query": ("chay mau", "bleeding", "hemorrhage", "haemorrhage"),
        "anchors": ("bleeding", "hemorrhage", "haemorrhage", "blood loss", "control bleeding"),
        "off_topic": ("silent chest", "stridor", "salbutamol"),
    },
    {
        "query": ("soc", "shock", "poor perfusion"),
        "anchors": ("shock", "perfusion", "hypovolaemic", "hypovolemic", "capillary refill"),
        "off_topic": ("silent chest", "stridor", "salbutamol"),
    },
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
    relevant = [_has_phrase(text, profile["anchors"]) for text in texts]
    if not any(relevant):
        return original

    kept: list[tuple[T, float]] = []
    for item, text, is_relevant in zip(original, texts, relevant):
        if is_relevant:
            kept.append(item)
            continue
        if _has_phrase(text, profile["off_topic"]):
            continue
        navigation_markers = ("glossary", "quick cards", "participant workbook", "refs & quick cards")
        if sum(marker in text for marker in navigation_markers) >= 2:
            continue
        # Precision-first: if another passage has an explicit topical anchor,
        # do not include passages that lack one in the model context.
    return kept or original
