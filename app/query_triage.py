"""Conservative query triage for the offline medical-document pilot.

This module deliberately does not diagnose, determine clinical urgency, or recommend
patient-specific treatment. It provides a transparent keyword gate for the document
lookup prototype; its output must not be treated as a clinical classifier.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum


class QueryClass(str, Enum):
    GREETING = "greeting"
    DOCUMENT_LOOKUP = "document_lookup"
    OUT_OF_SCOPE = "out_of_scope"
    POSSIBLE_EMERGENCY = "possible_emergency"
    PERSONAL_MEDICAL_ADVICE = "personal_medical_advice"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True)
class TriageResult:
    classification: QueryClass
    message: str
    matched_terms: tuple[str, ...] = ()


def _fold(text: str) -> str:
    value = unicodedata.normalize("NFKD", text.casefold()).replace("đ", "d")
    return "".join(ch for ch in value if not unicodedata.combining(ch))


# These are conservative lexical triggers, not a validated medical model.
_EMERGENCY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (label, re.compile(pattern))
    for label, pattern in [
        ("khó thở", r"\b(kho tho|khong tho duoc|ngat tho|ngung tho)\b"),
        ("đau ngực", r"\b(dau nguc|tuc nguc)\b"),
        ("mất ý thức", r"\b(hon me|bat tinh|mat y thuc|khong tinh)\b"),
        ("co giật", r"\b(co giat|len con kinh)\b"),
        ("chảy máu nhiều", r"\b(chay mau (nhieu|khong cam)|mat mau nhieu)\b"),
        ("dấu hiệu đột quỵ", r"\b(meo mieng|yeu liet (mot ben|nua nguoi)|noi kho|dot quy)\b"),
        ("ngộ độc/nguy cơ tự hại", r"\b(uong nham (thuoc|hoa chat)|qua lieu|tu tu|tu lam hai)\b"),
        ("phản ứng dị ứng nặng", r"\b(soc phan ve|phan ve|sung luoi kem kho tho)\b"),
    ]
)

_PERSONAL_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern)
    for pattern in [
        r"\btoi (nen|co nen|phai) (uong|dung|ngung|tang|giam)\b",
        r"\b(con toi|be nha toi|me toi|bo toi|vo toi|chong toi) (bi|dang)\b",
        r"\btoi (bi|dang bi|mac) (dau|sot|ho|non|buon non|tieu chay|dau bung|kho tho)\b",
        r"\blieu (thuoc|dung) (bao nhieu|cho)\b",
        r"\bco nen (uong|dung|ket hop) thuoc\b",
        r"\bket qua xet nghiem cua toi\b",
    ]
)

_MEDICAL_TERMS = {
    "so cuu", "cap cuu", "soc", "ha duong huyet", "ran can", "bong",
    "chay mau", "chan thuong", "kho tho", "dau nguc", "co giat",
    "danh gia ban dau", "benh nhan", "nguoi benh", "tinh trang",
}
_HEALTH_TERMS = {
    "benh", "trieu chung", "thuoc", "xet nghiem", "dinh duong",
    "huyet ap", "duong huyet", "sot", "dau dau", "ho", "ung thu",
    "tim mach", "tieu duong", "thai ky", "tre em", "vaccine",
}


def classify_query(question: str) -> TriageResult:
    """Classify the *request shape* with conservative, explainable lexical rules.

    A possible-emergency result is a precautionary prompt only. It neither
    establishes nor excludes an emergency. No match must never reassure users.
    """
    normalized = _fold(question).strip()
    if not normalized:
        return TriageResult(QueryClass.AMBIGUOUS, "Vui lòng nhập câu hỏi.")

    emergency_matches = tuple(
        label for label, pattern in _EMERGENCY_PATTERNS if pattern.search(normalized)
    )
    if emergency_matches:
        return TriageResult(
            QueryClass.POSSIBLE_EMERGENCY,
            "Câu hỏi có thể mô tả tình huống nguy hiểm. Nếu đây là tình huống đang xảy ra, "
            "hãy liên hệ dịch vụ cấp cứu hoặc cơ sở y tế tại địa phương ngay; đừng chờ câu trả lời "
            "của phần mềm. Bản thử nghiệm này không thể đánh giá tình trạng người bệnh. "
            "Các dấu hiệu từ khóa được phát hiện không phải là chẩn đoán.",
            emergency_matches,
        )

    if any(pattern.search(normalized) for pattern in _PERSONAL_PATTERNS):
        return TriageResult(
            QueryClass.PERSONAL_MEDICAL_ADVICE,
            "Ứng dụng hiện chỉ tra cứu tài liệu nguồn, không đủ cơ sở để quyết định chẩn đoán, "
            "liều thuốc hoặc xử trí cá nhân. Hãy trao đổi với nhân viên y tế phù hợp; nếu có dấu "
            "hiệu nguy hiểm, tìm trợ giúp khẩn cấp.",
        )

    greetings = {"xin chao", "chao", "hello", "hi", "cam on", "xin cam on"}
    if normalized in greetings:
        return TriageResult(
            QueryClass.GREETING,
            "Xin chào. Tôi có thể giúp tra cứu nội dung trong tài liệu WHO/ICRC Basic Emergency Care (2018).",
        )

    tokens = set(re.findall(r"[a-z0-9]+", normalized))
    medical_matches = tuple(sorted(term for term in _MEDICAL_TERMS if term in normalized))
    if medical_matches:
        return TriageResult(
            QueryClass.DOCUMENT_LOOKUP,
            "Yêu cầu có vẻ liên quan đến nội dung y tế trong phạm vi tra cứu tài liệu hiện có.",
            medical_matches,
        )

    health_matches = tuple(sorted(term for term in _HEALTH_TERMS if term in normalized))
    if health_matches:
        return TriageResult(
            QueryClass.OUT_OF_SCOPE,
            "Chủ đề có vẻ thuộc lĩnh vực y tế nhưng có thể nằm ngoài tài liệu hiện được tích hợp. "
            "Hệ thống chỉ trả lời khi tìm được bằng chứng liên quan trong kho nguồn.",
            health_matches,
        )

    if len(tokens) <= 2:
        return TriageResult(
            QueryClass.AMBIGUOUS,
            "Câu hỏi chưa đủ rõ để xác định nội dung cần tra cứu. Hãy nêu cụ thể chủ đề hoặc câu hỏi về tài liệu.",
        )

    return TriageResult(
        QueryClass.OUT_OF_SCOPE,
        "Chưa xác định được câu hỏi thuộc phạm vi tài liệu hiện có. Hệ thống sẽ không tự tạo câu trả lời y tế khi chưa tìm được nguồn phù hợp.",
    )
