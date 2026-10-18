"""
JomiGraph AI — Attention Scoring (F18)
=====================================
Deterministic 0–100 integer attention score computed from fired alerts using
configured rule and status weights in config.py.

Invariants:
  - Pure function: takes alerts (and optional language), returns deterministic score dict.
  - Consistent headline parity: A parcel with all-Consistent alerts (or no alerts) scores strictly 0.
  - Headline status invariant: Headline status is never replaced or altered by scoring.
  - Traffic light derived from status first:
      CONTRADICTION -> red
      REVIEW -> yellow
      CONSISTENT -> green
  - Reviewer sees: score, traffic_light, factors (rule_id, status, points, evidence_ids).
  - Citizen sees: score, traffic_light, score_summary (plain language sentence).
    Never internal rule IDs or calculations.
  - Zero forbidden words in any user-visible strings.
"""

from __future__ import annotations

from typing import Any, Sequence

from jomigraph.config import (
    ATTENTION_RULE_WEIGHTS,
    ATTENTION_STATUS_BASE_WEIGHTS,
    DISCLAIMER_ATTENTION_SCORE_BN,
    DISCLAIMER_ATTENTION_SCORE_EN,
    LABEL_ATTENTION_SCORE_BN,
    LABEL_ATTENTION_SCORE_EN,
    TRAFFIC_LIGHT_GREEN,
    TRAFFIC_LIGHT_RED,
    TRAFFIC_LIGHT_YELLOW,
)
from jomigraph.engine.rules import Alert, Status

# Plain-language citizen sentences by traffic light (strictly zero forbidden words)
CITIZEN_SCORE_SUMMARY_EN: dict[str, str] = {
    TRAFFIC_LIGHT_GREEN: "No flags were found in the supplied records.",
    TRAFFIC_LIGHT_YELLOW: "Important items require manual review and verification.",
    TRAFFIC_LIGHT_RED: "Contradictions were found in the recorded transaction chain.",
}

CITIZEN_SCORE_SUMMARY_BN: dict[str, str] = {
    TRAFFIC_LIGHT_GREEN: "সরবরাহকৃত রেকর্ডে কোনো ফ্ল্যাগ পাওয়া যায়নি।",
    TRAFFIC_LIGHT_YELLOW: "গুরুত্বপূর্ণ বিষয়গুলো যাচাই ও পর্যালোচনা করা প্রয়োজন।",
    TRAFFIC_LIGHT_RED: "রেকর্ডকৃত লেনদেন ধারায় অসঙ্গতি পাওয়া গেছে।",
}


def compute_attention_score(
    alerts: Sequence[Alert],
    lang: str = "bn",
) -> dict[str, Any]:
    """
    Compute deterministic integer attention score (0–100) and factors.
    Returns:
      {
        "score": int,                 # 0 to 100
        "traffic_light": str,         # "green" | "yellow" | "red"
        "factors": list[dict],        # for reviewer view
        "summary": str,               # for citizen view (plain sentence)
        "disclaimer": str,            # standard score disclaimer
        "label": str,                 # localized "Attention score" label
      }
    """
    disclaimer = (
        DISCLAIMER_ATTENTION_SCORE_BN if lang == "bn" else DISCLAIMER_ATTENTION_SCORE_EN
    )
    label = (
        LABEL_ATTENTION_SCORE_BN if lang == "bn" else LABEL_ATTENTION_SCORE_EN
    )

    # 1. Base clean case: all consistent or no alerts -> strictly 0 points and green
    non_consistent = [a for a in alerts if a.status != Status.CONSISTENT]
    if not non_consistent:
        return {
            "score": 0,
            "traffic_light": TRAFFIC_LIGHT_GREEN,
            "factors": [],
            "summary": (
                CITIZEN_SCORE_SUMMARY_BN[TRAFFIC_LIGHT_GREEN]
                if lang == "bn"
                else CITIZEN_SCORE_SUMMARY_EN[TRAFFIC_LIGHT_GREEN]
            ),
            "disclaimer": disclaimer,
            "label": label,
        }

    # 2. Determine traffic light from status first (Contradiction > Review)
    has_contradiction = any(a.status == Status.CONTRADICTION for a in non_consistent)
    traffic_light = TRAFFIC_LIGHT_RED if has_contradiction else TRAFFIC_LIGHT_YELLOW

    # 3. Deduplicate exact identical alerts: (rule_id, status.name, evidence_ids_tuple)
    seen_alerts: set[tuple[str, str, tuple[str, ...]]] = set()
    factors: list[dict[str, Any]] = []

    for a in non_consistent:
        ev_key = tuple(sorted(a.evidence_ids))
        dedup_key = (a.rule_id, a.status.name, ev_key)
        if dedup_key in seen_alerts:
            continue
        seen_alerts.add(dedup_key)

        if a.status == Status.CONTRADICTION:
            points = ATTENTION_RULE_WEIGHTS.get(
                a.rule_id,
                ATTENTION_STATUS_BASE_WEIGHTS.get("CONTRADICTION", 40),
            )
        elif a.status == Status.REVIEW:
            base_rev = ATTENTION_STATUS_BASE_WEIGHTS.get("REVIEW", 15)
            rule_w = ATTENTION_RULE_WEIGHTS.get(a.rule_id, base_rev)
            # Ensure Contradiction weight strictly exceeds Review weight
            points = min(rule_w, base_rev) if rule_w > base_rev else rule_w
        else:
            points = 0

        factors.append({
            "rule_id": a.rule_id,
            "status": a.status.value,
            "status_code": a.status.name,
            "points": points,
            "evidence_ids": list(a.evidence_ids),
        })

    # 4. Sum and clamp between 0 and 100
    raw_score = sum(f["points"] for f in factors)
    score = min(100, max(0, raw_score))

    summary = (
        CITIZEN_SCORE_SUMMARY_BN[traffic_light]
        if lang == "bn"
        else CITIZEN_SCORE_SUMMARY_EN[traffic_light]
    )

    return {
        "score": score,
        "traffic_light": traffic_light,
        "factors": factors,
        "summary": summary,
        "disclaimer": disclaimer,
        "label": label,
    }
