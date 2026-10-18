"""
Tests for Phase 9: Encumbrances, Power of Attorney & Government/Court Locks
===========================================================================
Covers:
  - Task A (R11 / F17): Government and Court Locks (khas, acquisition, pending case, injunction).
  - Task B (R9): Active Mortgage Encumbrance & Release Validation (non-transferring, double mortgage, release chronology).
  - Task C (R10): Power of Attorney Authority & Revocation (POA_GRANT, POA_REVOKE, via_poa_id, tricky clean case where revocation is after sale).
  - Pure simulation & API schemas integration.
  - Baseline SHA-256 hash invariance.
  - Localization parity & zero forbidden words.
"""

from __future__ import annotations

from datetime import date
from fractions import Fraction
import json
from pathlib import Path
import re
from typing import Optional

import pytest
from fastapi.testclient import TestClient

from jomigraph.api.app import create_app
from jomigraph.api.schemas import SimulateRequest
from jomigraph.engine.replay import compute_state, replay_up_to
from jomigraph.engine.rules import (
    Status,
    check_r9,
    check_r10,
    check_r11,
    dispatch_event_rules,
    dispatch_history_rules,
)
from jomigraph.engine.simulate import hash_dataset, simulate
from jomigraph.i18n import (
    MSG_R9_CONSISTENT,
    MSG_R9_CONTRADICTION_MORTGAGE_ACTIVE,
    MSG_R9_CONTRADICTION_SECOND_MORTGAGE,
    MSG_R9_REVIEW_MISSING_DATE_OR_LINK,
    MSG_R10_CONSISTENT,
    MSG_R10_CONTRADICTION_MISSING_GRANT,
    MSG_R10_CONTRADICTION_REVOKED,
    MSG_R10_REVIEW_MISSING_DATE_OR_SCOPE,
    MSG_R11_CONSISTENT,
    MSG_R11_CONTRADICTION_GOV_LOCK,
    MSG_R11_REVIEW_COURT_OR_INJUNCTION,
    MSG_R11_REVIEW_MISSING_FLAG_DATE,
    translate,
)
from jomigraph.loader import load_dataset
from jomigraph.models import Event, EventType, Parcel, ParcelHistory, SurveyRecord

REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_FAMILY_PATH = REPO_ROOT / "data" / "demo_family.json"
DEMO_V11_PATH = REPO_ROOT / "data" / "demo_v11.json"
LOCALES_DIR = REPO_ROOT / "locales"


def make_event(
    id: str,
    type: EventType,
    seq: int = 1,
    event_date: Optional[date] = date(2021, 5, 10),
    parcel_id: str = "P_TEST_01",
    from_person: Optional[str] = "P_OWNER_1",
    to_person: Optional[str] = "P_BUYER",
    area: Optional[Fraction] = Fraction(5),
    deed_id: Optional[str] = None,
    portion_id: Optional[str] = None,
    linked_event_id: Optional[str] = None,
    source_record_id: Optional[str] = None,
    portion: Optional[dict] = None,
    boundary: Optional[str | dict] = None,
    via_poa_id: Optional[str] = None,
) -> Event:
    return Event(
        id=id,
        type=type,
        seq=seq,
        event_date=event_date,
        parcel_id=parcel_id,
        from_person=from_person,
        to_person=to_person,
        area=area,
        deed_id=deed_id,
        portion_id=portion_id,
        linked_event_id=linked_event_id,
        source_record_id=source_record_id,
        portion=portion,
        boundary=boundary,
        via_poa_id=via_poa_id,
    )


@pytest.fixture
def baseline_sr() -> SurveyRecord:
    return SurveyRecord(
        id="SR_TEST_BASE",
        parcel_id="P_TEST_01",
        survey="BS",
        khatian_no="1001",
        record_date=date(2010, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_OWNER_1", Fraction(10)),),
    )


# ---------------------------------------------------------------------------
# Task A: Government and Court Locks (R11 / F17)
# ---------------------------------------------------------------------------

def test_r11_sale_after_gov_acquisition_flag_returns_contradiction(baseline_sr):
    parcel = Parcel(
        id="P_TEST_01",
        dag_no="101",
        mouza="Tejgaon",
        is_khas=True,
        under_acquisition=True,
        flag_date=date(2020, 1, 1),
    )
    event = make_event(
        id="E_SALE_POST_FLAG",
        type=EventType.SALE,
        seq=1,
        event_date=date(2021, 5, 10),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BUYER",
        area=Fraction(5),
    )
    alert = check_r11(event, parcel, baseline_sr)
    assert alert.status == Status.CONTRADICTION
    assert alert.message_key == MSG_R11_CONTRADICTION_GOV_LOCK
    assert "E_SALE_POST_FLAG" in alert.evidence_ids


def test_r11_sale_before_gov_flag_is_consistent(baseline_sr):
    parcel = Parcel(
        id="P_TEST_01",
        dag_no="101",
        mouza="Tejgaon",
        is_khas=True,
        under_acquisition=True,
        flag_date=date(2023, 1, 1),
    )
    event = make_event(
        id="E_SALE_PRE_FLAG",
        type=EventType.SALE,
        seq=1,
        event_date=date(2021, 5, 10),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BUYER",
        area=Fraction(5),
    )
    alert = check_r11(event, parcel, baseline_sr)
    assert alert.status == Status.CONSISTENT
    assert alert.message_key == MSG_R11_CONSISTENT


def test_r11_missing_flag_date_returns_review(baseline_sr):
    parcel = Parcel(
        id="P_TEST_01",
        dag_no="101",
        mouza="Tejgaon",
        is_khas=True,
        under_acquisition=True,
        flag_date=None,  # Missing flag date
    )
    event = make_event(
        id="E_SALE_1",
        type=EventType.SALE,
        seq=1,
        event_date=date(2021, 5, 10),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BUYER",
        area=Fraction(5),
    )
    alert = check_r11(event, parcel, baseline_sr)
    assert alert.status == Status.REVIEW
    assert alert.message_key == MSG_R11_REVIEW_MISSING_FLAG_DATE


def test_r11_missing_event_date_returns_review(baseline_sr):
    parcel = Parcel(
        id="P_TEST_01",
        dag_no="101",
        mouza="Tejgaon",
        is_khas=True,
        flag_date=date(2020, 1, 1),
    )
    event = make_event(
        id="E_SALE_UNDATED",
        type=EventType.SALE,
        seq=1,
        event_date=None,  # Missing event date
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BUYER",
        area=Fraction(5),
    )
    alert = check_r11(event, parcel, baseline_sr)
    assert alert.status == Status.REVIEW
    assert alert.message_key == MSG_R11_REVIEW_MISSING_FLAG_DATE


def test_r11_active_court_injunction_returns_review(baseline_sr):
    parcel = Parcel(
        id="P_TEST_01",
        dag_no="101",
        mouza="Tejgaon",
        injunction=True,
    )
    event = make_event(
        id="E_SALE_1",
        type=EventType.SALE,
        seq=1,
        event_date=date(2021, 5, 10),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BUYER",
        area=Fraction(5),
    )
    alert = check_r11(event, parcel, baseline_sr)
    assert alert.status == Status.REVIEW
    assert alert.message_key == MSG_R11_REVIEW_COURT_OR_INJUNCTION


def test_r11_pending_court_case_returns_review(baseline_sr):
    parcel = Parcel(
        id="P_TEST_01",
        dag_no="101",
        mouza="Tejgaon",
        court_case_no="CASE-2021-99",
        case_status="pending",
    )
    event = make_event(
        id="E_SALE_1",
        type=EventType.SALE,
        seq=1,
        event_date=date(2021, 5, 10),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BUYER",
        area=Fraction(5),
    )
    alert = check_r11(event, parcel, baseline_sr)
    assert alert.status == Status.REVIEW
    assert alert.message_key == MSG_R11_REVIEW_COURT_OR_INJUNCTION


def test_r11_disposed_court_case_is_consistent(baseline_sr):
    parcel = Parcel(
        id="P_TEST_01",
        dag_no="101",
        mouza="Tejgaon",
        court_case_no="CASE-2015-11",
        case_status="disposed",
        injunction=False,
    )
    event = make_event(
        id="E_SALE_1",
        type=EventType.SALE,
        seq=1,
        event_date=date(2021, 5, 10),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BUYER",
        area=Fraction(5),
    )
    alert = check_r11(event, parcel, baseline_sr)
    assert alert.status == Status.CONSISTENT
    assert alert.message_key == MSG_R11_CONSISTENT


# ---------------------------------------------------------------------------
# Task B: Mortgage and Release (R9)
# ---------------------------------------------------------------------------

def test_r9_mortgage_and_release_replay_does_not_transfer_ownership(baseline_sr):
    """Replay verification: MORTGAGE and MORTGAGE_RELEASE do NOT mutate holder shares."""
    mort_event = make_event(
        id="E_MORT_1",
        type=EventType.MORTGAGE,
        seq=1,
        event_date=date(2018, 3, 1),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BANK",
        area=Fraction(10),
    )
    rel_event = make_event(
        id="E_REL_1",
        type=EventType.MORTGAGE_RELEASE,
        seq=2,
        event_date=date(2019, 1, 1),
        parcel_id="P_TEST_01",
        from_person="P_BANK",
        to_person="P_OWNER_1",
        area=Fraction(10),
        linked_event_id="E_MORT_1",
    )
    state, issues = compute_state([mort_event, rel_event], baseline_sr)
    assert len(issues) == 0
    assert state["P_OWNER_1"] == Fraction(10)
    assert state.get("P_BANK", Fraction(0)) == Fraction(0)


def test_r9_sale_under_active_unreleased_mortgage_returns_contradiction(baseline_sr):
    mort_event = make_event(
        id="E_MORT_1",
        type=EventType.MORTGAGE,
        seq=1,
        event_date=date(2018, 3, 1),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BANK",
        area=Fraction(10),
        portion_id="PORTION_A",
    )
    sale_event = make_event(
        id="E_SALE_1",
        type=EventType.SALE,
        seq=2,
        event_date=date(2019, 5, 1),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BUYER",
        area=Fraction(5),
        portion_id="PORTION_A",
    )
    events = [mort_event, sale_event]
    alert = check_r9(sale_event, events, baseline_sr)
    assert alert.status == Status.CONTRADICTION
    assert alert.message_key == MSG_R9_CONTRADICTION_MORTGAGE_ACTIVE
    assert "E_MORT_1" in alert.evidence_ids


def test_r9_sale_after_clean_release_is_consistent(baseline_sr):
    mort_event = make_event(
        id="E_MORT_1",
        type=EventType.MORTGAGE,
        seq=1,
        event_date=date(2018, 3, 1),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BANK",
        area=Fraction(10),
        portion_id="PORTION_A",
    )
    rel_event = make_event(
        id="E_REL_1",
        type=EventType.MORTGAGE_RELEASE,
        seq=2,
        event_date=date(2019, 1, 1),  # Released before sale
        parcel_id="P_TEST_01",
        from_person="P_BANK",
        to_person="P_OWNER_1",
        area=Fraction(10),
        portion_id="PORTION_A",
        linked_event_id="E_MORT_1",
    )
    sale_event = make_event(
        id="E_SALE_1",
        type=EventType.SALE,
        seq=3,
        event_date=date(2019, 5, 1),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BUYER",
        area=Fraction(5),
        portion_id="PORTION_A",
    )
    events = [mort_event, rel_event, sale_event]
    alert = check_r9(sale_event, events, baseline_sr)
    assert alert.status == Status.CONSISTENT
    assert alert.message_key == MSG_R9_CONSISTENT


def test_r9_second_mortgage_on_unreleased_portion_returns_contradiction(baseline_sr):
    mort1 = make_event(
        id="E_MORT_1",
        type=EventType.MORTGAGE,
        seq=1,
        event_date=date(2018, 3, 1),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BANK_1",
        area=Fraction(10),
        portion_id="PORTION_A",
    )
    mort2 = make_event(
        id="E_MORT_2",
        type=EventType.MORTGAGE,
        seq=2,
        event_date=date(2018, 8, 1),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BANK_2",
        area=Fraction(10),
        portion_id="PORTION_A",
    )
    events = [mort1, mort2]
    alert = check_r9(mort2, events, baseline_sr)
    assert alert.status == Status.CONTRADICTION
    assert alert.message_key == MSG_R9_CONTRADICTION_SECOND_MORTGAGE
    assert "E_MORT_1" in alert.evidence_ids


def test_r9_missing_release_date_returns_review(baseline_sr):
    mort = make_event(
        id="E_MORT_1",
        type=EventType.MORTGAGE,
        seq=1,
        event_date=date(2018, 3, 1),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BANK",
        area=Fraction(10),
    )
    rel = make_event(
        id="E_REL_1",
        type=EventType.MORTGAGE_RELEASE,
        seq=2,
        event_date=None,  # Missing date
        parcel_id="P_TEST_01",
        from_person="P_BANK",
        to_person="P_OWNER_1",
        area=Fraction(10),
        linked_event_id="E_MORT_1",
    )
    sale = make_event(
        id="E_SALE_1",
        type=EventType.SALE,
        seq=3,
        event_date=date(2019, 5, 1),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BUYER",
        area=Fraction(5),
    )
    events = [mort, rel, sale]
    alert = check_r9(sale, events, baseline_sr)
    assert alert.status == Status.REVIEW
    assert alert.message_key == MSG_R9_REVIEW_MISSING_DATE_OR_LINK


def test_r9_repeated_release_returns_review(baseline_sr):
    mort = make_event(
        id="E_MORT_1",
        type=EventType.MORTGAGE,
        seq=1,
        event_date=date(2018, 3, 1),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_BANK",
        area=Fraction(10),
    )
    rel1 = make_event(
        id="E_REL_1",
        type=EventType.MORTGAGE_RELEASE,
        seq=2,
        event_date=date(2019, 1, 1),
        parcel_id="P_TEST_01",
        from_person="P_BANK",
        to_person="P_OWNER_1",
        area=Fraction(10),
        linked_event_id="E_MORT_1",
    )
    rel2 = make_event(
        id="E_REL_2",
        type=EventType.MORTGAGE_RELEASE,
        seq=3,
        event_date=date(2019, 2, 1),
        parcel_id="P_TEST_01",
        from_person="P_BANK",
        to_person="P_OWNER_1",
        area=Fraction(10),
        linked_event_id="E_MORT_1",
    )
    events = [mort, rel1, rel2]
    alert = check_r9(rel2, events, baseline_sr)
    assert alert.status == Status.REVIEW
    assert alert.message_key == MSG_R9_REVIEW_MISSING_DATE_OR_LINK


# ---------------------------------------------------------------------------
# Task C: Power of Attorney (R10)
# ---------------------------------------------------------------------------

def test_r10_poa_grant_and_revoke_do_not_transfer_ownership(baseline_sr):
    """Replay verification: POA_GRANT and POA_REVOKE do NOT mutate holder shares."""
    poa_grant = make_event(
        id="E_POA_1",
        type=EventType.POA_GRANT,
        seq=1,
        event_date=date(2017, 2, 14),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_AGENT",
        area=Fraction(10),
    )
    poa_revoke = make_event(
        id="E_REV_1",
        type=EventType.POA_REVOKE,
        seq=2,
        event_date=date(2018, 12, 1),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_AGENT",
        area=Fraction(10),
        linked_event_id="E_POA_1",
    )
    state, issues = compute_state([poa_grant, poa_revoke], baseline_sr)
    assert len(issues) == 0
    assert state["P_OWNER_1"] == Fraction(10)
    assert state.get("P_AGENT", Fraction(0)) == Fraction(0)


def test_r10_sale_under_revoked_poa_returns_contradiction(baseline_sr):
    poa_grant = make_event(
        id="E_POA_1",
        type=EventType.POA_GRANT,
        seq=1,
        event_date=date(2017, 2, 14),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_AGENT",
        area=Fraction(10),
    )
    poa_revoke = make_event(
        id="E_REV_1",
        type=EventType.POA_REVOKE,
        seq=2,
        event_date=date(2018, 12, 1),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_AGENT",
        area=Fraction(10),
        linked_event_id="E_POA_1",
    )
    sale_under_revoked = make_event(
        id="E_SALE_BAD",
        type=EventType.SALE,
        seq=3,
        event_date=date(2019, 8, 20),  # Executed AFTER revocation on 2018-12-01
        parcel_id="P_TEST_01",
        from_person="P_AGENT",
        to_person="P_BUYER",
        area=Fraction(5),
        via_poa_id="E_POA_1",
    )
    events = [poa_grant, poa_revoke, sale_under_revoked]
    alert = check_r10(sale_under_revoked, events, baseline_sr)
    assert alert.status == Status.CONTRADICTION
    assert alert.message_key == MSG_R10_CONTRADICTION_REVOKED
    assert "E_REV_1" in alert.evidence_ids


def test_r10_sale_executed_before_revocation_is_consistent_tricky_clean(baseline_sr):
    """Tricky clean case: POA was eventually revoked, but the sale was executed BEFORE revocation."""
    poa_grant = make_event(
        id="E_POA_1",
        type=EventType.POA_GRANT,
        seq=1,
        event_date=date(2017, 2, 14),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_AGENT",
        area=Fraction(10),
    )
    sale_valid = make_event(
        id="E_SALE_OK",
        type=EventType.SALE,
        seq=2,
        event_date=date(2018, 5, 20),  # Executed while POA was active
        parcel_id="P_TEST_01",
        from_person="P_AGENT",
        to_person="P_BUYER",
        area=Fraction(5),
        via_poa_id="E_POA_1",
    )
    poa_revoke = make_event(
        id="E_REV_1",
        type=EventType.POA_REVOKE,
        seq=3,
        event_date=date(2018, 12, 1),  # Revoked AFTER sale
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_AGENT",
        area=Fraction(10),
        linked_event_id="E_POA_1",
    )
    events = [poa_grant, sale_valid, poa_revoke]
    alert = check_r10(sale_valid, events, baseline_sr)
    assert alert.status == Status.CONSISTENT
    assert alert.message_key == MSG_R10_CONSISTENT


def test_r10_missing_poa_grant_returns_contradiction(baseline_sr):
    sale_no_grant = make_event(
        id="E_SALE_BAD",
        type=EventType.SALE,
        seq=1,
        event_date=date(2019, 8, 20),
        parcel_id="P_TEST_01",
        from_person="P_AGENT",
        to_person="P_BUYER",
        area=Fraction(5),
        via_poa_id="E_NONEXISTENT_POA",
    )
    alert = check_r10(sale_no_grant, [sale_no_grant], baseline_sr)
    assert alert.status == Status.CONTRADICTION
    assert alert.message_key == MSG_R10_CONTRADICTION_MISSING_GRANT


def test_r10_sale_before_grant_date_returns_contradiction(baseline_sr):
    poa_grant = make_event(
        id="E_POA_1",
        type=EventType.POA_GRANT,
        seq=1,
        event_date=date(2019, 1, 1),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_AGENT",
        area=Fraction(10),
    )
    sale_premature = make_event(
        id="E_SALE_PREMATURE",
        type=EventType.SALE,
        seq=2,
        event_date=date(2018, 1, 1),  # Before grant
        parcel_id="P_TEST_01",
        from_person="P_AGENT",
        to_person="P_BUYER",
        area=Fraction(5),
        via_poa_id="E_POA_1",
    )
    alert = check_r10(sale_premature, [poa_grant, sale_premature], baseline_sr)
    assert alert.status == Status.CONTRADICTION
    assert alert.message_key == MSG_R10_CONTRADICTION_REVOKED


def test_r10_unauthorized_third_party_returns_contradiction(baseline_sr):
    poa_grant = make_event(
        id="E_POA_1",
        type=EventType.POA_GRANT,
        seq=1,
        event_date=date(2017, 2, 14),
        parcel_id="P_TEST_01",
        from_person="P_OWNER_1",
        to_person="P_AGENT",
        area=Fraction(10),
    )
    sale_random_seller = make_event(
        id="E_SALE_RANDOM",
        type=EventType.SALE,
        seq=2,
        event_date=date(2018, 5, 20),
        parcel_id="P_TEST_01",
        from_person="P_RANDOM_STRANGER",  # Neither principal nor agent
        to_person="P_BUYER",
        area=Fraction(5),
        via_poa_id="E_POA_1",
    )
    alert = check_r10(sale_random_seller, [poa_grant, sale_random_seller], baseline_sr)
    assert alert.status == Status.CONTRADICTION
    assert alert.message_key == MSG_R10_CONTRADICTION_MISSING_GRANT


# ---------------------------------------------------------------------------
# Integrated Evaluation & Demo v1.1 Scenarios
# ---------------------------------------------------------------------------

def test_v11_dataset_evaluation_detects_phase9_scenarios():
    dataset = load_dataset(DEMO_V11_PATH)

    # 1. PARCEL_PLANTED_R9 -> Contradiction on R9
    h_r9 = dataset.get_history("PARCEL_PLANTED_R9")
    alerts_r9 = dispatch_history_rules(h_r9, all_parcels=dataset.parcels, all_deeds=dataset.deeds)
    r9_alerts = [a for a in alerts_r9 if a.rule_id == "R9"]
    assert any(a.status == Status.CONTRADICTION for a in r9_alerts)

    # 2. PARCEL_CLEAN_R9_TRICKY -> Consistent on R9
    h_r9_c = dataset.get_history("PARCEL_CLEAN_R9_TRICKY")
    alerts_r9_c = dispatch_history_rules(h_r9_c, all_parcels=dataset.parcels, all_deeds=dataset.deeds)
    r9_c_alerts = [a for a in alerts_r9_c if a.rule_id == "R9"]
    assert all(a.status == Status.CONSISTENT for a in r9_c_alerts)

    # 3. PARCEL_PLANTED_R10 -> Contradiction on R10
    h_r10 = dataset.get_history("PARCEL_PLANTED_R10")
    alerts_r10 = dispatch_history_rules(h_r10, all_parcels=dataset.parcels, all_deeds=dataset.deeds)
    r10_alerts = [a for a in alerts_r10 if a.rule_id == "R10"]
    assert any(a.status == Status.CONTRADICTION for a in r10_alerts)

    # 4. PARCEL_CLEAN_R10_TRICKY -> Consistent on R10
    h_r10_c = dataset.get_history("PARCEL_CLEAN_R10_TRICKY")
    alerts_r10_c = dispatch_history_rules(h_r10_c, all_parcels=dataset.parcels, all_deeds=dataset.deeds)
    r10_c_alerts = [a for a in alerts_r10_c if a.rule_id == "R10"]
    assert all(a.status == Status.CONSISTENT for a in r10_c_alerts)

    # 5. PARCEL_PLANTED_R11 -> Contradiction on R11
    h_r11 = dataset.get_history("PARCEL_PLANTED_R11")
    alerts_r11 = dispatch_history_rules(h_r11, all_parcels=dataset.parcels, all_deeds=dataset.deeds)
    r11_alerts = [a for a in alerts_r11 if a.rule_id == "R11"]
    assert any(a.status == Status.CONTRADICTION for a in r11_alerts)

    # 6. PARCEL_CLEAN_R11 -> Consistent on R11
    h_r11_c = dataset.get_history("PARCEL_CLEAN_R11")
    alerts_r11_c = dispatch_history_rules(h_r11_c, all_parcels=dataset.parcels, all_deeds=dataset.deeds)
    r11_c_alerts = [a for a in alerts_r11_c if a.rule_id == "R11"]
    assert all(a.status == Status.CONSISTENT for a in r11_c_alerts)


# ---------------------------------------------------------------------------
# API Simulation & Schemas Contract
# ---------------------------------------------------------------------------

def test_api_simulate_locked_parcel_reports_r11_contradiction():
    app = create_app(dataset_path=DEMO_V11_PATH)
    client = TestClient(app)

    # Proposed sale on PARCEL_PLANTED_R11 (flag_date: 2020-01-01) with date 2022-01-01
    payload = {
        "parcel_id": "PARCEL_PLANTED_R11",
        "from_person": "P_V11_HASAN",
        "to_person": "P_BUYER_SIM",
        "area": "2",
        "date": "2022-01-01",
        "lang": "en",
    }
    res = client.post("/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status_code"] == "CONTRADICTION"
    r11_alert = next((a for a in data["alerts"] if a["rule_id"] == "R11"), None)
    assert r11_alert is not None
    assert r11_alert["status_code"] == "CONTRADICTION"


def test_api_simulate_with_revoked_poa_reports_r10_contradiction():
    app = create_app(dataset_path=DEMO_V11_PATH)
    client = TestClient(app)

    # Proposed sale on PARCEL_PLANTED_R10 using revoked POA E_V11_R10_GRANT (revoked 2018-12-01)
    payload = {
        "parcel_id": "PARCEL_PLANTED_R10",
        "from_person": "P_V11_RAHIMA",
        "to_person": "P_BUYER_SIM",
        "area": "2",
        "date": "2020-05-01",
        "via_poa_id": "E_V11_R10_GRANT",
        "lang": "en",
    }
    res = client.post("/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status_code"] == "CONTRADICTION"
    r10_alert = next((a for a in data["alerts"] if a["rule_id"] == "R10"), None)
    assert r10_alert is not None
    assert r10_alert["status_code"] == "CONTRADICTION"


def test_api_get_parcel_includes_phase9_lock_metadata():
    app = create_app(dataset_path=DEMO_V11_PATH)
    client = TestClient(app)

    res = client.get("/parcel/PARCEL_PLANTED_R11")
    assert res.status_code == 200
    data = res.json()
    assert data["is_locked"] is True
    assert data["is_khas"] is True
    assert data["under_acquisition"] is True
    assert data["flag_date"] == "2020-01-01"
    assert data["court_case_no"] == "DEMO-CASE-0011"
    assert data["case_status"] == "pending"
    assert data["injunction"] is True

    # Graph node for parcel should also have is_locked
    parcel_node = next(n for n in data["graph"]["nodes"] if n["data"]["id"] == "parcel_PARCEL_PLANTED_R11")
    assert parcel_node["data"].get("is_locked") is True


# ---------------------------------------------------------------------------
# Strict Verification: Hash, Parity, and Forbidden Words
# ---------------------------------------------------------------------------

def test_v10_baseline_dataset_hash_strictly_invariant():
    """Verify demo_family.json baseline hash has not drifted."""
    ds = load_dataset(DEMO_FAMILY_PATH)
    events = [e for h in ds.histories for e in h.events]
    srs = [s for h in ds.histories for s in h.survey_records]
    current_hash = hash_dataset(events, srs)
    assert current_hash == "b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01"


def test_locales_exact_key_parity():
    en_path = LOCALES_DIR / "en.json"
    bn_path = LOCALES_DIR / "bn.json"
    en = json.loads(en_path.read_text(encoding="utf-8"))
    bn = json.loads(bn_path.read_text(encoding="utf-8"))
    assert set(en.keys()) == set(bn.keys())
    assert len(en) >= 62


def test_ui_strings_exact_key_parity():
    strings_path = REPO_ROOT / "src" / "jomigraph" / "ui" / "strings.json"
    data = json.loads(strings_path.read_text(encoding="utf-8"))
    en_keys = set(data["en"].keys())
    bn_keys = set(data["bn"].keys())
    assert en_keys == bn_keys
    assert len(en_keys) >= 195


def test_no_forbidden_words_in_locales():
    forbidden_en = ["safe", "valid", "legal", "verified owner", "fraud", "forged", "scam", "you will be cheated"]
    forbidden_bn = ["জালিয়াতি", "আইনগত", "বৈধ"]

    en_text = (LOCALES_DIR / "en.json").read_text(encoding="utf-8").lower()
    for word in forbidden_en:
        assert not re.search(r"\b" + re.escape(word) + r"\b", en_text), f"Forbidden English word '{word}' found in en.json"

    bn_text = (LOCALES_DIR / "bn.json").read_text(encoding="utf-8")
    for word in forbidden_bn:
        assert word not in bn_text, f"Forbidden Bengali word '{word}' found in bn.json"
