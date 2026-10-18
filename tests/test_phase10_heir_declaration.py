"""
Tests for Phase 10: R8 — Unaccounted Heir Declaration Consistency
=================================================================
Covers:
  - Explicit Contradiction: complete=True, baseline_complete=True, dates present,
    omitted declared heir without deed of sale, gift, or release.
  - Review Required: incomplete declaration (complete=False), incomplete baseline,
    missing dates, missing deceased_id, malformed heirs list.
  - Consistent: all declared heirs listed in subsequent khatian/deed,
    no subsequent records after declaration, or no declaration present.
  - Tricky Clean Case: heir omitted from subsequent khatian previously sold/released
    their interest by a documented deed (SALE, GIFT, RELEASE).
  - Pure simulation & shared evaluation dispatch.
  - Demo v11 dataset scenarios (PARCEL_PLANTED_R8, PARCEL_CLEAN_R8, PARCEL_CLEAN_R8_TRICKY).
  - API endpoints (/parcels, /parcels/{id}, /parcels/{id}/alerts, /report/{id}, /simulate).
  - Citizen vs Reviewer role separation (no leaked rule IDs or calculations to citizens).
  - Baseline SHA-256 dataset hash invariance.
  - Localization parity and forbidden words audit.
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

from jomigraph.api.app import create_app, localize_calculation
from jomigraph.api.schemas import SimulateRequest
from jomigraph.engine.replay import compute_state
from jomigraph.engine.rules import (
    Alert,
    Status,
    check_r8,
    dispatch_event_rules,
    dispatch_history_rules,
    run_rule,
)
from jomigraph.engine.simulate import evaluate, hash_dataset, simulate
from jomigraph.i18n import (
    MSG_R8_CONSISTENT,
    MSG_R8_CONTRADICTION,
    MSG_R8_REVIEW_INPUTS,
    MSG_R8_REVIEW_OMITTED_HEIR,
    NEXT_STEP_R8,
    translate,
)
from jomigraph.loader import load_dataset
from jomigraph.models import Deed, Event, EventType, Parcel, ParcelHistory, SurveyRecord

REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_FAMILY_PATH = REPO_ROOT / "data" / "demo_family.json"
DEMO_V11_PATH = REPO_ROOT / "data" / "demo_v11.json"
LOCALES_DIR = REPO_ROOT / "locales"


def make_event(
    id: str,
    type: EventType,
    seq: int,
    event_date: Optional[date],
    parcel_id: str,
    from_person: Optional[str] = None,
    to_person: Optional[str] = None,
    area: Optional[Fraction] = None,
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


# ===========================================================================
# 1. Direct Rule Logic & Branch Coverage
# ===========================================================================

def test_r8_no_heir_declaration_returns_consistent():
    """When no heir declaration exists on the parcel history, R8 returns Consistent."""
    sr = SurveyRecord(
        id="SR_01",
        parcel_id="P_R8_01",
        survey="CS",
        khatian_no="101",
        record_date=date(1960, 1, 1),
        recorded_area=Fraction(10),
        holders=(("H1", Fraction(10)),),
    )
    hist = ParcelHistory(
        parcel_id="P_R8_01",
        baseline_record_id="SR_01",
        baseline_complete=True,
        start_record_id="SR_01",
        end_date=None,
        survey_records=(sr,),
        events=(),
        heir_declaration=None,
    )

    alert = run_rule(check_r8, hist)
    assert alert.rule_id == "R8"
    assert alert.status == Status.CONSISTENT
    assert alert.message_key == MSG_R8_CONSISTENT
    assert len(alert.evidence_ids) > 0


def test_r8_explicit_contradiction_omitted_heir():
    """
    Contradiction Found ONLY when declaration is complete, baseline is complete,
    all dates present, and a declared heir is omitted without sale/gift/release deed.
    """
    sr_cs = SurveyRecord(
        id="SR_CS",
        parcel_id="P_R8_02",
        survey="CS",
        khatian_no="101",
        record_date=date(1960, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_FATHER", Fraction(10)),),
    )
    sr_rs = SurveyRecord(
        id="SR_RS",
        parcel_id="P_R8_02",
        survey="RS",
        khatian_no="201",
        record_date=date(1985, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_SON", Fraction(10)),),  # P_DAUGHTER omitted!
    )
    declaration = {
        "deceased_id": "P_FATHER",
        "complete": True,
        "declaration_date": "1980-01-01",
        "declared_heirs": [
            {"person_id": "P_SON", "relation": "son"},
            {"person_id": "P_DAUGHTER", "relation": "daughter"},
        ],
        "source_record_id": "SANAD_001",
    }
    hist = ParcelHistory(
        parcel_id="P_R8_02",
        baseline_record_id="SR_CS",
        baseline_complete=True,
        start_record_id="SR_CS",
        end_date=None,
        survey_records=(sr_cs, sr_rs),
        events=(),
        heir_declaration=declaration,
    )

    alert = run_rule(check_r8, hist)
    assert alert.rule_id == "R8"
    assert alert.status == Status.CONTRADICTION
    assert alert.message_key == MSG_R8_CONTRADICTION
    assert "P_DAUGHTER" in alert.calculation
    assert "SANAD_001" in alert.evidence_ids
    assert "SR_RS" in alert.evidence_ids


def test_r8_review_when_declaration_incomplete_flag():
    """When declaration complete flag is False, returns Review Required."""
    sr_cs = SurveyRecord(
        id="SR_CS",
        parcel_id="P_R8_03",
        survey="CS",
        khatian_no="101",
        record_date=date(1960, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_FATHER", Fraction(10)),),
    )
    sr_rs = SurveyRecord(
        id="SR_RS",
        parcel_id="P_R8_03",
        survey="RS",
        khatian_no="201",
        record_date=date(1985, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_SON", Fraction(10)),),
    )
    declaration = {
        "deceased_id": "P_FATHER",
        "complete": False,  # Incomplete declaration!
        "declaration_date": "1980-01-01",
        "declared_heirs": [
            {"person_id": "P_SON", "relation": "son"},
            {"person_id": "P_DAUGHTER", "relation": "daughter"},
        ],
        "source_record_id": "SANAD_002",
    }
    hist = ParcelHistory(
        parcel_id="P_R8_03",
        baseline_record_id="SR_CS",
        baseline_complete=True,
        start_record_id="SR_CS",
        end_date=None,
        survey_records=(sr_cs, sr_rs),
        events=(),
        heir_declaration=declaration,
    )

    alert = run_rule(check_r8, hist)
    assert alert.status == Status.REVIEW
    assert alert.message_key == MSG_R8_REVIEW_OMITTED_HEIR
    assert "complete flag is False" in alert.calculation


def test_r8_review_when_baseline_incomplete():
    """When baseline_complete is False, returns Review Required."""
    sr_cs = SurveyRecord(
        id="SR_CS",
        parcel_id="P_R8_04",
        survey="CS",
        khatian_no="101",
        record_date=date(1960, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_FATHER", Fraction(10)),),
    )
    sr_rs = SurveyRecord(
        id="SR_RS",
        parcel_id="P_R8_04",
        survey="RS",
        khatian_no="201",
        record_date=date(1985, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_SON", Fraction(10)),),
    )
    declaration = {
        "deceased_id": "P_FATHER",
        "complete": True,
        "declaration_date": "1980-01-01",
        "declared_heirs": [
            {"person_id": "P_SON", "relation": "son"},
            {"person_id": "P_DAUGHTER", "relation": "daughter"},
        ],
        "source_record_id": "SANAD_003",
    }
    hist = ParcelHistory(
        parcel_id="P_R8_04",
        baseline_record_id="SR_CS",
        baseline_complete=False,  # Baseline incomplete!
        start_record_id="SR_CS",
        end_date=None,
        survey_records=(sr_cs, sr_rs),
        events=(),
        heir_declaration=declaration,
    )

    alert = run_rule(check_r8, hist)
    assert alert.status == Status.REVIEW
    assert alert.message_key == MSG_R8_REVIEW_OMITTED_HEIR
    assert "baseline_complete is False" in alert.calculation


def test_r8_review_when_dates_missing():
    """When declaration date is missing, returns Review Required."""
    sr_cs = SurveyRecord(
        id="SR_CS",
        parcel_id="P_R8_05",
        survey="CS",
        khatian_no="101",
        record_date=date(1960, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_FATHER", Fraction(10)),),
    )
    sr_rs = SurveyRecord(
        id="SR_RS",
        parcel_id="P_R8_05",
        survey="RS",
        khatian_no="201",
        record_date=date(1985, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_SON", Fraction(10)),),
    )
    declaration = {
        "deceased_id": "P_FATHER",
        "complete": True,
        # No declaration_date!
        "declared_heirs": [
            {"person_id": "P_SON", "relation": "son"},
            {"person_id": "P_DAUGHTER", "relation": "daughter"},
        ],
        "source_record_id": "SANAD_004",
    }
    hist = ParcelHistory(
        parcel_id="P_R8_05",
        baseline_record_id="SR_CS",
        baseline_complete=True,
        start_record_id="SR_CS",
        end_date=None,
        survey_records=(sr_cs, sr_rs),
        events=(),
        heir_declaration=declaration,
    )

    alert = run_rule(check_r8, hist)
    assert alert.status == Status.REVIEW
    assert alert.message_key == MSG_R8_REVIEW_OMITTED_HEIR
    assert "dates on declaration or subsequent record are missing" in alert.calculation


def test_r8_review_malformed_inputs():
    """Missing deceased_id, empty declared_heirs, or missing source_record_id returns Review."""
    sr_cs = SurveyRecord(
        id="SR_CS",
        parcel_id="P_R8_06",
        survey="CS",
        khatian_no="101",
        record_date=date(1960, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_FATHER", Fraction(10)),),
    )

    # Missing deceased_id
    decl_no_dec = {"complete": True, "declared_heirs": ["H1"], "source_record_id": "S1"}
    h1 = ParcelHistory("P_R8_06", "SR_CS", True, "SR_CS", None, (sr_cs,), (), decl_no_dec)
    a1 = run_rule(check_r8, h1)
    assert a1.status == Status.REVIEW
    assert a1.message_key == MSG_R8_REVIEW_INPUTS

    # Empty declared_heirs
    decl_empty_heirs = {"deceased_id": "P_FATHER", "complete": True, "declared_heirs": [], "source_record_id": "S1"}
    h2 = ParcelHistory("P_R8_06", "SR_CS", True, "SR_CS", None, (sr_cs,), (), decl_empty_heirs)
    a2 = run_rule(check_r8, h2)
    assert a2.status == Status.REVIEW
    assert a2.message_key == MSG_R8_REVIEW_INPUTS

    # Missing source_record_id
    decl_no_src = {"deceased_id": "P_FATHER", "complete": True, "declared_heirs": ["H1"]}
    h3 = ParcelHistory("P_R8_06", "SR_CS", True, "SR_CS", None, (sr_cs,), (), decl_no_src)
    a3 = run_rule(check_r8, h3)
    assert a3.status == Status.REVIEW
    assert a3.message_key == MSG_R8_REVIEW_INPUTS


def test_r8_clean_all_declared_heirs_recorded():
    """Consistent when all declared heirs are recorded in the subsequent khatian."""
    sr_cs = SurveyRecord(
        id="SR_CS",
        parcel_id="P_R8_07",
        survey="CS",
        khatian_no="101",
        record_date=date(1960, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_FATHER", Fraction(10)),),
    )
    sr_rs = SurveyRecord(
        id="SR_RS",
        parcel_id="P_R8_07",
        survey="RS",
        khatian_no="201",
        record_date=date(1985, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_SON", Fraction(5)), ("P_DAUGHTER", Fraction(5))),
    )
    declaration = {
        "deceased_id": "P_FATHER",
        "complete": True,
        "declaration_date": "1980-01-01",
        "declared_heirs": [
            {"person_id": "P_SON", "relation": "son"},
            {"person_id": "P_DAUGHTER", "relation": "daughter"},
        ],
        "source_record_id": "SANAD_005",
    }
    hist = ParcelHistory(
        parcel_id="P_R8_07",
        baseline_record_id="SR_CS",
        baseline_complete=True,
        start_record_id="SR_CS",
        end_date=None,
        survey_records=(sr_cs, sr_rs),
        events=(),
        heir_declaration=declaration,
    )

    alert = run_rule(check_r8, hist)
    assert alert.status == Status.CONSISTENT
    assert alert.message_key == MSG_R8_CONSISTENT
    assert "All declared heirs under declaration" in alert.calculation


def test_r8_clean_no_subsequent_records_yet():
    """Consistent when declaration is recorded, but no subsequent khatian or deed has been made."""
    sr_cs = SurveyRecord(
        id="SR_CS",
        parcel_id="P_R8_08",
        survey="CS",
        khatian_no="101",
        record_date=date(1960, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_FATHER", Fraction(10)),),
    )
    declaration = {
        "deceased_id": "P_FATHER",
        "complete": True,
        "declaration_date": "1980-01-01",
        "declared_heirs": [
            {"person_id": "P_SON", "relation": "son"},
            {"person_id": "P_DAUGHTER", "relation": "daughter"},
        ],
        "source_record_id": "SANAD_006",
    }
    hist = ParcelHistory(
        parcel_id="P_R8_08",
        baseline_record_id="SR_CS",
        baseline_complete=True,
        start_record_id="SR_CS",
        end_date=None,
        survey_records=(sr_cs,),
        events=(),
        heir_declaration=declaration,
    )

    alert = run_rule(check_r8, hist)
    assert alert.status == Status.CONSISTENT
    assert alert.message_key == MSG_R8_CONSISTENT
    assert "no subsequent survey khatian or deed has omitted any declared heirs" in alert.calculation


# ===========================================================================
# 2. Tricky Clean Cases (Sale, Gift, and Release Deeds by Omitted Heir)
# ===========================================================================

def test_r8_tricky_clean_heir_sold_share_by_deed():
    """
    Tricky clean case: Omitted heir from subsequent survey khatian previously
    transferred their interest via a recorded SALE deed.
    Must be Consistent with supplied records!
    """
    sr_cs = SurveyRecord(
        id="SR_CS",
        parcel_id="P_R8_09",
        survey="CS",
        khatian_no="101",
        record_date=date(1960, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_FATHER", Fraction(10)),),
    )
    sale_by_heir = make_event(
        id="E_SALE_HEIR",
        type=EventType.SALE,
        seq=1,
        event_date=date(1982, 5, 10),
        parcel_id="P_R8_09",
        from_person="P_DAUGHTER",
        to_person="P_SON",
        area=Fraction(5),
        deed_id="DEED_SALE_01",
    )
    sr_rs = SurveyRecord(
        id="SR_RS",
        parcel_id="P_R8_09",
        survey="RS",
        khatian_no="201",
        record_date=date(1985, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_SON", Fraction(10)),),  # P_DAUGHTER omitted from RS khatian!
    )
    declaration = {
        "deceased_id": "P_FATHER",
        "complete": True,
        "declaration_date": "1980-01-01",
        "declared_heirs": [
            {"person_id": "P_SON", "relation": "son"},
            {"person_id": "P_DAUGHTER", "relation": "daughter"},
        ],
        "source_record_id": "SANAD_007",
    }
    hist = ParcelHistory(
        parcel_id="P_R8_09",
        baseline_record_id="SR_CS",
        baseline_complete=True,
        start_record_id="SR_CS",
        end_date=None,
        survey_records=(sr_cs, sr_rs),
        events=(sale_by_heir,),
        heir_declaration=declaration,
    )

    alert = run_rule(check_r8, hist, (sale_by_heir,))
    assert alert.status == Status.CONSISTENT
    assert alert.message_key == MSG_R8_CONSISTENT
    assert "P_DAUGHTER" in alert.calculation
    assert "DEED_SALE_01" in alert.calculation or "E_SALE_HEIR" in alert.calculation
    assert "accounted for by recorded deed" in alert.calculation


def test_r8_tricky_clean_heir_released_interest_by_nadabi_deed():
    """
    Tricky clean case: Omitted heir executed a registered RELEASE (না-দাবি) deed.
    Must be Consistent with supplied records!
    """
    sr_cs = SurveyRecord(
        id="SR_CS",
        parcel_id="P_R8_10",
        survey="CS",
        khatian_no="101",
        record_date=date(1960, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_FATHER", Fraction(10)),),
    )
    release_by_heir = make_event(
        id="E_REL_HEIR",
        type=EventType.RELEASE,
        seq=1,
        event_date=date(1982, 3, 1),
        parcel_id="P_R8_10",
        from_person="P_DAUGHTER",
        to_person="P_SON",
        area=Fraction(5),
        deed_id="DEED_NADABI_01",
    )
    sr_rs = SurveyRecord(
        id="SR_RS",
        parcel_id="P_R8_10",
        survey="RS",
        khatian_no="201",
        record_date=date(1985, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_SON", Fraction(10)),),
    )
    declaration = {
        "deceased_id": "P_FATHER",
        "complete": True,
        "declaration_date": "1980-01-01",
        "declared_heirs": [
            {"person_id": "P_SON", "relation": "son"},
            {"person_id": "P_DAUGHTER", "relation": "daughter"},
        ],
        "source_record_id": "SANAD_008",
    }
    hist = ParcelHistory(
        parcel_id="P_R8_10",
        baseline_record_id="SR_CS",
        baseline_complete=True,
        start_record_id="SR_CS",
        end_date=None,
        survey_records=(sr_cs, sr_rs),
        events=(release_by_heir,),
        heir_declaration=declaration,
    )

    alert = run_rule(check_r8, hist, (release_by_heir,))
    assert alert.status == Status.CONSISTENT
    assert alert.message_key == MSG_R8_CONSISTENT
    assert "DEED_NADABI_01" in alert.calculation or "E_REL_HEIR" in alert.calculation


def test_r8_tricky_clean_heir_gifted_share():
    """
    Tricky clean case: Omitted heir executed a registered GIFT (হেবা) deed to co-heir.
    Must be Consistent with supplied records!
    """
    sr_cs = SurveyRecord(
        id="SR_CS",
        parcel_id="P_R8_11",
        survey="CS",
        khatian_no="101",
        record_date=date(1960, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_FATHER", Fraction(10)),),
    )
    gift_by_heir = make_event(
        id="E_GIFT_HEIR",
        type=EventType.GIFT,
        seq=1,
        event_date=date(1983, 7, 15),
        parcel_id="P_R8_11",
        from_person="P_DAUGHTER",
        to_person="P_SON",
        area=Fraction(5),
        deed_id="DEED_HEBA_01",
    )
    sr_rs = SurveyRecord(
        id="SR_RS",
        parcel_id="P_R8_11",
        survey="RS",
        khatian_no="201",
        record_date=date(1985, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_SON", Fraction(10)),),
    )
    declaration = {
        "deceased_id": "P_FATHER",
        "complete": True,
        "declaration_date": "1980-01-01",
        "declared_heirs": [
            {"person_id": "P_SON", "relation": "son"},
            {"person_id": "P_DAUGHTER", "relation": "daughter"},
        ],
        "source_record_id": "SANAD_009",
    }
    hist = ParcelHistory(
        parcel_id="P_R8_11",
        baseline_record_id="SR_CS",
        baseline_complete=True,
        start_record_id="SR_CS",
        end_date=None,
        survey_records=(sr_cs, sr_rs),
        events=(gift_by_heir,),
        heir_declaration=declaration,
    )

    alert = run_rule(check_r8, hist, (gift_by_heir,))
    assert alert.status == Status.CONSISTENT
    assert alert.message_key == MSG_R8_CONSISTENT


# ===========================================================================
# 3. Non-Transferring Replay Behavior
# ===========================================================================

def test_heir_declaration_does_not_transfer_ownership_in_replay():
    """
    R8 invariant: An heir declaration alone does not alter computed holder shares.
    Shares remain governed by baseline survey records and explicit transfer events.
    """
    sr = SurveyRecord(
        id="SR_01",
        parcel_id="P_REPLAY",
        survey="BS",
        khatian_no="100",
        record_date=date(2000, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_FATHER", Fraction(10)),),
    )
    state, issues = compute_state(events=(), baseline_survey_record=sr)
    assert len(issues) == 0
    assert state == {"P_FATHER": Fraction(10)}


# ===========================================================================
# 4. Simulation Engine Integration & Counterfactual Purity
# ===========================================================================

def test_simulate_on_parcel_with_unaccounted_heir():
    """
    When simulating a proposed sale on a parcel with an unaccounted heir,
    simulation evaluates R8 and surfaces the contradiction without mutating history.
    """
    sr = SurveyRecord(
        id="SR_SIM_01",
        parcel_id="P_SIM_R8",
        survey="BS",
        khatian_no="101",
        record_date=date(2000, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_FATHER", Fraction(10)),),
    )
    declaration = {
        "deceased_id": "P_FATHER",
        "complete": True,
        "declaration_date": "2010-01-01",
        "declared_heirs": [
            {"person_id": "P_SON", "relation": "son"},
            {"person_id": "P_DAUGHTER", "relation": "daughter"},
        ],
        "source_record_id": "SANAD_SIM_01",
    }
    sr_rs = SurveyRecord(
        id="SR_SIM_02",
        parcel_id="P_SIM_R8",
        survey="RS",
        khatian_no="201",
        record_date=date(2012, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P_SON", Fraction(10)),),
    )
    hist = ParcelHistory(
        parcel_id="P_SIM_R8",
        baseline_record_id="SR_SIM_01",
        baseline_complete=True,
        start_record_id="SR_SIM_01",
        end_date=None,
        survey_records=(sr_rs,),
        events=(),
        heir_declaration=declaration,
    )

    proposed = make_event(
        id="E_PROPOSED_SALE",
        type=EventType.SALE,
        seq=1,
        event_date=date(2020, 1, 1),
        parcel_id="P_SIM_R8",
        from_person="P_SON",
        to_person="P_BUYER",
        area=Fraction(5),
    )

    result = simulate(events=(), proposed=proposed, parcel_history=hist)
    r8_alerts = [a for a in result.alerts if a.rule_id == "R8"]
    assert len(r8_alerts) == 1
    assert r8_alerts[0].status == Status.CONTRADICTION
    assert r8_alerts[0].message_key == MSG_R8_CONTRADICTION


# ===========================================================================
# 5. Demonstration Dataset Validation (generator_v11 & demo_v11.json)
# ===========================================================================

def test_demo_v11_planted_r8_detection():
    """PARCEL_PLANTED_R8 in demo_v11.json fires R8 Contradiction."""
    ds = load_dataset(DEMO_V11_PATH)
    hist = ds.get_history("PARCEL_PLANTED_R8")
    assert hist is not None
    assert hist.heir_declaration is not None

    alerts = dispatch_history_rules(
        history=hist,
        all_parcels=ds.parcels,
        all_deeds=ds.deeds,
        all_histories=ds.histories,
        all_persons=ds.persons,
    )

    r8_alerts = [a for a in alerts if a.rule_id == "R8"]
    assert len(r8_alerts) == 1
    assert r8_alerts[0].status == Status.CONTRADICTION
    assert r8_alerts[0].message_key == MSG_R8_CONTRADICTION


def test_demo_v11_clean_r8_passes():
    """PARCEL_CLEAN_R8 in demo_v11.json has zero Contradiction and zero Review alerts."""
    ds = load_dataset(DEMO_V11_PATH)
    hist = ds.get_history("PARCEL_CLEAN_R8")
    assert hist is not None

    alerts = dispatch_history_rules(
        history=hist,
        all_parcels=ds.parcels,
        all_deeds=ds.deeds,
        all_histories=ds.histories,
        all_persons=ds.persons,
    )

    r8_alerts = [a for a in alerts if a.rule_id == "R8"]
    assert len(r8_alerts) == 1
    assert r8_alerts[0].status == Status.CONSISTENT
    assert not any(a.status in (Status.CONTRADICTION, Status.REVIEW) for a in alerts)


def test_demo_v11_clean_r8_tricky_passes():
    """
    PARCEL_CLEAN_R8_TRICKY in demo_v11.json (omitted heir who previously released
    interest by recorded deed) is clean with zero Contradiction / Review alerts.
    """
    ds = load_dataset(DEMO_V11_PATH)
    hist = ds.get_history("PARCEL_CLEAN_R8_TRICKY")
    assert hist is not None

    alerts = dispatch_history_rules(
        history=hist,
        all_parcels=ds.parcels,
        all_deeds=ds.deeds,
        all_histories=ds.histories,
        all_persons=ds.persons,
    )

    r8_alerts = [a for a in alerts if a.rule_id == "R8"]
    assert len(r8_alerts) == 1
    assert r8_alerts[0].status == Status.CONSISTENT
    assert not any(a.status in (Status.CONTRADICTION, Status.REVIEW) for a in alerts)


# ===========================================================================
# 6. API Endpoints & Role Leak Protection
# ===========================================================================

@pytest.fixture(scope="module")
def v11_client() -> TestClient:
    app = create_app(dataset_path=str(DEMO_V11_PATH))
    return TestClient(app)


def test_api_parcel_detail_and_alerts_r8(v11_client: TestClient):
    """GET /parcel/{id} returns R8 alert in reviewer view with both en and bn localized status."""
    resp_en = v11_client.get("/parcel/PARCEL_PLANTED_R8?role=reviewer&lang=en")
    assert resp_en.status_code == 200
    detail_en = resp_en.json()
    r8_en = next((a for a in detail_en["alerts"] if a["rule_id"] == "R8"), None)
    assert r8_en is not None
    assert r8_en["status"] == "Contradiction Found"
    assert len(r8_en["evidence_ids"]) > 0

    resp_bn = v11_client.get("/parcel/PARCEL_PLANTED_R8?role=reviewer&lang=bn")
    assert resp_bn.status_code == 200
    detail_bn = resp_bn.json()
    r8_bn = next((a for a in detail_bn["alerts"] if a["rule_id"] == "R8"), None)
    assert r8_bn is not None
    assert r8_bn["status"] == "অসঙ্গতি পাওয়া গেছে"


def test_api_citizen_role_leak_protection(v11_client: TestClient):
    """Citizen view on parcel and report endpoints contains no internal rule IDs or calculations."""
    resp_detail = v11_client.get("/parcel/PARCEL_PLANTED_R8?role=citizen")
    assert resp_detail.status_code == 200
    detail = resp_detail.json()
    for a in detail["alerts"]:
        assert "rule_id" not in a
        assert "calculation" not in a
        assert "evidence_ids" not in a

    resp_rep = v11_client.get("/report/PARCEL_PLANTED_R8?role=citizen&lang=bn")
    assert resp_rep.status_code == 200
    rep_text = json.dumps(resp_rep.json(), ensure_ascii=False)
    assert "[R8]" not in rep_text
    assert "calculation" not in rep_text


def test_api_simulate_r8(v11_client: TestClient):
    """POST /simulate evaluates R8 on a proposed event."""
    payload = {
        "parcel_id": "PARCEL_PLANTED_R8",
        "from_person": "P_V11_HEIR_A",
        "to_person": "P_V11_BUYER_2",
        "area": "2",
        "event_date": "2024-05-01",
        "role": "reviewer",
    }
    resp = v11_client.post("/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "alerts" in data
    assert any(a["rule_id"] == "R8" for a in data["alerts"])


# ===========================================================================
# 7. Localization Parity & Forbidden Words Audit
# ===========================================================================

def test_r8_localization_key_parity():
    """All R8 message and next-step keys must resolve in both bn.json and en.json."""
    keys = [
        MSG_R8_CONTRADICTION,
        MSG_R8_REVIEW_OMITTED_HEIR,
        MSG_R8_REVIEW_INPUTS,
        MSG_R8_CONSISTENT,
        NEXT_STEP_R8,
    ]
    for key in keys:
        bn_val = translate(key, "bn")
        en_val = translate(key, "en")
        assert bn_val != key, f"Missing key in bn.json: {key}"
        assert en_val != key, f"Missing key in en.json: {key}"
        assert len(bn_val) > 0
        assert len(en_val) > 0


def test_r8_forbidden_words_audit():
    """
    Ensure zero forbidden words in R8 messages, next-step guides, and localized calculations.
    Forbidden: safe, valid, legal, verified owner, fraud, forged, scam, you will be cheated,
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

    keys = [
        MSG_R8_CONTRADICTION,
        MSG_R8_REVIEW_OMITTED_HEIR,
        MSG_R8_REVIEW_INPUTS,
        MSG_R8_CONSISTENT,
        NEXT_STEP_R8,
    ]
    for key in keys:
        en_str = translate(key, "en")
        bn_str = translate(key, "bn")
        for f in forbidden_en:
            assert not re.search(f, en_str, re.IGNORECASE), f"Forbidden word '{f}' in en key '{key}': {en_str}"
        for f in forbidden_bn:
            assert f not in bn_str, f"Forbidden Bengali word '{f}' in bn key '{key}': {bn_str}"

    # Audit sample R8 calculations
    sample_calcs = [
        "No heir declarations recorded in parcel history.",
        "Declared heir 'P_DAUGHTER' (relation: daughter) under complete declaration 'SANAD_001' is omitted from subsequent record 'SR_RS' without any recorded deed of sale, gift, or release.",
        "Declared heir 'P_DAUGHTER' (daughter) is omitted from subsequent record 'SR_RS', but interest is accounted for by recorded deed 'DEED_01' (SALE) dated 1982-05-10.",
    ]
    for calc in sample_calcs:
        bn_calc = localize_calculation(calc, "R8", lang="bn")
        for f in forbidden_bn:
            assert f not in bn_calc, f"Forbidden Bengali word '{f}' in calculation: {bn_calc}"


# ===========================================================================
# 8. Baseline Dataset SHA-256 Hash Invariance
# ===========================================================================

def test_v10_baseline_hash_strictly_invariant():
    """
    Baseline dataset (data/demo_family.json) hash must remain:
    b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01
    """
    BASELINE_HASH = "b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01"
    ds = load_dataset(DEMO_FAMILY_PATH)
    events = [e for h in ds.histories for e in h.events]
    srs = [s for h in ds.histories for s in h.survey_records]
    current_hash = hash_dataset(events, srs)
    assert current_hash == BASELINE_HASH, f"Hash changed! Expected {BASELINE_HASH}, got {current_hash}"
