"""
Tests for Phase 11: Decision Support & User Experience
=====================================================
Covers:
  - Checkpoint 1: F18 Deterministic Attention Score (0-100), factors, traffic light,
    boundary conditions, headline status invariance, citizen role leak protection.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import pytest
from fastapi.testclient import TestClient

from jomigraph.api.app import create_app
from jomigraph.config import (
    DISCLAIMER_ATTENTION_SCORE_BN,
    DISCLAIMER_ATTENTION_SCORE_EN,
    LABEL_ATTENTION_SCORE_BN,
    LABEL_ATTENTION_SCORE_EN,
    TRAFFIC_LIGHT_GREEN,
    TRAFFIC_LIGHT_RED,
    TRAFFIC_LIGHT_YELLOW,
)
from jomigraph.engine.rules import Alert, Status
from jomigraph.engine.scoring import (
    CITIZEN_SCORE_SUMMARY_BN,
    CITIZEN_SCORE_SUMMARY_EN,
    compute_attention_score,
)
from jomigraph.i18n import (
    MSG_CONSISTENT,
    MSG_R1_CONTRADICTION,
    MSG_R5_REVIEW_NO_LINK,
    NEXT_STEP_R1,
    NEXT_STEP_R5,
    translate,
)
from jomigraph.loader import load_dataset

REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_V11_PATH = REPO_ROOT / "data" / "demo_v11.json"
DEMO_FAMILY_PATH = REPO_ROOT / "data" / "demo_family.json"


# ===========================================================================
# Checkpoint 1: F18 Deterministic Attention Score Engine & Invariants
# ===========================================================================

def test_score_clean_parcel_scores_strictly_zero_and_green():
    """A parcel with all-Consistent alerts (or empty alerts) must score strictly 0 with green traffic light."""
    # 1. Empty alerts
    res_empty = compute_attention_score([])
    assert res_empty["score"] == 0
    assert res_empty["traffic_light"] == TRAFFIC_LIGHT_GREEN
    assert res_empty["factors"] == []
    assert res_empty["summary"] == CITIZEN_SCORE_SUMMARY_BN[TRAFFIC_LIGHT_GREEN]

    # 2. All consistent alerts
    alert_c1 = Alert(
        rule_id="R1",
        status=Status.CONSISTENT,
        message_key=MSG_CONSISTENT,
        evidence_ids=("P1",),
        calculation="Consistent",
        recommended_next_step=NEXT_STEP_R1,
    )
    alert_c2 = Alert(
        rule_id="R5",
        status=Status.CONSISTENT,
        message_key=MSG_CONSISTENT,
        evidence_ids=("P1", "SR1"),
        calculation="Consistent",
        recommended_next_step=NEXT_STEP_R5,
    )
    res_clean = compute_attention_score([alert_c1, alert_c2], lang="en")
    assert res_clean["score"] == 0
    assert res_clean["traffic_light"] == TRAFFIC_LIGHT_GREEN
    assert res_clean["factors"] == []
    assert res_clean["summary"] == CITIZEN_SCORE_SUMMARY_EN[TRAFFIC_LIGHT_GREEN]


def test_score_review_alert_yields_yellow_traffic_light():
    """A review alert yields yellow traffic light and positive score <= 100."""
    alert_rev = Alert(
        rule_id="R5",
        status=Status.REVIEW,
        message_key=MSG_R5_REVIEW_NO_LINK,
        evidence_ids=("SR1", "SR2"),
        calculation="Survey continuity gap requires review.",
        recommended_next_step=NEXT_STEP_R5,
    )
    res = compute_attention_score([alert_rev], lang="en")
    assert res["score"] == 15
    assert res["traffic_light"] == TRAFFIC_LIGHT_YELLOW
    assert len(res["factors"]) == 1
    assert res["factors"][0]["rule_id"] == "R5"
    assert res["factors"][0]["status_code"] == "REVIEW"
    assert res["factors"][0]["points"] == 15
    assert res["summary"] == CITIZEN_SCORE_SUMMARY_EN[TRAFFIC_LIGHT_YELLOW]


def test_score_contradiction_alert_yields_red_traffic_light():
    """A contradiction alert yields red traffic light and positive score <= 100."""
    alert_contra = Alert(
        rule_id="R1",
        status=Status.CONTRADICTION,
        message_key=MSG_R1_CONTRADICTION,
        evidence_ids=("E1", "SR1"),
        calculation="Excess transfer of 5 decimals.",
        recommended_next_step=NEXT_STEP_R1,
    )
    res = compute_attention_score([alert_contra], lang="en")
    assert res["score"] == 45
    assert res["traffic_light"] == TRAFFIC_LIGHT_RED
    assert len(res["factors"]) == 1
    assert res["factors"][0]["rule_id"] == "R1"
    assert res["factors"][0]["status_code"] == "CONTRADICTION"
    assert res["factors"][0]["points"] == 45
    assert res["summary"] == CITIZEN_SCORE_SUMMARY_EN[TRAFFIC_LIGHT_RED]


def test_score_boundary_duplicate_alerts_deduplicated():
    """Duplicate identical alerts must be deduplicated so points are not double counted."""
    alert_contra = Alert(
        rule_id="R1",
        status=Status.CONTRADICTION,
        message_key=MSG_R1_CONTRADICTION,
        evidence_ids=("E1", "SR1"),
        calculation="Excess transfer of 5 decimals.",
        recommended_next_step=NEXT_STEP_R1,
    )
    # Pass two identical alerts
    res = compute_attention_score([alert_contra, alert_contra])
    assert res["score"] == 45  # Not 90
    assert len(res["factors"]) == 1


def test_score_boundary_max_clamped_at_100():
    """When multiple severe contradictions fire, the score is capped strictly at 100."""
    alerts = [
        Alert(rule_id="R1", status=Status.CONTRADICTION, message_key="k1", evidence_ids=("E1",), calculation="c1", recommended_next_step=NEXT_STEP_R1),
        Alert(rule_id="R2", status=Status.CONTRADICTION, message_key="k2", evidence_ids=("E2",), calculation="c2", recommended_next_step="NEXT_STEP_R2"),
        Alert(rule_id="R11", status=Status.CONTRADICTION, message_key="k3", evidence_ids=("E3",), calculation="c3", recommended_next_step="NEXT_STEP_R11"),
    ]  # 45 + 45 + 50 = 140
    res = compute_attention_score(alerts)
    assert res["score"] == 100
    assert res["traffic_light"] == TRAFFIC_LIGHT_RED
    assert len(res["factors"]) == 3


def test_score_never_overrides_headline_status():
    """
    Score never overrides headline evaluation status.
    A parcel with R5 review has headline status 'Review Required' even if score is 15.
    A parcel with R1 contradiction has headline status 'Contradiction Found' even if score is 45.
    """
    app = create_app(dataset_path=str(DEMO_V11_PATH))
    client = TestClient(app)

    # 1. Clean parcel
    resp_clean = client.get("/parcel/PARCEL_CLEAN_R8?role=reviewer&lang=en")
    assert resp_clean.status_code == 200
    data_clean = resp_clean.json()
    assert data_clean["overall_status"] == "Consistent with supplied records"
    assert data_clean["overall_status_code"] == "CONSISTENT"
    assert data_clean["attention_score"] == 0
    assert data_clean["traffic_light"] == "green"

    # 2. Planted contradiction parcel
    resp_planted = client.get("/parcel/PARCEL_PLANTED_R8?role=reviewer&lang=en")
    assert resp_planted.status_code == 200
    data_planted = resp_planted.json()
    assert data_planted["overall_status"] == "Contradiction Found"
    assert data_planted["overall_status_code"] == "CONTRADICTION"
    assert data_planted["attention_score"] > 0
    assert data_planted["traffic_light"] == "red"
    assert isinstance(data_planted["score_factors"], list)
    assert len(data_planted["score_factors"]) > 0


def test_score_citizen_role_leak_protection():
    """Citizen view receives score, traffic light, and plain summary, but NEVER raw factors or rule IDs."""
    app = create_app(dataset_path=str(DEMO_V11_PATH))
    client = TestClient(app)

    # Parcel detail
    resp = client.get("/parcel/PARCEL_PLANTED_R8?role=citizen&lang=en")
    assert resp.status_code == 200
    data = resp.json()
    assert "attention_score" in data
    assert "traffic_light" in data
    assert "score_summary" in data
    assert "score_disclaimer" in data
    assert "score_factors" not in data
    assert "factors" not in data

    # Verify score_summary has no rule IDs
    assert "[R" not in data["score_summary"]


def test_score_simulation_and_report_endpoints():
    """Simulation and Report endpoints include attention score and traffic light."""
    app = create_app(dataset_path=str(DEMO_V11_PATH))
    client = TestClient(app)

    # Simulation reviewer view
    sim_payload = {
        "parcel_id": "PARCEL_CLEAN_R8",
        "from_person": "P_V11_JALIL_SON",
        "to_person": "P_BUYER",
        "area": "1",
        "date": "2024-06-01",
    }
    resp_sim = client.post("/simulate?role=reviewer&lang=en", json=sim_payload)
    assert resp_sim.status_code == 200
    sim_data = resp_sim.json()
    assert "attention_score" in sim_data
    assert "traffic_light" in sim_data
    assert "score_factors" in sim_data

    # Report reviewer view
    resp_rep = client.get("/report/PARCEL_PLANTED_R8?role=reviewer&lang=en")
    assert resp_rep.status_code == 200
    rep_data = resp_rep.json()
    assert "attention_score" in rep_data
    assert "traffic_light" in rep_data
    assert "score_factors" in rep_data


def test_score_forbidden_words_audit():
    """
    Ensure zero forbidden words in attention score labels, disclaimers, and citizen summaries.
    Forbidden words: safe, valid, legal, verified owner, fraud, forged, scam, you will be cheated,
                     জালিয়াতি, আইনগত, বৈধ
    """
    forbidden_en = [
        r"\bsafe\b",
        r"\bvalid\b",
        r"\blegal\b",
        r"\bverified owner\b",
        r"\bfraud\b",
        r"\bforged\b",
        r"\bscam\b",
        r"\byou will be cheated\b",
    ]
    forbidden_bn = ["জালিয়াতি", "আইনগত", "বৈধ"]

    en_texts = [
        LABEL_ATTENTION_SCORE_EN,
        DISCLAIMER_ATTENTION_SCORE_EN,
        CITIZEN_SCORE_SUMMARY_EN[TRAFFIC_LIGHT_GREEN],
        CITIZEN_SCORE_SUMMARY_EN[TRAFFIC_LIGHT_YELLOW],
        CITIZEN_SCORE_SUMMARY_EN[TRAFFIC_LIGHT_RED],
    ]
    bn_texts = [
        LABEL_ATTENTION_SCORE_BN,
        DISCLAIMER_ATTENTION_SCORE_BN,
        CITIZEN_SCORE_SUMMARY_BN[TRAFFIC_LIGHT_GREEN],
        CITIZEN_SCORE_SUMMARY_BN[TRAFFIC_LIGHT_YELLOW],
        CITIZEN_SCORE_SUMMARY_BN[TRAFFIC_LIGHT_RED],
    ]

    for text in en_texts:
        for f in forbidden_en:
            assert not re.search(f, text, re.IGNORECASE), f"Forbidden English term '{f}' found in: {text}"

    for text in bn_texts:
        for f in forbidden_bn:
            assert f not in text, f"Forbidden Bengali term '{f}' found in: {text}"


# ===========================================================================
# Checkpoint 3: X3 Rule-Specific Next-Step Guides (R1–R15)
# ===========================================================================

from jomigraph.engine.next_steps import (
    DISCLAIMER_LAW_MENTOR_BN,
    DISCLAIMER_LAW_MENTOR_EN,
    RULE_NEXT_STEPS_BN,
    RULE_NEXT_STEPS_EN,
    get_rule_next_steps,
)


def test_next_steps_all_rules_covered():
    """All rules R1-R15 and HYGIENE must provide 2-4 concrete actionable checks."""
    all_rules = [f"R{i}" for i in range(1, 16)] + ["HYGIENE"]
    for r in all_rules:
        guide_bn = get_rule_next_steps(r, lang="bn")
        guide_en = get_rule_next_steps(r, lang="en")

        assert guide_bn["rule_id"] == r
        assert guide_en["rule_id"] == r

        # 2 to 4 concrete steps
        assert 2 <= len(guide_bn["steps"]) <= 4, f"Rule {r} BN steps count {len(guide_bn['steps'])} not between 2 and 4"
        assert 2 <= len(guide_en["steps"]) <= 4, f"Rule {r} EN steps count {len(guide_en['steps'])} not between 2 and 4"
        assert len(guide_bn["steps"]) == len(guide_en["steps"]), f"Rule {r} step count mismatch between BN and EN"

        # Disclaimer included
        assert len(guide_bn["disclaimer"]) > 0
        assert len(guide_en["disclaimer"]) > 0
        assert "Law mentor" in guide_en["disclaimer"]


def test_next_steps_fallback_behavior():
    """Unknown or empty rule IDs fall back gracefully without raising an exception."""
    for unknown in ["R999", "UNKNOWN", "", None]:
        guide_bn = get_rule_next_steps(unknown, lang="bn")  # type: ignore[arg-type]
        guide_en = get_rule_next_steps(unknown, lang="en")  # type: ignore[arg-type]

        assert isinstance(guide_bn["steps"], list)
        assert len(guide_bn["steps"]) >= 2
        assert isinstance(guide_en["steps"], list)
        assert len(guide_en["steps"]) >= 2


def test_next_steps_forbidden_words_audit():
    """All rule next-step guides and disclaimers must have zero forbidden words."""
    forbidden_en = [
        r"\bsafe\b",
        r"\bvalid\b",
        r"\blegal\b",
        r"\bverified owner\b",
        r"\bfraud\b",
        r"\bforged\b",
        r"\bscam\b",
        r"\byou will be cheated\b",
    ]
    forbidden_bn = ["জালিয়াতি", "আইনগত", "বৈধ"]

    all_rules = [f"R{i}" for i in range(1, 16)] + ["HYGIENE"]
    for r in all_rules:
        guide_en = get_rule_next_steps(r, lang="en")
        guide_bn = get_rule_next_steps(r, lang="bn")

        for step in guide_en["steps"]:
            for f in forbidden_en:
                assert not re.search(f, step, re.IGNORECASE), f"Forbidden word '{f}' in {r} EN step: {step}"

        for step in guide_bn["steps"]:
            for f in forbidden_bn:
                assert f not in step, f"Forbidden word '{f}' in {r} BN step: {step}"

    for f in forbidden_en:
        assert not re.search(f, DISCLAIMER_LAW_MENTOR_EN, re.IGNORECASE)
    for f in forbidden_bn:
        assert f not in DISCLAIMER_LAW_MENTOR_BN


def test_next_steps_api_endpoint():
    """GET /next-steps/{rule_id} returns 200 with steps and disclaimer."""
    app = create_app(dataset_path=str(DEMO_V11_PATH))
    client = TestClient(app)

    resp = client.get("/next-steps/R8?lang=bn")
    assert resp.status_code == 200
    data = resp.json()
    assert data["rule_id"] == "R8"
    assert len(data["steps"]) >= 2
    assert "disclaimer" in data


# ===========================================================================
# Checkpoint 4: X4 USSD / Feature-Phone Simulator
# ===========================================================================

from jomigraph.engine.ussd import DEMO_USSD_CODE, MAX_USSD_CHARS, process_ussd_step


def test_ussd_flow_complete_and_length_limit():
    """USSD flow (language -> mouza -> dag -> result) completes with every screen <= 160 chars."""
    ds = load_dataset(DEMO_V11_PATH)

    # Step 1: Initial dial *123*45#
    res1 = process_ussd_step("*123*45#", ds)
    assert res1["action"] == "CON"
    assert res1["screen"] == "welcome"
    assert res1["character_count"] <= MAX_USSD_CHARS
    assert DEMO_USSD_CODE in res1["message"]

    # Step 2: Language choice 1 (Bangla)
    res2 = process_ussd_step("1", ds)
    assert res2["action"] == "CON"
    assert res2["screen"] == "mouza"
    assert res2["character_count"] <= MAX_USSD_CHARS
    assert "মৌজা" in res2["message"]

    # Step 3: Mouza input
    res3 = process_ussd_step("1*রূপনগর", ds)
    assert res3["action"] == "CON"
    assert res3["screen"] == "dag"
    assert res3["character_count"] <= MAX_USSD_CHARS
    assert "দাগ নম্বর" in res3["message"]

    # Step 4: Dag input
    # In demo_v11.json, PARCEL_CLEAN_R8 is Rupnagar dag 101 or similar
    p_clean = ds.get_parcel("PARCEL_CLEAN_R8")
    assert p_clean is not None
    res4 = process_ussd_step(f"1*{p_clean.mouza}*{p_clean.dag_no}", ds)
    assert res4["action"] == "END"
    assert res4["screen"] == "result"
    assert res4["character_count"] <= MAX_USSD_CHARS
    assert "স্কোর" in res4["message"]
    # Verify no internal rule IDs leak into citizen USSD output
    assert "[R" not in res4["message"]


def test_ussd_english_flow_and_not_found():
    """USSD English flow and graceful handling of unknown dag numbers."""
    ds = load_dataset(DEMO_V11_PATH)

    # Step 2: Language choice 2 (English)
    res2 = process_ussd_step("2", ds)
    assert res2["action"] == "CON"
    assert res2["screen"] == "mouza"
    assert res2["lang"] == "en"
    assert res2["character_count"] <= MAX_USSD_CHARS

    # Unknown dag
    res_unknown = process_ussd_step("2*Rupnagar*99999", ds)
    assert res_unknown["action"] == "END"
    assert res_unknown["screen"] == "not_found"
    assert res_unknown["character_count"] <= MAX_USSD_CHARS
    assert "not found" in res_unknown["message"].lower()


def test_ussd_cancellation_with_zero():
    """User entering 0 terminates the USSD session gracefully."""
    ds = load_dataset(DEMO_V11_PATH)
    res = process_ussd_step("1*0", ds)
    assert res["action"] == "END"
    assert res["screen"] == "cancelled"
    assert res["character_count"] <= MAX_USSD_CHARS


def test_ussd_api_endpoint():
    """POST /ussd returns HTTP 200 with conforming schema and <= 160 characters."""
    app = create_app(dataset_path=str(DEMO_V11_PATH))
    client = TestClient(app)

    payload = {"text": "*123*45#", "phone_number": "01712345678"}
    resp = client.post("/ussd", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["action"] == "CON"
    assert data["character_count"] <= 160
    assert len(data["message"]) <= 160
    assert DEMO_USSD_CODE in data["message"]


# ===========================================================================
# Checkpoint 5: X5 Digital Vetting Certificate
# ===========================================================================

def test_certificate_data_and_qr_inclusion():
    """
    Digital Vetting Certificate report endpoint returns:
      - Parcel summary
      - Three-status result unaltered
      - Attention score and explanation
      - Dataset / records hash
      - QR payload for supported verification workflow
      - Standard non-judicial advisory disclaimer
    """
    app = create_app(dataset_path=str(DEMO_V11_PATH))
    client = TestClient(app)

    resp = client.get("/report/PARCEL_PLANTED_R8?role=citizen&lang=en")
    assert resp.status_code == 200
    data = resp.json()

    # 1. Parcel summary
    assert "parcel" in data
    assert data["parcel"]["dag_no"] is not None
    assert data["parcel"]["mouza"] is not None

    # 2. Three-status result unaltered
    assert data["overall_status"] in (
        "Consistent with supplied records",
        "Review Required",
        "Contradiction Found",
    )
    assert data["overall_status_code"] in ("CONSISTENT", "REVIEW", "CONTRADICTION")

    # 3. Attention score
    assert "attention_score" in data
    assert isinstance(data["attention_score"], int)
    assert 0 <= data["attention_score"] <= 100
    assert "traffic_light" in data
    assert data["traffic_light"] in ("green", "yellow", "red")

    # 4. Relevant record hash
    assert "dataset_hash" in data
    assert len(data["dataset_hash"]) == 64

    # 5. QR code payload for supported verification
    assert "certificate_qr_payload" in data
    assert data["certificate_qr_payload"] is not None
    assert data["certificate_qr_payload"].startswith("#/verify-deed")

    # 6. Standard non-judicial disclaimer
    assert "disclaimer" in data
    assert len(data["disclaimer"]) > 0
    assert "not a legal ruling" in data["disclaimer"].lower()


# ===========================================================================
# Checkpoint 2: X2 Offline Bangla Voice Speech Synthesis & Fallback Verification
# ===========================================================================

def test_offline_voice_ui_implementation_and_fallback():
    """
    Verify X2 implementation in app.js:
      - Uses browser speechSynthesis and SpeechSynthesisUtterance.
      - Prioritizes bn-BD, then bn-IN.
      - Gracefully falls back to on-screen text when voice/API is unavailable.
      - Handles repeated clicks via cancel().
      - Introduces zero network/cloud speech dependencies.
    """
    app_js_path = REPO_ROOT / "src" / "jomigraph" / "ui" / "app.js"
    assert app_js_path.exists(), "app.js must exist"
    content = app_js_path.read_text(encoding="utf-8")

    # 1. Inspect function definition
    assert "function speakResult(" in content
    # 2. Check browser API check and graceful fallback
    assert "speechSynthesis" in content
    assert "SpeechSynthesisUtterance" in content
    assert "voice_fallback_msg" in content
    # 3. Check voice priority: bn-BD then bn-IN
    assert "bn-BD" in content
    assert "bn-IN" in content
    # 4. Repeated clicks handled via cancel
    assert "speechSynthesis.cancel()" in content
    # 5. Zero cloud speech network dependencies
    assert "googleapis" not in content.lower()
    assert "texttospeech" not in content.lower()
    assert "elevenlabs" not in content.lower()
    assert "azure" not in content.lower()


# ===========================================================================
# Checkpoint 5: Print Styles and Certificate Verification
# ===========================================================================

def test_print_css_excludes_navigation_and_buttons():
    """
    Verify style.css @media print rule excludes all navigation, buttons, and app-root.
    """
    css_path = REPO_ROOT / "src" / "jomigraph" / "ui" / "style.css"
    assert css_path.exists(), "style.css must exist"
    content = css_path.read_text(encoding="utf-8")

    assert "@media print" in content
    print_section = content.split("@media print")[1]

    # Exclude nav, buttons, header, inputs
    assert "#app-root" in print_section
    assert ".app-header" in print_section
    assert "button" in print_section
    assert "display: none !important" in print_section
    assert "#print-modal-container" in print_section


def test_ussd_simulator_contract_in_extras_js():
    """
    Verify X4 USSD simulator in extras.js:
      - *123*45# code
      - 160 character limit display
      - Dedicated screen and cancel / restart buttons
    """
    extras_js_path = REPO_ROOT / "src" / "jomigraph" / "ui" / "extras.js"
    assert extras_js_path.exists(), "extras.js must exist"
    content = extras_js_path.read_text(encoding="utf-8")

    assert "ussdSimulatorScreen" in content
    assert "*123*45#" in content
    assert "/ussd" in content
    assert "160" in content


# ===========================================================================
# Comprehensive Verification: Dataset Baseline Invariance & Full Audit
# ===========================================================================

def test_demo_family_baseline_dataset_hash_invariant():
    """
    The normalized baseline dataset hash for demo_family.json must remain exactly:
    b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01
    """
    from jomigraph.engine.simulate import hash_dataset

    ds = load_dataset(str(DEMO_FAMILY_PATH))
    all_events = [e for h in ds.histories for e in h.events]
    all_srs = [sr for h in ds.histories for sr in h.survey_records]

    computed = hash_dataset(all_events, all_srs)
    expected = "b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01"
    assert computed == expected, f"Baseline hash modified! Expected {expected}, got {computed}"
