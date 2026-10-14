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
    run_rule,
)
from jomigraph.loader import Dataset
from jomigraph.models import Deed, Event, EventType, Parcel, ParcelHistory, SurveyRecord


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
    planted_parcel_count: int
    planted_detected_count: int
    coverage_table: tuple[RuleCoverageRow, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_parcels": self.total_parcels,
            "clean_parcel_count": self.clean_parcel_count,
            "clean_false_alarm_count": self.clean_false_alarm_count,
            "planted_parcel_count": self.planted_parcel_count,
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
) -> list[Alert]:
    """
    Evaluate all applicable rules across the complete history of one parcel.
    """
    alerts: list[Alert] = []
    baseline = history.survey_records[0]

    # Pre-condition hygiene
    hygiene_alert = check_history_hygiene(
        history.events,
        baseline,
        rule_id="HYGIENE",
        trigger_event_id=history.events[0].id if history.events else baseline.id,
    )
    if hygiene_alert:
        return [hygiene_alert]

    deeds_by_id = {d.id: d for d in all_deeds}

    # Evaluate event rules
    for event in history.events:
        if event.type in (EventType.SALE, EventType.GIFT):
            alerts.append(run_rule(check_r3, event, history, history.events))
            alerts.append(run_rule(check_r1, event, history, history.events))
            if event.portion_id or event.linked_event_id:
                alerts.append(run_rule(check_r2, event, history.events, baseline))

        elif event.type == EventType.SUBDIVIDE:
            # Find child parcels referencing this parcel as parent
            child_parcel_ids = {p.id for p in all_parcels if p.parent_id == history.parcel_id}
            child_srs: list[SurveyRecord] = []
            for h in all_histories:
                if h.parcel_id in child_parcel_ids:
                    child_srs.extend(h.survey_records)
            alerts.append(run_rule(check_r4, event, child_srs, history.events, baseline))

        elif event.type == EventType.MUTATION:
            deed = deeds_by_id.get(event.deed_id) if event.deed_id else None
            alerts.append(run_rule(check_r6, event, deed, history.events, baseline))
            alerts.append(run_rule(check_r7, event, deed, history.events, baseline))

    # Evaluate survey continuity (R5) between successive survey records
    if len(history.survey_records) > 1:
        # Sort survey records by record_date
        sorted_srs = sorted(history.survey_records, key=lambda sr: sr.record_date)
        for i in range(len(sorted_srs) - 1):
            earlier = sorted_srs[i]
            later = sorted_srs[i + 1]
            # Linking events between survey publication dates
            linking = [
                e for e in history.events
                if e.event_date is not None
                and earlier.record_date <= e.event_date <= later.record_date
            ]
            alerts.append(run_rule(check_r5, earlier, later, linking, history.events))

    return alerts


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
        planted_detected_count=planted_detected,
        coverage_table=tuple(coverage_rows),
    )
