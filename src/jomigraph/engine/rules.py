"""
JomiGraph AI — Rule Layer
=========================
Pure-function implementation of rules R1, R2, R3, and R6.
Follows SPEC § Evaluation Order:
  1. Check required inputs and parcel history hygiene; if missing/ambiguous return Review Required.
  2. Apply baseline_complete and rule logic. baseline_complete NEVER overrides a missing input.

Mutual Exclusivity:
  - R3 fires only when the seller is not a recorded holder at all.
  - R1 fires only when the seller is a recorded holder with insufficient share.
  - One case never yields both alerts.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from fractions import Fraction
from typing import Callable, Optional, Sequence

from jomigraph.config import R4_TOLERANCE
from jomigraph.engine.replay import (
    HolderState,
    compute_state,
    get_available_area,
    has_undated_events,
    replay_up_to,
)
from jomigraph.i18n import (
    MSG_CONSISTENT,
    MSG_R1_CONTRADICTION,
    MSG_R1_REVIEW_INCOMPLETE_BASELINE,
    MSG_R1_REVIEW_INPUTS,
    MSG_R2_CONTRADICTION,
    MSG_R2_REVIEW_INPUTS,
    MSG_R2_REVIEW_UNESTABLISHED,
    MSG_R3_CONTRADICTION,
    MSG_R3_REVIEW_INCOMPLETE_BASELINE,
    MSG_R3_REVIEW_INPUTS,
    MSG_R4_CONTRADICTION,
    MSG_R4_REVIEW_INPUTS,
    MSG_R4_REVIEW_MISSING_CHILDREN,
    MSG_R4_REVIEW_TOLERANCE,
    MSG_R5_CONSISTENT,
    MSG_R5_REVIEW_NO_LINK,
    MSG_R6_CONSISTENT,
    MSG_R6_REVIEW_MISMATCH,
    MSG_R6_REVIEW_MISSING_DEED,
    MSG_R7_CONTRADICTION,
    MSG_R7_CONSISTENT,
    MSG_R7_REVIEW_MISSING_LINK_OR_DATE,
    MSG_REVIEW_UNDATED_HISTORY,
    MSG_REVIEW_UNSUPPORTED_HISTORY,
    NEXT_STEP_BY_RULE,
    NEXT_STEP_REVIEW_HISTORY,
)
from jomigraph.models import Deed, Event, EventType, ParcelHistory, SurveyRecord


# ---------------------------------------------------------------------------
# Status and Alert dataclasses
# ---------------------------------------------------------------------------

class Status(str, Enum):
    CONSISTENT    = "Consistent with supplied records"
    CONTRADICTION = "Contradiction Found"
    REVIEW        = "Review Required"


@dataclass(frozen=True)
class Alert:
    rule_id: str                          # e.g. "R1", "R2", "R3", "R6"
    status: Status
    message_key: str                      # Key into translation JSON (bn.json, en.json)
    evidence_ids: tuple[str, ...]         # Record/event IDs used to establish result (non-empty)
    calculation: str                      # Exact rational arithmetic / explanation
    recommended_next_step: str            # Key into translation JSON
    impact_event_ids: tuple[str, ...] = ()# Downstream dependent events (if any)


# ---------------------------------------------------------------------------
# Rule runner wrapper (enforces non-empty evidence_ids per test 14)
# ---------------------------------------------------------------------------

def run_rule(fn: Callable[..., Alert], *args, **kwargs) -> Alert:
    """
    Execute a rule function and enforce core invariants:
      - alert.rule_id is set
      - len(alert.evidence_ids) > 0
    """
    alert = fn(*args, **kwargs)
    if not alert.rule_id:
        raise AssertionError("Alert rule_id must not be empty.")
    if len(alert.evidence_ids) == 0:
        raise AssertionError(
            f"Rule {alert.rule_id} returned empty evidence_ids — "
            "SPEC requires every alert to include non-empty evidence_ids."
        )
    return alert


# ---------------------------------------------------------------------------
# History hygiene checks
# ---------------------------------------------------------------------------

def check_history_hygiene(
    events: Sequence[Event],
    baseline_record: SurveyRecord,
    rule_id: str,
    trigger_event_id: str,
) -> Optional[Alert]:
    """
    Pre-check for history hygiene:
      - Returns Review Required if ANY event in parcel history is undated.
      - Returns Review Required if replay discovers unsupported CANCEL or CORRECT.
    """
    if has_undated_events(events):
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_REVIEW_UNDATED_HISTORY,
            evidence_ids=(trigger_event_id, baseline_record.id),
            calculation="Parcel history contains undated events; chronological ordering cannot be established.",
            recommended_next_step=NEXT_STEP_REVIEW_HISTORY,
        )

    _, issues = compute_state(events, baseline_record)
    if issues:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_REVIEW_UNSUPPORTED_HISTORY,
            evidence_ids=(trigger_event_id, baseline_record.id),
            calculation=f"Parcel history contains invalid or unsupported events: {'; '.join(issues)}",
            recommended_next_step=NEXT_STEP_REVIEW_HISTORY,
        )

    return None


def is_recorded_holder(
    person_id: str,
    events: Sequence[Event],
    baseline_record: SurveyRecord,
    cutoff_date: Optional[date] = None,
    cutoff_seq: Optional[int] = None,
) -> bool:
    """
    Return True if person_id is a recorded holder in the parcel's history:
      (a) Listed in the baseline SurveyRecord with non-zero area, OR
      (b) Listed as to_person in any prior SALE or GIFT prior to (cutoff_date, cutoff_seq).

    NOTE: A person introduced ONLY by a CORRECT event is NOT a "recorded holder" for R3.
    A CORRECT event adjusts an existing recorded holder's share or corrects an erroneous
    recording, but does not establish root title or substitute for a baseline survey entry
    or a registered conveyance deed.
    """
    for pid, area in baseline_record.holders:
        if pid == person_id and area > Fraction(0):
            return True

    for e in events:
        if e.type in (EventType.SALE, EventType.GIFT) and e.to_person == person_id:
            if cutoff_date is not None and cutoff_seq is not None:
                if e.event_date is not None and (e.event_date, e.seq) < (cutoff_date, cutoff_seq):
                    return True
            else:
                return True

    return False


# ---------------------------------------------------------------------------
# Rule R1: Excess Transfer
# ---------------------------------------------------------------------------

def check_r1(
    event: Event,
    parcel_history: ParcelHistory,
    all_events: Sequence[Event],
) -> Alert:
    """
    R1 Excess transfer:
      "If baseline_complete is true for the relevant interval and a transfer
      exceeds the seller's modeled available share at the event date, return
      Contradiction Found. Otherwise return Review Required."

    Mutual Exclusivity:
      R1 fires only when the seller is a recorded holder with insufficient share.
      If the seller is not a recorded holder at all, R3 owns that evaluation.
    """
    rule_id = "R1"
    baseline = parcel_history.survey_records[0]

    # Pre-condition hygiene
    hygiene_alert = check_history_hygiene(all_events, baseline, rule_id, event.id)
    if hygiene_alert:
        return hygiene_alert

    # Step 1: Input validation
    if event.event_date is None or event.from_person is None or event.area is None:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R1_REVIEW_INPUTS,
            evidence_ids=(event.id, baseline.id),
            calculation="Event date, seller, or transfer area is missing.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    # Check if seller is a recorded holder (if not, R3 evaluates)
    if not is_recorded_holder(event.from_person, all_events, baseline, event.event_date, event.seq):
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_CONSISTENT,
            evidence_ids=(event.id, baseline.id),
            calculation=f"Seller '{event.from_person}' is not a recorded holder; evaluated under R3.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    # Step 2: Replay up to event date/seq to find available share
    state, _ = replay_up_to(
        events=all_events,
        baseline_survey_record=baseline,
        cutoff_date=event.event_date,
        cutoff_seq=event.seq,
        exclude_event_id=event.id,
    )
    available = get_available_area(state, event.from_person)
    excess = event.area - available

    # Gather evidence IDs: baseline + prior events that touched from_person
    events_by_id = {e.id: e for e in all_events}
    prior_events: list[str] = []
    for e in all_events:
        if e.event_date is None or (e.event_date, e.seq) >= (event.event_date, event.seq):
            continue
        if e.from_person == event.from_person or e.to_person == event.from_person:
            prior_events.append(e.id)
        elif e.type == EventType.CANCEL and e.linked_event_id:
            linked = events_by_id.get(e.linked_event_id)
            if linked and (linked.from_person == event.from_person or linked.to_person == event.from_person):
                prior_events.append(e.id)
        elif e.type == EventType.CORRECT and e.from_person == event.from_person:
            prior_events.append(e.id)

    evidence_ids = (event.id, baseline.id) + tuple(prior_events)

    if excess <= Fraction(0):
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_CONSISTENT,
            evidence_ids=evidence_ids,
            calculation=f"requested {event.area}, available {available}",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    # excess > 0
    if parcel_history.baseline_complete:
        return Alert(
            rule_id=rule_id,
            status=Status.CONTRADICTION,
            message_key=MSG_R1_CONTRADICTION,
            evidence_ids=evidence_ids,
            calculation=f"requested {event.area}, available {available}, excess {excess}",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )
    else:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R1_REVIEW_INCOMPLETE_BASELINE,
            evidence_ids=evidence_ids,
            calculation=f"requested {event.area}, available {available}, excess {excess}, baseline incomplete",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )


# ---------------------------------------------------------------------------
# Rule R2: Duplicate Allocation
# ---------------------------------------------------------------------------

def check_r2(
    event: Event,
    all_events: Sequence[Event],
    baseline_record: SurveyRecord,
) -> Alert:
    """
    R2 Duplicate allocation:
      "Incompatible transfers allocate the same identified portion.
      Contradiction Found if overlap is established through portion_id and
      lineage; otherwise Review Required. Never match on dag number or deed
      number alone."

    Cancelled sales do not count toward duplicate-portion detection.
    """
    rule_id = "R2"

    # Pre-condition hygiene
    hygiene_alert = check_history_hygiene(all_events, baseline_record, rule_id, event.id)
    if hygiene_alert:
        return hygiene_alert

    # Step 1: Input validation (must have portion_id and linked_event_id for lineage)
    if event.portion_id is None or event.linked_event_id is None:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R2_REVIEW_INPUTS,
            evidence_ids=(event.id, baseline_record.id),
            calculation="Portion ID or lineage link is missing; cannot establish duplicate allocation.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    # Identify events cancelled by a CANCEL event in the history
    cancelled_ids = {
        e.linked_event_id for e in all_events
        if e.type == EventType.CANCEL and e.linked_event_id
    }

    # Step 2: Lineage match on portion_id and linked_event_id (excluding cancelled events)
    conflicting = [
        e.id for e in all_events
        if e.id != event.id
        and e.id not in cancelled_ids
        and e.type in (EventType.SALE, EventType.GIFT)
        and e.portion_id == event.portion_id
        and e.linked_event_id == event.linked_event_id
    ]

    if conflicting:
        return Alert(
            rule_id=rule_id,
            status=Status.CONTRADICTION,
            message_key=MSG_R2_CONTRADICTION,
            evidence_ids=(event.id,) + tuple(conflicting),
            calculation=f"Portion '{event.portion_id}' with lineage '{event.linked_event_id}' allocated in {conflicting}.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    # If same deed is used on other uncancelled events with different portion_ids, overlap is unestablished -> Review Required
    if event.deed_id is not None:
        same_deed_events = [
            e.id for e in all_events
            if e.id != event.id
            and e.id not in cancelled_ids
            and e.type in (EventType.SALE, EventType.GIFT)
            and e.deed_id == event.deed_id
        ]
        if same_deed_events:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R2_REVIEW_UNESTABLISHED,
                evidence_ids=(event.id,) + tuple(same_deed_events),
                calculation=f"Same deed '{event.deed_id}' used in {same_deed_events}, but distinct portion_ids; overlap unestablished.",
                recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
            )

    return Alert(
        rule_id=rule_id,
        status=Status.CONSISTENT,
        message_key=MSG_CONSISTENT,
        evidence_ids=(event.id, baseline_record.id),
        calculation=f"No duplicate allocation for portion '{event.portion_id}' with lineage '{event.linked_event_id}'.",
        recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
    )


# ---------------------------------------------------------------------------
# Rule R3: Seller's Recorded Interest
# ---------------------------------------------------------------------------

def check_r3(
    event: Event,
    parcel_history: ParcelHistory,
    all_events: Sequence[Event],
) -> Alert:
    """
    R3 Seller's recorded interest:
      "If baseline_complete is true for the relevant interval and complete
      supplied evidence disproves the seller's modeled interest at the event
      date, return Contradiction Found. If the interest cannot be established
      because evidence is missing or ambiguous, return Review Required."

    Mutual Exclusivity:
      R3 fires only when the seller is not a recorded holder at all.
    """
    rule_id = "R3"
    baseline = parcel_history.survey_records[0]

    # Pre-condition hygiene
    hygiene_alert = check_history_hygiene(all_events, baseline, rule_id, event.id)
    if hygiene_alert:
        return hygiene_alert

    # Step 1: Input validation
    if event.event_date is None or event.from_person is None:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R3_REVIEW_INPUTS,
            evidence_ids=(event.id, baseline.id),
            calculation="Event date or seller information is missing.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    # Step 2: Check recorded interest
    has_interest = is_recorded_holder(
        event.from_person, all_events, baseline, event.event_date, event.seq
    )

    if has_interest:
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_CONSISTENT,
            evidence_ids=(event.id, baseline.id),
            calculation=f"Seller '{event.from_person}' has documented recorded interest in parcel history.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    # Seller is NOT a recorded holder at all
    if parcel_history.baseline_complete:
        return Alert(
            rule_id=rule_id,
            status=Status.CONTRADICTION,
            message_key=MSG_R3_CONTRADICTION,
            evidence_ids=(event.id, baseline.id),
            calculation=f"Seller '{event.from_person}' is not a recorded holder and baseline is complete.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )
    else:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R3_REVIEW_INCOMPLETE_BASELINE,
            evidence_ids=(event.id, baseline.id),
            calculation=f"Seller '{event.from_person}' has no recorded interest, but baseline is incomplete.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )


# ---------------------------------------------------------------------------
# Rule R6: Deed-Mutation Reconciliation
# ---------------------------------------------------------------------------

def check_r6(
    mutation_event: Event,
    deed: Optional[Deed],
    all_events: Sequence[Event],
    baseline_record: SurveyRecord,
) -> Alert:
    """
    R6 Deed-mutation reconciliation:
      "If a mutation's linked deed, area or supplied transaction information
      does not reconcile, return Review Required."
      Returns CONSISTENT when everything reconciles completely.
    """
    rule_id = "R6"

    # Pre-condition hygiene
    hygiene_alert = check_history_hygiene(all_events, baseline_record, rule_id, mutation_event.id)
    if hygiene_alert:
        return hygiene_alert

    # Step 1: Input validation
    if mutation_event.deed_id is None or deed is None:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R6_REVIEW_MISSING_DEED,
            evidence_ids=(mutation_event.id, baseline_record.id),
            calculation="Mutation is missing linked deed_id or deed record is not supplied.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    if mutation_event.area is None:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R6_REVIEW_MISMATCH,
            evidence_ids=(mutation_event.id, deed.id),
            calculation="Mutation area is missing; cannot reconcile with deed.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    # Step 2: Reconcile mutation with linked transfer event
    linked_sale: Optional[Event] = None
    if mutation_event.linked_event_id:
        linked_sale = next((e for e in all_events if e.id == mutation_event.linked_event_id), None)
    if linked_sale is None:
        linked_sale = next((e for e in all_events if e.deed_id == deed.id), None)

    if linked_sale is None:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R6_REVIEW_MISSING_DEED,
            evidence_ids=(mutation_event.id, deed.id),
            calculation=f"No underlying transfer event found for deed '{deed.id}'.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    evidence_ids = (mutation_event.id, deed.id, linked_sale.id)

    # Check area match and beneficiary match
    area_matches = (mutation_event.area == linked_sale.area)
    beneficiary_matches = (
        mutation_event.to_person is None or mutation_event.to_person == linked_sale.to_person
    )

    if area_matches and beneficiary_matches:
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_R6_CONSISTENT,
            evidence_ids=evidence_ids,
            calculation=f"Mutation area {mutation_event.area} reconciles with deed {deed.deed_no} (sale {linked_sale.area}).",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    return Alert(
        rule_id=rule_id,
        status=Status.REVIEW,
        message_key=MSG_R6_REVIEW_MISMATCH,
        evidence_ids=evidence_ids,
        calculation=f"Mutation area {mutation_event.area} does not reconcile with deed {deed.deed_no} (sale {linked_sale.area}).",
        recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
    )


# ---------------------------------------------------------------------------
# Rule R4: Subdivision Reconciliation
# ---------------------------------------------------------------------------

def check_r4(
    subdivide_event: Event,
    child_survey_records: Sequence[SurveyRecord],
    all_events: Sequence[Event],
    baseline_record: SurveyRecord,
    tolerance: Fraction = R4_TOLERANCE,
) -> Alert:
    """
    R4 Subdivision reconciliation:
      "All area and share calculations use exact rational arithmetic. An exact
      area match passes. A difference greater than zero and at most the
      declared tolerance returns Review Required. A difference greater than
      the declared tolerance returns Contradiction Found. The tolerance is a
      named, explicit parameter in config."
    """
    rule_id = "R4"

    # Pre-condition hygiene
    hygiene_alert = check_history_hygiene(all_events, baseline_record, rule_id, subdivide_event.id)
    if hygiene_alert:
        return hygiene_alert

    # Step 1: Input validation
    if subdivide_event.area is None:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R4_REVIEW_INPUTS,
            evidence_ids=(subdivide_event.id, baseline_record.id),
            calculation="Subdivide event has no declared area.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    if len(child_survey_records) == 0:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R4_REVIEW_MISSING_CHILDREN,
            evidence_ids=(subdivide_event.id, baseline_record.id),
            calculation="No child parcel survey records supplied for subdivision reconciliation.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    # Step 2: Exact rational arithmetic reconciliation
    evidence_ids = (subdivide_event.id,) + tuple(sr.id for sr in child_survey_records)
    total_child_area = sum((sr.recorded_area for sr in child_survey_records), Fraction(0))
    diff = abs(subdivide_event.area - total_child_area)

    if diff == Fraction(0):
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_CONSISTENT,
            evidence_ids=evidence_ids,
            calculation=f"Exact match: parent subdivide area {subdivide_event.area} == child total {total_child_area}.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )
    elif diff <= tolerance:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R4_REVIEW_TOLERANCE,
            evidence_ids=evidence_ids,
            calculation=f"parent {subdivide_event.area}, children {total_child_area}, diff {diff} <= tolerance {tolerance}",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )
    else:
        return Alert(
            rule_id=rule_id,
            status=Status.CONTRADICTION,
            message_key=MSG_R4_CONTRADICTION,
            evidence_ids=evidence_ids,
            calculation=f"parent {subdivide_event.area}, children {total_child_area}, diff {diff} > tolerance {tolerance}",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )


# ---------------------------------------------------------------------------
# Rule R5: Survey Continuity
# ---------------------------------------------------------------------------

def check_r5(
    earlier_record: SurveyRecord,
    later_record: SurveyRecord,
    linking_events: Sequence[Event],
    all_events: Sequence[Event],
) -> Alert:
    """
    R5 Survey continuity:
      "If no documented relationship connects two successive survey records
      for the parcel, return Review Required."
      R5 NEVER returns Contradiction Found.
      Returns CONSISTENT when documented links connect the successive records.
    """
    rule_id = "R5"

    # Pre-condition hygiene on earlier record
    hygiene_alert = check_history_hygiene(all_events, earlier_record, rule_id, earlier_record.id)
    if hygiene_alert:
        return hygiene_alert

    # Step 1: Input validation
    if earlier_record is None or later_record is None:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R5_REVIEW_NO_LINK,
            evidence_ids=(earlier_record.id,) if earlier_record else ("MISSING_RECORD",),
            calculation="Successive survey records are missing or incomplete.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    # Step 2: Continuity check
    if len(linking_events) == 0:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R5_REVIEW_NO_LINK,
            evidence_ids=(earlier_record.id, later_record.id),
            calculation=f"No documented transaction links {earlier_record.survey} record {earlier_record.id} to {later_record.survey} record {later_record.id}.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    evidence_ids = (earlier_record.id, later_record.id) + tuple(e.id for e in linking_events)
    return Alert(
        rule_id=rule_id,
        status=Status.CONSISTENT,
        message_key=MSG_R5_CONSISTENT,
        evidence_ids=evidence_ids,
        calculation=f"Documented continuity from {earlier_record.survey} to {later_record.survey} via events {[e.id for e in linking_events]}.",
        recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
    )


# ---------------------------------------------------------------------------
# Rule R7: Chronological Consistency
# ---------------------------------------------------------------------------

def check_r7(
    mutation_event: Event,
    deed: Optional[Deed],
    all_events: Sequence[Event],
    baseline_record: SurveyRecord,
) -> Alert:
    """
    R7 Chronological consistency:
      "If the deed-mutation link and both dates are supplied and the mutation
      date precedes the deed registration date, return Contradiction Found.
      If the link or either date is missing, return Review Required."
    """
    rule_id = "R7"

    # Pre-condition hygiene
    hygiene_alert = check_history_hygiene(all_events, baseline_record, rule_id, mutation_event.id)
    if hygiene_alert:
        return hygiene_alert

    # Step 1: Input validation
    if (
        mutation_event.deed_id is None
        or deed is None
        or mutation_event.event_date is None
        or deed.registration_date is None
    ):
        evidence_ids = (mutation_event.id,) + ((deed.id,) if deed else ())
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R7_REVIEW_MISSING_LINK_OR_DATE,
            evidence_ids=evidence_ids,
            calculation="Deed-mutation link or date information is missing or ambiguous.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    evidence_ids = (mutation_event.id, deed.id)

    # Step 2: Chronological check
    if mutation_event.event_date < deed.registration_date:
        return Alert(
            rule_id=rule_id,
            status=Status.CONTRADICTION,
            message_key=MSG_R7_CONTRADICTION,
            evidence_ids=evidence_ids,
            calculation=f"Mutation date {mutation_event.event_date} precedes deed registration date {deed.registration_date}.",
            recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
        )

    return Alert(
        rule_id=rule_id,
        status=Status.CONSISTENT,
        message_key=MSG_R7_CONSISTENT,
        evidence_ids=evidence_ids,
        calculation=f"Mutation date {mutation_event.event_date} is on or after deed registration date {deed.registration_date}.",
        recommended_next_step=NEXT_STEP_BY_RULE[rule_id],
    )

