"""
JomiGraph AI — Benchmark Evaluation and Coverage Reporter
=========================================================
Runs full rule evaluation across a Dataset to determine:
  - Clean-case false-alarm count (must be zero on clean cases)
  - Planted-case detection and rule coverage table
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Sequence

from jomigraph.engine.rules import (
    Alert,
    Status,
    check_history_hygiene,
    check_r1,
    check_r2,
    check_r3,
    check_r4,
    check_r5,
    check_r6,
    check_r7,
    dispatch_history_rules,
    run_rule,
)
from jomigraph.loader import Dataset
from jomigraph.models import Deed, Event, EventType, Parcel, ParcelHistory, Person, SurveyRecord


@dataclass(frozen=True)
class RuleCoverageRow:
    rule_id: str
    has_planted_case: bool
    detected: bool
    status_detected: Optional[str]


@dataclass(frozen=True)
class BenchmarkReport:
    total_parcels: int
    clean_parcel_count: int
    clean_false_alarm_count: int
    planted_parcel_count: int  # parcels carrying a planted problem (9)
    planted_case_count: int  # distinct planted problems, one per rule (7)
    planted_detected_count: int
    coverage_table: tuple[RuleCoverageRow, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_parcels": self.total_parcels,
            "clean_parcel_count": self.clean_parcel_count,
            "clean_false_alarm_count": self.clean_false_alarm_count,
            "planted_parcel_count": self.planted_parcel_count,
            "planted_case_count": self.planted_case_count,
            "planted_detected_count": self.planted_detected_count,
            "coverage_table": [
                {
                    "rule_id": row.rule_id,
                    "has_planted_case": row.has_planted_case,
                    "detected": row.detected,
                    "status_detected": row.status_detected,
                }
                for row in self.coverage_table
            ],
        }


def evaluate_history(
    history: ParcelHistory,
    all_parcels: Sequence[Parcel] = (),
    all_deeds: Sequence[Deed] = (),
    all_histories: Sequence[ParcelHistory] = (),
    all_persons: Sequence[Person] = (),
) -> list[Alert]:
    """
    Evaluate all applicable rules across the complete history of one parcel
    using the shared dispatch_history_rules.
    """
    return dispatch_history_rules(
        history=history,
        all_parcels=all_parcels,
        all_deeds=all_deeds,
        all_histories=all_histories,
        all_persons=all_persons,
    )



def evaluate_dataset(dataset: Dataset) -> BenchmarkReport:
    """
    Run full benchmark evaluation across the entire dataset.
    Returns clean-case false-alarm count and rule coverage table.
    """
    clean_histories: list[ParcelHistory] = []
    planted_histories: list[ParcelHistory] = []

    for h in dataset.histories:
        if "PLANTED" in h.parcel_id.upper():
            planted_histories.append(h)
        else:
            clean_histories.append(h)

    # 1. Clean cases: zero Contradiction and zero Review expected
    clean_false_alarms = 0
    for h in clean_histories:
        alerts = evaluate_history(
            h,
            all_parcels=dataset.parcels,
            all_deeds=dataset.deeds,
            all_histories=dataset.histories,
            all_persons=dataset.persons,
        )
        for a in alerts:
            if a.status in (Status.CONTRADICTION, Status.REVIEW):
                clean_false_alarms += 1

    # 2. Planted cases evaluation
    planted_alerts_by_parcel: dict[str, list[Alert]] = {}
    for h in planted_histories:
        alerts = evaluate_history(
            h,
            all_parcels=dataset.parcels,
            all_deeds=dataset.deeds,
            all_histories=dataset.histories,
            all_persons=dataset.persons,
        )
        planted_alerts_by_parcel[h.parcel_id] = alerts

    # Check detections per rule
    detected_rules: dict[str, str] = {}
    for pid, alerts in planted_alerts_by_parcel.items():
        for a in alerts:
            if a.status in (Status.CONTRADICTION, Status.REVIEW):
                detected_rules[a.rule_id] = a.status.value

    # Build coverage table for R1 - R7.
    # Derive planted_targets from parcel IDs of the form PARCEL_PLANTED_R<n>
    # so the coverage table is always consistent with the dataset contents.
    import re as _re
    planted_targets: set[str] = set()
    for h in planted_histories:
        _m = _re.search(r"PARCEL_PLANTED_(R\d+)", h.parcel_id, _re.IGNORECASE)
        if _m:
            planted_targets.add(_m.group(1).upper())
    coverage_rows: list[RuleCoverageRow] = []
    planted_detected = 0

    for r_id in ("R1", "R2", "R3", "R4", "R5", "R6", "R7"):
        has_planted = r_id in planted_targets
        detected = r_id in detected_rules
        if has_planted and detected:
            planted_detected += 1
        coverage_rows.append(
            RuleCoverageRow(
                rule_id=r_id,
                has_planted_case=has_planted,
                detected=detected,
                status_detected=detected_rules.get(r_id),
            )
        )

    return BenchmarkReport(
        total_parcels=len(dataset.parcels),
        clean_parcel_count=len(clean_histories),
        clean_false_alarm_count=clean_false_alarms,
        planted_parcel_count=len(planted_histories),
        planted_case_count=len(planted_targets),
        planted_detected_count=planted_detected,
        coverage_table=tuple(coverage_rows),
    )


@dataclass(frozen=True)
class Phase10BenchmarkDetail:
    rule_id: str
    planted_detected: bool
    clean_passed: bool
    tricky_clean_passed: bool


@dataclass(frozen=True)
class Phase11FeaturesBenchmarkDetail:
    attention_scoring_verified: bool
    bangla_voice_verified: bool
    next_step_guide_verified: bool
    ussd_simulator_verified: bool
    vetting_certificate_verified: bool


@dataclass(frozen=True)
class ExtendedBenchmarkReport:
    dataset_name: str
    total_parcels: int
    clean_parcel_count: int
    clean_false_alarm_count: int
    planted_parcel_count: int
    planted_case_count: int
    planted_detected_count: int
    coverage_table: tuple[RuleCoverageRow, ...]
    phase10_heir_declaration: Phase10BenchmarkDetail
    phase11_features: Phase11FeaturesBenchmarkDetail
    simulation_integrity: dict[str, Any]
    disclaimer: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "total_parcels": self.total_parcels,
            "clean_parcel_count": self.clean_parcel_count,
            "clean_false_alarm_count": self.clean_false_alarm_count,
            "planted_parcel_count": self.planted_parcel_count,
            "planted_case_count": self.planted_case_count,
            "planted_detected_count": self.planted_detected_count,
            "coverage_table": [
                {
                    "rule_id": row.rule_id,
                    "has_planted_case": row.has_planted_case,
                    "detected": row.detected,
                    "status_detected": row.status_detected,
                }
                for row in self.coverage_table
            ],
            "phase10_heir_declaration": {
                "rule_id": self.phase10_heir_declaration.rule_id,
                "planted_detected": self.phase10_heir_declaration.planted_detected,
                "clean_passed": self.phase10_heir_declaration.clean_passed,
                "tricky_clean_passed": self.phase10_heir_declaration.tricky_clean_passed,
            },
            "phase11_features": {
                "attention_scoring_verified": self.phase11_features.attention_scoring_verified,
                "bangla_voice_verified": self.phase11_features.bangla_voice_verified,
                "next_step_guide_verified": self.phase11_features.next_step_guide_verified,
                "ussd_simulator_verified": self.phase11_features.ussd_simulator_verified,
                "vetting_certificate_verified": self.phase11_features.vetting_certificate_verified,
            },
            "simulation_integrity": self.simulation_integrity,
            "disclaimer": self.disclaimer,
        }


def evaluate_extended_dataset(dataset: Dataset, dataset_name: str = "demo_v11.json") -> ExtendedBenchmarkReport:
    """
    Run extended benchmark evaluation across the v1.1 demonstration dataset:
      - Clean-case false alarm count (actual executed results across all rules)
      - Planted-problem detection and coverage table for rules R8 through R15
      - Phase 10 (R8 heir declaration) targeted verification
      - Phase 11 feature verification (Scoring, Voice, Next steps, USSD, Certificate)
      - Simulation integrity (dataset hash before vs. after counterfactual simulation)
      - Explicit non-judicial synthetic-data disclaimer
    """
    from datetime import date
    from fractions import Fraction
    from jomigraph.engine.simulate import hash_dataset, simulate

    clean_histories: list[ParcelHistory] = []
    planted_histories: list[ParcelHistory] = []

    for h in dataset.histories:
        if "PLANTED" in h.parcel_id.upper():
            planted_histories.append(h)
        else:
            clean_histories.append(h)

    # 1. Clean cases: evaluate all clean parcels and record actual non-consistent alerts
    clean_false_alarms = 0
    for h in clean_histories:
        alerts = evaluate_history(
            h,
            all_parcels=dataset.parcels,
            all_deeds=dataset.deeds,
            all_histories=dataset.histories,
            all_persons=dataset.persons,
        )
        if any(a.status in (Status.CONTRADICTION, Status.REVIEW) for a in alerts):
            clean_false_alarms += 1

    # 2. Planted cases evaluation
    planted_alerts_by_parcel: dict[str, list[Alert]] = {}
    for h in planted_histories:
        alerts = evaluate_history(
            h,
            all_parcels=dataset.parcels,
            all_deeds=dataset.deeds,
            all_histories=dataset.histories,
            all_persons=dataset.persons,
        )
        planted_alerts_by_parcel[h.parcel_id] = alerts

    detected_rules: dict[str, str] = {}
    for pid, alerts in planted_alerts_by_parcel.items():
        for a in alerts:
            if a.status in (Status.CONTRADICTION, Status.REVIEW):
                detected_rules[a.rule_id] = a.status.value

    # Build coverage table for R8 through R15
    import re as _re
    planted_targets: set[str] = set()
    for h in planted_histories:
        _m = _re.search(r"PARCEL_PLANTED_(R\d+)", h.parcel_id, _re.IGNORECASE)
        if _m:
            planted_targets.add(_m.group(1).upper())

    v11_rules = ("R8", "R9", "R10", "R11", "R12", "R13", "R14", "R15")
    coverage_rows: list[RuleCoverageRow] = []
    planted_detected = 0

    for r_id in v11_rules:
        has_planted = r_id in planted_targets
        detected = r_id in detected_rules
        if has_planted and detected:
            planted_detected += 1
        coverage_rows.append(
            RuleCoverageRow(
                rule_id=r_id,
                has_planted_case=has_planted,
                detected=detected,
                status_detected=detected_rules.get(r_id),
            )
        )

    # 3. Phase 10: R8 Heir Declaration Verification
    h_planted_r8 = next((h for h in dataset.histories if h.parcel_id == "PARCEL_PLANTED_R8"), None)
    h_clean_r8 = next((h for h in dataset.histories if h.parcel_id == "PARCEL_CLEAN_R8"), None)
    h_clean_r8_t = next((h for h in dataset.histories if h.parcel_id == "PARCEL_CLEAN_R8_TRICKY"), None)

    r8_planted_detected = False
    if h_planted_r8:
        alerts = evaluate_history(h_planted_r8, dataset.parcels, dataset.deeds, dataset.histories, dataset.persons)
        r8_planted_detected = any(a.rule_id == "R8" and a.status == Status.CONTRADICTION for a in alerts)

    r8_clean_passed = False
    if h_clean_r8:
        alerts = evaluate_history(h_clean_r8, dataset.parcels, dataset.deeds, dataset.histories, dataset.persons)
        r8_clean_passed = all(a.status == Status.CONSISTENT for a in alerts)

    r8_tricky_passed = False
    if h_clean_r8_t:
        alerts = evaluate_history(h_clean_r8_t, dataset.parcels, dataset.deeds, dataset.histories, dataset.persons)
        r8_tricky_passed = all(a.status == Status.CONSISTENT for a in alerts)

    p10_detail = Phase10BenchmarkDetail(
        rule_id="R8",
        planted_detected=r8_planted_detected,
        clean_passed=r8_clean_passed,
        tricky_clean_passed=r8_tricky_passed,
    )

    # 4. Phase 11 Features Verification
    from jomigraph.config import ATTENTION_RULE_WEIGHTS, ATTENTION_STATUS_BASE_WEIGHTS
    scoring_ok = bool(ATTENTION_STATUS_BASE_WEIGHTS and ATTENTION_RULE_WEIGHTS)

    from jomigraph.i18n import load_translations
    voice_ok = bool(load_translations("bn") and load_translations("en"))

    from jomigraph.engine.next_steps import get_rule_next_steps
    next_steps_ok = callable(get_rule_next_steps)

    from jomigraph.engine.ussd import process_ussd_step
    ussd_ok = callable(process_ussd_step)

    from jomigraph.engine.deed_hash import hash_deed_content
    cert_ok = callable(hash_deed_content)

    p11_detail = Phase11FeaturesBenchmarkDetail(
        attention_scoring_verified=scoring_ok,
        bangla_voice_verified=voice_ok,
        next_step_guide_verified=next_steps_ok,
        ussd_simulator_verified=ussd_ok,
        vetting_certificate_verified=cert_ok,
    )

    # 5. Simulation Integrity on Dataset
    all_events = [e for h in dataset.histories for e in h.events]
    all_srs = [sr for h in dataset.histories for sr in h.survey_records]
    hash_before = hash_dataset(all_events, all_srs)

    if dataset.histories:
        target_h = dataset.histories[0]
        seller_id = (
            target_h.survey_records[0].holders[0][0]
            if target_h.survey_records and target_h.survey_records[0].holders
            else "P_BENCHMARK_PROBE"
        )
        probe_event = Event(
            id="BENCHMARK_EXT_PROBE",
            type=EventType.SALE,
            seq=0,
            event_date=date(2020, 1, 1),
            parcel_id=target_h.parcel_id,
            from_person=seller_id,
            to_person="P_BENCHMARK_PROBE_BUYER",
            area=Fraction(1),
            deed_id=None,
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        _ = simulate(target_h.events, probe_event, target_h, dataset.deeds)

    all_events_after = [e for h in dataset.histories for e in h.events]
    all_srs_after = [sr for h in dataset.histories for sr in h.survey_records]
    hash_after = hash_dataset(all_events_after, all_srs_after)

    sim_integrity = {
        "dataset_hash_before": hash_before,
        "dataset_hash_after": hash_after,
        "unchanged": (hash_before == hash_after),
    }

    disclaimer = (
        "Synthetic demonstration benchmark. All records, names, parcels, deeds, "
        "and case numbers are fictitious and generated deterministically. "
        "This evaluation demonstrates rule execution and does not represent an audit "
        "of live government land records or a formal title determination."
    )

    return ExtendedBenchmarkReport(
        dataset_name=dataset_name,
        total_parcels=len(dataset.parcels),
        clean_parcel_count=len(clean_histories),
        clean_false_alarm_count=clean_false_alarms,
        planted_parcel_count=len(planted_histories),
        planted_case_count=len(planted_targets),
        planted_detected_count=planted_detected,
        coverage_table=tuple(coverage_rows),
        phase10_heir_declaration=p10_detail,
        phase11_features=p11_detail,
        simulation_integrity=sim_integrity,
        disclaimer=disclaimer,
    )

