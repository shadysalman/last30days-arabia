"""Arabic-script helpers: detection, orthographic normalization, stopwords.

Arabic text reaches the engine in many spellings of the same word: with or
without short-vowel diacritics (tashkeel), with decorative tatweel stretching
(ـ), and with alef/yaa/taa-marbuta variants that native writers use
interchangeably (أ/إ/آ/ا, ى/ي, ة/ه). Token-overlap relevance and Jaccard
de-duplication treat each variant as a different token, so an Arabic query
like "الذكاء الاصطناعي" would fail to match a post spelled "الذكاء الإصطناعي".

``normalize(text)`` folds those variants to one canonical form. It is a no-op
for text with no Arabic characters, so it is safe to apply to every string.
Zero dependencies, matching the rest of the skill.
"""

from __future__ import annotations

import re

# Arabic, Arabic Supplement, Arabic Extended-A, Presentation Forms A and B.
_ARABIC_CHARS = r"؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿"
_ARABIC_RE = re.compile(f"[{_ARABIC_CHARS}]")

# Tashkeel (harakat, tanween, shadda, sukun, superscript alef) + Quranic marks.
_DIACRITICS_RE = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭ]")
_TATWEEL = "ـ"

_CHAR_MAP = str.maketrans({
    "أ": "ا",  # أ -> ا
    "إ": "ا",  # إ -> ا
    "آ": "ا",  # آ -> ا
    "ٱ": "ا",  # ٱ -> ا
    "ى": "ي",  # ى -> ي
    "ة": "ه",  # ة -> ه
    "ؤ": "و",  # ؤ -> و
    "ئ": "ي",  # ئ -> ي
    # Persian/Urdu letterforms that show up in Gulf social posts
    "ی": "ي",  # ی -> ي
    "ک": "ك",  # ک -> ك
    # Arabic-Indic and Eastern Arabic-Indic digits -> ASCII
    **{chr(0x0660 + i): str(i) for i in range(10)},
    **{chr(0x06F0 + i): str(i) for i in range(10)},
    # Arabic punctuation -> ASCII so \w-based tokenizers split on it
    "،": ",",  # ،
    "؛": ";",  # ؛
    "؟": "?",  # ؟
})

# High-frequency Arabic function words and research-meta filler. Stored in
# normalized form so they match normalized tokens.
_RAW_STOPWORDS = {
    # prepositions / conjunctions / particles
    "في", "من", "الى", "إلى", "على", "عن", "مع", "او", "أو", "ثم", "حتى",
    "لكن", "بل", "ان", "أن", "إن", "كان", "كانت", "يكون", "قد", "لقد", "لا",
    "لم", "لن", "ما", "ماذا", "هل", "كيف", "لماذا", "متى", "اين", "أين",
    "كم", "اي", "أي", "التي", "الذي", "الذين", "اللذين", "هذا", "هذه",
    "ذلك", "تلك", "هناك", "هنا", "هو", "هي", "هم", "هن", "نحن", "انا", "أنا",
    "انت", "أنت", "كل", "بعض", "غير", "عند", "بين", "حول", "خلال", "بعد",
    "قبل", "منذ", "ايضا", "أيضا", "فقط", "جدا", "وفي", "ومن", "وعلى", "و",
    "ف", "ب", "ل", "ك",
    # research / meta descriptors
    "افضل", "أفضل", "احدث", "أحدث", "جديد", "جديدة", "اخبار", "أخبار",
    "اخر", "آخر", "الاخيرة", "الأخيرة", "يقول", "يقولون", "الناس", "رأي",
    "اراء", "آراء", "مراجعة", "مراجعات", "مقارنة", "نصائح", "دليل",
    "شهر", "الشهر", "يوم", "ايام", "أيام", "اسبوع", "أسبوع",
}


def has_arabic(text: str) -> bool:
    """Return True when ``text`` contains any Arabic-script character."""
    return bool(text) and bool(_ARABIC_RE.search(text))


def normalize(text: str) -> str:
    """Fold Arabic orthographic variants; leave non-Arabic text unchanged."""
    if not text or not _ARABIC_RE.search(text):
        return text
    text = _DIACRITICS_RE.sub("", text).replace(_TATWEEL, "")
    return text.translate(_CHAR_MAP)


ARABIC_STOPWORDS = frozenset(normalize(w) for w in _RAW_STOPWORDS)

# Common question/meta prefixes stripped from Arabic queries before keyword
# extraction (mirrors query.PREFIXES for English and Hebrew).
ARABIC_PREFIXES = [
    "ماذا يقول الناس عن", "ما رأي الناس في", "ما هي آخر أخبار", "ما هو آخر",
    "ما هي افضل", "ما هي أفضل", "ما هو افضل", "ما هو أفضل", "ما الجديد في",
    "ما الجديد عن", "كيف استخدم", "كيف أستخدم", "ما هي", "ما هو",
]

# Raw + normalized forms, for modules that compare un-normalized words
# (query.NOISE_WORDS filters the user's raw topic text).
ARABIC_NOISE_WORDS = frozenset(_RAW_STOPWORDS) | ARABIC_STOPWORDS
