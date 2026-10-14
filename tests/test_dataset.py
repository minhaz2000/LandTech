"""
JomiGraph AI — Dataset and Benchmark Test Suite
================================================
Verifies:
  1. The dataset loader works and parses data/demo_family.json into typed dataclasses.
  2. All areas strictly go through load_fraction() and are Fractions (zero floats).
  3. Every planted problem yields exactly the expected rule_id and status:
     - PARCEL_PLANTED_R1: R1 Contradiction Found with excess 2.
     - PARCEL_PLANTED_R2: R2 Contradiction Found (duplicate portion).
     - PARCEL_PLANTED_R3: R3 Contradiction Found (stranger sells, not recorded holder).
     - PARCEL_PLANTED_R4: R4 Contradiction Found (children sum to parent minus > tolerance).
     - PARCEL_PLANTED_R5: R5 Review Required (survey gap with unlinked records).
  4. Every clean case yields ONLY Status.CONSISTENT (zero Contradiction, zero Review).
  5. PARCEL_LAB_DEMO:
     - Baseline holder H=10, recorded sale of 7 to buyer B, baseline_complete=True.
     - Evaluates to only Status.CONSISTENT.
     - simulate() of 5-decimal sale from H returns R1 Contradiction with
       "requested 5, available 3, excess 2".
     - simulate() of 3-decimal sale from H returns Consistent.
  6. The generator output is bit-identical across two runs with seed=42.
  7. get_clean_false_alarms_and_coverage returns clean_false_alarm_count == 0 and
     a complete coverage table for rules R1-R7 (with R1, R2, R3, R4, R5 planted & detected).
"""

from datetime import date
from fractions import Fraction
import json
from pathlib import Path

import pytest

from data.generator import build_demo_dataset, build_raw_dataset_dict
from jomigraph.config import R4_TOLERANCE
from jomigraph.engine.benchmark import evaluate_history
from jomigraph.engine.rules import Status
from jomigraph.engine.simulate import simulate
from jomigraph.loader import (
    Dataset,
    get_clean_false_alarms_and_coverage,
    load_dataset,
)
from jomigraph.models import Event, EventType


@pytest.fixture(scope="module")
def demo_dataset() -> Dataset:
    dataset_path = Path("data/demo_family.json")
    assert dataset_path.is_file(), "data/demo_family.json must exist"
    return load_dataset(dataset_path)


# ---------------------------------------------------------------------------
# 1. Dataset Loader Tests
# ---------------------------------------------------------------------------

class TestDatasetLoader:
    def test_loader_works_and_populates_typed_models(self, demo_dataset: Dataset):
        """The loader correctly populates Dataset with persons, parcels, deeds, histories."""
        assert len(demo_dataset.persons) >= 20
        assert len(demo_dataset.parcels) == 30
        assert len(demo_dataset.deeds) >= 20
        assert len(demo_dataset.histories) == 30

    def test_all_areas_are_fractions_and_no_floats_exist(self, demo_dataset: Dataset):
        """
        All recorded and event areas must be instances of fractions.Fraction.
        Floats are strictly forbidden.
        """
        for h in demo_dataset.histories:
            for sr in h.survey_records:
                assert isinstance(sr.recorded_area, Fraction)
                assert not isinstance(sr.recorded_area, float)
                for person_id, area in sr.holders:
                    assert isinstance(area, Fraction)
                    assert not isinstance(area, float)
            for e in h.events:
                if e.area is not None:
                    assert isinstance(e.area, Fraction)
                    assert not isinstance(e.area, float)

    def test_loader_lookup_methods(self, demo_dataset: Dataset):
        """Dataset lookup helper methods return correct instances."""
        parcel = demo_dataset.get_parcel("PARCEL_STORY_01")
        assert parcel is not None
        assert parcel.id == "PARCEL_STORY_01"

        history = demo_dataset.get_history("PARCEL_STORY_01")
        assert history is not None
        assert history.parcel_id == "PARCEL_STORY_01"

        person = demo_dataset.get_person("P_G1_RAHIM")
        assert person is not None
        assert person.name == "Abdur Rahim Chowdhury"

        deed = demo_dataset.get_deed("DEED_STORY_01_GIFT1")
        assert deed is not None
        assert deed.deed_no == "D-1948-001"


# ---------------------------------------------------------------------------
# 2. Planted Problems Tests
# ---------------------------------------------------------------------------

class TestPlantedProblems:
    def test_planted_r1_over_transfer(self, demo_dataset: Dataset):
        """
        Planted problem (a): holder has 10, sells 7, later sells 5.
        Must yield R1 Contradiction Found with excess 2.
        All other alerts on this parcel must be CONSISTENT.
        """
        h = demo_dataset.get_history("PARCEL_PLANTED_R1")
        assert h is not None

        alerts = evaluate_history(
            h,
            all_parcels=demo_dataset.parcels,
            all_deeds=demo_dataset.deeds,
            all_histories=demo_dataset.histories,
        )

        non_consistent = [a for a in alerts if a.status != Status.CONSISTENT]
        assert len(non_consistent) == 1, f"Expected 1 non-consistent alert, got {non_consistent}"

        alert = non_consistent[0]
        assert alert.rule_id == "R1"
        assert alert.status == Status.CONTRADICTION
        assert "excess 2" in alert.calculation or "excess: 2" in alert.calculation

    def test_planted_r2_duplicate_portion_sale(self, demo_dataset: Dataset):
        """
        Planted problem (b): duplicate sale of the same portion_id to two buyers.
        Must yield R2 Contradiction Found.
        """
        h = demo_dataset.get_history("PARCEL_PLANTED_R2")
        assert h is not None

        alerts = evaluate_history(
            h,
            all_parcels=demo_dataset.parcels,
            all_deeds=demo_dataset.deeds,
            all_histories=demo_dataset.histories,
        )

        non_consistent = [a for a in alerts if a.status != Status.CONSISTENT]
        assert len(non_consistent) >= 1
        for a in non_consistent:
            assert a.rule_id == "R2"
            assert a.status == Status.CONTRADICTION

    def test_planted_r3_stranger_sells(self, demo_dataset: Dataset):
        """
        Planted problem R3: a stranger sells (not a recorded holder at all).
        Must yield R3 Contradiction Found.
        """
        h = demo_dataset.get_history("PARCEL_PLANTED_R3")
        assert h is not None

        alerts = evaluate_history(
            h,
            all_parcels=demo_dataset.parcels,
            all_deeds=demo_dataset.deeds,
            all_histories=demo_dataset.histories,
        )

        non_consistent = [a for a in alerts if a.status != Status.CONSISTENT]
        assert len(non_consistent) == 1
        alert = non_consistent[0]
        assert alert.rule_id == "R3"
        assert alert.status == Status.CONTRADICTION
        assert "not a recorded holder" in alert.calculation

    def test_planted_r4_subdivision_area_mismatch(self, demo_dataset: Dataset):
        """
        Planted problem R4: parent (20) subdivided into children summing to 18 (diff 2 > tolerance).
        Must yield R4 Contradiction Found.
        """
        h = demo_dataset.get_history("PARCEL_PLANTED_R4")
        assert h is not None

        alerts = evaluate_history(
            h,
            all_parcels=demo_dataset.parcels,
            all_deeds=demo_dataset.deeds,
            all_histories=demo_dataset.histories,
        )

        non_consistent = [a for a in alerts if a.status != Status.CONSISTENT]
        assert len(non_consistent) == 1
        alert = non_consistent[0]
        assert alert.rule_id == "R4"
        assert alert.status == Status.CONTRADICTION
        # Dynamically verify area gap > R4_TOLERANCE read from config
        parent_sr = h.survey_records[0]
        children = [p for p in demo_dataset.parcels if p.parent_id == "PARCEL_PLANTED_R4"]
        assert len(children) > 0, "PARCEL_PLANTED_R4 must have child parcels"
        child_total = sum(demo_dataset.get_history(c.id).survey_records[0].recorded_area for c in children)
        area_gap = abs(parent_sr.recorded_area - child_total)

        assert area_gap > R4_TOLERANCE, (
            f"Planted gap {area_gap} must be greater than R4_TOLERANCE ({R4_TOLERANCE}) "
            "read from config."
        )

    def test_planted_r5_survey_gap(self, demo_dataset: Dataset):
        """
        Planted problem (c): survey gap where later survey holder has no linking event.
        Must yield R5 Review Required (R5 never returns Contradiction).
        """
        h = demo_dataset.get_history("PARCEL_PLANTED_R5")
        assert h is not None

        alerts = evaluate_history(
            h,
            all_parcels=demo_dataset.parcels,
            all_deeds=demo_dataset.deeds,
            all_histories=demo_dataset.histories,
        )

        non_consistent = [a for a in alerts if a.status != Status.CONSISTENT]
        assert len(non_consistent) == 1
        alert = non_consistent[0]
        assert alert.rule_id == "R5"
        assert alert.status == Status.REVIEW

    def test_planted_r6_deed_mutation_mismatch(self, demo_dataset: Dataset):
        """
        Planted problem (f): mutation area (7) differs from sale area (9) on the same deed.
        R6 must yield Review Required.
        """
        h = demo_dataset.get_history("PARCEL_PLANTED_R6")
        assert h is not None

        alerts = evaluate_history(
            h,
            all_parcels=demo_dataset.parcels,
            all_deeds=demo_dataset.deeds,
            all_histories=demo_dataset.histories,
        )

        r6_non_consistent = [a for a in alerts if a.rule_id == "R6" and a.status != Status.CONSISTENT]
        assert len(r6_non_consistent) == 1
        assert r6_non_consistent[0].status == Status.REVIEW

    def test_planted_r7_mutation_before_deed(self, demo_dataset: Dataset):
        """
        Planted problem (g): mutation date (1994-12-01) precedes deed registration (1995-06-20).
        R7 must yield Contradiction Found.
        """
        h = demo_dataset.get_history("PARCEL_PLANTED_R7")
        assert h is not None

        alerts = evaluate_history(
            h,
            all_parcels=demo_dataset.parcels,
            all_deeds=demo_dataset.deeds,
            all_histories=demo_dataset.histories,
        )

        r7_contradictions = [a for a in alerts if a.rule_id == "R7" and a.status == Status.CONTRADICTION]
        assert len(r7_contradictions) == 1


# ---------------------------------------------------------------------------
# 3. Clean Cases Tests
# ---------------------------------------------------------------------------

class TestCleanCases:
    def test_every_clean_parcel_yields_only_consistent(self, demo_dataset: Dataset):
        """
        All clean parcels (including PARCEL_LAB_DEMO) must return zero Contradiction
        and zero Review alerts. Every alert returned must be Status.CONSISTENT.
        """
        clean_histories = [
            h for h in demo_dataset.histories
            if "PLANTED" not in h.parcel_id.upper()
        ]
        assert len(clean_histories) == 21, f"Expected 21 clean parcels, got {len(clean_histories)}"

        total_clean_alerts = 0
        for h in clean_histories:
            alerts = evaluate_history(
                h,
                all_parcels=demo_dataset.parcels,
                all_deeds=demo_dataset.deeds,
                all_histories=demo_dataset.histories,
            )
            for a in alerts:
                total_clean_alerts += 1
                assert a.status == Status.CONSISTENT, (
                    f"Parcel {h.parcel_id} got unexpected {a.status} for rule {a.rule_id}: {a.calculation}"
                )

        assert total_clean_alerts > 0, "Clean parcels should have generated rule alerts"

    def test_parcel_lab_demo_clean_and_simulation(self, demo_dataset: Dataset):
        """
        PARCEL_LAB_DEMO:
          - Baseline holder H=10, one recorded sale of 7 to buyer B, baseline_complete=True.
          - Stored history must yield only Status.CONSISTENT.
          - simulate() of 5-decimal sale from H returns R1 Contradiction with:
            'requested 5, available 3, excess 2'.
          - simulate() of 3-decimal sale from H returns Consistent.
        """
        h = demo_dataset.get_history("PARCEL_LAB_DEMO")
        assert h is not None

        # 1. Stored evaluation must be only CONSISTENT
        stored_alerts = evaluate_history(
            h,
            all_parcels=demo_dataset.parcels,
            all_deeds=demo_dataset.deeds,
            all_histories=demo_dataset.histories,
        )
        assert len(stored_alerts) > 0
        for a in stored_alerts:
            assert a.status == Status.CONSISTENT

        # 2. simulate() of 5-decimal sale from H
        prop_5 = Event(
            id="SIM_PROPOSAL_5",
            type=EventType.SALE,
            seq=0,
            event_date=date(1996, 5, 15),
            parcel_id="PARCEL_LAB_DEMO",
            from_person="P_G3_TAREQ",  # holder H
            to_person="P_EXT_MONIR",
            area=Fraction(5),
            deed_id=None,
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        res_5 = simulate(h.events, prop_5, h, demo_dataset.deeds)
        assert res_5.available_before == Fraction(3)
        assert res_5.available_after == Fraction(-2)

        r1_alerts_5 = [a for a in res_5.alerts if a.rule_id == "R1"]
        assert len(r1_alerts_5) == 1
        assert r1_alerts_5[0].status == Status.CONTRADICTION
        assert "requested 5, available 3, excess 2" in r1_alerts_5[0].calculation

        # 3. simulate() of 3-decimal sale from H
        prop_3 = Event(
            id="SIM_PROPOSAL_3",
            type=EventType.SALE,
            seq=0,
            event_date=date(1996, 5, 15),
            parcel_id="PARCEL_LAB_DEMO",
            from_person="P_G3_TAREQ",  # holder H
            to_person="P_EXT_MONIR",
            area=Fraction(3),
            deed_id=None,
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        res_3 = simulate(h.events, prop_3, h, demo_dataset.deeds)
        assert res_3.available_before == Fraction(3)
        assert res_3.available_after == Fraction(0)

        r1_alerts_3 = [a for a in res_3.alerts if a.rule_id == "R1"]
        assert len(r1_alerts_3) == 1
        assert r1_alerts_3[0].status == Status.CONSISTENT
        for a in res_3.alerts:
            assert a.status == Status.CONSISTENT

    def test_story_subdivision_reconciles_exactly(self, demo_dataset: Dataset):
        """
        Valid subdivision in story parcels (parent 20 == child 1 (12) + child 2 (8))
        must return R4 Status.CONSISTENT.
        """
        parent_history = demo_dataset.get_history("PARCEL_STORY_08")
        assert parent_history is not None

        alerts = evaluate_history(
            parent_history,
            all_parcels=demo_dataset.parcels,
            all_deeds=demo_dataset.deeds,
            all_histories=demo_dataset.histories,
        )
        r4_alerts = [a for a in alerts if a.rule_id == "R4"]
        assert len(r4_alerts) == 1
        assert r4_alerts[0].status == Status.CONSISTENT


# ---------------------------------------------------------------------------
# 4. Generator Determinism Tests
# ---------------------------------------------------------------------------

class TestGeneratorDeterminism:
    def test_generator_output_identical_across_two_runs(self):
        """Generator output must be identical across two runs with fixed seed=42."""
        raw_1 = build_raw_dataset_dict(seed=42)
        raw_2 = build_raw_dataset_dict(seed=42)

        # Dictionary structure equality
        assert raw_1 == raw_2

        # JSON serialization bit-identical check
        json_1 = json.dumps(raw_1, sort_keys=True, indent=2)
        json_2 = json.dumps(raw_2, sort_keys=True, indent=2)
        assert json_1 == json_2


# ---------------------------------------------------------------------------
# 5. Benchmark and Coverage Function Tests
# ---------------------------------------------------------------------------

class TestBenchmarkAndCoverage:
    def test_clean_case_false_alarm_count_and_coverage_table(self, demo_dataset: Dataset):
        """
        get_clean_false_alarms_and_coverage must return:
          - clean_false_alarm_count == 0
          - coverage table covering rules R1 to R7, with all seven planted and detected.
        """
        clean_false_alarms, coverage_table = get_clean_false_alarms_and_coverage(demo_dataset)

        # Clean false alarms must be strictly 0
        assert clean_false_alarms == 0

        # Coverage table inspection
        coverage_by_rule = {row.rule_id: row for row in coverage_table}
        assert set(coverage_by_rule.keys()) == {"R1", "R2", "R3", "R4", "R5", "R6", "R7"}

        # Planted cases must be flagged and detected
        assert coverage_by_rule["R1"].has_planted_case is True
        assert coverage_by_rule["R1"].detected is True
        assert coverage_by_rule["R1"].status_detected == Status.CONTRADICTION.value

        assert coverage_by_rule["R2"].has_planted_case is True
        assert coverage_by_rule["R2"].detected is True
        assert coverage_by_rule["R2"].status_detected == Status.CONTRADICTION.value

        assert coverage_by_rule["R3"].has_planted_case is True
        assert coverage_by_rule["R3"].detected is True
        assert coverage_by_rule["R3"].status_detected == Status.CONTRADICTION.value

        assert coverage_by_rule["R4"].has_planted_case is True
        assert coverage_by_rule["R4"].detected is True
        assert coverage_by_rule["R4"].status_detected == Status.CONTRADICTION.value

        assert coverage_by_rule["R5"].has_planted_case is True
        assert coverage_by_rule["R5"].detected is True
        assert coverage_by_rule["R5"].status_detected == Status.REVIEW.value

        # R6: planted (area mismatch) -> Review Required
        assert coverage_by_rule["R6"].has_planted_case is True
        assert coverage_by_rule["R6"].detected is True
        assert coverage_by_rule["R6"].status_detected == Status.REVIEW.value

        # R7: planted (mutation before deed) -> Contradiction Found
        assert coverage_by_rule["R7"].has_planted_case is True
        assert coverage_by_rule["R7"].detected is True
        assert coverage_by_rule["R7"].status_detected == Status.CONTRADICTION.value
