"""Local-only, source-first demonstration UI for the WHO/ICRC BEC document.

Run from the project root with: python app/internal_pilot.py
Requires a running local Ollama service and the qwen2.5:7b-instruct-q4_K_M model.
"""

from __future__ import annotations

import html
import json
import math
import os
import re
import threading
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterable

# Support both documented launch styles:
#   python app/internal_pilot.py
#   python -m app.internal_pilot
try:
    from app.query_triage import QueryClass, classify_query
except ModuleNotFoundError as exc:
    if exc.name != "app":
        raise
    from query_triage import QueryClass, classify_query


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "knowledge_base" / "03_cleaned" / "WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt"
MODEL = os.environ.get("BEC_OLLAMA_MODEL", "qwen2.5:7b-instruct-q4_K_M")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
HOST = "127.0.0.1"
PORT = int(os.environ.get("BEC_PILOT_PORT", "8765"))
MAX_BODY = 12_000
MAX_CONTEXT_CHARS = 10_000

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for", "from",
    "give", "how", "i", "in", "is", "it", "me", "of", "on", "or", "patient", "please",
    "the", "to", "what", "when", "with", "you", "your", "la", "gi", "bao", "nhieu", "nao",
    "theo", "trong", "cho", "cua", "va", "neu", "thi", "co", "khong", "mot", "nhung",
    "tai", "lieu", "liet", "ke", "dau", "hieu", "soc", "hay", "nao",
}

# Small transparent query expansion for common Vietnamese terms. This helps
# locate English source passages; it does not translate or alter source text.
VI_TO_EN = {
    "sot": "fever", "thai": "pregnant pregnancy", "tuan": "week weeks", "garo": "tourniquet",
    "tranh chan thuong": "prevent injury protect falls hard sharp objects", "ran": "snake", "ran can": "snake bite", "kho tho": "difficulty breathing DIB overview causes initial assessment acute management airway ABCDE",
    "tho": "breathing respiratory", "dau hieu": "signs symptoms", "chay mau": "bleeding hemorrhage control severe bleeding", "tuoi mau": "perfusion", "tuoi mau kem": "poor perfusion shock", "ngoai vi": "peripheral perfusion circulation",
    "co giat": "seizure convulsion protect falls injury hard sharp objects", "duong huyet": "glucose blood sugar",
    "co the noi va nuot": "speak swallow", "khong the noi": "cannot speak",
    "hon me": "unconscious", "duong uong": "oral glucose",
    "duong tinh mach": "iv glucose intravenous", "niem mac ma": "buccal cheek",
    "duong": "glucose", "ha duong huyet": "hypoglycaemia low blood glucose", "mach": "pulse heart rate", "bong": "burn burns",
    "naloxone": "naloxone", "thuoc": "medication medicine",
    # A question about shock signs should retrieve the source table, not merely
    # passages that mention the word "shock" in passing.
    "soc": "shock perfusion tachycardia tachypnoea capillary refill hypotension pale cool skin sweating dizziness confusion",
    "tre em": "child children pediatric", "phu nu mang thai": "pregnant pregnancy",
    "mang thai": "pregnant pregnancy", "nghieng trai": "left side",
    "trieu chung": "signs symptoms", "xu tri": "management treatment",
    "lam gi": "management treatment", "can lam gi": "management treatment",
    # Compact anchors help broad prompts land on module headings and tables.
    "chan thuong": "trauma primary survey ABCDE injured patients",
    "danh gia ban dau": "initial assessment ABCDE primary survey SAMPLE",
    "cap cuu": "emergency ABCDE primary survey initial assessment",
    "bong": "burn burns burn management inhalational circumferential",
    "nguyen nhan": "causes result from blood loss fluid loss burns",
}


def fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold()).replace("đ", "d")
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def terms(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+(?:'[a-z]+)?", fold(text)) if len(t) > 1 and t not in STOPWORDS]


@dataclass(frozen=True)
class Chunk:
    index: int
    page: str
    start_line: int
    end_line: int
    text: str

    @property
    def citation(self) -> str:
        page = f"PDF p. {self.page}; " if self.page else ""
        return f"{page}cleaned lines {self.start_line}-{self.end_line}"


def load_chunks() -> tuple[str, list[Chunk]]:
    if not SOURCE_PATH.is_file():
        raise FileNotFoundError(f"Cleaned source not found: {SOURCE_PATH}")
    lines = SOURCE_PATH.read_text(encoding="utf-8").splitlines()
    page = ""
    paragraphs: list[tuple[str, int, int, str]] = []
    buf: list[str] = []
    start = 1

    def flush(end: int) -> None:
        nonlocal buf
        text = "\n".join(buf).strip()
        if text:
            paragraphs.append((page, start, end, text))
        buf = []

    for number, line in enumerate(lines, 1):
        marker = re.search(r"TRANG PDF\s+(\d+)", line, flags=re.IGNORECASE)
        if marker:
            flush(number - 1)
            page = marker.group(1)
            start = number
            continue
        if not line.strip():
            flush(number - 1)
            start = number + 1
            continue
        if not buf:
            start = number
        buf.append(line)
        # Avoid giant flattened tables or paragraphs; split at line boundaries.
        if sum(len(x) for x in buf) >= 850:
            flush(number)
            start = number + 1
    flush(len(lines))

    chunks: list[Chunk] = []
    pending: list[tuple[str, int, int, str]] = []
    for record in paragraphs:
        p, first, last, text = record
        if pending and pending[-1][0] == p and last - pending[0][1] < 8 and sum(len(x[3]) for x in pending) + len(text) <= 1100:
            old = pending.pop()
            pending.append((p, old[1], last, old[3] + "\n" + text))
        else:
            pending.append(record)
    for idx, (p, first, last, text) in enumerate(pending, 1):
        chunks.append(Chunk(idx, p, first, last, text))
    return SOURCE_PATH.read_text(encoding="utf-8"), chunks


SOURCE_TEXT, CHUNKS = load_chunks()

# Build retrieval statistics once at startup instead of retokenizing all 1,496
# chunks for every question.
CHUNK_TERMS = [terms(chunk.text) for chunk in CHUNKS]
CHUNK_TERM_COUNTS: list[dict[str, int]] = []
DOCUMENT_FREQUENCY: dict[str, int] = {}
for chunk_terms in CHUNK_TERMS:
    counts: dict[str, int] = {}
    for term in chunk_terms:
        counts[term] = counts.get(term, 0) + 1
    CHUNK_TERM_COUNTS.append(counts)
    for term in counts:
        DOCUMENT_FREQUENCY[term] = DOCUMENT_FREQUENCY.get(term, 0) + 1
N_CHUNKS = len(CHUNKS)
IDF = {
    term: math.log(1 + (N_CHUNKS - df + 0.5) / (df + 0.5))
    for term, df in DOCUMENT_FREQUENCY.items()
}


def expand_query(query: str) -> list[str]:
    normalized = fold(query)
    expanded = [normalized]
    for vi, en in VI_TO_EN.items():
        if re.search(rf"\b{re.escape(vi)}\b", normalized):
            expanded.append(en)
    return list(dict.fromkeys(terms(" ".join(expanded))))


def retrieve(query: str, limit: int = 2) -> list[tuple[Chunk, float]]:
    qterms = list(dict.fromkeys(expand_query(query)))
    if not qterms:
        return []
    scored: list[tuple[Chunk, float]] = []
    for chunk, counts in zip(CHUNKS, CHUNK_TERM_COUNTS):
        overlap = [t for t in qterms if counts.get(t, 0)]
        if not overlap:
            continue
        coverage = len(overlap) / max(1, min(len(qterms), 6))
        weighted = 0.0
        for term in overlap:
            tf = counts[term]
            weighted += IDF.get(term, 0.0) * (tf * 2.2) / (tf + 1.2)
        norm = sum(IDF.get(t, 0.0) for t in qterms)
        score = coverage * 0.55 + (weighted / norm * 0.45 if norm else 0)
        scored.append((chunk, score))
    scored.sort(key=lambda item: (item[1], -len(item[0].text)), reverse=True)
    chosen: list[tuple[Chunk, float]] = []
    seen_pages: set[tuple[str, int]] = set()
    for item in scored:
        key = (item[0].page, item[0].start_line // 12)
        if key in seen_pages:
            continue
        chosen.append(item)
        seen_pages.add(key)
        if len(chosen) >= limit:
            break
    # Require at least two meaningful query terms to overlap, or substantial
    # coverage for a very short question. This is a conservative pilot gate.
    if not chosen:
        return []
    best = chosen[0]
    matched = set(terms(best[0].text)) & set(qterms)
    minimum = 1 if len(qterms) <= 2 else 2
    if len(matched) < minimum or best[1] < 0.55:
        return []
    return chosen


def ollama_chat(system: str, user: str, num_predict: int = 650) -> str:
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "think": False,
        "stream": False,
        "options": {"temperature": 0, "seed": 42, "num_predict": num_predict},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL.rstrip('/')}/api/chat", data=body,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=240) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result.get("message", {}).get("content", "").strip()


def appears_english(text: str) -> bool:
    words = re.findall(r"[a-z]+", fold(text))
    common = {"the", "is", "are", "according", "source", "provided", "not", "stated", "patient", "give", "if", "and", "or", "with", "for", "this", "that", "of", "to", "in", "on", "may", "can", "should", "must"}
    untranslated_medical = {
        "shock", "hypovolaemic", "tachycardia", "tachypnoea", "hypotension", "capillary",
        "perfusion", "diaphoresis", "dizziness", "confusion", "systolic", "bleeding",
        "management", "assessment", "symptoms", "signs", "patient", "breathing",
    }
    if untranslated_medical.intersection(words):
        return True
    english_count = sum(1 for word in words if word in common)
    return english_count >= 3 and english_count / max(1, len(words)) >= 0.10


def repeated_output(text: str) -> bool:
    lines = [re.sub(r"\W+", " ", fold(line)).strip() for line in text.splitlines() if line.strip()]
    if len(lines) >= 3 and sum(lines.count(line) - 1 for line in set(lines) if len(line.split()) >= 4) >= 2:
        return True
    words = terms(text)
    if len(words) < 30:
        return False
    for size in (6, 7, 8):
        counts: dict[tuple[str, ...], int] = {}
        for i in range(len(words) - size + 1):
            gram = tuple(words[i:i + size])
            counts[gram] = counts.get(gram, 0) + 1
        if max(counts.values(), default=0) >= 3:
            return True
    return False


def translation_quality_warning(output: str) -> str | None:
    if not output.strip():
        return "Chưa tạo được bản tiếng Việt. Hãy đối chiếu đoạn nguồn tiếng Anh bên dưới."
    if repeated_output(output):
        return "Bản dịch có dấu hiệu lặp hoặc lỗi sinh văn bản nên đã bị ẩn. Hãy đối chiếu nguồn tiếng Anh."
    if re.search(r"[\u3400-\u9fff\u3040-\u30ff\uac00-\ud7af]", output):
        return "Câu trả lời có ký tự ngoài tiếng Việt nên đã bị ẩn. Hãy đối chiếu đoạn nguồn bên dưới."
    folded = fold(output)
    known_bad_phrases = ("dieu kien mach duong", "bien dinh", "thieu mau cap la tinh trang khong cung cap", "tinh trang canh sat", "modu 1")
    if any(phrase in folded for phrase in known_bad_phrases):
        return "Bản dịch có dấu hiệu sai thuật ngữ nên đã bị ẩn. Hãy đối chiếu nguồn tiếng Anh."
    if appears_english(output):
        return "Bản dịch còn nhiều tiếng Anh nên đã bị ẩn. Hãy đối chiếu nguồn tiếng Anh."
    return None


def localize_medical_terms(text: str, source_text: str = "") -> str:
    """Apply a small explicit terminology list to generated Vietnamese text."""
    text = re.sub(r"\s*\((?:tachycardia|tachypnoea|diaphoresis|hypotension|systolic|immobilize)\)", "", text, flags=re.IGNORECASE)
    replacements = (
        (r"\bsigns and symptoms\b", "dấu hiệu và triệu chứng"),
        (r"\bstart an IV\b", "đặt đường truyền tĩnh mạch"),
        (r"\bgive IV fluids\b|\bIV fluids\b", "truyền dịch tĩnh mạch"),
        (r"tiếp nước\s+IV", "truyền dịch tĩnh mạch"),
        (r"\bintravenous fluids\b", "dịch truyền tĩnh mạch"),
        (r"\bpatient\b", "người bệnh"),
        (r"\bmanagement\b", "xử trí"),
        (r"\bassessment\b", "đánh giá"),
        (r"\bcondition\b", "tình trạng"),
        (r"\bpulselessness\b", "mất mạch"),
        (r"\bunconscious(?:ness)?\b", "mất ý thức"),
        (r"\bnot breathing\b", "không thở"),
        (r"\bseconds\b", "giây"),
        (r"\bhypovolaemic shock\b", "sốc giảm thể tích"),
        (r"\bpoor perfusion\b", "tưới máu kém"),
        (r"\bperfusion\b", "tưới máu"),
        (r"\btachycardia\b", "nhịp tim nhanh"),
        (r"\btachypnoea\b", "thở nhanh"),
        (r"\bpale and cool skin\b", "da tái và lạnh"),
        (r"\bcapillary refill(?: time)?\b", "thời gian làm đầy mao mạch"),
        (r"\bdiaphoresis\b|\bsweating\b", "vã mồ hôi"),
        (r"\bdizziness\b", "chóng mặt"),
        (r"\bconfusion\b", "lú lẫn"),
        (r"\baltered mental status\b", "thay đổi trạng thái tinh thần"),
        (r"\bhypotension\b", "hạ huyết áp"),
        (r"\bsystolic(?: blood pressure)?\b", "huyết áp tâm thu"),
        (r"\bexternal bleeding\b", "chảy máu ngoài"),
        (r"\binternal bleeding\b", "chảy máu trong"),
        (r"\bshock\b", "sốc"),
        (r"\bimmobilize(?:d|s|ing)?\b", "bất động"),
        (r"\bmalaria\b", "sốt rét"),
        (r"\bglucose\b", "đường"),
        (r"\bbuccal\b", "niêm mạc má"),
        (r"\boral\b", "\u0111\u01b0\u1eddng u\u1ed1ng"),
        (r"\bvenom\b", "n\u1ecdc \u0111\u1ed9c"),
        (r"\bvital signs\b", "d\u1ea5u hi\u1ec7u sinh t\u1ed3n"),
        (r"\boxygen saturation\b", "\u0111\u1ed9 b\u00e3o h\u00f2a oxy"),
        (r"\bmay have\b", "c\u00f3 th\u1ec3 c\u00f3"),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    def drop_repeated_parenthetical(match: re.Match[str]) -> str:
        inner = match.group(1).strip()
        parts = [re.sub(r"[^a-z0-9]", "", fold(part)) for part in inner.split("/")]
        if len(parts) > 1 and parts[0] and len(set(parts)) == 1:
            return ""
        before = text[:match.start()]
        normalized_inner = re.sub(r"[^a-z0-9]", "", fold(inner))
        normalized_before = re.sub(r"[^a-z0-9]", "", fold(before[-180:]))
        if len(normalized_inner) >= 12 and normalized_inner in normalized_before:
            return ""
        return match.group(0)
    text = re.sub(r"\s*\(([^()]*)\)", drop_repeated_parenthetical, text)
    text = re.sub(r"\u9971\u548c\u8840\u6c27", "bão hòa oxy", text)
    text = re.sub(r"giữ nguyên trạng thái\s+vùng bị cắn", "Bất động vùng bị cắn", text, flags=re.IGNORECASE)
    text = re.sub("cho u\u1ed1ng d\u1ecbch t\u0129nh m\u1ea1ch", "truy\u1ec1n d\u1ecbch t\u0129nh m\u1ea1ch", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsaturat(?:ion)?\s+oxy\b", "b\u00e3o h\u00f2a oxy", text, flags=re.IGNORECASE)
    text = re.sub(r"\\s*\\(\\u0111\\u00f3ng g\\u00e1y\\)", "", text, flags=re.IGNORECASE)
    if "confusion" in fold(source_text) and "hoang loan" in fold(text):
        text = re.sub(r"hoảng loạn", "lú lẫn", text, flags=re.IGNORECASE)
    if "control bleeding" in fold(source_text):
        text = re.sub(r"kìm hãm chảy máu", "kiểm soát chảy máu", text, flags=re.IGNORECASE)
    for phrase in ("nhịp tim nhanh", "thở nhanh", "da tái và lạnh", "thời gian làm đầy mao mạch", "vã mồ hôi", "chóng mặt", "lú lẫn", "thay đổi trạng thái tinh thần", "hạ huyết áp", "tưới máu kém"):
        text = re.sub(rf"({re.escape(phrase)})\s*[\[(]\s*{re.escape(phrase)}\s*[\])]", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^(\s*•\s*\n)kiểm soát chảy máu", r"\1Kiểm soát chảy máu", text)
    return text


def source_list_answer(query: str, retrieved: list[tuple[Chunk, float]]) -> tuple[str, str | None] | None:
    """Translate two verified source decision lists without generative omissions."""
    q = fold(query)
    asks_causes = any(term in q for term in ("nguyen nhan", "causes", "cause"))
    for index, (chunk, _) in enumerate(retrieved, 1):
        text = chunk.text
        cite = f"[S{index}]"
        if (asks_causes and "Hypovolaemic shock can result from rapid loss of" in text
                and any(term in q for term in ("soc", "tuoi mau", "ngoai vi kem"))):
            signs_source = next((i for i, (candidate, _) in enumerate(retrieved, 1)
                                 if "Shock \u2022" in candidate.text), None)
            answer = "Trong phần về sốc giảm thể tích, tài liệu nêu:\n"
            if signs_source is not None:
                answer += (
                    f"- Dấu hiệu gồm nhịp tim nhanh, thở nhanh, da tái, đầu chi lạnh, thời gian làm đầy mao mạch chậm; có thể chóng mặt, lú lẫn/thay đổi trạng thái tinh thần hoặc hạ huyết áp. [S{signs_source}]\n"
                )
            answer += f"- Nguyên nhân có thể là mất máu nhanh hoặc mất dịch liên quan đến bỏng. {cite}"
            return answer, None
        if "Shock \u2022" in text and any(term in q for term in ("soc", "tuoi mau", "ngoai vi kem")) and any(term in q for term in ("dau hieu", "trieu chung", "bieu hien", "signs")):
            answer = (
                "C\u00e1c d\u1ea5u hi\u1ec7u c\u1ee7a s\u1ed1c/t\u01b0\u1edbi m\u00e1u k\u00e9m \u0111\u01b0\u1ee3c li\u1ec7t k\u00ea trong t\u00e0i li\u1ec7u g\u1ed3m:\n"
                f"- Nh\u1ecbp tim nhanh. {cite}\n"
                f"- Th\u1edf nhanh. {cite}\n"
                f"- Da t\u00e1i v\u00e0 l\u1ea1nh. {cite}\n"
                f"- Th\u1eddi gian l\u00e0m \u0111\u1ea7y mao m\u1ea1ch tr\u00ean 3 gi\u00e2y. {cite}\n"
                f"- V\u00e3 m\u1ed3 h\u00f4i. {cite}\n"
                f"- C\u00f3 th\u1ec3 ch\u00f3ng m\u1eb7t, l\u00fa l\u1eabn ho\u1eb7c thay \u0111\u1ed5i tr\u1ea1ng th\u00e1i tinh th\u1ea7n. {cite}\n"
                f"- C\u00f3 th\u1ec3 h\u1ea1 huy\u1ebft \u00e1p. {cite}"
            )
            return answer, None
        if "hypoglycaemia" in fold(text) and "If the person can speak and swallow" in text and "If IV glucose is not possible or available" in text:
            asks_management = any(term in q for term in ("xu tri", "lam gi", "cach cho", "khong the noi", "hon me", "khong the nuot", "khong tinh tao"))
            if asks_management:
                if "khong the noi" in q or "hon me" in q or "khong tinh tao" in q:
                    answer = (
                        "Nếu người bệnh không thể nói hoặc đang hôn mê, tài liệu nêu:\n"
                        f"- Dùng glucose qua đường tĩnh mạch nếu có thể. {cite}\n"
                        f"- Nếu không thể hoặc không có sẵn đường tĩnh mạch, dùng glucose qua niêm mạc má. {cite}"
                    )
                else:
                    answer = (
                        "Cách cho glucose theo tài liệu:\n"
                        f"- Nếu người bệnh có thể nói và nuốt, cho glucose qua đường uống. {cite}\n"
                        f"- Nếu người bệnh không thể nói hoặc đang hôn mê, dùng glucose qua đường tĩnh mạch nếu có thể. {cite}\n"
                        f"- Nếu không thể hoặc không có sẵn đường tĩnh mạch, dùng glucose qua niêm mạc má. {cite}"
                    )
                return answer, None
        if ("pregnant uterus can" in text and "always place on the left" in text
                and "thai" in q and ("20" in q or "tuan" in q)):
            answer = (
                f"T\u00e0i li\u1ec7u cho bi\u1ebft t\u1eed cung khi mang thai tr\u00ean 20 tu\u1ea7n c\u00f3 th\u1ec3 ch\u00e8n \u00e9p t\u0129nh m\u1ea1ch ch\u1ee7 d\u01b0\u1edbi khi n\u1eb1m ng\u1eeda, c\u1ea3n tr\u1edf m\u00e1u v\u1ec1 tim v\u00e0 c\u00f3 th\u1ec3 g\u00e2y s\u1ed1c. Khi n\u1eb1m, \u0111\u1eb7t ng\u01b0\u1eddi b\u1ec7nh nghi\u00eang sang tr\u00e1i. {cite}"
            )
            return answer, None
        if ("chay mau" in q and any(term in q for term in ("lam gi", "xu tri", "kiem soat", "noi gi", "the nao", "khuyen"))
                and not any(term in q for term in ("ngoai", "vet thuong", "chuan khoa", "sau sinh", "chan thuong"))):
            answer = f"C\u00e1c \u0111o\u1ea1n t\u00ecm \u0111\u01b0\u1ee3c ch\u01b0a x\u00e1c \u0111\u1ecbnh lo\u1ea1i v\u00e0 v\u1ecb tr\u00ed ch\u1ea3y m\u00e1u, n\u00ean ch\u01b0a \u0111\u1ee7 c\u01a1 s\u1edf \u0111\u1ec3 ch\u1ecdn h\u01b0\u1edbng d\u1eabn ph\u00f9 h\u1ee3p. H\u00e3y xem c\u00e1c ngu\u1ed3n b\u00ean d\u01b0\u1edbi ho\u1eb7c n\u00eau r\u00f5 b\u1ed1i c\u1ea3nh. [S1] [S2]"
            return answer, "C\u00e2u tr\u1ea3 l\u1eddi \u0111\u01b0\u1ee3c gi\u1edbi h\u1ea1n v\u00ec c\u00e2u h\u1ecfi ch\u01b0a n\u00eau lo\u1ea1i ch\u1ea3y m\u00e1u."
        specific_breathing_topics = ("hen", "asthma", "stridor", "tac nghen", "choking", "di vat", "oxy", "tre em", "tre nho")
        if ("kho tho" in q and any(term in q for term in ("lam gi", "xu tri", "ban dau", "dau tien"))
                and not any(term in q for term in specific_breathing_topics)):
            answer = f"C\u00e1c \u0111o\u1ea1n t\u00ecm \u0111\u01b0\u1ee3c ch\u01b0a \u0111\u1ee7 \u0111\u1ec3 ch\u1ecdn m\u1ed9t h\u01b0\u1edbng d\u1eabn chung cho t\u00ecnh hu\u1ed1ng kh\u00f3 th\u1edf. H\u00e3y xem c\u00e1c ngu\u1ed3n b\u00ean d\u01b0\u1edbi ho\u1eb7c n\u00eau r\u00f5 b\u1ed1i c\u1ea3nh c\u1ea7n tra. [S1] [S2]"
            return answer, "C\u00e2u tr\u1ea3 l\u1eddi \u0111\u01b0\u1ee3c gi\u1edbi h\u1ea1n v\u00ec c\u00e2u h\u1ecfi ch\u01b0a n\u00eau t\u00ecnh hu\u1ed1ng c\u1ee5 th\u1ec3."
        if ("Protect the seizing person from falls" in text and "co giat" in q
                and any(term in q for term in ("chan thuong", "bao ve", "nga", "lam gi"))):
            answer = (
                "\u0110\u1ec3 h\u1ea1n ch\u1ebf ch\u1ea5n th\u01b0\u01a1ng khi co gi\u1eadt, t\u00e0i li\u1ec7u h\u01b0\u1edbng d\u1eabn:\n"
                f"- B\u1ea3o v\u1ec7 ng\u01b0\u1eddi \u0111ang co gi\u1eadt kh\u1ecfi b\u1ecb ng\u00e3 v\u00e0 tr\u00e1nh xa c\u00e1c v\u1eadt c\u1ee9ng ho\u1eb7c s\u1eafc nh\u1ecdn. {cite}\n"
                f"- Kh\u00f4ng \u0111\u1eb7t b\u1ea5t c\u1ee9 th\u1ee9 g\u00ec v\u00e0o mi\u1ec7ng khi ng\u01b0\u1eddi b\u1ec7nh \u0111ang co gi\u1eadt; ngo\u1ea1i l\u1ec7 l\u00e0 h\u00fat d\u1ecbch \u0111\u01b0\u1eddng th\u1edf. {cite}"
            )
            return answer, None
        if ("DO NOT put a tourniquet around the snake bite or limb." in text
                and "ran can" in q and any(term in q for term in ("garo", "tourniquet"))):
            answer = f"Kh\u00f4ng. T\u00e0i li\u1ec7u h\u01b0\u1edbng d\u1eabn kh\u00f4ng \u0111\u1eb7t gar\u00f4 quanh v\u1ebft r\u1eafn c\u1eafn ho\u1eb7c chi b\u1ecb c\u1eafn. {cite}"
            return answer, None
        if ("The goal of managing snake bites" in text
                and re.search(r"\bI\s+mmobilize the extremity", text, flags=re.IGNORECASE)
                and "Give IV fluids if evidence of shock" in text and "plan early for" in text):
            if "ran can" in q and any(term in q for term in ("xu tri", "buoc", "lam gi", "management", "treat")):
                answer = (
                    "Tài liệu nêu các bước xử trí rắn cắn sau:\n"
                    f"- Mục tiêu là hạn chế nọc độc lan rộng và tác động của nọc độc lên cơ thể. {cite}\n"
                    f"- Bất động chi bị cắn. {cite}\n"
                    f"- Nếu có thể, chụp ảnh con rắn và gửi ảnh cùng người bệnh. {cite}\n"
                    f"- Truyền dịch tĩnh mạch nếu có bằng chứng sốc. {cite}\n"
                    f"- Theo dõi sát vì có thể xuất hiện sốc muộn hoặc vấn đề đường thở; chuẩn bị chuyển giao hoặc chuyển viện sớm. {cite}"
                )
                return answer, None
    return None


def call_model_uncached(query: str, retrieved: list[tuple[Chunk, float]]) -> tuple[str, str | None]:
    answer_sources = retrieved
    normalized_query = fold(query)
    asks_shock_signs = (bool(re.search(r"\bsoc\b", normalized_query)) or "tuoi mau" in normalized_query or "ngoai vi kem" in normalized_query) and any(
        phrase in normalized_query for phrase in ("dau hieu", "trieu chung", "bieu hien", "signs", "symptoms")
    )
    if asks_shock_signs:
        direct = next(((chunk, score) for chunk, score in retrieved if "Shock •" in chunk.text), None)
        if direct:
            chunk, score = direct
            start = chunk.text.find("Shock •")
            end = chunk.text.find("Poor perfusion is", start)
            if end > start:
                answer_sources = [(Chunk(chunk.index, chunk.page, chunk.start_line, chunk.end_line, chunk.text[start:end].strip()), score)]
    contexts = []
    total = 0
    for i, (chunk, _) in enumerate(answer_sources, 1):
        piece = f"[S{i}] {chunk.citation}\n{chunk.text}"
        if total + len(piece) > MAX_CONTEXT_CHARS:
            break
        contexts.append(piece)
        total += len(piece)
    system = (
        "Bạn là trợ lý tra cứu một tài liệu huấn luyện cấp cứu. Chỉ được dùng các đoạn nguồn được cung cấp. "
        "Không chẩn đoán, kê đơn, suy luận hoặc bổ sung kiến thức y khoa. Trả lời hoàn toàn bằng tiếng Việt; "
        "không để sót từ chuyên môn tiếng Anh. Chỉ giữ chữ viết tắt và tên riêng khi cần. "
        "Không để thuật ngữ tiếng Anh trong ngoặc. Dùng các cách dịch thống nhất sau: shock = sốc; hypovolaemic shock = sốc giảm thể tích; "
        "tachycardia = nhịp tim nhanh; tachypnoea = thở nhanh; pale and cool skin = da tái và lạnh; "
        "capillary refill = thời gian làm đầy mao mạch; sweating/diaphoresis = vã mồ hôi; dizziness = chóng mặt; "
        "confusion = lú lẫn; altered mental status = thay đổi trạng thái tinh thần; hypotension = hạ huyết áp; "
        "poor perfusion = tưới máu kém; perfusion = tưới máu; external bleeding = chảy máu ngoài; internal bleeding = chảy máu trong; "
        "systolic blood pressure = huyết áp tâm thu. "
        "Trả lời đủ tất cả ý liên quan có trong nguồn, gồm từng dấu hiệu, điều kiện, phủ định, ngoại lệ, số liệu và đơn vị. "
        "Với câu hỏi yêu cầu liệt kê, nêu từng mục riêng và không bỏ mục nào. Không thêm diễn giải nền, định nghĩa, "
        "điều trị hoặc mục ngoài phần nguồn trực tiếp trả lời câu hỏi; không lặp lại cùng một ý bằng cách diễn đạt khác. "
        "Chỉ trả lời đúng nội dung được hỏi. Mỗi ý thực tế phải có mã trích dẫn [S1] tương ứng. "
        "Nếu nguồn không nêu câu trả lời, nói rõ điều đó. Không chép lại chỉ dẫn hoặc nội dung nguồn thay cho câu trả lời."
    )
    system += " Include every distinct instruction and condition listed in the source. Do not claim there are no further steps unless you have covered them all. Answer in Vietnamese only. Cite every factual bullet. Never output Han, Japanese, or Korean characters. For a conditional question, answer only the requested branch and include alternatives only when the source states them as fallbacks."
    user = f"CÂU HỎI:\n{query}\n\nCÁC ĐOẠN NGUỒN:\n{'\n\n'.join(contexts)}\n\nHãy trả lời bằng tiếng Việt, đầy đủ và chỉ dựa trên nguồn. Không chèn từ tiếng Anh trong ngoặc."
    try:
        answer = ollama_chat(system, user, 450)
        answer = localize_medical_terms(answer, "\n".join(chunk.text for chunk, _ in retrieved))
        if asks_shock_signs:
            answer = re.sub(r"(?m)^(-\s+[^\n]+?)(?<!\[S1\])$", r"\1 [S1]", answer)
        valid = {f"S{i}" for i in range(1, len(contexts) + 1)}
        refs = re.findall(r"\[(S\d+)\]", answer)
        if any(ref not in valid for ref in refs):
            return "Không thể hiển thị câu trả lời đáng tin cậy. Vui lòng đọc các đoạn nguồn đã dịch bên dưới.", "Mô hình tạo mã trích dẫn không có trong nguồn; câu trả lời đã bị ẩn."
        cited_lines = []
        for line in answer.splitlines():
            if re.match(r"\s*(?:[-*]|\d+[.)])\s+", line) and not re.search(r"\[\s*S\d+(?:\s*,\s*S\d+)*\s*\]", line):
                claim_text = re.sub(r"\[S\d+\]", "", line)
                claim_terms = set(terms(claim_text)) | set(expand_query(claim_text))
                overlaps = [len(claim_terms & set(terms(chunk.text))) for chunk, _ in answer_sources]
                best = max(range(len(overlaps)), key=overlaps.__getitem__, default=-1)
                if best < 0 or overlaps[best] < 1:
                    return "Ch\u01b0a th\u1ec3 tr\u1ea3 l\u1eddi ch\u1eafc ch\u1eafn t\u1eeb c\u00e1c \u0111o\u1ea1n v\u1eeba t\u00ecm \u0111\u01b0\u1ee3c. H\u00e3y xem ngu\u1ed3n ho\u1eb7c th\u1eed h\u1ecfi c\u1ee5 th\u1ec3 h\u01a1n.", "C\u00e2u tr\u1ea3 l\u1eddi thi\u1ebfu tr\u00edch d\u1eabn \u0111\u1ee7 \u0111\u1ec3 \u0111\u1ed1i chi\u1ebfu; c\u00e2u tr\u1ea3 l\u1eddi \u0111\u00e3 \u0111\u01b0\u1ee3c \u1ea9n."
                line += f" [S{best + 1}]"
            cited_lines.append(line)
        answer = "\n".join(cited_lines)
        refs = re.findall(r"\[(S\d+)\]", answer)
        if not refs:
            return "Ch\u01b0a th\u1ec3 tr\u1ea3 l\u1eddi ch\u1eafc ch\u1eafn t\u1eeb c\u00e1c \u0111o\u1ea1n v\u1eeba t\u00ecm \u0111\u01b0\u1ee3c. H\u00e3y xem ngu\u1ed3n ho\u1eb7c th\u1eed h\u1ecfi c\u1ee5 th\u1ec3 h\u01a1n.", "C\u00e2u tr\u1ea3 l\u1eddi kh\u00f4ng c\u00f3 tr\u00edch d\u1eabn \u0111\u1ee7 \u0111\u1ec3 \u0111\u1ed1i chi\u1ebfu; c\u00e2u tr\u1ea3 l\u1eddi \u0111\u00e3 \u0111\u01b0\u1ee3c \u1ea9n."
        warning = translation_quality_warning(answer)
        if warning:
            return "Chưa tạo được câu trả lời tiếng Việt đạt kiểm tra. Vui lòng xem các đoạn nguồn đã dịch bên dưới.", warning
        return answer, None
    except urllib.error.URLError as exc:
        return "", f"Không kết nối được Ollama cục bộ tại {OLLAMA_URL}: {exc}"
    except TimeoutError:
        return "", "Mô hình cục bộ hết thời gian chờ. Hãy thử lại với câu hỏi ngắn hơn."


_ANSWER_CACHE: dict[tuple[str, tuple[int, ...]], tuple[str, str | None]] = {}
_ANSWER_CACHE_LOCK = threading.Lock()

def call_model(query: str, retrieved: list[tuple[Chunk, float]]) -> tuple[str, str | None]:
    key = (query, tuple(chunk.index for chunk, _ in retrieved))
    with _ANSWER_CACHE_LOCK:
        if key in _ANSWER_CACHE:
            return _ANSWER_CACHE[key]
    result = call_model_uncached(query, retrieved)
    with _ANSWER_CACHE_LOCK:
        if len(_ANSWER_CACHE) >= 128:
            _ANSWER_CACHE.pop(next(iter(_ANSWER_CACHE)))
        _ANSWER_CACHE[key] = result
    return result


def translate_excerpts(texts: list[str]) -> tuple[str, str | None]:
    source_chunks = {chunk.text for chunk in CHUNKS}
    if not texts or len(texts) > 4 or any(text not in source_chunks for text in texts):
        return "", "Đoạn yêu cầu dịch không khớp với nguồn đã truy xuất. Hãy tìm nguồn lại."
    translated: list[str] = []
    warnings: list[str] = []
    system = (
        "Bạn là biên dịch viên. Hãy dịch toàn bộ văn bản nguồn sang tiếng Việt. Không bỏ câu, tiêu đề, nhãn, "
        "gạch đầu dòng hoặc cụm từ. Không tóm tắt, không thêm giải thích, không thêm kiến thức ngoài nguồn. "
        "Dịch mọi nội dung thông thường; chỉ giữ nguyên chữ viết tắt, tên riêng, tên thuốc, đơn vị và ký hiệu. Không giữ thuật ngữ tiếng Anh trong ngoặc. "
        "Dùng đúng: module = mô-đun; shock = sốc; tachycardia = nhịp tim nhanh; tachypnoea = thở nhanh; "
        "pale and cool skin = da tái và lạnh; capillary refill = thời gian làm đầy mao mạch; diaphoresis = vã mồ hôi; "
        "confusion = lú lẫn; hypotension = hạ huyết áp; poor perfusion = tưới máu kém; death = tử vong. "
        "Dùng nhất quán các cách dịch: shock = sốc; hypovolaemic shock = sốc giảm thể tích; "
        "tachycardia = nhịp tim nhanh; tachypnoea = thở nhanh; hypotension = hạ huyết áp; "
        "capillary refill = thời gian làm đầy mao mạch; perfusion = tưới máu; confusion = lú lẫn; "
        "poor perfusion = tưới máu kém; management = xử trí; signs and symptoms = dấu hiệu và triệu chứng; "
        "circulation conditions = tình trạng tuần hoàn; in-depth description and management = mô tả chi tiết và xử trí; "
        "pulselessness = mất mạch; unconscious = mất ý thức; not breathing = không thở. "
        "Với thuật ngữ chuyên môn, chỉ dùng tiếng Việt; không chép từ tiếng Anh trong ngoặc. "
        "Giữ nguyên thứ tự, phủ định, điều kiện, mức độ chắc chắn, số liệu, đơn vị, dấu câu có ý nghĩa và cấu trúc danh sách. "
        "Chỉ trả về bản dịch tiếng Việt, không nhắc lại nguyên văn tiếng Anh."
    )
    for index, source in enumerate(texts, 1):
        try:
            user = f"Hãy dịch nguyên vẹn đoạn dưới đây sang tiếng Việt theo các quy tắc đã nêu. Dịch cả tiêu đề bảng; ví dụ CIRCULATION CONDITIONS phải là TÌNH TRẠNG TUẦN HOÀN, SIGNS AND SYMPTOMS là DẤU HIỆU VÀ TRIỆU CHỨNG, IN-DEPTH DESCRIPTION AND MANAGEMENT là MÔ TẢ CHI TIẾT VÀ XỬ TRÍ. Không để lại câu tiếng Anh. Chỉ xuất bản dịch.\n\nVĂN BẢN NGUỒN:\n{source}"
            output = ollama_chat(system, user, 1800)
            output = localize_medical_terms(output, source)
            warning = translation_quality_warning(output)
            if warning:
                warnings.append(f"Đoạn {index}: {warning}")
            else:
                translated.append(f"[ĐOẠN {index}]\n{output}")
        except Exception as exc:
            warnings.append(f"Dịch đoạn {index} thất bại: {exc}")
    if warnings:
        return "", "Không hiển thị bản dịch vì chưa dịch đạt yêu cầu toàn bộ các đoạn nguồn. " + " ".join(warnings)
    return "\n\n".join(translated), None


HTML = r'''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Thử nghiệm nội bộ — Cấp cứu cơ bản WHO/ICRC</title>
<style>
:root{font-family:system-ui,Segoe UI,sans-serif;color:#17212b;background:#f4f7f9}body{margin:0}main{max-width:920px;margin:0 auto;padding:24px}
h1{font-size:1.55rem;margin:0 0 8px}.warning{background:#fff3cd;border:1px solid #e3c56b;padding:14px 16px;border-radius:8px;margin:16px 0}
.panel{background:white;border:1px solid #d8e0e6;border-radius:10px;padding:18px;margin:14px 0}.muted{color:#566575;font-size:.92rem}
textarea{box-sizing:border-box;width:100%;min-height:100px;padding:12px;border:1px solid #aab8c4;border-radius:7px;font:inherit}button{margin-top:10px;background:#145e83;color:white;border:0;border-radius:7px;padding:10px 18px;font:inherit;cursor:pointer}button:disabled{opacity:.5}
.answer{white-space:pre-wrap;line-height:1.55}.source{white-space:pre-wrap;background:#f7f9fa;border-left:3px solid #8ba8b7;padding:10px;margin:10px 0;font: .9rem ui-monospace,Consolas,monospace;max-height:240px;overflow:auto}.status{color:#566575}.notice{color:#8a4200;font-weight:600}.footer{font-size:.85rem;color:#566575}
</style></head><body><main>
<h1>WHO/ICRC — Cấp cứu cơ bản | Bản thử nghiệm nội bộ</h1>
<div class="warning"><strong>MỨC AN TOÀN 0 — TRA CỨU TÀI LIỆU.</strong> Bản này chỉ tìm và diễn đạt lại nội dung trong tài liệu; chưa hỗ trợ chẩn đoán, phân loại cấp cứu, kê đơn hoặc quyết định xử trí. Chỉ dùng để đánh giá nội bộ. Câu trả lời có thể sai hoặc bỏ sót điều kiện quan trọng; người có chuyên môn phải kiểm tra trực tiếp nguồn. Khi có tình huống cấp cứu, làm theo quy trình tại cơ sở và liên hệ nhân viên y tế đủ chuyên môn.</div>
<p class="muted">Câu hỏi được xử lý trên máy này qua Ollama cục bộ. Bản demo không lưu lịch sử trò chuyện. Không nhập thông tin nhận dạng hoặc dữ liệu nhạy cảm của người bệnh.</p>
<div class="panel"><label for="q"><strong>Đặt câu hỏi về tài liệu nguồn</strong></label><textarea id="q" maxlength="2000" placeholder="Ví dụ: Tài liệu liệt kê những dấu hiệu nào của sốc?"></textarea><button id="send">Tìm trong tài liệu và hỏi mô hình</button><span class="status" id="status"></span></div>
<div id="results"></div>
<p class="footer">Nguồn gốc vẫn là tiếng Anh. Nút dịch chỉ dịch các đoạn vừa tìm được, không tạo bản dịch toàn bộ tài liệu; bản dịch tự động chưa được thẩm định. Tìm kiếm từ khóa có thể bỏ sót đoạn liên quan. Trích dẫn không chứng minh mọi ý trong câu trả lời đều được nguồn hỗ trợ.</p>
</main>
<script>
const q=document.querySelector('#q'),btn=document.querySelector('#send'),status=document.querySelector('#status'),out=document.querySelector('#results');let currentSources=[];
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
btn.onclick=async()=>{const question=q.value.trim();if(!question)return;btn.disabled=true;status.textContent=' Đang tìm trong tài liệu và hỏi mô hình...';out.innerHTML='';try{const r=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question})});const d=await r.json();if(!r.ok)throw new Error(d.error||'Yêu cầu không thành công');currentSources=d.sources||[];let autoTranslation=d.translation||'';let autoTranslationWarning=d.translation_warning||'';let h='<section class="panel"><h2>Câu trả lời bằng tiếng Việt <span class="muted">(cần đối chiếu nguồn)</span></h2>';if(d.warning)h+='<p class="notice">'+esc(d.warning)+'</p>';h+='<div class="answer">'+esc(d.answer||'Không có câu trả lời.')+'</div></section>';if(currentSources.length){h+='<section class="panel"><h2>Các đoạn nguồn gốc (tiếng Anh)</h2>';for(const s of currentSources)h+='<details class="source"><summary>'+esc(s.id+' — '+s.citation+' (điểm tìm kiếm '+s.score.toFixed(2)+')')+'</summary>'+esc(s.text)+'</details>';h+='<button id="translate">Dịch các đoạn nguồn sang tiếng Việt</button><p class="muted">Bản dịch tự động chỉ để tham khảo, chưa được thẩm định chuyên môn. Luôn đối chiếu với nguyên văn tiếng Anh.</p><div id="translated">'+(autoTranslationWarning?'<p class="notice">'+esc(autoTranslationWarning)+'</p>':'')+'<div class="source">'+esc(autoTranslation||'Ban dich se xuat hien khi ban bam nut ben duoi.')+'</div></div></section>';}out.innerHTML=h;const tb=document.querySelector('#translate');if(tb)tb.onclick=async()=>{tb.disabled=true;tb.textContent='Đang dịch...';try{const tr=await fetch('/api/translate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({texts:currentSources.map(s=>s.text)})});const td=await tr.json();const box=document.querySelector('#translated');box.innerHTML=(td.warning?'<p class="notice">'+esc(td.warning)+'</p>':'')+'<div class="source">'+esc(td.translation||'Không tạo được bản dịch.')+'</div>';}catch(e){const box=document.querySelector('#translated');box.textContent='Không dịch được: '+e.message;}finally{tb.disabled=false;tb.textContent='Dịch các đoạn nguồn sang tiếng Việt';}};status.textContent=' Hoàn tất.';}catch(e){out.innerHTML='<section class="panel notice">'+esc(e.message)+'</section>';status.textContent='';}finally{btn.disabled=false;}};
q.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter')btn.click();});
</script></body></html>'''


class Handler(BaseHTTPRequestHandler):
    server_version = "BECInternalPilot/0.1"

    def log_message(self, fmt: str, *args: object) -> None:
        # Do not log prompts or answers; only suppress default request logging.
        return

    def send_json(self, status: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/":
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/health":
            self.send_json(200, {"ok": True, "safety_tier": 0, "mode": "document_lookup_with_conservative_triage", "model": MODEL, "source_exists": SOURCE_PATH.is_file(), "source_chunks": len(CHUNKS), "triage_enabled": True, "triage_type": "keyword_rules_unvalidated"})
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:
        if self.path == "/api/translate":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 1 or length > MAX_BODY:
                    self.send_json(413, {"error": "Yêu cầu trống hoặc quá dài."})
                    return
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                texts = payload.get("texts", [])
                if not isinstance(texts, list) or not all(isinstance(text, str) for text in texts):
                    self.send_json(400, {"error": "Danh sách đoạn nguồn không hợp lệ."})
                    return
                translation, warning = translate_excerpts(texts)
                self.send_json(200, {"translation": translation, "warning": warning})
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                self.send_json(400, {"error": f"Yêu cầu không hợp lệ: {exc}"})
            except Exception as exc:
                self.send_json(500, {"error": f"Lỗi dịch đoạn nguồn: {exc}"})
            return
        if self.path != "/api/ask":
            self.send_json(404, {"error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > MAX_BODY:
                self.send_json(413, {"error": "Yêu cầu trống hoặc quá dài."})
                return
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            question = str(payload.get("question", "")).strip()
            if not question or len(question) > 2000:
                self.send_json(400, {"error": "Nhập câu hỏi không quá 2.000 ký tự."})
                return
            triage = classify_query(question)
            if triage.classification == QueryClass.AMBIGUOUS:
                self.send_json(200, {
                    "answer": triage.message,
                    "warning": "Hãy làm rõ câu hỏi trước khi tra cứu; chưa truy xuất hoặc gọi mô hình.",
                    "sources": [],
                    "classification": triage.classification.value,
                    "matched_terms": list(triage.matched_terms),
                })
                return
            if triage.classification == QueryClass.GREETING:
                self.send_json(200, {
                    "answer": triage.message,
                    "warning": "Ứng dụng chỉ tra cứu tài liệu WHO/ICRC BEC 2018.",
                    "sources": [],
                    "classification": triage.classification.value,
                    "matched_terms": list(triage.matched_terms),
                })
                return
            if triage.classification == QueryClass.POSSIBLE_EMERGENCY:
                self.send_json(200, {
                    "answer": triage.message,
                    "warning": "Cảnh báo từ khóa có thể có báo động giả hoặc bỏ sót; không phải đánh giá lâm sàng.",
                    "sources": [],
                    "classification": triage.classification.value,
                    "matched_terms": list(triage.matched_terms),
                })
                return
            if triage.classification == QueryClass.PERSONAL_MEDICAL_ADVICE:
                self.send_json(200, {
                    "answer": triage.message,
                    "warning": "Không đưa ra lời khuyên chẩn đoán hoặc điều trị cá nhân.",
                    "sources": [],
                    "classification": triage.classification.value,
                    "matched_terms": list(triage.matched_terms),
                })
                return

            found = retrieve(question)
            if not found:
                self.send_json(200, {
                    "answer": "Chưa tìm thấy đoạn đủ liên quan trong tài liệu. Hãy diễn đạt lại câu hỏi hoặc tra cứu trực tiếp tài liệu nguồn.",
                    "warning": "Không gọi mô hình vì mức phù hợp của kết quả tìm kiếm thấp.",
                    "sources": [],
                    "classification": triage.classification.value,
                    "matched_terms": list(triage.matched_terms),
                })
                return
            answer_result = source_list_answer(question, found)
            answer, warning = answer_result if answer_result is not None else call_model(question, found)
            sources = [{"id": f"S{i}", "citation": chunk.citation, "text": chunk.text, "score": score}
                       for i, (chunk, score) in enumerate(found, 1)]
            if triage.classification == QueryClass.OUT_OF_SCOPE:
                out_of_scope_warning = (
                    "Câu hỏi có thể nằm ngoài phạm vi tài liệu đang tích hợp. "
                    "Câu trả lời (nếu có) chỉ dựa trên các đoạn nguồn đã truy xuất; "
                    "không suy rộng thành tư vấn y khoa tổng quát."
                )
                warning = f"{warning} {out_of_scope_warning}".strip() if warning else out_of_scope_warning
            self.send_json(200, {"answer": answer, "warning": warning, "sources": sources,
                                 "translation": "", "translation_warning": None,
                                 "classification": triage.classification.value,
                                 "matched_terms": list(triage.matched_terms)})
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            self.send_json(400, {"error": f"Yêu cầu không hợp lệ: {exc}"})
        except Exception as exc:
            self.send_json(500, {"error": f"Lỗi xử lý yêu cầu: {exc}"})


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"BEC internal pilot listening at http://{HOST}:{PORT}")
    print(f"Model: {MODEL}; source chunks: {len(CHUNKS)}")
    print("Local-only demo. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping pilot.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
