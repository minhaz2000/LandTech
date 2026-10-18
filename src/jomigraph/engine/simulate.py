"""
JomiGraph AI — Simulation Engine
================================
Pure-function counterfactual simulation.
SPEC § Simulation Integrity:
  "evaluate(events, parcel_history) is a pure function returning (state, alerts).
  Simulation calls evaluate(events + [proposed]) on a new list and never mutates
  the original data. Canonical serialization hash of baseline must match before
  and after every simulation."
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from fractions import Fraction
from typing import Optional, Sequence

from jomigraph.engine.replay import compute_state, get_available_area, replay_up_to
from jomigraph.engine.rules import (
    Alert,
    Status,
    check_r1,
    check_r2,
    check_r3,
    check_r4,
    check_r6,
    check_r7,
    check_r8,
    check_r15,
    dispatch_event_rules,
    run_rule,
)
from jomigraph.models import Deed, Event, EventType, Parcel, ParcelHistory, SurveyRecord


@dataclass(frozen=True)
class SimulationResult:
    proposed_event: Event
    available_before: Fraction
    available_after: Fraction
    alerts: tuple[Alert, ...]
    r1_calculation: Optional[str] = None


def hash_dataset(events: Sequence[Event], survey_records: Sequence[SurveyRecord] = ()) -> str:
    """
    Compute a deterministic canonical SHA-256 hash of events and survey records.
    Used to guarantee that baseline dataset state is never mutated by simulations.
    """
    items = []
    for sr in survey_records:
        items.append({
            "type": "SR",
            "id": sr.id,
            "parcel_id": sr.parcel_id,
            "survey": sr.survey,
            "khatian_no": sr.khatian_no,
            "record_date": str(sr.record_date),
            "recorded_area": str(sr.recorded_area),
            "holders": [(h[0], str(h[1])) for h in sr.holders],
        })
    for e in events:
        ev_item = {
            "type": "EVENT",
            "id": e.id,
            "event_type": e.type.value,
            "seq": e.seq,
            "event_date": str(e.event_date) if e.event_date else None,
            "parcel_id": e.parcel_id,
            "from_person": e.from_person,
            "to_person": e.to_person,
            "area": str(e.area) if e.area is not None else None,
            "deed_id": e.deed_id,
            "portion_id": e.portion_id,
            "linked_event_id": e.linked_event_id,
            "source_record_id": e.source_record_id,
        }
        if e.portion is not None:
            ev_item["portion"] = e.portion
        if e.boundary is not None:
            ev_item["boundary"] = e.boundary
        if e.via_poa_id is not None:
            ev_item["via_poa_id"] = e.via_poa_id
        items.append(ev_item)
    payload = json.dumps(items, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def evaluate(
    events: Sequence[Event],
    parcel_history: ParcelHistory,
    target_event: Optional[Event] = None,
    deeds: Sequence[Deed] = (),
    parcel: Optional[Parcel] = None,
) -> tuple[dict[str, Fraction], list[Alert]]:
    """
    Pure evaluation function returning (holder_state, alerts).

    Evaluates rules for target_event (or the last event in events if target_event is None)
    in the context of the supplied events list using the shared dispatch_event_rules.
    """
    baseline = parcel_history.survey_records[0]
    state, _ = compute_state(events, baseline)

    if not events:
        return state, []

    eval_target = target_event if target_event is not None else events[-1]
    deeds_by_id = {d.id: d for d in deeds}
    alerts = dispatch_event_rules(
        event=eval_target,
        parcel_history=parcel_history,
        events=events,
        baseline_record=baseline,
        deeds_by_id=deeds_by_id,
        parcel=parcel,
    )

    if parcel_history.heir_declaration:
        alerts.append(run_rule(check_r8, parcel_history, events, deeds, baseline, target_event=eval_target))

    return state, alerts



def simulate(
    events: Sequence[Event],
    proposed: Event,
    parcel_history: ParcelHistory,
    deeds: Sequence[Deed] = (),
    parcel: Optional[Parcel] = None,
) -> SimulationResult:
    """
    Pure simulation function:
      simulate(events, proposed) = evaluate(events + [proposed])

    Assigns proposed event seq = max(existing seq) + 1.
    Never mutates the input list or input Event objects.
    """
    # 1. Compute max sequence without mutating original list
    max_seq = max((e.seq for e in events), default=0)

    # 2. Assign proposed seq = max_seq + 1 on a NEW Event instance
    sim_proposed = replace(proposed, seq=max_seq + 1)

    # 3. Create a NEW event list (never mutating the original events sequence)
    sim_events = list(events) + [sim_proposed]

    baseline = parcel_history.survey_records[0]

    # 4. Available area BEFORE the proposed event
    if sim_proposed.from_person and sim_proposed.event_date:
        state_before, _ = replay_up_to(
            events=events,
            baseline_survey_record=baseline,
            cutoff_date=sim_proposed.event_date,
            cutoff_seq=sim_proposed.seq,
            exclude_event_id=sim_proposed.id,
        )
        avail_before = get_available_area(state_before, sim_proposed.from_person)
    elif sim_proposed.from_person:
        state_before, _ = compute_state(events, baseline)
        avail_before = get_available_area(state_before, sim_proposed.from_person)
    else:
        avail_before = Fraction(0)

    # 5. Pure evaluate(events + [proposed])
    sim_history = replace(parcel_history, events=tuple(sim_events))
    state_after, alerts = evaluate(
        events=sim_events,
        parcel_history=sim_history,
        target_event=sim_proposed,
        deeds=deeds,
        parcel=parcel,
    )

    # 6. Available area AFTER the proposed event
    if sim_proposed.from_person:
        avail_after = get_available_area(state_after, sim_proposed.from_person)
    else:
        avail_after = Fraction(0)

    # 7. Extract R1 calculation if present
    r1_calc: Optional[str] = None
    for alert in alerts:
        if alert.rule_id == "R1":
            r1_calc = alert.calculation
            break

    return SimulationResult(
        proposed_event=sim_proposed,
        available_before=avail_before,
        available_after=avail_after,
        alerts=tuple(alerts),
        r1_calculation=r1_calc,
    )
