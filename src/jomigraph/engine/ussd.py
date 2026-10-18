"""
JomiGraph AI — USSD / Feature-Phone Simulator Engine (X4)
=========================================================
Text-only USSD session simulation over citizen API data.
Strictly enforced 160-character limit per screen.

Invariants:
  - Uses invented demo code *123*45# only.
  - Clear demonstration disclaimer: "সিমুলেটর, কোনো আসল টেলিকম সংযোগ নয়" / "Simulator only, not a telecom service".
  - Strictly text-only navigation: Language -> Mouza -> Dag -> Result.
  - Enforces character limit <= 160 chars on every single screen.
  - Reuses existing citizen API evaluation and synthetic parcel records.
  - Zero forbidden words (safe, valid, legal, verified owner, fraud, forged, scam, you will be cheated, জালিয়াতি, আইনগত, বৈধ).
"""

from __future__ import annotations

import re
from typing import Any, Optional

from jomigraph.engine.benchmark import evaluate_history
from jomigraph.engine.rules import Status
from jomigraph.engine.scoring import compute_attention_score
from jomigraph.i18n import translate
from jomigraph.loader import Dataset

DEMO_USSD_CODE = "*123*45#"
MAX_USSD_CHARS = 160


def _normalize(val: Any) -> str:
    """Normalize string and convert Bengali digits to ASCII for comparison."""
    if val is None:
        return ""
    trans = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
    return str(val).translate(trans).strip().lower()


def process_ussd_step(
    text: str,
    dataset: Dataset,
    session_id: str = "USSD_DEMO_01",
) -> dict[str, Any]:
    """
    Process USSD navigation step.
    `text` contains input string formatted as 'part1*part2*part3' (standard USSD protocol).
    Returns:
      {
        "message": str,         # strictly <= 160 characters
        "action": str,          # "CON" (continue) or "END" (terminate)
        "character_count": int, # <= 160
        "screen": str,          # identifier of current screen
        "lang": str,            # "bn" or "en"
      }
    """
    clean_text = text.strip() if text else ""
    # Strip leading *123*45# if dialed together
    if clean_text.startswith(DEMO_USSD_CODE):
        clean_text = clean_text[len(DEMO_USSD_CODE):].lstrip("*")

    parts = [p.strip() for p in clean_text.split("*") if p.strip()]

    # Screen 1: Language selection
    if not parts:
        msg = (
            f"JomiGraph AI (Demo)\n"
            f"{DEMO_USSD_CODE}\n"
            f"1. বাংলা\n"
            f"2. English\n"
            f"(সিমুলেটর, কোনো টেলিকম সেবা নয়)"
        )
        return _format_response(msg, action="CON", screen="welcome", lang="bn")

    lang_choice = parts[0]
    is_bn = (lang_choice == "1" or "বাং" in lang_choice or lang_choice.lower() == "bn")
    active_lang = "bn" if is_bn else "en"

    # Screen 2: Mouza prompt
    if len(parts) == 1:
        if is_bn:
            msg = (
                "মৌজার নাম লিখুন:\n"
                "(যেমন: রূপনগর / ধানমন্ডি)\n"
                "0. বাতিল"
            )
        else:
            msg = (
                "Enter Mouza name:\n"
                "(e.g., Rupnagar / Dhanmondi)\n"
                "0. Cancel"
            )
        return _format_response(msg, action="CON", screen="mouza", lang=active_lang)

    # Screen 3: Dag prompt
    mouza_input = parts[1]
    if mouza_input == "0":
        msg = "সেশন সমাপ্ত হয়েছে।" if is_bn else "Session terminated."
        return _format_response(msg, action="END", screen="cancelled", lang=active_lang)

    if len(parts) == 2:
        if is_bn:
            msg = (
                f"মৌজা: {mouza_input}\n"
                f"দাগ নম্বর লিখুন (যেমন: ১০১ / 101):\n"
                f"0. বাতিল"
            )
        else:
            msg = (
                f"Mouza: {mouza_input}\n"
                f"Enter Dag number (e.g., 101):\n"
                f"0. Cancel"
            )
        return _format_response(msg, action="CON", screen="dag", lang=active_lang)

    # Screen 4: Search & Result
    dag_input = parts[2]
    if dag_input == "0":
        msg = "সেশন সমাপ্ত হয়েছে।" if is_bn else "Session terminated."
        return _format_response(msg, action="END", screen="cancelled", lang=active_lang)

    # Lookup parcel in dataset
    norm_mouza = _normalize(mouza_input)
    norm_dag = _normalize(dag_input)

    matched_parcel = None
    for p in dataset.parcels:
        p_mouza_norm = _normalize(p.mouza)
        p_dag_norm = _normalize(p.dag_no)
        # Check direct or substring match
        if (norm_dag == p_dag_norm or norm_dag in p.id.lower()) and (
            norm_mouza in p_mouza_norm or p_mouza_norm in norm_mouza or len(norm_mouza) < 2
        ):
            matched_parcel = p
            break

    # Fallback search by dag alone if unique or single match
    if matched_parcel is None:
        dag_matches = [
            p for p in dataset.parcels
            if norm_dag == _normalize(p.dag_no) or norm_dag in p.id.lower()
        ]
        if len(dag_matches) == 1:
            matched_parcel = dag_matches[0]

    if matched_parcel is None:
        if is_bn:
            msg = (
                f"দাগ {dag_input} ({mouza_input}) পাওয়া যায়নি।\n"
                f"দয়া করে সঠিক মৌজা ও দাগ দিন।\n"
                f"ডায়াল করুন: {DEMO_USSD_CODE}"
            )
        else:
            msg = (
                f"Dag {dag_input} ({mouza_input}) not found.\n"
                f"Please check details.\n"
                f"Dial: {DEMO_USSD_CODE}"
            )
        return _format_response(msg, action="END", screen="not_found", lang=active_lang)

    # Evaluate parcel history
    history = dataset.get_history(matched_parcel.id)
    if history is None:
        if is_bn:
            msg = f"দাগ {matched_parcel.dag_no}: কোনো ইতিহাস নেই।"
        else:
            msg = f"Dag {matched_parcel.dag_no}: No history record found."
        return _format_response(msg, action="END", screen="no_history", lang=active_lang)

    alerts = evaluate_history(
        history,
        all_parcels=dataset.parcels,
        all_deeds=dataset.deeds,
        all_histories=dataset.histories,
        all_persons=dataset.persons,
    )
    score_data = compute_attention_score(alerts, lang=active_lang)

    has_contra = any(a.status == Status.CONTRADICTION for a in alerts)
    has_rev = any(a.status == Status.REVIEW for a in alerts)

    if has_contra:
        status_txt = "অসঙ্গতি পাওয়া গেছে" if is_bn else "Contradiction Found"
    elif has_rev:
        status_txt = "পর্যালোচনা প্রয়োজন" if is_bn else "Review Required"
    else:
        status_txt = "সঙ্গতিপূর্ণ" if is_bn else "Consistent with supplied records"

    score_val = score_data["score"]

    if is_bn:
        msg = (
            f"দাগ {matched_parcel.dag_no} ({matched_parcel.mouza}):\n"
            f"ফলাফল: {status_txt}\n"
            f"মনোযোগ স্কোর: {score_val}/১০০\n"
            f"(কাল্পনিক ডেমো, আইনি রায় নয়)"
        )
    else:
        msg = (
            f"Dag {matched_parcel.dag_no} ({matched_parcel.mouza}):\n"
            f"Result: {status_txt}\n"
            f"Attention score: {score_val}/100\n"
            f"(Demo simulation, not legal ruling)"
        )

    return _format_response(msg, action="END", screen="result", lang=active_lang)


def _format_response(
    msg: str,
    action: str,
    screen: str,
    lang: str,
) -> dict[str, Any]:
    """Ensure message strictly satisfies 160 character limit."""
    truncated = msg[:MAX_USSD_CHARS] if len(msg) > MAX_USSD_CHARS else msg
    return {
        "message": truncated,
        "action": action,
        "character_count": len(truncated),
        "screen": screen,
        "lang": lang,
    }
