"""
JomiGraph AI — Internationalization (i18n)
===========================================
Message keys and recommended next-step keys for rules R1-R7.
Rule outputs store key strings only; human-readable text is loaded from
locales/bn.json and locales/en.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

# Next-step keys
NEXT_STEP_R1 = "NEXT_STEP_R1"
NEXT_STEP_R2 = "NEXT_STEP_R2"
NEXT_STEP_R3 = "NEXT_STEP_R3"
NEXT_STEP_R4 = "NEXT_STEP_R4"
NEXT_STEP_R5 = "NEXT_STEP_R5"
NEXT_STEP_R6 = "NEXT_STEP_R6"
NEXT_STEP_R7 = "NEXT_STEP_R7"
NEXT_STEP_REVIEW_HISTORY = "NEXT_STEP_REVIEW_HISTORY"

NEXT_STEP_BY_RULE: dict[str, str] = {
    "R1": NEXT_STEP_R1,
    "R2": NEXT_STEP_R2,
    "R3": NEXT_STEP_R3,
    "R4": NEXT_STEP_R4,
    "R5": NEXT_STEP_R5,
    "R6": NEXT_STEP_R6,
    "R7": NEXT_STEP_R7,
}

# Message keys
MSG_CONSISTENT = "MSG_CONSISTENT"
MSG_R1_CONTRADICTION = "MSG_R1_CONTRADICTION"
MSG_R1_REVIEW_INCOMPLETE_BASELINE = "MSG_R1_REVIEW_INCOMPLETE_BASELINE"
MSG_R1_REVIEW_INPUTS = "MSG_R1_REVIEW_INPUTS"
MSG_R2_CONTRADICTION = "MSG_R2_CONTRADICTION"
MSG_R2_REVIEW_UNESTABLISHED = "MSG_R2_REVIEW_UNESTABLISHED"
MSG_R2_REVIEW_INPUTS = "MSG_R2_REVIEW_INPUTS"
MSG_R3_CONTRADICTION = "MSG_R3_CONTRADICTION"
MSG_R3_REVIEW_INCOMPLETE_BASELINE = "MSG_R3_REVIEW_INCOMPLETE_BASELINE"
MSG_R3_REVIEW_INPUTS = "MSG_R3_REVIEW_INPUTS"
MSG_R4_CONTRADICTION = "MSG_R4_CONTRADICTION"
MSG_R4_REVIEW_TOLERANCE = "MSG_R4_REVIEW_TOLERANCE"
MSG_R4_REVIEW_MISSING_CHILDREN = "MSG_R4_REVIEW_MISSING_CHILDREN"
MSG_R4_REVIEW_INPUTS = "MSG_R4_REVIEW_INPUTS"
MSG_R5_CONSISTENT = "MSG_R5_CONSISTENT"
MSG_R5_REVIEW_NO_LINK = "MSG_R5_REVIEW_NO_LINK"
MSG_R6_CONSISTENT = "MSG_R6_CONSISTENT"
MSG_R6_REVIEW_MISMATCH = "MSG_R6_REVIEW_MISMATCH"
MSG_R6_REVIEW_MISSING_DEED = "MSG_R6_REVIEW_MISSING_DEED"
MSG_R7_CONTRADICTION = "MSG_R7_CONTRADICTION"
MSG_R7_CONSISTENT = "MSG_R7_CONSISTENT"
MSG_R7_REVIEW_MISSING_LINK_OR_DATE = "MSG_R7_REVIEW_MISSING_LINK_OR_DATE"
MSG_REVIEW_UNDATED_HISTORY = "MSG_REVIEW_UNDATED_HISTORY"
MSG_REVIEW_UNSUPPORTED_HISTORY = "MSG_REVIEW_UNSUPPORTED_HISTORY"

# Locale file directory discovery
_LOCALES_DIR = Path(__file__).resolve().parent.parent.parent / "locales"
_TRANSLATION_CACHE: dict[str, dict[str, str]] = {}


def load_translations(lang: str = "bn") -> dict[str, str]:
    """Load translation JSON for 'bn' or 'en'."""
    if lang in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[lang]

    path = _LOCALES_DIR / f"{lang}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Translation file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _TRANSLATION_CACHE[lang] = data
    return data


def translate(key: str, lang: str = "bn") -> str:
    """Resolve key to localized string, returning key itself if missing."""
    translations = load_translations(lang)
    return translations.get(key, key)
