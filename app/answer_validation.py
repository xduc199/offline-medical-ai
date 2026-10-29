"""Deterministic output-contract checks for source-grounded medical QA.

These checks validate response structure and citation integrity only. They do
not prove that a clinical statement is entailed by the cited passage.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence


_CITATION_RE = re.compile(r"\[(S\d+(?:\s*,\s*S\d+)*)\]")
_CITATION_TOKEN_RE = re.compile(r"\[(S\d+(?:\s*,\s*S\d+)*)\]")


@dataclass(frozen=True)
class AnswerCheck:
    accepted: bool
    answer: str
    warning: str | None
    issues: tuple[str, ...] = ()


def validate_grounded_answer(
    answer: str,
    source_count: int,
    *,
    require_citation: bool = True,
    max_chars: int = 8000,
) -> AnswerCheck:
    """Fail closed on empty, overlong, missing or invalid source citations.

    Only citation IDs [S1]..[SN] are checked. This is deliberately not described
    as factuality or medical-safety verification.
    """
    text = (answer or "").strip()
    if not text:
        return AnswerCheck(
            False,
            "Chưa thể tạo câu trả lời từ các đoạn nguồn hiện có. Hãy mở và đọc trực tiếp tài liệu được hiển thị.",
            "Câu trả lời trống; nội dung do mô hình sinh đã bị ẩn.",
            ("empty_answer",),
        )
    if len(text) > max_chars:
        return AnswerCheck(
            False,
            "Câu trả lời quá dài để kiểm tra trong bản thử nghiệm. Hãy hỏi một câu cụ thể hơn và đối chiếu các đoạn nguồn.",
            "Câu trả lời vượt giới hạn ký tự; nội dung do mô hình sinh đã bị ẩn.",
            ("answer_too_long",),
        )
    if source_count < 1:
        return AnswerCheck(
            False,
            "Không có đoạn nguồn để hỗ trợ câu trả lời. Hệ thống không tạo kết luận y tế khi chưa tìm được bằng chứng phù hợp.",
            "Không có nguồn truy xuất; nội dung do mô hình sinh đã bị ẩn.",
            ("missing_sources",),
        )

    refs = [ref for match in _CITATION_RE.findall(text) for ref in re.findall(r"S\d+", match)]
    if require_citation and not refs:
        return AnswerCheck(
            False,
            "Chưa thể hiển thị câu trả lời vì không có trích dẫn nguồn để đối chiếu. Hãy đọc các đoạn nguồn bên dưới hoặc thử đặt câu hỏi cụ thể hơn.",
            "Câu trả lời không có mã trích dẫn; nội dung do mô hình sinh đã bị ẩn.",
            ("missing_citation",),
        )

    invalid = sorted({
        int(number)
        for match in _CITATION_RE.findall(text)
        for number in re.findall(r"S(\d+)", match)
        if int(number) < 1 or int(number) > source_count
    })
    if invalid:
        return AnswerCheck(
            False,
            "Chưa thể hiển thị câu trả lời vì mã trích dẫn không khớp với các nguồn được cung cấp. Hãy đọc các đoạn nguồn bên dưới.",
            "Mô hình tạo mã trích dẫn không tồn tại; nội dung do mô hình sinh đã bị ẩn.",
            ("invalid_citation",),
        )

    # Ensure every factual-looking list item has at least one citation. This is
    # a structural heuristic, not semantic entailment checking.
    uncited_bullets = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line) and not _CITATION_TOKEN_RE.search(line):
            uncited_bullets.append(line_number)
    if uncited_bullets:
        return AnswerCheck(
            False,
            "Chưa thể hiển thị câu trả lời vì có gạch đầu dòng chưa gắn nguồn để đối chiếu. Hãy đọc trực tiếp các đoạn nguồn.",
            "Một hoặc nhiều mục liệt kê thiếu mã trích dẫn; nội dung do mô hình sinh đã bị ẩn.",
            ("uncited_bullet",),
        )
    return AnswerCheck(True, text, None)


def citations_are_in_range(answer: str, source_ids: Sequence[str]) -> bool:
    """Small helper for callers/tests that use explicit source labels."""
    allowed = set(source_ids)
    seen = set(_CITATION_TOKEN_RE.findall(answer or ""))
    return bool(seen) and seen.issubset(allowed)
