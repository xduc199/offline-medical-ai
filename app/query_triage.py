"""Conservative request triage for the offline medical-document pilot.

This is an explainable lexical guard, not a validated medical or emergency
classifier. It must never be used to reassure a user that no emergency exists.
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


# Lexical triggers are intentionally conservative and require external validation.
_EMERGENCY_PATTERNS = tuple(
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

_PERSONAL_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in [
        r"\btoi\b.*\b(nen|co nen|phai|co the)\b.*\b(uong|dung|ngung|tang|giam|ket hop)\b.*\bthuoc\b",
        r"\b(con toi|be nha toi|me toi|bo toi|vo toi|chong toi|nguoi nha toi)\b.*\b(bi|dang|co dau hieu)\b",
        r"\btoi\b.*\b(bi|dang bi|mac|co trieu chung)\b.*\b(dau|sot|ho|non|buon non|tieu chay|dau bung|kho tho|chong mat)\b",
        r"\b(lieu|lieu dung)\b.*\b(thuoc|dung)\b.*\b(bao nhieu|the nao|cho tre|cho be)\b",
        r"\b(ket qua xet nghiem|chi so xet nghiem)\b.*\b(cua toi|cua be|cua con toi)\b",
        r"\bco nen\b.*\b(uong|dung|ket hop|ngung)\b.*\bthuoc\b",
    ]
)

_MEDICAL_TERMS = (
    "so cuu", "cap cuu", "soc", "ha duong huyet", "ran can", "bong",
    "chay mau", "chan thuong", "kho tho", "dau nguc", "co giat",
    "danh gia ban dau", "benh nhan", "nguoi benh", "tinh trang",
)
_HEALTH_TERMS = (
    "benh", "trieu chung", "thuoc", "xet nghiem", "dinh duong",
    "huyet ap", "duong huyet", "sot", "dau dau", "ho", "ung thu",
    "tim mach", "tieu duong", "thai ky", "tre em", "vaccine",
)
_GREETINGS = {"xin chao", "chao", "hello", "hi", "cam on", "xin cam on"}


def classify_query(question: str) -> TriageResult:
    """Return a cautious request-shape label; this is not clinical triage."""
    normalized = _fold(question).strip()
    if not normalized:
        return TriageResult(QueryClass.AMBIGUOUS, "Vui lòng nhập câu hỏi.")

    emergency_matches = tuple(label for label, pattern in _EMERGENCY_PATTERNS if pattern.search(normalized))
    if emergency_matches:
        return TriageResult(
            QueryClass.POSSIBLE_EMERGENCY,
            "Câu hỏi có thể mô tả tình huống nguy hiểm. Nếu tình huống đang xảy ra, hãy liên hệ "
            "dịch vụ cấp cứu hoặc cơ sở y tế tại địa phương ngay; đừng chờ câu trả lời của phần mềm. "
            "Bản thử nghiệm không thể đánh giá tình trạng người bệnh. Cảnh báo từ khóa không phải chẩn đoán.",
            emergency_matches,
        )

    if any(pattern.search(normalized) for pattern in _PERSONAL_PATTERNS):
        return TriageResult(
            QueryClass.PERSONAL_MEDICAL_ADVICE,
            "Ứng dụng hiện chỉ tra cứu tài liệu nguồn, không đủ cơ sở để quyết định chẩn đoán, liều thuốc "
            "hoặc xử trí cá nhân. Hãy trao đổi với nhân viên y tế phù hợp; nếu có dấu hiệu nguy hiểm, "
            "tìm trợ giúp khẩn cấp.",
        )

    if normalized in _GREETINGS:
        return TriageResult(
            QueryClass.GREETING,
            "Xin chào. Tôi có thể giúp tra cứu nội dung trong tài liệu WHO/ICRC Basic Emergency Care (2018).",
        )

    medical_matches = tuple(term for term in _MEDICAL_TERMS if term in normalized)
    if medical_matches:
        return TriageResult(
            QueryClass.DOCUMENT_LOOKUP,
            "Yêu cầu có vẻ liên quan đến chủ đề trong phạm vi tra cứu tài liệu. Hệ thống vẫn cần tìm được "
            "đoạn nguồn phù hợp trước khi tạo câu trả lời.",
            medical_matches,
        )

    health_matches = tuple(term for term in _HEALTH_TERMS if term in normalized)
    if health_matches:
        return TriageResult(
            QueryClass.OUT_OF_SCOPE,
            "Chủ đề thuộc lĩnh vực sức khỏe nhưng có thể nằm ngoài tài liệu được tích hợp. Hệ thống chỉ "
            "trả lời khi tìm được bằng chứng liên quan trong kho nguồn.",
            health_matches,
        )

    tokens = set(re.findall(r"[a-z0-9]+", normalized))
    if len(tokens) <= 2:
        return TriageResult(
            QueryClass.AMBIGUOUS,
            "Câu hỏi chưa đủ rõ để xác định nội dung cần tra cứu. Hãy nêu cụ thể chủ đề hoặc câu hỏi về tài liệu.",
        )

    return TriageResult(
        QueryClass.OUT_OF_SCOPE,
        "Chưa xác định được câu hỏi thuộc phạm vi tài liệu hiện có. Hệ thống sẽ không tự tạo câu trả lời "
        "y tế khi chưa tìm được nguồn phù hợp.",
    )
