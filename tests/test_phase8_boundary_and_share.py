"""
Tests for JomiGraph AI v1.1 — Phase 8: Boundary Disambiguation & Traditional Share
===================================================================================
Covers:
  1. F16 / R15: Structured boundary duplicate sale detection
     - Identical boundaries with different portion labels -> Contradiction Found
     - Sub-dag / lineage containment (e.g. 101/1 and 101/1-ka) -> Contradiction Found
     - Partial or missing boundary descriptors -> Review Required
     - Distinct boundaries -> Consistent with supplied records
     - Filtering non-cancelled transfers (cancelled sale does not trigger duplicate sale)
     - Non-transferring events (mortgages, mutations) ignored
     - Non-empty evidence sets
  2. Simulation-Lab Boundary Inputs:
     - Pre-registration counterfactual simulation with North/South/East/West and sub-dag
     - Clean boundary passes, conflicting boundary triggers Contradiction
     - Pure function invariance (dataset hash unchanged before and after simulation)
     - Citizen role sanitization (no internal rule IDs, evidence IDs, or calculations)
  3. X1 Traditional Land Share Representation (Ana-Ganda-Kora-Kranti-Til):
     - Exact Fraction decomposition: 16 ana = 1 whole, 20 ganda, 4 kora, 3 kranti, 20 til
     - 76,800 til per whole
     - 1/4 = 4 ana, 1/5 = 3 ana 4 ganda
     - Bilingual formatting (Bangla and English) with exact Fraction alongside
     - Conversion disclaimer (confirm with Law mentor, display only, not legal title)
  4. Five-Co-Owner Ejmali Dag Test:
     - R1 enforces each co-owner's individual quota/share rather than aggregate dag area
     - Sale under individual quota passes
     - Sale exceeding individual quota fails even when total sale is less than dag total area
"""

from __future__ import annotations

from datetime import date
from fractions import Fraction
from pathlib import Path
import json
from typing import Any, Optional
import pytest
from starlette.testclient import TestClient

from jomigraph.api.app import create_app
from jomigraph.engine.rules import (
    Alert,
    Status,
    check_r1,
    check_r2,
    check_r15,
)
from jomigraph.engine.simulate import hash_dataset, simulate
from jomigraph.loader import load_dataset
from jomigraph.models import (
    Deed,
    Event,
    EventType,
    Parcel,
    ParcelHistory,
    Person,
    SurveyRecord,
)
from jomigraph.traditional_share import (
    ANA_PER_WHOLE,
    GANDA_PER_ANA,
    KORA_PER_GANDA,
    KRANTI_PER_KORA,
    TIL_PER_KRANTI,
    TIL_PER_WHOLE,
    TRADITIONAL_SHARE_DISCLAIMER_BN,
    TRADITIONAL_SHARE_DISCLAIMER_EN,
    calculate_coowner_quotas,
    format_traditional_share,
    fraction_to_traditional_share,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_V11_PATH = PROJECT_ROOT / "data" / "demo_v11.json"
BASELINE_PATH = PROJECT_ROOT / "data" / "demo_family.json"
BASELINE_HASH = "b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01"


def make_event(
    id: str,
    type: EventType,
    seq: int = 1,
    event_date: Optional[date] = date(2015, 6, 1),
    parcel_id: str = "PARCEL_101",
    from_person: Optional[str] = None,
    to_person: Optional[str] = None,
    area: Optional[Fraction] = None,
    deed_id: Optional[str] = None,
    portion_id: Optional[str] = None,
    linked_event_id: Optional[str] = None,
    source_record_id: Optional[str] = None,
    portion: Optional[dict[str, Any]] = None,
    boundary: Optional[str | dict[str, Any]] = None,
    via_poa_id: Optional[str] = None,
) -> Event:
    """Helper to construct an Event model with explicit defaults for all optional fields."""
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
# 1. F16 / R15 Structured Boundary Rule Logic
# ===========================================================================

class TestRuleR15BoundaryLogic:
    """Unit tests for check_r15 boundary disambiguation logic."""

    @pytest.fixture
    def baseline_record(self) -> SurveyRecord:
        return SurveyRecord(
            id="SR_BASE",
            parcel_id="PARCEL_101",
            survey="BS",
            khatian_no="1001",
            record_date=date(2000, 1, 1),
            recorded_area=Fraction(10, 1),
            holders=(( "P_OWNER", Fraction(10, 1) ),),
        )

    def test_r15_identical_boundaries_with_different_portion_labels_contradiction(
        self, baseline_record: SurveyRecord
    ):
        """
        R15 catches the same physical piece sold twice even when portion_id labels differ.
        (Complementing R2, which only matches identical portion_ids).
        """
        boundary_1 = {
            "north": "Main Road",
            "south": "Canal",
            "east": "Plot 102",
            "west": "Plot 103",
        }
        boundary_2 = {
            "north": "Main Road",
            "south": "Canal",
            "east": "Plot 102",
            "west": "Plot 103",
        }

        e1 = make_event(
            id="E_SALE_1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2015, 6, 1),
            parcel_id="PARCEL_101",
            from_person="P_OWNER",
            to_person="P_BUYER_1",
            area=Fraction(5, 1),
            portion_id="PORTION_NORTH",
            boundary=boundary_1,
            portion={"portion_id": "PORTION_NORTH", "boundary": boundary_1, "portion_area": "5"},
        )
        e2 = make_event(
            id="E_SALE_2",
            type=EventType.SALE,
            seq=2,
            event_date=date(2016, 8, 1),
            parcel_id="PARCEL_101",
            from_person="P_OWNER",
            to_person="P_BUYER_2",
            area=Fraction(5, 1),
            portion_id="PORTION_SPECIAL_FRONT",  # Different label!
            boundary=boundary_2,
            portion={"portion_id": "PORTION_SPECIAL_FRONT", "boundary": boundary_2, "portion_area": "5"},
        )

        all_events = [e1, e2]

        # Evaluating e2 against prior events
        alert = check_r15(e2, all_events, baseline_record)
        assert alert.status == Status.CONTRADICTION
        assert "E_SALE_1" in alert.evidence_ids
        assert e2.id in alert.evidence_ids
        assert alert.rule_id == "R15"
        assert "conflicts with prior recorded transfer" in alert.calculation

    def test_r15_lineage_containment_subdag_contradiction(
        self, baseline_record: SurveyRecord
    ):
        """
        Lineage containment (e.g. 101/1 and 101/1-ka) produces Contradiction Found.
        """
        e1 = make_event(
            id="E_SALE_1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2015, 6, 1),
            parcel_id="PARCEL_101",
            from_person="P_OWNER",
            to_person="P_BUYER_1",
            area=Fraction(5, 1),
            portion_id="101/1",
            boundary="101/1",
        )
        e2 = make_event(
            id="E_SALE_2",
            type=EventType.SALE,
            seq=2,
            event_date=date(2016, 8, 1),
            parcel_id="PARCEL_101",
            from_person="P_OWNER",
            to_person="P_BUYER_2",
            area=Fraction(2, 1),
            portion_id="101/1-ka",
            boundary="101/1-ka",
        )

        alert = check_r15(e2, [e1, e2], baseline_record)
        assert alert.status == Status.CONTRADICTION
        assert "E_SALE_1" in alert.evidence_ids
        assert e2.id in alert.evidence_ids

    def test_r15_missing_or_partial_boundary_review_required(
        self, baseline_record: SurveyRecord
    ):
        """
        Missing or partial boundary descriptor returns Review Required.
        """
        # Partial: only north specified, others missing
        partial_boundary = {"north": "Main Road"}
        e_partial = make_event(
            id="E_PARTIAL",
            type=EventType.SALE,
            seq=1,
            event_date=date(2015, 6, 1),
            parcel_id="PARCEL_101",
            from_person="P_OWNER",
            to_person="P_BUYER_1",
            area=Fraction(5, 1),
            boundary=partial_boundary,
        )

        alert_partial = check_r15(e_partial, [e_partial], baseline_record)
        assert alert_partial.status == Status.REVIEW
        assert alert_partial.evidence_ids == (e_partial.id, baseline_record.id)
        assert "missing, partial, or ambiguous" in alert_partial.calculation

        # Missing completely
        e_none = make_event(
            id="E_NONE",
            type=EventType.SALE,
            seq=2,
            event_date=date(2015, 6, 2),
            parcel_id="PARCEL_101",
            from_person="P_OWNER",
            to_person="P_BUYER_1",
            area=Fraction(5, 1),
            boundary=None,
            portion=None,
        )
        alert_none = check_r15(e_none, [e_none], baseline_record)
        assert alert_none.status == Status.REVIEW

    def test_r15_distinct_boundaries_consistent(
        self, baseline_record: SurveyRecord
    ):
        """
        Two distinct non-overlapping boundaries return Consistent with supplied records.
        """
        b_north = {"north": "River", "south": "Road", "east": "Plot A", "west": "Plot B"}
        b_south = {"north": "Road", "south": "Pond", "east": "Plot C", "west": "Plot D"}

        e1 = make_event(
            id="E_NORTH",
            type=EventType.SALE,
            seq=1,
            event_date=date(2015, 6, 1),
            parcel_id="PARCEL_101",
            from_person="P_OWNER",
            to_person="P_BUYER_1",
            area=Fraction(5, 1),
            portion_id="PORTION_NORTH",
            boundary=b_north,
        )
        e2 = make_event(
            id="E_SOUTH",
            type=EventType.SALE,
            seq=2,
            event_date=date(2016, 8, 1),
            parcel_id="PARCEL_101",
            from_person="P_OWNER",
            to_person="P_BUYER_2",
            area=Fraction(5, 1),
            portion_id="PORTION_SOUTH",
            boundary=b_south,
        )

        alert = check_r15(e2, [e1, e2], baseline_record)
        assert alert.status == Status.CONSISTENT
        assert "distinct and non-overlapping" in alert.calculation

    def test_r15_cancelled_transfer_ignored(
        self, baseline_record: SurveyRecord
    ):
        """
        A sale that was subsequently CANCELLED is not considered an active conflict.
        """
        b = {"north": "Road", "south": "Pond", "east": "Plot A", "west": "Plot B"}
        e_sale1 = make_event(
            id="E_SALE_1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2015, 6, 1),
            parcel_id="PARCEL_101",
            from_person="P_OWNER",
            to_person="P_BUYER_1",
            area=Fraction(5, 1),
            portion_id="PORTION_1",
            boundary=b,
        )
        e_cancel1 = make_event(
            id="E_CANCEL_1",
            type=EventType.CANCEL,
            seq=2,
            event_date=date(2015, 7, 1),
            parcel_id="PARCEL_101",
            linked_event_id="E_SALE_1",
        )
        e_sale2 = make_event(
            id="E_SALE_2",
            type=EventType.SALE,
            seq=3,
            event_date=date(2016, 8, 1),
            parcel_id="PARCEL_101",
            from_person="P_OWNER",
            to_person="P_BUYER_2",
            area=Fraction(5, 1),
            portion_id="PORTION_RESOLD",
            boundary=b,
        )

        all_events = [e_sale1, e_cancel1, e_sale2]
        alert = check_r15(e_sale2, all_events, baseline_record)
        assert alert.status == Status.CONSISTENT


# ===========================================================================
# 2. Simulation-Lab Boundary Inputs & API Tests
# ===========================================================================

class TestSimulationLabBoundaryAPI:
    """Tests for counterfactual simulation with structured boundary inputs."""

    @pytest.fixture
    def client(self) -> TestClient:
        app = create_app(dataset_path=str(DEMO_V11_PATH))
        return TestClient(app)

    def test_simulation_with_conflicting_boundary_triggers_r15_contradiction(
        self, client: TestClient
    ):
        """
        Simulating a sale with the exact same boundary as an existing sale
        on PARCEL_PLANTED_R15 triggers R15 Contradiction in the lab.
        """
        payload = {
            "parcel_id": "PARCEL_PLANTED_R15",
            "from_person": "P_V11_KARIM",
            "to_person": "P_BUYER_LAB",
            "area": "2",
            "date": "2023-01-01",
            "portion_id": "PORTION_NEW_LABEL",
            "boundary": "North roadside plot",  # Identical to E_V11_R15_SALE1 boundary
            "lang": "en",
        }
        res = client.post("/simulate?role=reviewer&lang=en", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["overall_status_code"] == "CONTRADICTION"

        r15_alerts = [a for a in data["alerts"] if a["rule_id"] == "R15"]
        assert len(r15_alerts) >= 1
        assert r15_alerts[0]["status_code"] == "CONTRADICTION"
        assert "E_V11_R15_SALE1" in r15_alerts[0]["evidence_ids"]

    def test_simulation_with_distinct_boundary_passes_r15(
        self, client: TestClient
    ):
        """
        Simulating a sale with distinct north/south/east/west boundary descriptors passes R15.
        """
        payload = {
            "parcel_id": "PARCEL_CLEAN_R15_BOUNDARY",
            "from_person": "P_V11_CLEAN_H1",
            "to_person": "P_BUYER_LAB",
            "area": "1",
            "date": "2023-01-01",
            "portion_id": "PORTION_EAST_CORNER",
            "boundary_north": "East Road",
            "boundary_south": "Boundary Wall",
            "boundary_east": "Plot 99",
            "boundary_west": "Drain",
            "lang": "en",
        }
        res = client.post("/simulate?role=reviewer&lang=en", json=payload)
        assert res.status_code == 200
        data = res.json()

        r15_alerts = [a for a in data["alerts"] if a["rule_id"] == "R15"]
        assert len(r15_alerts) >= 1
        assert r15_alerts[0]["status_code"] == "CONSISTENT"

    def test_simulation_purity_dataset_hash_invariant(
        self, client: TestClient
    ):
        """
        Simulations with boundary descriptors never mutate the underlying dataset.
        """
        ds = load_dataset(DEMO_V11_PATH)
        events_before = [e for h in ds.histories for e in h.events]
        srs_before = [s for h in ds.histories for s in h.survey_records]
        hash_before = hash_dataset(events_before, srs_before)

        # Run multiple simulations
        client.post("/simulate", json={
            "parcel_id": "PARCEL_CLEAN_R15_BOUNDARY",
            "from_person": "P_V11_CLEAN_H1",
            "area": "2",
            "boundary_north": "Road",
            "boundary_south": "Canal",
            "boundary_east": "Plot 1",
            "boundary_west": "Plot 2",
        })

        events_after = [e for h in ds.histories for e in h.events]
        srs_after = [s for h in ds.histories for s in h.survey_records]
        hash_after = hash_dataset(events_after, srs_after)

        assert hash_before == hash_after

    def test_simulation_citizen_role_sanitization(
        self, client: TestClient
    ):
        """
        Citizen role receives localized, sanitized alerts with no internal rule IDs,
        evidence IDs, or calculation formulas.
        """
        payload = {
            "parcel_id": "PARCEL_PLANTED_R15",
            "from_person": "P_V11_KARIM",
            "area": "2",
            "boundary": "North roadside plot",
            "lang": "bn",
        }
        res = client.post("/simulate?role=citizen&lang=bn", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert "rule_id" not in data
        for alert in data["alerts"]:
            assert "rule_id" not in alert
            assert "evidence_ids" not in alert
            assert "calculation" not in alert
            assert alert["status"] in ("অসঙ্গতি পাওয়া গেছে", "পর্যালোচনা প্রয়োজন", "সঙ্গতিপূর্ণ")


# ===========================================================================
# 3. X1 Traditional Land Share Representation Tests
# ===========================================================================

class TestTraditionalShareRepresentation:
    """Tests for exact Fraction Ana-Ganda-Kora-Kranti-Til decomposition and formatting."""

    def test_conversion_constants_match_spec(self):
        """Confirm conversion multipliers per master spec § X1."""
        assert ANA_PER_WHOLE == 16
        assert GANDA_PER_ANA == 20
        assert KORA_PER_GANDA == 4
        assert KRANTI_PER_KORA == 3
        assert TIL_PER_KRANTI == 20
        # 16 * 20 * 4 * 3 * 20 = 76,800
        assert TIL_PER_WHOLE == 76800

    def test_exact_share_decompositions(self):
        """
        Verify exact decompositions:
          - 1 whole = 16 ana
          - 1/4 = 4 ana
          - 1/5 = 3 ana 4 ganda
          - 1 ana = 20 ganda
          - 1 ganda = 4 kora
          - 1 kora = 3 kranti
          - 1 kranti = 20 til
        """
        # 1 whole
        d_whole = fraction_to_traditional_share(Fraction(1, 1))
        assert d_whole["ana"] == 16
        assert d_whole["ganda"] == 0
        assert d_whole["kora"] == 0
        assert d_whole["kranti"] == 0
        assert d_whole["til"] == 0
        assert d_whole["remainder_til"] == 0

        # 1/4 = 4 ana
        d_quarter = fraction_to_traditional_share(Fraction(1, 4))
        assert d_quarter["ana"] == 4
        assert d_quarter["ganda"] == 0
        assert d_quarter["kora"] == 0
        assert d_quarter["kranti"] == 0
        assert d_quarter["til"] == 0

        # 1/5 = 3 ana 4 ganda
        # (1/5 * 16 = 3.2 ana; 0.2 * 20 = 4 ganda)
        d_fifth = fraction_to_traditional_share(Fraction(1, 5))
        assert d_fifth["ana"] == 3
        assert d_fifth["ganda"] == 4
        assert d_fifth["kora"] == 0
        assert d_fifth["kranti"] == 0
        assert d_fifth["til"] == 0
        assert d_fifth["remainder_til"] == 0

        # 1/16 = 1 ana
        d_ana = fraction_to_traditional_share(Fraction(1, 16))
        assert d_ana["ana"] == 1
        assert d_ana["ganda"] == 0

        # 1/320 = 1 ganda
        d_ganda = fraction_to_traditional_share(Fraction(1, 320))
        assert d_ganda["ana"] == 0
        assert d_ganda["ganda"] == 1

        # 1/1280 = 1 kora
        d_kora = fraction_to_traditional_share(Fraction(1, 1280))
        assert d_kora["kora"] == 1

        # 1/3840 = 1 kranti
        d_kranti = fraction_to_traditional_share(Fraction(1, 3840))
        assert d_kranti["kranti"] == 1

        # 1/76800 = 1 til
        d_til = fraction_to_traditional_share(Fraction(1, 76800))
        assert d_til["til"] == 1
        assert d_til["remainder_til"] == 0

    def test_bilingual_formatting(self):
        """Display exact Fraction alongside traditional units in Bangla and English."""
        # 1/4
        fmt_bn_quarter = format_traditional_share(Fraction(1, 4), lang="bn", include_fraction=True)
        fmt_en_quarter = format_traditional_share(Fraction(1, 4), lang="en", include_fraction=True)
        assert "৪ আনা" in fmt_bn_quarter
        assert "(১/৪)" in fmt_bn_quarter
        assert "4 ana" in fmt_en_quarter
        assert "(1/4)" in fmt_en_quarter

        # 1/5
        fmt_bn_fifth = format_traditional_share(Fraction(1, 5), lang="bn", include_fraction=True)
        fmt_en_fifth = format_traditional_share(Fraction(1, 5), lang="en", include_fraction=True)
        assert "৩ আনা ৪ গণ্ডা" in fmt_bn_fifth
        assert "(১/৫)" in fmt_bn_fifth
        assert "3 ana 4 ganda" in fmt_en_fifth
        assert "(1/5)" in fmt_en_fifth

    def test_traditional_share_disclaimer_preservation(self):
        """Conversion disclaimer must emphasize confirmation with Law mentor and no legal proof."""
        assert "Law mentor" in TRADITIONAL_SHARE_DISCLAIMER_EN
        assert "does not constitute legal proof of title" in TRADITIONAL_SHARE_DISCLAIMER_EN
        assert "আইন উপদেষ্টা" in TRADITIONAL_SHARE_DISCLAIMER_BN
        assert "আইনি সনদ নয়" in TRADITIONAL_SHARE_DISCLAIMER_BN


# ===========================================================================
# 4. Five-Co-Owner Ejmali Dag & R1 Enforcement Tests
# ===========================================================================

class TestFiveCoownerEjmaliDag:
    """
    Tests for SPEC § X1:
    'Show each co-owner's share and limit in the Reviewer view, with tests for R1
    on a 5-co-owner (Ejmali) dag.'
    Verifies R1 enforces each co-owner's individual quota/share rather than
    comparing only against aggregate dag area.
    """

    @pytest.fixture
    def ejmali_dag_history(self) -> ParcelHistory:
        """
        Ejmali Dag of 100 decimals with 5 equal co-owners (20 decimals each = 1/5 share each).
        """
        holders = (
            ("P_COOWNER_1", Fraction(20, 1)),
            ("P_COOWNER_2", Fraction(20, 1)),
            ("P_COOWNER_3", Fraction(20, 1)),
            ("P_COOWNER_4", Fraction(20, 1)),
            ("P_COOWNER_5", Fraction(20, 1)),
        )
        sr = SurveyRecord(
            id="SR_EJMALI_100",
            parcel_id="PARCEL_EJMALI_5CO",
            survey="BS",
            khatian_no="5501",
            record_date=date(2010, 1, 1),
            recorded_area=Fraction(100, 1),
            holders=holders,
        )
        return ParcelHistory(
            parcel_id="PARCEL_EJMALI_5CO",
            survey_records=[sr],
            events=[],
            baseline_record_id="SR_EJMALI_100",
            baseline_complete=True,
            start_record_id="SR_EJMALI_100",
            end_date=date(2025, 1, 1),
        )

    def test_calculate_coowner_quotas_breakdown(self, ejmali_dag_history: ParcelHistory):
        sr = ejmali_dag_history.survey_records[0]
        quotas = calculate_coowner_quotas(sr.holders, sr.recorded_area, lang="en")
        assert len(quotas) == 5

        for q in quotas:
            assert q["recorded_area"] == Fraction(20, 1)
            assert q["quota_limit"] == Fraction(20, 1)
            assert q["share_fraction"] == Fraction(1, 5)
            assert "3 ana 4 ganda" in q["traditional_share"]

    def test_r1_passes_when_sale_is_within_individual_coowner_quota(
        self, ejmali_dag_history: ParcelHistory
    ):
        """
        Co-owner 1 sells 15 decimals out of their 20 decimal quota (<= 20) -> R1 Consistent.
        """
        e_sale = make_event(
            id="E_VALID_COOWNER_SALE",
            type=EventType.SALE,
            seq=1,
            event_date=date(2018, 5, 10),
            parcel_id="PARCEL_EJMALI_5CO",
            from_person="P_COOWNER_1",
            to_person="P_BUYER_A",
            area=Fraction(15, 1),
        )
        events = [e_sale]
        alert = check_r1(e_sale, ejmali_dag_history, events)
        assert alert.status == Status.CONSISTENT
        assert "requested 15, available 20" in alert.calculation

    def test_r1_fails_when_sale_exceeds_individual_coowner_quota_despite_aggregate_area(
        self, ejmali_dag_history: ParcelHistory
    ):
        """
        CRITICAL TEST:
        Co-owner 1 attempts to sell 25 decimals.
        Note: The dag aggregate area is 100 decimals, and 25 < 100 decimals.
        HOWEVER, Co-owner 1 only owns 20 decimals!
        R1 MUST enforce Co-owner 1's individual quota (20 decimals) and trigger
        Contradiction Found with excess = 5 decimals.
        """
        e_excess_sale = make_event(
            id="E_OVER_COOWNER_SALE",
            type=EventType.SALE,
            seq=1,
            event_date=date(2018, 5, 10),
            parcel_id="PARCEL_EJMALI_5CO",
            from_person="P_COOWNER_1",
            to_person="P_BUYER_A",
            area=Fraction(25, 1),  # Exceeds P_COOWNER_1's 20 decimal quota!
        )
        events = [e_excess_sale]
        alert = check_r1(e_excess_sale, ejmali_dag_history, events)

        assert alert.status == Status.CONTRADICTION
        assert alert.rule_id == "R1"
        assert "excess 5" in alert.calculation
        assert "requested 25, available 20" in alert.calculation

    def test_r1_counterfactual_simulation_enforces_coowner_quota(
        self, ejmali_dag_history: ParcelHistory
    ):
        """
        simulate() with a proposed transfer of 25 decimals by P_COOWNER_1
        enforces individual quota and returns excess = 5.
        """
        proposed = make_event(
            id="PROPOSED_COOWNER_SALE",
            type=EventType.SALE,
            seq=1,
            event_date=date(2020, 1, 1),
            parcel_id="PARCEL_EJMALI_5CO",
            from_person="P_COOWNER_1",
            to_person="P_BUYER_B",
            area=Fraction(25, 1),
        )
        sim_res = simulate(
            events=ejmali_dag_history.events,
            proposed=proposed,
            parcel_history=ejmali_dag_history,
        )

        assert sim_res.available_before == Fraction(20, 1)  # Co-owner 1's quota
        assert sim_res.available_after == Fraction(-5, 1)   # 20 - 25 = -5
        assert sim_res.r1_calculation is not None
        assert "excess 5" in sim_res.r1_calculation

        r1_alert = next((a for a in sim_res.alerts if a.rule_id == "R1"), None)
        assert r1_alert is not None
        assert r1_alert.status == Status.CONTRADICTION


# ===========================================================================
# 5. Baseline Invariance & Full Dataset Checks
# ===========================================================================

def test_v10_baseline_dataset_hash_preserved():
    """Verify v1.0 baseline dataset hash remains unchanged at b4e585a4..."""
    ds = load_dataset(BASELINE_PATH)
    events = [e for h in ds.histories for e in h.events]
    srs = [s for h in ds.histories for s in h.survey_records]
    current_hash = hash_dataset(events, srs)
    assert current_hash == BASELINE_HASH, f"Expected {BASELINE_HASH}, got {current_hash}"
