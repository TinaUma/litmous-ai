"""Post evaluator — scores generated text 0-100 and assigns Red/Orange/Green zone.

Scoring breakdown (max 100):
  +20  Length in target range (250-700 chars)
  +15  First-person voice (я/мне/мой/мы/нас/наш)
  +15  Concrete numbers or facts (digits present)
  +20  Structure: hook → body → punchline (heuristic)
  +10  No banned openers ("В современном мире", etc.)
  +20  Readability (avg word length ≤ 7, no wall-of-text)
  -5   Per AI-ism word found (революционный, уникальный, etc.)

Zones:
  Green  80-100  — can post as-is
  Orange 60-79   — needs editing
  Red    0-59    — not acceptable
"""

import re
from dataclasses import dataclass, field

# Words that scream "AI wrote this" — each costs -5 points
AI_ISMS_RU = [
    "революционный", "революционная", "революционное", "революционных",
    "впечатляющий", "впечатляющая", "впечатляющее",
    "уникальный", "уникальная", "уникальное",
    "инновационный", "инновационная", "инновационное",
    "передовой", "передовая", "передовые",
    "прорывной", "прорывная", "прорывное",
    "невероятный", "невероятная", "невероятное",
    "потрясающий", "потрясающая", "потрясающее",
    "трансформационный", "трансформационная",
    "беспрецедентный", "беспрецедентная",
    "экосистема",
    "синергия", "синергии",
    "дорожная карта",
    "стейкхолдер", "стейкхолдеры",
]
AI_ISMS_EN = [
    "revolutionary", "impressive", "unique", "innovative",
    "cutting-edge", "groundbreaking", "incredible", "transformative",
    "unprecedented", "ecosystem", "synergy", "leverage", "seamless",
    "robust", "scalable",
]

BANNED_OPENERS = [
    r"в современном мире",
    r"сегодня мы рассмотрим",
    r"стоит отметить",
    r"время покажет",
    r"остаётся следить",
    r"это изменит всё",
    r"в эпоху",
    r"на сегодняшний день",
]

FIRST_PERSON = re.compile(
    r"\b(я|мне|меня|мой|моя|моё|мои|мы|нас|нам|наш|наша|наше|наши)\b",
    re.IGNORECASE,
)
HAS_DIGITS = re.compile(r"\d")


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text)


def _score_length(clean: str) -> int:
    n = len(clean.strip())
    if 250 <= n <= 700:
        return 20
    if 150 <= n < 250 or 700 < n <= 900:
        return 10
    return 0


def _score_first_person(clean: str) -> int:
    return 15 if FIRST_PERSON.search(clean) else 0


def _score_digits(clean: str) -> int:
    return 15 if HAS_DIGITS.search(clean) else 0


def _score_structure(clean: str) -> int:
    sentences = [s.strip() for s in re.split(r"[.!?]+", clean) if s.strip()]
    if len(sentences) < 3:
        return 0
    last = sentences[-1]
    if len(last) < 120:
        return 20
    return 10


def _score_no_banned_opener(text: str) -> int:
    lower = text.lower()
    for pattern in BANNED_OPENERS:
        if re.search(pattern, lower):
            return 0
    return 10


def _score_readability(clean: str) -> int:
    words = clean.split()
    if not words:
        return 0
    avg_len = sum(len(w) for w in words) / len(words)
    if avg_len <= 7:
        return 20
    if avg_len <= 9:
        return 12
    return 5


def _count_ai_isms(text: str) -> list[str]:
    lower = text.lower()
    return [w for w in AI_ISMS_RU + AI_ISMS_EN if w.lower() in lower]


@dataclass
class EvalResult:
    score: int
    zone: str           # "Green" | "Orange" | "Red"
    breakdown: dict     # criterion → points
    ai_isms_found: list[str] = field(default_factory=list)


def evaluate(text: str) -> EvalResult:
    """Score a generated post text and return an EvalResult."""
    clean = _strip_html(text)

    breakdown = {
        "length":       _score_length(clean),
        "first_person": _score_first_person(clean),
        "digits":       _score_digits(clean),
        "structure":    _score_structure(clean),
        "no_opener":    _score_no_banned_opener(text),
        "readability":  _score_readability(clean),
    }
    ai_isms = _count_ai_isms(text)
    penalty = len(ai_isms) * 5
    breakdown["ai_isms_penalty"] = -penalty

    raw_score = sum(v for k, v in breakdown.items() if k != "ai_isms_penalty") - penalty
    score = max(0, min(100, raw_score))

    if score >= 80:
        zone = "Green"
    elif score >= 60:
        zone = "Orange"
    else:
        zone = "Red"

    return EvalResult(score=score, zone=zone, breakdown=breakdown, ai_isms_found=ai_isms)
