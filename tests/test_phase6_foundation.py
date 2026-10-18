"""
Tests for JomiGraph AI v1.1 — Phase 6 Foundation
=================================================
Verifies:
  1. Shared rule dispatcher (dispatch_event_rules, dispatch_history_rules)
  2. Model extensions and backwards compatibility defaults
  3. Non-transferring replay of encumbrance/authorization event types
  4. Dataset loader compatibility with v1.0 and v1.1 formats
  5. Baseline SHA-256 hash immutability
  6. Attention Score configuration constants
  7. Deterministic demo_v11 dataset generation and schema
"""

from __future__ import annotations

from datetime import date
from fractions import Fraction
from pathlib import Path
import pytest

from jomigraph.config import (
    ATTENTION_RULE_WEIGHTS,
    ATTENTION_STATUS_BASE_WEIGHTS,
    TRAFFIC_LIGHT_GREEN,
    TRAFFIC_LIGHT_RED,
    TRAFFIC_LIGHT_YELLOW,
)
from jomigraph.engine.benchmark import evaluate_dataset, evaluate_history
from jomigraph.engine.replay import compute_state
from jomigraph.engine.rules import (
    Alert,
    Status,
    dispatch_event_rules,
    dispatch_history_rules,
)
from jomigraph.engine.simulate import evaluate, hash_dataset, simulate
from jomigraph.loader import (
    Dataset,
    dataset_to_dict,
    load_dataset,
    parse_dataset_dict,
)
from jomigraph.models import (
    Deed,
    Event,
    EventType,
    Parcel,
    ParcelHistory,
    Person,
    SurveyRecord,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
BASELINE_HASH = "b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01"


# ===========================================================================
# 1. Model Extensions & Backward Compatibility
# ===========================================================================

def test_person_model_defaults_and_dummy_id():
    p1 = Person(id="P1", name="Tariq")
    assert p1.dummy_id is None

    p2 = Person(id="P2", name="Tariq", dummy_id="DUMMY-ID-0001")
    assert p2.dummy_id == "DUMMY-ID-0001"


def test_parcel_model_defaults_and_lock_fields():
    p1 = Parcel(id="PR1", dag_no="101", mouza="Dhaka")
    assert p1.parent_id is None
    assert p1.is_khas is False
    assert p1.under_acquisition is False
    assert p1.flag_date is None
    assert p1.court_case_no is None
    assert p1.case_status is None
    assert p1.injunction is False

    p2 = Parcel(
        id="PR2",
        dag_no="102",
        mouza="Mirpur",
        is_khas=True,
        under_acquisition=True,
        flag_date=date(2020, 1, 1),
        court_case_no="DEMO-CASE-001",
        case_status="pending",
        injunction=True,
    )
    assert p2.is_khas is True
    assert p2.court_case_no == "DEMO-CASE-001"


def test_deed_model_content_hash():
    d1 = Deed(id="D1", deed_no="1001", registration_date=date(2020, 1, 1))
    assert d1.content_hash is None

    d2 = Deed(id="D2", deed_no="1002", registration_date=date(2020, 1, 1), content_hash="abc123hash")
    assert d2.content_hash == "abc123hash"


def test_event_types_extended():
    assert EventType.MORTGAGE == "MORTGAGE"
    assert EventType.MORTGAGE_RELEASE == "MORTGAGE_RELEASE"
    assert EventType.POA_GRANT == "POA_GRANT"
    assert EventType.POA_REVOKE == "POA_REVOKE"


def test_event_model_portion_boundary_poa_defaults():
    e1 = Event(
        id="E1",
        type=EventType.SALE,
        seq=1,
        event_date=date(2020, 1, 1),
        parcel_id="P1",
        from_person="P1",
        to_person="P2",
        area=Fraction(5),
        deed_id=None,
        portion_id=None,
        linked_event_id=None,
        source_record_id=None,
    )
    assert e1.portion is None
    assert e1.boundary is None
    assert e1.via_poa_id is None

    e2 = Event(
        id="E2",
        type=EventType.SALE,
        seq=2,
        event_date=date(2020, 2, 1),
        parcel_id="P1",
        from_person="P1",
        to_person="P2",
        area=Fraction(5),
        deed_id=None,
        portion_id="PORTION_1",
        linked_event_id=None,
        source_record_id=None,
        portion={"portion_id": "PORTION_1", "boundary": "North plot"},
        boundary="North plot",
        via_poa_id="POA_1",
    )
    assert e2.boundary == "North plot"
    assert e2.via_poa_id == "POA_1"


def test_parcel_history_heir_declaration_default():
    sr = SurveyRecord(
        id="SR1",
        parcel_id="P1",
        survey="BS",
        khatian_no="K1",
        record_date=date(2000, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P1", Fraction(10)),),
    )
    h = ParcelHistory(
        parcel_id="P1",
        baseline_record_id="SR1",
        baseline_complete=True,
        start_record_id="SR1",
        end_date=None,
        survey_records=(sr,),
        events=(),
    )
    assert h.heir_declaration is None


# ===========================================================================
# 2. Non-Transferring Replay of New Event Types
# ===========================================================================

def test_mortgage_and_poa_non_transferring_in_replay():
    baseline = SurveyRecord(
        id="SR1",
        parcel_id="P1",
        survey="BS",
        khatian_no="K1",
        record_date=date(2000, 1, 1),
        recorded_area=Fraction(10),
        holders=(("P1", Fraction(10)),),
    )
    events = [
        Event(
            id="E1",
            type=EventType.POA_GRANT,
            seq=1,
            event_date=date(2010, 1, 1),
            parcel_id="P1",
            from_person="P1",
            to_person="AGENT_1",
            area=Fraction(10),
            deed_id=None,
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        ),
        Event(
            id="E2",
            type=EventType.MORTGAGE,
            seq=2,
            event_date=date(2012, 1, 1),
            parcel_id="P1",
            from_person="P1",
            to_person="BANK_1",
            area=Fraction(10),
            deed_id=None,
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        ),
        Event(
            id="E3",
            type=EventType.MORTGAGE_RELEASE,
            seq=3,
            event_date=date(2014, 1, 1),
            parcel_id="P1",
            from_person="BANK_1",
            to_person="P1",
            area=Fraction(10),
            deed_id=None,
            portion_id=None,
            linked_event_id="E2",
            source_record_id=None,
        ),
        Event(
            id="E4",
            type=EventType.POA_REVOKE,
            seq=4,
            event_date=date(2015, 1, 1),
            parcel_id="P1",
            from_person="P1",
            to_person="AGENT_1",
            area=Fraction(10),
            deed_id=None,
            portion_id=None,
            linked_event_id="E1",
            source_record_id=None,
        ),
    ]
    state, issues = compute_state(events, baseline)
    assert not issues
    # P1's area must still be exactly 10; AGENT_1 and BANK_1 must not receive transfer area
    assert state.get("P1") == Fraction(10)
    assert "AGENT_1" not in state
    assert "BANK_1" not in state


# ===========================================================================
# 3. Shared Rule Dispatcher Consistency
# ===========================================================================

def test_shared_dispatch_matches_v10_benchmark_dataset():
    ds = load_dataset(DATA_DIR / "demo_family.json")
    # All 21 clean parcels must return 0 contradiction and 0 review alerts via shared dispatch
    report = evaluate_dataset(ds)
    assert report.clean_false_alarm_count == 0
    assert report.planted_detected_count == 7


def test_evaluate_and_dispatch_event_rules_consistency():
    ds = load_dataset(DATA_DIR / "demo_family.json")
    history = ds.get_history("PARCEL_STORY_01")
    assert history is not None
    last_event = history.events[-1]

    # Call evaluate (uses dispatch_event_rules)
    state, alerts = evaluate(history.events, history, target_event=last_event, deeds=ds.deeds)
    assert isinstance(alerts, list)
    for a in alerts:
        assert isinstance(a, Alert)
        assert a.evidence_ids


def test_simulation_integrity_and_dataset_hash():
    ds = load_dataset(DATA_DIR / "demo_family.json")
    all_events_before = [e for h in ds.histories for e in h.events]
    all_srs_before = [s for h in ds.histories for s in h.survey_records]

    # Verify baseline hash matches README exactly
    hash_before = hash_dataset(all_events_before, all_srs_before)
    assert hash_before == BASELINE_HASH

    history = ds.get_history("PARCEL_LAB_DEMO")
    assert history is not None

    # Run simulation
    proposed = Event(
        id="SIM_E1",
        type=EventType.SALE,
        seq=999,
        event_date=date(2025, 1, 1),
        parcel_id="PARCEL_LAB_DEMO",
        from_person="P_G3_TAREQ",
        to_person="P_EXT_LATIF",
        area=Fraction(3),
        deed_id=None,
        portion_id=None,
        linked_event_id=None,
        source_record_id=None,
    )
    res = simulate(history.events, proposed, history, deeds=ds.deeds)
    assert res.available_before == Fraction(3)
    assert res.available_after == Fraction(0)

    # Verify full dataset hash after simulation is strictly identical
    all_events_after = [e for h in ds.histories for e in h.events]
    all_srs_after = [s for h in ds.histories for s in h.survey_records]
    hash_after = hash_dataset(all_events_after, all_srs_after)
    assert hash_after == BASELINE_HASH



# ===========================================================================
# 4. v1.1 Dataset Loader & Serialization Roundtrip
# ===========================================================================

def test_demo_v11_dataset_loads_cleanly():
    v11_file = DATA_DIR / "demo_v11.json"
    assert v11_file.is_file(), "data/demo_v11.json must exist"

    ds = load_dataset(v11_file)
    assert len(ds.parcels) >= 15
    assert len(ds.deeds) >= 10
    assert len(ds.persons) >= 10

    # Verify new model fields loaded properly
    khas_parcel = ds.get_parcel("PARCEL_PLANTED_R11")
    assert khas_parcel is not None
    assert khas_parcel.is_khas is True
    assert khas_parcel.court_case_no == "DEMO-CASE-0011"
    assert khas_parcel.injunction is True

    # Verify deed content hash loaded
    deed_r12 = ds.get_deed("DEED_V11_R12_REC")
    assert deed_r12 is not None
    assert deed_r12.content_hash is not None

    # Verify heir declaration loaded
    hist_r8 = ds.get_history("PARCEL_PLANTED_R8")
    assert hist_r8 is not None
    assert hist_r8.heir_declaration is not None
    assert hist_r8.heir_declaration["complete"] is True


def test_dataset_to_dict_roundtrip():
    v11_file = DATA_DIR / "demo_v11.json"
    ds1 = load_dataset(v11_file)
    as_dict = dataset_to_dict(ds1)
    ds2 = parse_dataset_dict(as_dict)

    assert len(ds1.parcels) == len(ds2.parcels)
    assert len(ds1.persons) == len(ds2.persons)
    assert len(ds1.deeds) == len(ds2.deeds)
    assert len(ds1.histories) == len(ds2.histories)

    p1 = ds1.get_parcel("PARCEL_PLANTED_R11")
    p2 = ds2.get_parcel("PARCEL_PLANTED_R11")
    assert p1.is_khas == p2.is_khas
    assert p1.court_case_no == p2.court_case_no


# ===========================================================================
# 5. Attention Weights Configuration
# ===========================================================================

def test_attention_score_weights_configuration():
    assert "CONTRADICTION" in ATTENTION_STATUS_BASE_WEIGHTS
    assert "REVIEW" in ATTENTION_STATUS_BASE_WEIGHTS
    assert "CONSISTENT" in ATTENTION_STATUS_BASE_WEIGHTS
    assert ATTENTION_STATUS_BASE_WEIGHTS["CONTRADICTION"] > ATTENTION_STATUS_BASE_WEIGHTS["REVIEW"]
    assert ATTENTION_STATUS_BASE_WEIGHTS["CONSISTENT"] == 0

    for rule in ("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14", "R15"):
        assert rule in ATTENTION_RULE_WEIGHTS
        assert ATTENTION_RULE_WEIGHTS[rule] > 0

    assert TRAFFIC_LIGHT_RED == "red"
    assert TRAFFIC_LIGHT_YELLOW == "yellow"
    assert TRAFFIC_LIGHT_GREEN == "green"
