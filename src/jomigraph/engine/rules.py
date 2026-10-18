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
    MSG_R8_CONTRADICTION,
    MSG_R8_REVIEW_OMITTED_HEIR,
    MSG_R8_REVIEW_INPUTS,
    MSG_R8_CONSISTENT,
    MSG_R9_CONTRADICTION_MORTGAGE_ACTIVE,
    MSG_R9_CONTRADICTION_SECOND_MORTGAGE,
    MSG_R9_REVIEW_MISSING_DATE_OR_LINK,
    MSG_R9_CONSISTENT,
    MSG_R10_CONTRADICTION_REVOKED,
    MSG_R10_CONTRADICTION_MISSING_GRANT,
    MSG_R10_REVIEW_MISSING_DATE_OR_SCOPE,
    MSG_R10_CONSISTENT,
    MSG_R11_CONTRADICTION_GOV_LOCK,
    MSG_R11_REVIEW_COURT_OR_INJUNCTION,
    MSG_R11_REVIEW_MISSING_FLAG_DATE,
    MSG_R11_CONSISTENT,
    MSG_R12_CONTRADICTION,
    MSG_R12_REVIEW_NO_HASH,
    MSG_R12_CONSISTENT,
    MSG_R13_REVIEW_REUSED,
    MSG_R13_CONSISTENT,
    MSG_R14_REVIEW_NAME_COLLISION,
    MSG_R14_REVIEW_SPELLING_VARIATION,
    MSG_R14_CONSISTENT,
    MSG_R15_CONTRADICTION,
    MSG_R15_REVIEW_PARTIAL_BOUNDARY,
    MSG_R15_CONSISTENT,
    MSG_REVIEW_UNDATED_HISTORY,
    MSG_REVIEW_UNSUPPORTED_HISTORY,
    NEXT_STEP_BY_RULE,
    NEXT_STEP_R8,
    NEXT_STEP_R9,
    NEXT_STEP_R10,
    NEXT_STEP_R11,
    NEXT_STEP_R12,
    NEXT_STEP_R13,
    NEXT_STEP_R14,
    NEXT_STEP_R15,
    NEXT_STEP_REVIEW_HISTORY,
)
from jomigraph.engine.deed_hash import hash_deed_content
from jomigraph.models import Deed, Event, EventType, Parcel, ParcelHistory, Person, SurveyRecord


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


# ---------------------------------------------------------------------------
# Rule R8 — Unaccounted Heir Declaration Consistency
# ---------------------------------------------------------------------------

def check_r8(
    parcel_history: ParcelHistory,
    events: Sequence[Event] = (),
    deeds: Sequence[Deed] = (),
    baseline_record: Optional[SurveyRecord] = None,
    target_event: Optional[Event] = None,
    rule_id: str = "R8",
) -> Alert:
    """
    R8: Unaccounted Heir Declaration Consistency.
    Checks documentary consistency of recorded heir declarations against subsequent
    survey records (khatians) and transfer deeds.

    STRICT CONSTRAINTS (SPEC § Text R8):
      - DO NOT calculate inheritance shares by religious/statutory law (Muslim Farayez,
        Hindu succession acts).
      - Do not decide whether a succession sanad or warish certificate is legally genuine.
      - Do not infer heirs, relationships, religion, or ownership from names.
      - Never change ownership records or calculate inheritance entitlements.

    Semantics:
      - When the next survey khatian or transfer deed after a holder's death omits
        a previously declared heir, check whether there is a recorded deed executed
        by that heir documenting a sale, gift, or release/না-দাবি of their interest.
      - Contradiction Found: ONLY when the declaration is explicitly complete
        (complete is True and parcel_history.baseline_complete is True), all required
        dates are present, the documentary chain is explicit, and no recorded deed
        accounts for the omitted heir.
      - Review Required: when declaration completeness flag is False/missing,
        or baseline_complete is False, or dates/records/links are ambiguous/missing.
      - Consistent with supplied records: when all declared heirs are recorded in the
        subsequent record, OR when the omitted heir previously transferred/released their
        interest by a documented deed (tricky clean case), OR when no heir declaration exists.
    """
    if not parcel_history.heir_declaration:
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_R8_CONSISTENT,
            evidence_ids=(parcel_history.parcel_id,),
            calculation="No heir declarations recorded in parcel history.",
            recommended_next_step=NEXT_STEP_R8,
        )

    # Normalize declaration(s)
    raw_decl = parcel_history.heir_declaration
    if isinstance(raw_decl, dict):
        decl_list = [raw_decl]
    elif isinstance(raw_decl, (list, tuple)):
        decl_list = list(raw_decl)
    else:
        decl_list = []

    if not decl_list:
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_R8_CONSISTENT,
            evidence_ids=(parcel_history.parcel_id,),
            calculation="No heir declarations recorded in parcel history.",
            recommended_next_step=NEXT_STEP_R8,
        )

    all_events_list = list(events)
    if target_event is not None and target_event not in all_events_list:
        all_events_list.append(target_event)

    overall_alert: Optional[Alert] = None

    for decl in decl_list:
        if not isinstance(decl, dict):
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R8_REVIEW_INPUTS,
                evidence_ids=(parcel_history.parcel_id,),
                calculation="Heir declaration entry is malformed (not a dictionary).",
                recommended_next_step=NEXT_STEP_R8,
            )

        deceased_id = decl.get("deceased_id")
        declared_heirs = decl.get("declared_heirs")
        complete_flag = decl.get("complete")
        source_record_id = decl.get("source_record_id")
        raw_date = (
            decl.get("declaration_date")
            or decl.get("death_date")
            or decl.get("record_date")
            or decl.get("date")
        )

        # 1. Input hygiene
        if not deceased_id or declared_heirs is None or not source_record_id:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R8_REVIEW_INPUTS,
                evidence_ids=(parcel_history.parcel_id, str(source_record_id or "UNKNOWN_DECLARATION")),
                calculation="Heir declaration missing required fields (deceased_id, declared_heirs, or source_record_id).",
                recommended_next_step=NEXT_STEP_R8,
            )

        heir_entries: list[tuple[str, str]] = []
        if isinstance(declared_heirs, (list, tuple)):
            for item in declared_heirs:
                if isinstance(item, dict):
                    hid = item.get("person_id") or item.get("id") or item.get("name")
                    rel = item.get("relation", "heir")
                    if hid:
                        heir_entries.append((str(hid), str(rel)))
                elif isinstance(item, str) and item:
                    heir_entries.append((item, "heir"))

        if not heir_entries:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R8_REVIEW_INPUTS,
                evidence_ids=(parcel_history.parcel_id, str(source_record_id)),
                calculation="Declared heirs list is empty or contains no valid person identifiers.",
                recommended_next_step=NEXT_STEP_R8,
            )

        # Parse declaration date
        decl_date: Optional[date] = None
        date_explicit = True
        if raw_date:
            if isinstance(raw_date, date):
                decl_date = raw_date
            elif isinstance(raw_date, str):
                try:
                    decl_date = date.fromisoformat(raw_date)
                except ValueError:
                    decl_date = None
                    date_explicit = False
        else:
            date_explicit = False

        # Identify deceased's prior records
        deceased_srs = [
            sr for sr in parcel_history.survey_records
            if any(h[0] == deceased_id for h in sr.holders)
        ]
        if not decl_date and deceased_srs:
            decl_date = max(sr.record_date for sr in deceased_srs)

        # Find subsequent survey records
        subsequent_srs: list[SurveyRecord] = []
        for sr in parcel_history.survey_records:
            if sr in deceased_srs:
                continue
            if decl_date and sr.record_date > decl_date:
                subsequent_srs.append(sr)
            elif not decl_date and sr not in deceased_srs:
                subsequent_srs.append(sr)
        subsequent_srs.sort(key=lambda s: s.record_date)

        # Find subsequent transfer events
        subsequent_events: list[Event] = []
        for e in all_events_list:
            if e.from_person == deceased_id:
                continue
            if decl_date and e.event_date and e.event_date >= decl_date:
                subsequent_events.append(e)
            elif not decl_date:
                subsequent_events.append(e)
        subsequent_events.sort(key=lambda ev: (ev.event_date or date.min, ev.seq))

        next_sr = subsequent_srs[0] if subsequent_srs else None
        next_events = [e for e in subsequent_events if e.type in (EventType.SALE, EventType.GIFT, EventType.RELEASE, "RELEASE")]
        next_event = next_events[0] if next_events else None

        # If no subsequent khatian or transfer deed exists after the declaration:
        if not next_sr and not next_event:
            return Alert(
                rule_id=rule_id,
                status=Status.CONSISTENT,
                message_key=MSG_R8_CONSISTENT,
                evidence_ids=(parcel_history.parcel_id, str(source_record_id)),
                calculation=f"Heir declaration '{source_record_id}' recorded; no subsequent survey khatian or deed has omitted any declared heirs.",
                recommended_next_step=NEXT_STEP_R8,
            )

        next_record_id = next_sr.id if next_sr else (next_event.id if next_event else parcel_history.parcel_id)
        next_record_date = (
            str(next_sr.record_date)
            if next_sr
            else (str(next_event.event_date) if next_event and next_event.event_date else "undated")
        )

        unaccounted_heirs: list[tuple[str, str]] = []
        accounting_evidence: list[str] = [parcel_history.parcel_id, str(source_record_id)]
        if next_sr:
            accounting_evidence.append(next_sr.id)
        if next_event:
            accounting_evidence.append(next_event.id)

        tricky_accounted_details: list[str] = []
        next_sr_holders = {h[0] for h in next_sr.holders} if next_sr else set()

        for hid, rel in heir_entries:
            # Way 1: Listed as a holder in next survey record
            if hid in next_sr_holders:
                continue

            # Way 2: Documented deed executed by that heir (SALE, GIFT, RELEASE)
            accounting_deed = next(
                (
                    e for e in all_events_list
                    if e.from_person == hid
                    and e.type in (EventType.SALE, EventType.GIFT, EventType.RELEASE, "RELEASE")
                    and (e.deed_id or e.source_record_id or e.id)
                    and (not decl_date or not e.event_date or e.event_date >= decl_date or (next_sr and e.event_date <= next_sr.record_date))
                ),
                None,
            )

            if accounting_deed is not None:
                accounting_evidence.append(accounting_deed.id)
                if accounting_deed.deed_id:
                    accounting_evidence.append(accounting_deed.deed_id)
                tricky_accounted_details.append(
                    f"Declared heir '{hid}' ({rel}) is omitted from subsequent record '{next_record_id}', "
                    f"but interest is accounted for by recorded deed '{accounting_deed.deed_id or accounting_deed.id}' "
                    f"({accounting_deed.type.value if hasattr(accounting_deed.type, 'value') else accounting_deed.type}) "
                    f"dated {accounting_deed.event_date}."
                )
                continue

            # Way 3: Party in the immediate next deed
            if next_event and (next_event.from_person == hid or next_event.to_person == hid):
                continue

            # If not accounted for:
            unaccounted_heirs.append((hid, rel))

        # Evaluate outcome for this declaration
        if not unaccounted_heirs:
            calc_msg = (
                " ".join(tricky_accounted_details)
                if tricky_accounted_details
                else f"All declared heirs under declaration '{source_record_id}' are recorded in subsequent khatian '{next_record_id}'."
            )
            decl_alert = Alert(
                rule_id=rule_id,
                status=Status.CONSISTENT,
                message_key=MSG_R8_CONSISTENT,
                evidence_ids=tuple(dict.fromkeys(accounting_evidence)),
                calculation=calc_msg,
                recommended_next_step=NEXT_STEP_R8,
            )
        else:
            omitted_desc = ", ".join(f"'{hid}' ({rel})" for hid, rel in unaccounted_heirs)
            has_undated = (
                not date_explicit
                or (next_sr and next_sr.record_date is None)
                or (next_event and next_event.event_date is None)
            )

            is_complete = (complete_flag is True) and (parcel_history.baseline_complete is True)

            if is_complete and not has_undated:
                decl_alert = Alert(
                    rule_id=rule_id,
                    status=Status.CONTRADICTION,
                    message_key=MSG_R8_CONTRADICTION,
                    evidence_ids=tuple(dict.fromkeys([parcel_history.parcel_id, str(source_record_id), next_record_id])),
                    calculation=(
                        f"Declared heir {omitted_desc} under complete declaration '{source_record_id}' "
                        f"is omitted from subsequent record '{next_record_id}' ({next_record_date}) "
                        f"without any recorded deed of sale, gift, or release."
                    ),
                    recommended_next_step=NEXT_STEP_R8,
                )
            else:
                reasons = []
                if not is_complete:
                    reasons.append(f"declaration complete flag is {complete_flag!r}, baseline_complete is {parcel_history.baseline_complete!r}")
                if has_undated:
                    reasons.append("dates on declaration or subsequent record are missing/ambiguous")
                reason_str = "; ".join(reasons)

                decl_alert = Alert(
                    rule_id=rule_id,
                    status=Status.REVIEW,
                    message_key=MSG_R8_REVIEW_OMITTED_HEIR,
                    evidence_ids=tuple(dict.fromkeys([parcel_history.parcel_id, str(source_record_id), next_record_id])),
                    calculation=(
                        f"Declared heir {omitted_desc} under declaration '{source_record_id}' is omitted from subsequent record '{next_record_id}', "
                        f"and review is required ({reason_str})."
                    ),
                    recommended_next_step=NEXT_STEP_R8,
                )

        if overall_alert is None:
            overall_alert = decl_alert
        elif decl_alert.status == Status.CONTRADICTION:
            overall_alert = decl_alert
        elif decl_alert.status == Status.REVIEW and overall_alert.status == Status.CONSISTENT:
            overall_alert = decl_alert

    return overall_alert or Alert(
        rule_id=rule_id,
        status=Status.CONSISTENT,
        message_key=MSG_R8_CONSISTENT,
        evidence_ids=(parcel_history.parcel_id,),
        calculation="All declared heirs accounted for.",
        recommended_next_step=NEXT_STEP_R8,
    )


# ---------------------------------------------------------------------------
# Rule R12 — Deed Content Integrity & Tamper Detection (F13)
# ---------------------------------------------------------------------------

def check_r12(
    deed: Optional[Deed],
    trigger_event: Optional[Event] = None,
    claimed_hash: Optional[str] = None,
    rule_id: str = "R12",
) -> Alert:
    """
    R12: Deed Content Integrity and Tamper Detection (F13).
    Compares the cryptographic SHA-256 fingerprint computed over canonical deed fields
    (deed_no, registration_date, parcel_id, seller, buyer, area) against the registry-recorded
    deed.content_hash and any optional claimed_hash.

    Statuses:
      - Contradiction Found: presented fields differ from registry-recorded content_hash
        (tamper detected) OR claimed_hash does not match computed/recorded hash.
      - Review Required: deed has no content_hash on file (legacy deed) OR claimed_hash
        is missing when verification is explicitly requested.
      - Consistent with supplied records: computed hash matches registry-recorded content_hash.
    """
    if deed is None or trigger_event is None:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R12_REVIEW_NO_HASH,
            evidence_ids=(getattr(trigger_event, "id", "UNKNOWN"),),
            calculation="Deed or event records missing for content verification.",
            recommended_next_step=NEXT_STEP_R12,
        )

    # Missing mandatory participating fields -> Review Required
    if (
        not deed.deed_no
        or not deed.registration_date
        or not trigger_event.parcel_id
        or not trigger_event.from_person
        or not trigger_event.to_person
        or trigger_event.area is None
    ):
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R12_REVIEW_NO_HASH,
            evidence_ids=(deed.id, trigger_event.id),
            calculation="Deed or event fields required for canonical fingerprinting are missing or ambiguous.",
            recommended_next_step=NEXT_STEP_R12,
        )

    computed = hash_deed_content(
        deed_no=deed.deed_no,
        registration_date=deed.registration_date,
        parcel_id=trigger_event.parcel_id,
        seller=trigger_event.from_person,
        buyer=trigger_event.to_person,
        area=trigger_event.area,
    )

    clean_recorded = deed.content_hash.strip().lower() if deed.content_hash else None
    clean_claimed = claimed_hash.strip().lower() if claimed_hash else None

    # Case A: Claimed hash provided
    if clean_claimed is not None:
        if clean_recorded is None:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R12_REVIEW_NO_HASH,
                evidence_ids=(deed.id, trigger_event.id),
                calculation=f"Claimed hash provided ({clean_claimed[:16]}...) but no registry-recorded fingerprint on file.",
                recommended_next_step=NEXT_STEP_R12,
            )
        claimed_matches_recorded = (
            clean_claimed == clean_recorded
            or (len(clean_claimed) >= 16 and clean_recorded.startswith(clean_claimed))
        )
        claimed_matches_computed = (
            clean_claimed == computed
            or (len(clean_claimed) >= 16 and computed.startswith(clean_claimed))
        )
        if not claimed_matches_recorded or not claimed_matches_computed:
            return Alert(
                rule_id=rule_id,
                status=Status.CONTRADICTION,
                message_key=MSG_R12_CONTRADICTION,
                evidence_ids=(deed.id, trigger_event.id),
                calculation=(
                    f"Claimed/presented hash {clean_claimed[:16]}... differs from "
                    f"registry-recorded fingerprint {clean_recorded[:16]}... (tamper detected)."
                ),
                recommended_next_step=NEXT_STEP_R12,
            )
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_R12_CONSISTENT,
            evidence_ids=(deed.id, trigger_event.id),
            calculation=f"Presented fingerprint matches registry-recorded hash {clean_recorded[:16]}....",
            recommended_next_step=NEXT_STEP_R12,
        )

    # Case B: No claimed hash provided
    if clean_recorded is None:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R12_REVIEW_NO_HASH,
            evidence_ids=(deed.id, trigger_event.id),
            calculation="No registry content fingerprint recorded on file for this deed.",
            recommended_next_step=NEXT_STEP_R12,
        )

    if computed != clean_recorded:
        return Alert(
            rule_id=rule_id,
            status=Status.CONTRADICTION,
            message_key=MSG_R12_CONTRADICTION,
            evidence_ids=(deed.id, trigger_event.id),
            calculation=(
                f"Event fields produce fingerprint {computed[:16]}... which differs from "
                f"registry-recorded fingerprint {clean_recorded[:16]}... (tamper detected)."
            ),
            recommended_next_step=NEXT_STEP_R12,
        )

    return Alert(
        rule_id=rule_id,
        status=Status.CONSISTENT,
        message_key=MSG_R12_CONSISTENT,
        evidence_ids=(deed.id, trigger_event.id),
        calculation=f"Event fields match registry-recorded fingerprint {clean_recorded[:16]}....",
        recommended_next_step=NEXT_STEP_R12,
    )


# ---------------------------------------------------------------------------
# Rule R13 — Deed Number Reuse Detection (F14)
# ---------------------------------------------------------------------------

def check_r13(
    deed: Optional[Deed],
    trigger_event: Event,
    all_events: Sequence[Event] = (),
    all_deeds: Sequence[Deed] = (),
    rule_id: str = "R13",
) -> Alert:
    """
    R13: Deed Number Reuse Detection (F14).
    Checks if the same deed_no is reused across multiple parcels/events.

    Semantics (SPEC § F14):
      - Same deed_no with different registration date, seller, buyer, or area -> Review Required ONLY.
      - Never Contradiction Found.
      - Never claim double sale: legitimate multi-dag deeds covering several dags with identical terms
        are Consistent with supplied records.
      - Evidence includes all parcels and events sharing the deed number.
    """
    if deed is None or not deed.deed_no:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R13_REVIEW_REUSED,
            evidence_ids=(trigger_event.id,),
            calculation="No deed record linked to event to verify deed number reuse.",
            recommended_next_step=NEXT_STEP_R13,
        )

    # Find all deeds and events sharing this deed_no
    matching_deeds = [d for d in all_deeds if d.deed_no == deed.deed_no]
    matching_deed_ids = {d.id for d in matching_deeds} | {deed.id}
    matching_events = [e for e in all_events if e.deed_id in matching_deed_ids]

    if trigger_event not in matching_events:
        matching_events.append(trigger_event)

    # If appears in at most one recorded event
    if len(matching_events) <= 1:
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_R13_CONSISTENT,
            evidence_ids=(trigger_event.id, deed.id),
            calculation=f"Deed number {deed.deed_no} appears in a single recorded transaction.",
            recommended_next_step=NEXT_STEP_R13,
        )

    # Check for differing dates, parties, or area across matching records
    reg_dates = {d.registration_date for d in matching_deeds}
    sellers = {e.from_person for e in matching_events if e.from_person is not None}
    buyers = {e.to_person for e in matching_events if e.to_person is not None}
    areas = {e.area for e in matching_events if e.area is not None}
    parcels = {e.parcel_id for e in matching_events if e.parcel_id is not None}

    diffs = []
    if len(reg_dates) > 1:
        diffs.append("different registration dates")
    if len(sellers) > 1:
        diffs.append("different sellers")
    if len(buyers) > 1:
        diffs.append("different buyers")
    if len(areas) > 1:
        diffs.append("different transaction areas")

    evidence_ids = tuple(sorted(set([trigger_event.id, deed.id] + [e.id for e in matching_events] + [d.id for d in matching_deeds])))

    if diffs:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R13_REVIEW_REUSED,
            evidence_ids=evidence_ids,
            calculation=(
                f"Deed number {deed.deed_no} reused across records with {', '.join(diffs)} "
                f"on parcels {sorted(parcels)}."
            ),
            recommended_next_step=NEXT_STEP_R13,
        )

    # Legitimate multi-dag deed with identical dates, parties, and terms
    return Alert(
        rule_id=rule_id,
        status=Status.CONSISTENT,
        message_key=MSG_R13_CONSISTENT,
        evidence_ids=evidence_ids,
        calculation=(
            f"Deed number {deed.deed_no} legitimately covers multiple parcels ({sorted(parcels)}) "
            f"with identical registration date, parties, and terms."
        ),
        recommended_next_step=NEXT_STEP_R13,
    )


# ---------------------------------------------------------------------------
# Rule R14 — Dummy Identity Numbers & Disambiguation (F15)
# ---------------------------------------------------------------------------

def check_r14(
    history: ParcelHistory,
    all_persons: Sequence[Person] = (),
    rule_id: str = "R14",
) -> Alert:
    """
    R14: Dummy Identity Numbers & Disambiguation (F15).
    Checks that person entities in a parcel history are properly disambiguated by dummy_id.

    Semantics (SPEC § F15):
      - Same name + different dummy_id = different people (Consistent).
      - Same dummy_id + different spelling of name = Review Required (possible same person, needs checking).
      - Missing dummy_id on a name that appears on multiple distinct Person entities in parcel history = Review Required.
      - Distinct persons with distinct names = Consistent.
    """
    person_ids: set[str] = set()
    for sr in history.survey_records:
        for h_id, _ in sr.holders:
            if h_id:
                person_ids.add(h_id)
    for e in history.events:
        if e.from_person:
            person_ids.add(e.from_person)
        if e.to_person:
            person_ids.add(e.to_person)

    persons = [p for p in all_persons if p.id in person_ids]
    if not persons:
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_R14_CONSISTENT,
            evidence_ids=(history.parcel_id,),
            calculation="No person records to disambiguate in parcel history.",
            recommended_next_step=NEXT_STEP_R14,
        )

    # Check 1: Spelling variations on the same dummy_id
    dummy_map: dict[str, list[Person]] = {}
    for p in persons:
        if p.dummy_id:
            dummy_map.setdefault(p.dummy_id, []).append(p)

    for dummy_id, plist in dummy_map.items():
        distinct_spellings = set(p.name.strip().lower() for p in plist)
        if len(distinct_spellings) > 1:
            evidence_ids = tuple(sorted(set(p.id for p in plist)))
            names = sorted(set(p.name for p in plist))
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R14_REVIEW_SPELLING_VARIATION,
                evidence_ids=evidence_ids,
                calculation=f"Dummy ID {dummy_id} is associated with multiple name spellings: {names}.",
                recommended_next_step=NEXT_STEP_R14,
            )

    # Check 2: Name collision without dummy_id
    name_map: dict[str, list[Person]] = {}
    for p in persons:
        name_map.setdefault(p.name.strip().lower(), []).append(p)

    for norm_name, plist in name_map.items():
        if len(plist) > 1:
            # If any distinct person record in this group lacks a dummy_id
            if any(p.dummy_id is None for p in plist):
                evidence_ids = tuple(sorted(set(p.id for p in plist)))
                return Alert(
                    rule_id=rule_id,
                    status=Status.REVIEW,
                    message_key=MSG_R14_REVIEW_NAME_COLLISION,
                    evidence_ids=evidence_ids,
                    calculation=(
                        f"Person name '{plist[0].name}' appears on multiple records in this parcel history "
                        f"without disambiguating dummy identity numbers."
                    ),
                    recommended_next_step=NEXT_STEP_R14,
                )

    return Alert(
        rule_id=rule_id,
        status=Status.CONSISTENT,
        message_key=MSG_R14_CONSISTENT,
        evidence_ids=(history.parcel_id,),
        calculation="All person identities in parcel history are unique or disambiguated with dummy identity numbers.",
        recommended_next_step=NEXT_STEP_R14,
    )



# ---------------------------------------------------------------------------
# Rule R15: Structured Boundary / Duplicate Physical Portion (F16 / P3 Core)
# ---------------------------------------------------------------------------

def _normalize_boundary_data(boundary: Any) -> tuple[Optional[Any], bool]:
    """
    Normalize raw boundary data from an Event (event.boundary or event.portion['boundary']).
    Returns:
      (normalized_value, is_valid_complete)
      If partially given or invalid, returns ("PARTIAL", False)
      If completely missing, returns (None, False)
      If complete, returns (normalized_repr, True)
    """
    if boundary is None:
        return None, False

    if isinstance(boundary, str):
        val = boundary.strip()
        if not val:
            return None, False
        return val.lower(), True

    if isinstance(boundary, dict):
        has_dirs = any(d in boundary for d in ("north", "south", "east", "west"))
        if has_dirs:
            north = str(boundary.get("north") or "").strip()
            south = str(boundary.get("south") or "").strip()
            east = str(boundary.get("east") or "").strip()
            west = str(boundary.get("west") or "").strip()
            if north and south and east and west:
                return {
                    "north": north.lower(),
                    "south": south.lower(),
                    "east": east.lower(),
                    "west": west.lower(),
                }, True
            elif north or south or east or west:
                return "PARTIAL", False
            else:
                return None, False

        if "sub_dag" in boundary or "sub_dag_no" in boundary:
            sub = str(boundary.get("sub_dag") or boundary.get("sub_dag_no") or "").strip()
            if sub:
                return sub.lower(), True
            return None, False

        if "description" in boundary:
            desc = str(boundary.get("description", "")).strip()
            if desc:
                return desc.lower(), True
            return None, False

        return "PARTIAL", False

    return "PARTIAL", False


def _extract_event_boundary(event: Event) -> tuple[Optional[Any], bool, bool]:
    """
    Extract boundary representation from Event.
    Returns:
      (normalized_boundary, is_complete, has_portion_or_boundary_claim)
    """
    has_claim = False
    raw_b = None

    if event.boundary is not None:
        has_claim = True
        raw_b = event.boundary
    elif isinstance(event.portion, dict):
        has_claim = True
        raw_b = event.portion.get("boundary")

    if not has_claim:
        return None, False, False

    norm_b, is_complete = _normalize_boundary_data(raw_b)
    return norm_b, is_complete, True


def _boundaries_overlap(b1: Any, b2: Any) -> bool:
    """
    Check if two complete boundary representations are identical or one contains the other.
    """
    if b1 is None or b2 is None:
        return False

    if isinstance(b1, dict) and isinstance(b2, dict):
        return (
            b1.get("north") == b2.get("north")
            and b1.get("south") == b2.get("south")
            and b1.get("east") == b2.get("east")
            and b1.get("west") == b2.get("west")
        )

    if isinstance(b1, str) and isinstance(b2, str):
        if b1 == b2:
            return True
        if b1.startswith(b2 + "-") or b1.startswith(b2 + "/"):
            return True
        if b2.startswith(b1 + "-") or b2.startswith(b1 + "/"):
            return True

    return False


def check_r15(
    event: Event,
    all_events: Sequence[Event],
    baseline_record: SurveyRecord,
    rule_id: str = "R15",
) -> Alert:
    """
    R15: Same portion sold twice, structured boundary / portion marks (F16 / P3 core).
    Complements R2: R2 matches on exact portion_id; R15 catches the same physical piece
    under different portion_ids by inspecting structured boundary descriptors (north, south,
    east, west) or named sub-dags.

    Statuses:
      - Contradiction Found: Two non-cancelled transfers in lineage have identical structured
        boundary descriptors, or one contains the other.
      - Review Required: Boundary descriptors are missing, partial, or ambiguous.
      - Consistent with supplied records: Boundary descriptors are complete and distinct
        from all prior transfers.
    """
    # Pre-condition hygiene
    hygiene_alert = check_history_hygiene(all_events, baseline_record, rule_id, event.id)
    if hygiene_alert:
        return hygiene_alert

    norm_b, is_complete, has_claim = _extract_event_boundary(event)

    # If boundaries are missing or only partly given -> Review Required
    if not has_claim or not is_complete or norm_b == "PARTIAL":
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R15_REVIEW_PARTIAL_BOUNDARY,
            evidence_ids=(event.id, baseline_record.id),
            calculation="Portion boundary descriptors are missing, partial, or ambiguous; physical plot isolation cannot be verified.",
            recommended_next_step=NEXT_STEP_R15,
        )

    # Find non-cancelled transfers in history
    cancelled_ids = {
        e.linked_event_id for e in all_events
        if e.type == EventType.CANCEL and e.linked_event_id
    }

    conflicting_ids: list[str] = []
    for other in all_events:
        if other.id == event.id:
            continue
        if other.id in cancelled_ids:
            continue
        if other.type not in (EventType.SALE, EventType.GIFT):
            continue

        other_b, other_complete, other_has_claim = _extract_event_boundary(other)
        if other_has_claim and other_complete and other_b != "PARTIAL":
            if _boundaries_overlap(norm_b, other_b):
                conflicting_ids.append(other.id)

    if conflicting_ids:
        portion_label = event.portion_id or (event.portion.get("portion_id") if isinstance(event.portion, dict) else "unlabeled")
        b_repr = norm_b if isinstance(norm_b, str) else f"N:{norm_b.get('north')}, S:{norm_b.get('south')}, E:{norm_b.get('east')}, W:{norm_b.get('west')}"
        return Alert(
            rule_id=rule_id,
            status=Status.CONTRADICTION,
            message_key=MSG_R15_CONTRADICTION,
            evidence_ids=(event.id,) + tuple(conflicting_ids),
            calculation=(
                f"Boundary/sub-dag '{b_repr}' for portion '{portion_label}' conflicts with "
                f"prior recorded transfer(s) {conflicting_ids}."
            ),
            recommended_next_step=NEXT_STEP_R15,
        )

    portion_label = event.portion_id or (event.portion.get("portion_id") if isinstance(event.portion, dict) else "unlabeled")
    return Alert(
        rule_id=rule_id,
        status=Status.CONSISTENT,
        message_key=MSG_R15_CONSISTENT,
        evidence_ids=(event.id, baseline_record.id),
        calculation=f"Boundary descriptors for portion '{portion_label}' are distinct and non-overlapping with recorded transfers.",
        recommended_next_step=NEXT_STEP_R15,
    )


# ---------------------------------------------------------------------------
# Rule R11: Government and Court Lockouts (Phase 9)
# ---------------------------------------------------------------------------

def check_r11(
    event: Event,
    parcel: Optional[Parcel],
    baseline_record: SurveyRecord,
    rule_id: str = "R11",
) -> Alert:
    """
    R11: Government and Court Lockouts.
    SPEC § 4 F17 + text R11:
      - Optional parcel metadata:
          is_khas (bool)
          under_acquisition (bool) with flag_date
          court_case_no (string, fictional) with case_status ('pending' | 'disposed')
          injunction (bool)
      - A SALE/GIFT dated after a khas or acquisition flag -> Contradiction Found
        (records conflict with the recorded flag).
      - A pending case or injunction -> Review Required
        (a case alone does not prove the sale is invalid).
      - Flag missing a date -> Review Required.
      - Pre-flag transfers (event_date < flag_date) or clean parcels -> Consistent.
    """
    if parcel is None:
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_R11_CONSISTENT,
            evidence_ids=(event.id, baseline_record.id),
            calculation="No parcel metadata provided to evaluate government or court locks.",
            recommended_next_step=NEXT_STEP_R11,
        )

    has_gov_flag = bool(parcel.is_khas or parcel.under_acquisition)
    if has_gov_flag:
        if parcel.flag_date is None:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R11_REVIEW_MISSING_FLAG_DATE,
                evidence_ids=(event.id, baseline_record.id),
                calculation=(
                    f"Parcel {parcel.id} has government khas or acquisition flag "
                    f"(is_khas={parcel.is_khas}, under_acquisition={parcel.under_acquisition}) "
                    f"but flag_date is missing."
                ),
                recommended_next_step=NEXT_STEP_R11,
            )
        if event.event_date is None:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R11_REVIEW_MISSING_FLAG_DATE,
                evidence_ids=(event.id, baseline_record.id),
                calculation=f"Event {event.id} date is missing while parcel carries government flag dated {parcel.flag_date}.",
                recommended_next_step=NEXT_STEP_R11,
            )
        if event.event_date >= parcel.flag_date:
            return Alert(
                rule_id=rule_id,
                status=Status.CONTRADICTION,
                message_key=MSG_R11_CONTRADICTION_GOV_LOCK,
                evidence_ids=(event.id, baseline_record.id),
                calculation=(
                    f"Transfer event {event.id} dated {event.event_date} is recorded after "
                    f"government flag date {parcel.flag_date} "
                    f"(is_khas={parcel.is_khas}, under_acquisition={parcel.under_acquisition})."
                ),
                recommended_next_step=NEXT_STEP_R11,
            )

    if parcel.injunction:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R11_REVIEW_COURT_OR_INJUNCTION,
            evidence_ids=(event.id, baseline_record.id),
            calculation=f"Parcel {parcel.id} is subject to an active court injunction.",
            recommended_next_step=NEXT_STEP_R11,
        )

    if parcel.court_case_no:
        status_norm = (parcel.case_status or "").lower()
        if status_norm == "pending" or not status_norm:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R11_REVIEW_COURT_OR_INJUNCTION,
                evidence_ids=(event.id, baseline_record.id),
                calculation=f"Parcel {parcel.id} is subject to pending court case {parcel.court_case_no}.",
                recommended_next_step=NEXT_STEP_R11,
            )

    return Alert(
        rule_id=rule_id,
        status=Status.CONSISTENT,
        message_key=MSG_R11_CONSISTENT,
        evidence_ids=(event.id, baseline_record.id),
        calculation=f"No active government acquisition, khas declaration, or court injunction conflicts with event {event.id}.",
        recommended_next_step=NEXT_STEP_R11,
    )


# ---------------------------------------------------------------------------
# Rule R9: Mortgage and Release (Phase 9)
# ---------------------------------------------------------------------------

def check_r9(
    event: Event,
    events: Sequence[Event],
    baseline_record: SurveyRecord,
    rule_id: str = "R9",
) -> Alert:
    """
    R9: Active Mortgage Encumbrance & Release Validation.
    SPEC § 4 Text R9:
      - New event types MORTGAGE and MORTGAGE_RELEASE.
      - A SALE/GIFT by the mortgagor while a mortgage on that portion is unreleased -> Contradiction Found.
      - A second MORTGAGE on a portion with an unreleased one -> Contradiction Found.
      - Release date missing or unclear -> Review Required.
      - Replay treats these types as non-transferring (does not change holder areas).
    """
    if event.event_date is None:
        return Alert(
            rule_id=rule_id,
            status=Status.REVIEW,
            message_key=MSG_R9_REVIEW_MISSING_DATE_OR_LINK,
            evidence_ids=(event.id, baseline_record.id),
            calculation=f"Event {event.id} date is missing.",
            recommended_next_step=NEXT_STEP_R9,
        )

    def _portions_overlap(p1: Optional[str], p2: Optional[str]) -> bool:
        if p1 is None or p2 is None:
            return True
        return p1 == p2

    # Case A: SALE or GIFT
    if event.type in (EventType.SALE, EventType.GIFT):
        prior_mortgages = [
            e for e in events
            if e.type == EventType.MORTGAGE
            and e.id != event.id
            and e.from_person == event.from_person
            and (e.event_date, e.seq) < (event.event_date, event.seq)
            and _portions_overlap(e.portion_id, event.portion_id)
        ]

        for m in prior_mortgages:
            if m.event_date is None:
                return Alert(
                    rule_id=rule_id,
                    status=Status.REVIEW,
                    message_key=MSG_R9_REVIEW_MISSING_DATE_OR_LINK,
                    evidence_ids=(event.id, m.id),
                    calculation=f"Prior mortgage {m.id} lacks an event date.",
                    recommended_next_step=NEXT_STEP_R9,
                )

            releases = [
                e for e in events
                if e.type == EventType.MORTGAGE_RELEASE
                and (e.linked_event_id == m.id or (e.linked_event_id is None and _portions_overlap(e.portion_id, m.portion_id) and e.to_person == m.from_person))
            ]

            if not releases:
                unlinked = [e for e in events if e.type == EventType.MORTGAGE_RELEASE and e.linked_event_id is None]
                if unlinked:
                    return Alert(
                        rule_id=rule_id,
                        status=Status.REVIEW,
                        message_key=MSG_R9_REVIEW_MISSING_DATE_OR_LINK,
                        evidence_ids=(event.id, m.id, unlinked[0].id),
                        calculation=f"Mortgage {m.id} has no explicit release, but unlinked release {unlinked[0].id} exists.",
                        recommended_next_step=NEXT_STEP_R9,
                    )
                return Alert(
                    rule_id=rule_id,
                    status=Status.CONTRADICTION,
                    message_key=MSG_R9_CONTRADICTION_MORTGAGE_ACTIVE,
                    evidence_ids=(event.id, m.id),
                    calculation=(
                        f"Transfer event {event.id} by mortgagor {event.from_person} occurs while "
                        f"prior mortgage {m.id} dated {m.event_date} on portion "
                        f"{event.portion_id or m.portion_id or 'all'} remains unreleased."
                    ),
                    recommended_next_step=NEXT_STEP_R9,
                )

            rel = releases[0]
            if rel.event_date is None:
                return Alert(
                    rule_id=rule_id,
                    status=Status.REVIEW,
                    message_key=MSG_R9_REVIEW_MISSING_DATE_OR_LINK,
                    evidence_ids=(event.id, m.id, rel.id),
                    calculation=f"Mortgage release {rel.id} for mortgage {m.id} lacks an event date.",
                    recommended_next_step=NEXT_STEP_R9,
                )
            if rel.event_date > event.event_date:
                return Alert(
                    rule_id=rule_id,
                    status=Status.CONTRADICTION,
                    message_key=MSG_R9_CONTRADICTION_MORTGAGE_ACTIVE,
                    evidence_ids=(event.id, m.id, rel.id),
                    calculation=(
                        f"Transfer event {event.id} dated {event.event_date} occurred before "
                        f"prior mortgage {m.id} was released on {rel.event_date}."
                    ),
                    recommended_next_step=NEXT_STEP_R9,
                )

        if prior_mortgages:
            ev = [event.id]
            for m in prior_mortgages:
                ev.append(m.id)
                for r in events:
                    if r.type == EventType.MORTGAGE_RELEASE and r.linked_event_id == m.id:
                        ev.append(r.id)
            return Alert(
                rule_id=rule_id,
                status=Status.CONSISTENT,
                message_key=MSG_R9_CONSISTENT,
                evidence_ids=tuple(dict.fromkeys(ev)),
                calculation=f"All prior mortgages on parcel/portion were released before transfer event {event.id}.",
                recommended_next_step=NEXT_STEP_R9,
            )
        else:
            return Alert(
                rule_id=rule_id,
                status=Status.CONSISTENT,
                message_key=MSG_R9_CONSISTENT,
                evidence_ids=(event.id, baseline_record.id),
                calculation=f"No active unreleased mortgage found encumbering event {event.id}.",
                recommended_next_step=NEXT_STEP_R9,
            )

    # Case B: MORTGAGE
    elif event.type == EventType.MORTGAGE:
        prior_mortgages = [
            e for e in events
            if e.type == EventType.MORTGAGE
            and e.id != event.id
            and e.from_person == event.from_person
            and (e.event_date, e.seq) < (event.event_date, event.seq)
            and _portions_overlap(e.portion_id, event.portion_id)
        ]

        for m in prior_mortgages:
            releases = [
                e for e in events
                if e.type == EventType.MORTGAGE_RELEASE
                and (e.linked_event_id == m.id or (e.linked_event_id is None and _portions_overlap(e.portion_id, m.portion_id) and e.to_person == m.from_person))
            ]
            if not releases:
                return Alert(
                    rule_id=rule_id,
                    status=Status.CONTRADICTION,
                    message_key=MSG_R9_CONTRADICTION_SECOND_MORTGAGE,
                    evidence_ids=(event.id, m.id),
                    calculation=(
                        f"Second mortgage {event.id} executed on portion "
                        f"{event.portion_id or m.portion_id or 'all'} while prior mortgage {m.id} "
                        f"dated {m.event_date} remains unreleased."
                    ),
                    recommended_next_step=NEXT_STEP_R9,
                )
            rel = releases[0]
            if rel.event_date is None:
                return Alert(
                    rule_id=rule_id,
                    status=Status.REVIEW,
                    message_key=MSG_R9_REVIEW_MISSING_DATE_OR_LINK,
                    evidence_ids=(event.id, m.id, rel.id),
                    calculation=f"Release {rel.id} for prior mortgage {m.id} lacks an event date.",
                    recommended_next_step=NEXT_STEP_R9,
                )
            if rel.event_date > event.event_date:
                return Alert(
                    rule_id=rule_id,
                    status=Status.CONTRADICTION,
                    message_key=MSG_R9_CONTRADICTION_SECOND_MORTGAGE,
                    evidence_ids=(event.id, m.id, rel.id),
                    calculation=(
                        f"Second mortgage {event.id} dated {event.event_date} executed before "
                        f"prior mortgage {m.id} was released on {rel.event_date}."
                    ),
                    recommended_next_step=NEXT_STEP_R9,
                )

        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_R9_CONSISTENT,
            evidence_ids=(event.id, baseline_record.id),
            calculation=f"Mortgage {event.id} does not conflict with any unreleased prior mortgages.",
            recommended_next_step=NEXT_STEP_R9,
        )

    # Case C: MORTGAGE_RELEASE
    elif event.type == EventType.MORTGAGE_RELEASE:
        if not event.linked_event_id:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R9_REVIEW_MISSING_DATE_OR_LINK,
                evidence_ids=(event.id, baseline_record.id),
                calculation=f"Mortgage release {event.id} lacks linked_event_id reference to an established mortgage.",
                recommended_next_step=NEXT_STEP_R9,
            )
        linked_m = next((e for e in events if e.id == event.linked_event_id), None)
        if linked_m is None:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R9_REVIEW_MISSING_DATE_OR_LINK,
                evidence_ids=(event.id, baseline_record.id),
                calculation=f"Mortgage release {event.id} references linked_event_id={event.linked_event_id}, which is not found.",
                recommended_next_step=NEXT_STEP_R9,
            )
        if linked_m.type != EventType.MORTGAGE:
            return Alert(
                rule_id=rule_id,
                status=Status.CONTRADICTION,
                message_key=MSG_R9_CONTRADICTION_MORTGAGE_ACTIVE,
                evidence_ids=(event.id, linked_m.id),
                calculation=f"Mortgage release {event.id} is linked to event {linked_m.id} of type {linked_m.type.value}, not a MORTGAGE.",
                recommended_next_step=NEXT_STEP_R9,
            )
        if linked_m.event_date is not None and event.event_date < linked_m.event_date:
            return Alert(
                rule_id=rule_id,
                status=Status.CONTRADICTION,
                message_key=MSG_R9_CONTRADICTION_MORTGAGE_ACTIVE,
                evidence_ids=(event.id, linked_m.id),
                calculation=f"Mortgage release {event.id} dated {event.event_date} precedes mortgage creation date {linked_m.event_date}.",
                recommended_next_step=NEXT_STEP_R9,
            )
        prior_rel = [
            e for e in events
            if e.type == EventType.MORTGAGE_RELEASE
            and e.id != event.id
            and e.linked_event_id == linked_m.id
            and (e.event_date, e.seq) < (event.event_date, event.seq)
        ]
        if prior_rel:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R9_REVIEW_MISSING_DATE_OR_LINK,
                evidence_ids=(event.id, linked_m.id, prior_rel[0].id),
                calculation=f"Mortgage {linked_m.id} was already released by {prior_rel[0].id}; repeated release {event.id} requires review.",
                recommended_next_step=NEXT_STEP_R9,
            )
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_R9_CONSISTENT,
            evidence_ids=(event.id, linked_m.id),
            calculation=f"Mortgage release {event.id} properly releases mortgage {linked_m.id}.",
            recommended_next_step=NEXT_STEP_R9,
        )

    return Alert(
        rule_id=rule_id,
        status=Status.CONSISTENT,
        message_key=MSG_R9_CONSISTENT,
        evidence_ids=(event.id, baseline_record.id),
        calculation="Event is not an encumbering transaction.",
        recommended_next_step=NEXT_STEP_R9,
    )


# ---------------------------------------------------------------------------
# Rule R10: Power of Attorney (Phase 9)
# ---------------------------------------------------------------------------

def check_r10(
    event: Event,
    events: Sequence[Event],
    baseline_record: SurveyRecord,
    rule_id: str = "R10",
) -> Alert:
    """
    R10: Power of Attorney Authority & Revocation.
    SPEC § 4 Text R10:
      - New event types POA_GRANT and POA_REVOKE, plus optional via_poa_id on SALE/GIFT.
      - A sale by an agent needs a grant from the owner that covers the parcel
        (and the portion if scoped) and no revocation dated before the sale ->
        otherwise Contradiction Found (revoked or missing grant when all dates are present),
        Review Required when dates or scope are missing.
      - Tricky clean case: POA revoked AFTER the sale -> Consistent.
      - Replay treats these types as non-transferring.
    """
    # Case A: SALE or GIFT
    if event.type in (EventType.SALE, EventType.GIFT):
        if not event.via_poa_id:
            return Alert(
                rule_id=rule_id,
                status=Status.CONSISTENT,
                message_key=MSG_R10_CONSISTENT,
                evidence_ids=(event.id, baseline_record.id),
                calculation=f"Direct transfer by seller {event.from_person}; no Power of Attorney authority cited.",
                recommended_next_step=NEXT_STEP_R10,
            )

        if event.event_date is None:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R10_REVIEW_MISSING_DATE_OR_SCOPE,
                evidence_ids=(event.id, baseline_record.id),
                calculation=f"Sale event {event.id} under POA lacks an event date.",
                recommended_next_step=NEXT_STEP_R10,
            )

        grant = next((e for e in events if e.id == event.via_poa_id), None)
        if grant is None:
            return Alert(
                rule_id=rule_id,
                status=Status.CONTRADICTION,
                message_key=MSG_R10_CONTRADICTION_MISSING_GRANT,
                evidence_ids=(event.id, baseline_record.id),
                calculation=f"Sale event {event.id} cites via_poa_id={event.via_poa_id}, but no corresponding POA_GRANT event exists in supplied records.",
                recommended_next_step=NEXT_STEP_R10,
            )

        if grant.type != EventType.POA_GRANT:
            return Alert(
                rule_id=rule_id,
                status=Status.CONTRADICTION,
                message_key=MSG_R10_CONTRADICTION_MISSING_GRANT,
                evidence_ids=(event.id, grant.id),
                calculation=f"Event {event.via_poa_id} referenced by via_poa_id is of type {grant.type.value}, not a POA_GRANT.",
                recommended_next_step=NEXT_STEP_R10,
            )

        if grant.event_date is None:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R10_REVIEW_MISSING_DATE_OR_SCOPE,
                evidence_ids=(event.id, grant.id),
                calculation=f"POA grant {grant.id} lacks an event date.",
                recommended_next_step=NEXT_STEP_R10,
            )

        if grant.event_date > event.event_date:
            return Alert(
                rule_id=rule_id,
                status=Status.CONTRADICTION,
                message_key=MSG_R10_CONTRADICTION_REVOKED,
                evidence_ids=(event.id, grant.id),
                calculation=f"Sale event {event.id} dated {event.event_date} occurred before POA {grant.id} was granted on {grant.event_date}.",
                recommended_next_step=NEXT_STEP_R10,
            )

        # Check principal and agent identity
        if event.from_person != grant.from_person and event.from_person != grant.to_person:
            return Alert(
                rule_id=rule_id,
                status=Status.CONTRADICTION,
                message_key=MSG_R10_CONTRADICTION_MISSING_GRANT,
                evidence_ids=(event.id, grant.id),
                calculation=f"Seller {event.from_person} in event {event.id} matches neither principal {grant.from_person} nor agent {grant.to_person} in POA grant {grant.id}.",
                recommended_next_step=NEXT_STEP_R10,
            )

        # Check parcel scope
        if grant.parcel_id != event.parcel_id:
            return Alert(
                rule_id=rule_id,
                status=Status.CONTRADICTION,
                message_key=MSG_R10_CONTRADICTION_MISSING_GRANT,
                evidence_ids=(event.id, grant.id),
                calculation=f"POA grant {grant.id} covers parcel {grant.parcel_id}, but sale {event.id} is for parcel {event.parcel_id}.",
                recommended_next_step=NEXT_STEP_R10,
            )

        # Check portion scope
        if grant.portion_id is not None:
            if event.portion_id is None:
                return Alert(
                    rule_id=rule_id,
                    status=Status.REVIEW,
                    message_key=MSG_R10_REVIEW_MISSING_DATE_OR_SCOPE,
                    evidence_ids=(event.id, grant.id),
                    calculation=f"POA grant {grant.id} is scoped to portion {grant.portion_id}, but sale {event.id} does not specify a portion.",
                    recommended_next_step=NEXT_STEP_R10,
                )
            if event.portion_id != grant.portion_id:
                return Alert(
                    rule_id=rule_id,
                    status=Status.CONTRADICTION,
                    message_key=MSG_R10_CONTRADICTION_MISSING_GRANT,
                    evidence_ids=(event.id, grant.id),
                    calculation=f"POA grant {grant.id} is scoped to portion {grant.portion_id}, but sale {event.id} is for portion {event.portion_id}.",
                    recommended_next_step=NEXT_STEP_R10,
                )

        # Check revocations
        revocations = [
            e for e in events
            if e.type == EventType.POA_REVOKE
            and (e.linked_event_id == grant.id or (e.linked_event_id is None and e.from_person == grant.from_person and e.to_person == grant.to_person and e.parcel_id == grant.parcel_id))
        ]
        for rev in revocations:
            if rev.event_date is None:
                return Alert(
                    rule_id=rule_id,
                    status=Status.REVIEW,
                    message_key=MSG_R10_REVIEW_MISSING_DATE_OR_SCOPE,
                    evidence_ids=(event.id, grant.id, rev.id),
                    calculation=f"POA revocation {rev.id} lacks an event date.",
                    recommended_next_step=NEXT_STEP_R10,
                )
            if rev.event_date <= event.event_date:
                return Alert(
                    rule_id=rule_id,
                    status=Status.CONTRADICTION,
                    message_key=MSG_R10_CONTRADICTION_REVOKED,
                    evidence_ids=(event.id, grant.id, rev.id),
                    calculation=f"Sale event {event.id} dated {event.event_date} was executed after POA {grant.id} was revoked by {rev.id} on {rev.event_date}.",
                    recommended_next_step=NEXT_STEP_R10,
                )

        ev_ids = [event.id, grant.id]
        for rev in revocations:
            ev_ids.append(rev.id)
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_R10_CONSISTENT,
            evidence_ids=tuple(dict.fromkeys(ev_ids)),
            calculation=f"Sale {event.id} executed under valid, unrevoked Power of Attorney {grant.id} granted by {grant.from_person} to {grant.to_person}.",
            recommended_next_step=NEXT_STEP_R10,
        )

    # Case B: POA_REVOKE
    elif event.type == EventType.POA_REVOKE:
        if event.event_date is None:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R10_REVIEW_MISSING_DATE_OR_SCOPE,
                evidence_ids=(event.id, baseline_record.id),
                calculation=f"POA revocation {event.id} lacks an event date.",
                recommended_next_step=NEXT_STEP_R10,
            )
        if not event.linked_event_id:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R10_REVIEW_MISSING_DATE_OR_SCOPE,
                evidence_ids=(event.id, baseline_record.id),
                calculation=f"POA revocation {event.id} lacks linked_event_id.",
                recommended_next_step=NEXT_STEP_R10,
            )
        grant = next((e for e in events if e.id == event.linked_event_id), None)
        if grant is None:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R10_REVIEW_MISSING_DATE_OR_SCOPE,
                evidence_ids=(event.id, baseline_record.id),
                calculation=f"POA revocation {event.id} links to {event.linked_event_id}, which is not found.",
                recommended_next_step=NEXT_STEP_R10,
            )
        if grant.type != EventType.POA_GRANT:
            return Alert(
                rule_id=rule_id,
                status=Status.CONTRADICTION,
                message_key=MSG_R10_CONTRADICTION_MISSING_GRANT,
                evidence_ids=(event.id, grant.id),
                calculation=f"POA revocation {event.id} links to {grant.id} of type {grant.type.value}, not a POA_GRANT.",
                recommended_next_step=NEXT_STEP_R10,
            )
        if grant.event_date is not None and event.event_date < grant.event_date:
            return Alert(
                rule_id=rule_id,
                status=Status.CONTRADICTION,
                message_key=MSG_R10_CONTRADICTION_REVOKED,
                evidence_ids=(event.id, grant.id),
                calculation=f"POA revocation {event.id} dated {event.event_date} precedes POA grant {grant.id} dated {grant.event_date}.",
                recommended_next_step=NEXT_STEP_R10,
            )
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_R10_CONSISTENT,
            evidence_ids=(event.id, grant.id),
            calculation=f"POA revocation {event.id} validly revokes POA grant {grant.id}.",
            recommended_next_step=NEXT_STEP_R10,
        )

    # Case C: POA_GRANT
    elif event.type == EventType.POA_GRANT:
        if event.event_date is None:
            return Alert(
                rule_id=rule_id,
                status=Status.REVIEW,
                message_key=MSG_R10_REVIEW_MISSING_DATE_OR_SCOPE,
                evidence_ids=(event.id, baseline_record.id),
                calculation=f"POA grant {event.id} lacks an event date.",
                recommended_next_step=NEXT_STEP_R10,
            )
        return Alert(
            rule_id=rule_id,
            status=Status.CONSISTENT,
            message_key=MSG_R10_CONSISTENT,
            evidence_ids=(event.id, baseline_record.id),
            calculation=f"POA grant {event.id} recorded.",
            recommended_next_step=NEXT_STEP_R10,
        )

    return Alert(
        rule_id=rule_id,
        status=Status.CONSISTENT,
        message_key=MSG_R10_CONSISTENT,
        evidence_ids=(event.id, baseline_record.id),
        calculation="Event is not a Power of Attorney transaction.",
        recommended_next_step=NEXT_STEP_R10,
    )


# ---------------------------------------------------------------------------
# Shared Rule Dispatchers (Phase 6 Foundation)
# ---------------------------------------------------------------------------

def dispatch_event_rules(
    event: Event,
    parcel_history: ParcelHistory,
    events: Sequence[Event],
    baseline_record: SurveyRecord,
    deeds_by_id: Optional[dict[str, Deed]] = None,
    child_survey_records: Sequence[SurveyRecord] = (),
    all_events: Sequence[Event] = (),
    all_deeds: Sequence[Deed] = (),
    parcel: Optional[Parcel] = None,
) -> list[Alert]:
    """
    Evaluate all applicable rules for a single trigger event in deterministic order.
    Shared dispatch path used by evaluate(), evaluate_history(), and simulate().

    Order:
      SALE / GIFT:
        1. R3: Seller's recorded interest
        2. R1: Excess transfer (evaluates share if seller is recorded)
        3. R2: Duplicate allocation (if portion_id or linked_event_id present)
        4. R15: Duplicate physical portion by structured boundary (if boundary or portion present)
        5. R12: Deed content integrity (if deed has recorded content_hash)
        6. R13: Deed number reuse (if all_events and all_deeds provided)
        7. R11: Government and court locks (if parcel provided)
        8. R9: Active mortgage encumbrance (if mortgage events exist in history)
        9. R10: Power of attorney (if via_poa_id or POA events exist in history)
      MORTGAGE / MORTGAGE_RELEASE:
        1. R9: Mortgage encumbrance and release validation
      POA_GRANT / POA_REVOKE:
        1. R10: Power of attorney authority & revocation validation
      SUBDIVIDE:
        1. R4: Subdivision reconciliation
      MUTATION:
        1. R6: Deed-mutation reconciliation
        2. R7: Chronological consistency
    """
    alerts: list[Alert] = []

    if event.type in (EventType.SALE, EventType.GIFT):
        alerts.append(run_rule(check_r3, event, parcel_history, events))
        alerts.append(run_rule(check_r1, event, parcel_history, events))
        if event.portion_id or event.linked_event_id:
            alerts.append(run_rule(check_r2, event, events, baseline_record))

        if event.boundary is not None or event.portion is not None:
            alerts.append(run_rule(check_r15, event, events, baseline_record))

        if deeds_by_id and event.deed_id:
            deed = deeds_by_id.get(event.deed_id)
            if deed and deed.content_hash is not None:
                alerts.append(run_rule(check_r12, deed, event))
            if deed and all_events and all_deeds:
                alerts.append(run_rule(check_r13, deed, event, all_events, all_deeds))

        # Phase 9: R11 Government & Court Locks
        if parcel is not None:
            alerts.append(run_rule(check_r11, event, parcel, baseline_record))

        # Phase 9: R9 Active Mortgage
        if any(e.type in (EventType.MORTGAGE, EventType.MORTGAGE_RELEASE) for e in events):
            alerts.append(run_rule(check_r9, event, events, baseline_record))

        # Phase 9: R10 Power of Attorney
        if event.via_poa_id or any(e.type in (EventType.POA_GRANT, EventType.POA_REVOKE) for e in events):
            alerts.append(run_rule(check_r10, event, events, baseline_record))

    elif event.type in (EventType.MORTGAGE, EventType.MORTGAGE_RELEASE):
        alerts.append(run_rule(check_r9, event, events, baseline_record))

    elif event.type in (EventType.POA_GRANT, EventType.POA_REVOKE):
        alerts.append(run_rule(check_r10, event, events, baseline_record))

    elif event.type == EventType.SUBDIVIDE:
        if not child_survey_records:
            # Fallback for simulate: find child records in parcel_history.survey_records
            child_survey_records = [
                sr for sr in parcel_history.survey_records
                if sr.parcel_id != event.parcel_id
            ]
        alerts.append(run_rule(check_r4, event, child_survey_records, events, baseline_record))

    elif event.type == EventType.MUTATION:
        deed = deeds_by_id.get(event.deed_id) if deeds_by_id and event.deed_id else None
        alerts.append(run_rule(check_r6, event, deed, events, baseline_record))
        alerts.append(run_rule(check_r7, event, deed, events, baseline_record))

    return alerts


def dispatch_history_rules(
    history: ParcelHistory,
    all_parcels: Sequence[Any] = (),
    all_deeds: Sequence[Deed] = (),
    all_histories: Sequence[ParcelHistory] = (),
    all_persons: Sequence[Person] = (),
) -> list[Alert]:
    """
    Evaluate all applicable rules across the complete history of one parcel.
    Shared dispatch path used by evaluate_history() and API endpoints.
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
    all_events_across = [e for h in all_histories for e in h.events] if all_histories else list(history.events)
    parcel = next((p for p in all_parcels if getattr(p, "id", None) == history.parcel_id), None)

    # Evaluate event rules via shared dispatch_event_rules
    for event in history.events:
        child_srs: list[SurveyRecord] = []
        if event.type == EventType.SUBDIVIDE:
            child_parcel_ids = {p.id for p in all_parcels if getattr(p, "parent_id", None) == history.parcel_id}
            for h in all_histories:
                if h.parcel_id in child_parcel_ids:
                    child_srs.extend(h.survey_records)

        alerts.extend(
            dispatch_event_rules(
                event=event,
                parcel_history=history,
                events=history.events,
                baseline_record=baseline,
                deeds_by_id=deeds_by_id,
                child_survey_records=child_srs,
                all_events=all_events_across,
                all_deeds=all_deeds,
                parcel=parcel,
            )
        )

    # Evaluate survey continuity (R5) between successive survey records
    if len(history.survey_records) > 1:
        sorted_srs = sorted(history.survey_records, key=lambda sr: sr.record_date)
        for i in range(len(sorted_srs) - 1):
            earlier = sorted_srs[i]
            later = sorted_srs[i + 1]
            linking = [
                e for e in history.events
                if e.event_date is not None
                and earlier.record_date <= e.event_date <= later.record_date
            ]
            alerts.append(run_rule(check_r5, earlier, later, linking, history.events))

    # Evaluate person disambiguation (R14) if person records provided
    if all_persons:
        alerts.append(run_rule(check_r14, history, all_persons))

    # Phase 10: Evaluate unaccounted heir declaration consistency (R8)
    if history.heir_declaration:
        alerts.append(run_rule(check_r8, history, history.events, all_deeds, baseline))

    return alerts


