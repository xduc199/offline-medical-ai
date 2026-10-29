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
_PARENTHETICAL_CITATION_RE = re.compile(r"\(\s*S\d+(?:\s*,\s*S\d+)*\s*\)")
_LIST_ITEM_RE = re.compile(r"^(?P<indent>[ \t]*)(?:[-+*]|\d+[.)]|[A-Za-z][.)])\s+(?P<body>.*)$")
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}(?:\s|$)")
_CONTAINER_PREDICATE_RE = re.compile(
    r"\b(?:is|are|was|were|includes?|contains?|consists? of|means?|"
    r"la|la\s+la|gom|bao gom|co|neu|liet ke|trinh bay)\b",
    flags=re.IGNORECASE,
)
_NONCLAIM_INTRO_RE = re.compile(
    r"^(?:summary|tom tat|cac (?:noi dung|y|diem) chinh(?: ve [^:]+)? trong tai lieu bao gom|"
    r"d[u\u01b0]oi day la(?: phan)?(?: tom tat| cac (?:y(?: chinh)?|buoc|muc|thanh phan))?|"
    r"sau day la(?: phan)?(?: tom tat| cac (?:y(?: chinh)?|buoc|muc|thanh phan))?|"
    r"here (?:is|are) (?:a )?(?:summary|brief answer|main points?|steps?)|"
    r"the following (?:is|are) (?:a )?(?:summary|answer|points?|steps?))\s*[.!:]?$",
    flags=re.IGNORECASE,
)
_ABCDE_COMPONENTS = (
    ("A", "airway"),
    ("B", "breathing"),
    ("C", "circulation"),
    ("D", "disability"),
    ("E", "exposure"),
)


def _fold(text: str) -> str:
    import unicodedata

    normalized = unicodedata.normalize("NFKD", (text or "").casefold()).replace("đ", "d")
    return "".join(char for char in normalized if not unicodedata.combining(char))


def asks_for_abcde_steps(question: str) -> bool:
    """Recognize an explicit request for the complete ABCDE assessment list."""
    query = _fold(question)
    asks_steps = bool(re.search(r"\b(buoc|steps?|step|survey)\b", query))
    asks_assessment = any(
        phrase in query
        for phrase in ("danh gia ban dau", "danh gia", "initial assessment", "primary survey")
    )
    is_trauma_or_emergency = any(
        phrase in query for phrase in ("chan thuong", "trauma", "cap cuu", "abcde")
    )
    return "abcde" in query or (asks_steps and asks_assessment and is_trauma_or_emergency)


def abcde_source_coverage(question: str, source_texts: Sequence[str]) -> bool | None:
    """Return whether the retrieved text contains all five ABCDE stage names.

    ``None`` means the query or passages do not identify this assessment, so
    callers should leave the existing answer path unchanged.
    """
    if not asks_for_abcde_steps(question):
        return None
    text = _fold("\n".join(source_texts))
    if "abcde" not in text and "primary survey" not in text:
        return None
    return all(name in text for _, name in _ABCDE_COMPONENTS)


def missing_abcde_answer_stages(question: str, answer: str) -> tuple[str, ...]:
    """Find missing stage labels in an answer to an explicit ABCDE-list query.

    The prompt asks for one ``A:`` through ``E:`` line per stage, which makes
    this check narrow and deterministic instead of treating topic word overlap
    as proof of completeness.
    """
    if not asks_for_abcde_steps(question):
        return ()
    labels: list[str] = []
    for line in (answer or "").splitlines():
        match = re.match(
            r"\s*(?:[-*•]\s*)?(?:\*\*)?([ABCDE])(?:\*\*)?\s*[:.)–—-]\s+",
            line,
            flags=re.IGNORECASE,
        )
        if match:
            labels.append(match.group(1).upper())
    present = set(labels)
    return tuple(letter for letter, _ in _ABCDE_COMPONENTS if letter not in present)


@dataclass(frozen=True)
class AnswerCheck:
    accepted: bool
    answer: str
    warning: str | None
    issues: tuple[str, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class _ClaimUnit:
    kind: str
    start_line: int
    text: str
    has_children: bool = False


def _visible_markdown_lines(text: str) -> list[tuple[int, str]]:
    """Return answer lines outside Markdown headings and fenced code blocks."""
    visible: list[tuple[int, str]] = []
    fence: str | None = None
    for line_number, line in enumerate((text or "").splitlines(), start=1):
        fence_match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence_match:
            marker = fence_match.group(1)[0]
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            continue
        if fence is not None or _HEADING_RE.match(line):
            continue
        visible.append((line_number, re.sub(r"`[^`]*`", "", line)))
    return visible


def _claim_units(lines: Sequence[tuple[int, str]]) -> list[_ClaimUnit]:
    """Split prose and Markdown list items into independently checked units."""
    units: list[_ClaimUnit] = []
    paragraph: list[tuple[int, str]] = []
    items: list[dict[str, object]] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        text = " ".join(line.strip() for _, line in paragraph if line.strip()).strip()
        if text:
            units.append(_ClaimUnit("paragraph", paragraph[0][0], text))
        paragraph = []

    def flush_item() -> None:
        item = items.pop()
        text = " ".join(str(line).strip() for line in item["lines"] if str(line).strip()).strip()
        if text:
            units.append(_ClaimUnit("bullet", int(item["start_line"]), text, bool(item["has_children"])))

    def flush_items() -> None:
        while items:
            flush_item()

    for line_number, line in lines:
        if not line.strip():
            flush_paragraph()
            continue

        match = _LIST_ITEM_RE.match(line)
        if match:
            flush_paragraph()
            indent = len(match.group("indent").expandtabs(4))
            while items and indent <= int(items[-1]["indent"]):
                flush_item()
            if items:
                items[-1]["has_children"] = True
            items.append({
                "indent": indent,
                "start_line": line_number,
                "lines": [match.group("body")],
                "has_children": False,
            })
            continue

        if items:
            indentation = len(line) - len(line.lstrip(" \t"))
            if indentation > int(items[-1]["indent"]):
                items[-1]["lines"].append(line.strip())
                continue
            flush_items()
        paragraph.append((line_number, line))

    flush_paragraph()
    flush_items()
    return units


def _is_label_only(unit: _ClaimUnit) -> bool:
    text = unit.text.strip()
    if _NONCLAIM_INTRO_RE.match(_fold(text)):
        return True
    if not text.endswith(":"):
        return False
    if _CONTAINER_PREDICATE_RE.search(_fold(text[:-1])):
        return False
    return True


def _sentence_units(unit: _ClaimUnit) -> list[_ClaimUnit]:
    """Keep a trailing citation with its sentence and isolate later claims."""
    text = unit.text
    segments: list[str] = []
    start = 0
    index = 0
    while index < len(text):
        if text[index] not in ".!?" or index + 1 >= len(text) or not text[index + 1].isspace():
            index += 1
            continue
        end = index + 1
        next_part = end
        while next_part < len(text) and text[next_part].isspace():
            next_part += 1
        # A source marker placed after sentence punctuation belongs to the
        # sentence before it, as in "The source states X. [S1]".
        while True:
            citation = _CITATION_TOKEN_RE.match(text, next_part)
            if citation is None:
                break
            next_part = citation.end()
            while next_part < len(text) and text[next_part].isspace():
                next_part += 1
        if next_part < len(text):
            segment = text[start:next_part].strip()
            if segment:
                segments.append(segment)
            start = next_part
            index = next_part
        else:
            index = len(text)
    tail = text[start:].strip()
    if tail:
        segments.append(tail)
    return [
        _ClaimUnit(unit.kind, unit.start_line, segment, unit.has_children)
        for segment in segments
    ]


def _citation_misplaced(text: str) -> bool:
    matches = list(_CITATION_TOKEN_RE.finditer(text))
    if not matches:
        return False
    # A citation must follow the claim it labels. A source marker at the start,
    # or substantive prose after the last marker, cannot validate the unit.
    if not text[:matches[0].start()].strip():
        return True
    trailing = text[matches[-1].end():]
    trailing = re.sub(r"[\s.,;:!?…*)\]}*_`~>-]*$", "", trailing)
    return bool(trailing.strip())


def validate_grounded_answer(
    answer: str,
    source_count: int,
    *,
    require_citation: bool = True,
    max_chars: int = 8000,
    allowed_source_ids: Sequence[str] | None = None,
) -> AnswerCheck:
    """Fail closed on empty, overlong, missing or invalid source citations.

    Citation IDs are checked against the supplied IDs, or [S1]..[SN] when none
    are supplied. This is deliberately not described as factuality or
    medical-safety verification.
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

    visible_lines = _visible_markdown_lines(text)
    citation_text = "\n".join(line for _, line in visible_lines)
    refs = [ref for match in _CITATION_RE.findall(citation_text) for ref in re.findall(r"S\d+", match)]
    units = _claim_units(visible_lines)

    malformed = [
        (line_number, match.group(0))
        for line_number, line in visible_lines
        for match in _PARENTHETICAL_CITATION_RE.finditer(line)
    ]
    if malformed:
        details = tuple(
            f"Dòng {line_number}: {marker} không đúng cú pháp; dùng [S1] hoặc [S1, S2], không dùng ngoặc tròn."
            for line_number, marker in malformed
        )
        return AnswerCheck(
            False,
            "Chưa thể hiển thị câu trả lời vì cú pháp mã trích dẫn không hợp lệ. Hãy đọc các đoạn nguồn bên dưới.",
            "Mã nguồn đặt trong ngoặc tròn; cú pháp bắt buộc dùng ngoặc vuông, nội dung do mô hình sinh đã bị ẩn.",
            ("invalid_citation_format",),
            details,
        )

    allowed = set(allowed_source_ids) if allowed_source_ids is not None else {
        f"S{number}" for number in range(1, source_count + 1)
    }
    invalid = sorted({
        token
        for match in _CITATION_RE.findall(citation_text)
        for token in re.findall(r"S\d+", match)
        if token not in allowed
    })
    if invalid:
        return AnswerCheck(
            False,
            "Chưa thể hiển thị câu trả lời vì mã trích dẫn không khớp với các nguồn được cung cấp. Hãy đọc các đoạn nguồn bên dưới.",
            "Mô hình tạo mã trích dẫn không tồn tại; nội dung do mô hình sinh đã bị ẩn.",
            ("invalid_citation",),
            tuple(f"Mã [{source_id}] không nằm trong tập nguồn được truy xuất." for source_id in invalid),
        )

    sentence_units = [sentence for unit in units for sentence in _sentence_units(unit)]
    if require_citation and not refs:
        missing_units = [unit for unit in sentence_units if not _is_label_only(unit)]
        details = tuple(
            f"{'Mục liệt kê' if unit.kind == 'bullet' else 'Đoạn văn'} ở dòng {unit.start_line} chưa có mã trích dẫn."
            for unit in missing_units
        ) or ("Không tìm thấy mã nguồn dạng [S1] trong phần nội dung câu trả lời.",)
        return AnswerCheck(
            False,
            "Chưa thể hiển thị câu trả lời vì không có trích dẫn nguồn để đối chiếu. Hãy đọc các đoạn nguồn bên dưới hoặc thử đặt câu hỏi cụ thể hơn.",
            "Câu trả lời không có mã trích dẫn hợp lệ; nội dung do mô hình sinh đã bị ẩn.",
            ("missing_citation",),
            details,
        )

    misplaced = [
        unit for unit in sentence_units
        if _citation_misplaced(unit.text)
        and not _is_label_only(unit)
    ]
    uncited_bullets = [
        unit for unit in sentence_units
        if unit.kind == "bullet"
        and not _CITATION_TOKEN_RE.search(unit.text)
        and not _is_label_only(unit)
    ]
    if uncited_bullets:
        return AnswerCheck(
            False,
            "Chưa thể hiển thị câu trả lời vì có gạch đầu dòng nêu ý chưa gắn nguồn để đối chiếu. Hãy đọc trực tiếp các đoạn nguồn.",
            "Một hoặc nhiều mục liệt kê thiếu mã trích dẫn; nội dung do mô hình sinh đã bị ẩn.",
            ("uncited_bullet",),
            tuple(f"Mục liệt kê ở dòng {unit.start_line} chưa có mã trích dẫn." for unit in uncited_bullets),
        )

    uncited_paragraphs = [
        unit for unit in sentence_units
        if unit.kind == "paragraph"
        and not _CITATION_TOKEN_RE.search(unit.text)
        and not _is_label_only(unit)
        and not _NONCLAIM_INTRO_RE.match(_fold(unit.text))
    ]
    structural_issues: list[str] = []
    structural_details: list[str] = []
    warnings: list[str] = []
    if misplaced:
        structural_issues.append("citation_misplaced")
        structural_details.extend(
            f"Dòng {unit.start_line}: đặt mã nguồn sau nội dung mà mã đó hỗ trợ."
            for unit in misplaced
        )
        warnings.append("Một hoặc nhiều mã trích dẫn không nằm ở cuối ý tương ứng.")
    if uncited_bullets:
        structural_issues.append("uncited_bullet")
        structural_details.extend(
            f"Mục liệt kê ở dòng {unit.start_line} chưa có mã trích dẫn."
            for unit in uncited_bullets
        )
        warnings.append("Một hoặc nhiều mục liệt kê thiếu mã trích dẫn.")
    if uncited_paragraphs:
        structural_issues.append("uncited_claim")
        structural_details.extend(
            f"Đoạn văn ở dòng {unit.start_line} chưa có mã trích dẫn."
            for unit in uncited_paragraphs
        )
        warnings.append("Một hoặc nhiều đoạn văn có ý thực tế nhưng thiếu mã trích dẫn.")
    if structural_issues:
        return AnswerCheck(
            False,
            "Chưa thể hiển thị câu trả lời vì có ý chưa được gắn trích dẫn đúng cách. Hãy đọc trực tiếp các đoạn nguồn.",
            " ".join(warnings) + " Nội dung do mô hình sinh đã bị ẩn.",
            tuple(structural_issues),
            tuple(structural_details),
        )
    return AnswerCheck(True, text, None, (), ())


def citations_are_in_range(answer: str, source_ids: Sequence[str]) -> bool:
    """Small helper for callers/tests that use explicit source labels."""
    allowed = set(source_ids)
    seen = {
        token
        for match in _CITATION_RE.findall(answer or "")
        for token in re.findall(r"S\d+", match)
    }
    return bool(seen) and seen.issubset(allowed)
