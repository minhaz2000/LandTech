"""
REPLAY SEMANTICS
================
compute_state(events, baseline_survey_record) -> (HolderState, issues)

HolderState = dict[str, Fraction]
    person_id -> current area.  Values MAY be negative; replay does NOT clamp.
    A negative value is meaningful evidence of over-allocation in the supplied
    history and must not be hidden by clamping.

issues : list[str]
    Validation errors found during replay (invalid CANCEL, CORRECT without
    source_record_id, etc.).  The RULE LAYER must treat any non-empty issues
    list as grounds to return Review Required before applying rule logic.

PRE-CONDITION (rule layer responsibility, NOT replay's):
    If ANY event in the evaluated parcel's history has event_date=None,
    EVERY rule that depends on that history MUST return Review Required before
    calling compute_state.  Use has_undated_events() for this check.
    Replay skips undated events internally but does NOT signal this ambiguity —
    the rule layer owns that responsibility.

SORT ORDER:
    Dated events are sorted by (event_date, seq).  seq is an explicit int
    field on Event, assigned at dataset creation time (monotonically increasing
    integer, NOT raw string comparison).  This guarantees a stable, deterministic
    order independent of event ID format.  Undated events are excluded before
    sorting.

PER-PARCEL STATE:
    compute_state operates on ONE parcel (the parcel of baseline_survey_record).
    Each parcel has its own independent HolderState.
    SUBDIVIDE reduces the parent parcel's state only.
    The child parcel's HolderState is initialised from the child's own
    SurveyRecord in a separate compute_state call.
    R4 locates child parcels via Parcel.parent_id.
    Sales on a child parcel are evaluated against the child's own HolderState,
    not the parent's remaining share.

NEGATIVE SHARES:
    Replay does NOT clamp.  R1 evaluates the trigger event against the state
    produced by replay_up_to() with the trigger excluded, using the same
    (event_date, seq) sort order as full replay.  "Available area before the
    trigger" is therefore unambiguous.

EVENT SEMANTICS:

SALE / GIFT
    Subtract event.area from holder_state[from_person].
    Add    event.area to   holder_state[to_person].
    If from_person or to_person is None: skip; rule layer checks.

SUBDIVIDE
    Subtract event.area from holder_state[from_person] on the parent parcel.
    Child parcel state is not modified here (see PER-PARCEL STATE above).

MUTATION
    Does not alter holder_state.  Records a register change only.
    Reconciliation is handled by R6 and R7.

CANCEL -- validation before application (failure adds to issues; NOT silent):
    (a) linked_event_id must resolve to a known event in the supplied list.
    (b) The linked event must be of type SALE or GIFT.
    (c) No other CANCEL in this history may already reference the same
        linked_event_id.  Double-cancel is rejected and flagged distinctly.
    (d) The linked event's event_date must be <= the CANCEL event's event_date
        (cannot cancel a future event).
    If valid: add linked_event.area back to linked_event.from_person;
              subtract linked_event.area from linked_event.to_person.

    ANCHORS (minimal-evidence algorithm, evaluated parcel only):
        The CANCEL event itself is an anchor.
        Its linked event (the cancelled SALE/GIFT) is also an anchor.
        Anchors are never deletion candidates in minimal_evidence().

CORRECT
    from_person identifies the holder being corrected (NOT a transfer).
    to_person is unused for CORRECT and is ignored even if present.
    Validation: source_record_id must be non-None.  If missing, an error
    is added to issues and the event is skipped.  A correction without
    documented evidence is ambiguous; dependent rules return Review Required.
    If valid: holder_state[from_person] = event.area  (replaces old share).

    ANCHORS: CORRECT events on the evaluated parcel are anchors.
"""

from __future__ import annotations

from datetime import date
from fractions import Fraction
from typing import Optional, Sequence

from jomigraph.models import Event, EventType, SurveyRecord

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

# HolderState maps person_id -> area.  Values may be negative; never clamped.
HolderState = dict[str, Fraction]


# ---------------------------------------------------------------------------
# Public utility functions
# ---------------------------------------------------------------------------

def has_undated_events(events: Sequence[Event]) -> bool:
    """
    Return True if any event in the sequence has event_date=None.

    Rule layer MUST call this before any rule logic.  If True, the rule
    must return Review Required for the whole parcel history.
    """
    return any(e.event_date is None for e in events)


def get_available_area(state: HolderState, person_id: str) -> Fraction:
    """Return the holder's area, or Fraction(0) if not present in state."""
    return state.get(person_id, Fraction(0))


def anchor_ids_for_parcel(events: Sequence[Event], parcel_id: str) -> frozenset[str]:
    """
    Return the set of event IDs that are anchors for the given parcel.

    Anchors are never deletion candidates in minimal_evidence():
      - CANCEL events on the parcel (and their linked events).
      - CORRECT events on the parcel.

    Baseline SurveyRecord IDs are passed separately by the caller.
    """
    anchors: set[str] = set()
    for e in events:
        if e.parcel_id != parcel_id:
            continue
        if e.type == EventType.CANCEL:
            anchors.add(e.id)
            if e.linked_event_id:
                anchors.add(e.linked_event_id)
        elif e.type == EventType.CORRECT:
            anchors.add(e.id)
    return frozenset(anchors)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sort_key(event: Event) -> tuple[date, int]:
    """
    Deterministic sort key: (event_date, seq).

    seq is an explicit integer — stable regardless of event ID format.
    Only call this on events where event_date is not None.
    """
    return (event.event_date, event.seq)  # type: ignore[return-value]


def _validate_cancel(
    cancel_event: Event,
    events_by_id: dict[str, Event],
    cancelled_event_ids: set[str],
) -> Optional[str]:
    """
    Validate a CANCEL event against conditions (a)-(d).

    Returns an error string if invalid, None if valid.
    Errors are non-silent: callers append them to issues so the rule layer
    can detect them and return Review Required.
    """
    lid = cancel_event.linked_event_id

    # (a) linked event must exist in supplied list
    if lid is None or lid not in events_by_id:
        return (
            f"CANCEL {cancel_event.id!r}: linked_event_id {lid!r} not found "
            f"in supplied history — dependent rules return Review Required."
        )

    linked = events_by_id[lid]

    # (b) linked event must be SALE or GIFT
    if linked.type not in (EventType.SALE, EventType.GIFT):
        return (
            f"CANCEL {cancel_event.id!r}: linked event {lid!r} has type "
            f"{linked.type.value!r}; only SALE or GIFT may be cancelled."
        )

    # (c) double-cancel: no other CANCEL already cancelled this linked_event_id
    if lid in cancelled_event_ids:
        return (
            f"CANCEL {cancel_event.id!r}: event {lid!r} is already cancelled. "
            f"Double-cancel rejected and flagged."
        )

    # (d) linked event must not be dated after the CANCEL
    if (
        linked.event_date is not None
        and cancel_event.event_date is not None
        and linked.event_date > cancel_event.event_date
    ):
        return (
            f"CANCEL {cancel_event.id!r}: linked event {lid!r} is dated "
            f"{linked.event_date} which is after the cancel date "
            f"{cancel_event.event_date}."
        )

    return None  # valid


# ---------------------------------------------------------------------------
# Core replay engine
# ---------------------------------------------------------------------------

def compute_state(
    events: Sequence[Event],
    baseline_survey_record: SurveyRecord,
) -> tuple[HolderState, list[str]]:
    """
    Compute holder state for one parcel by replaying events chronologically.

    Returns (holder_state, validation_issues).

    The rule layer must check len(validation_issues) > 0 and return
    Review Required before applying rule logic if any issues are present.

    Does NOT clamp negative values (see module docstring).
    """
    issues: list[str] = []
    cancelled_event_ids: set[str] = set()

    # Initialise state from baseline survey record
    state: HolderState = {}
    for person_id, area in baseline_survey_record.holders:
        state[person_id] = Fraction(area)

    # Index all events by id for O(1) CANCEL resolution
    events_by_id: dict[str, Event] = {e.id: e for e in events}

    # Exclude undated events from replay (rule layer owns that pre-check)
    dated = [e for e in events if e.event_date is not None]
    dated.sort(key=_sort_key)

    for event in dated:

        if event.type in (EventType.SALE, EventType.GIFT, EventType.RELEASE):
            if event.from_person is None or event.to_person is None or event.area is None:
                # Incomplete event — rule layer will detect missing fields
                continue
            state[event.from_person] = state.get(event.from_person, Fraction(0)) - event.area
            state[event.to_person]   = state.get(event.to_person,   Fraction(0)) + event.area

        elif event.type == EventType.SUBDIVIDE:
            if event.from_person is None or event.area is None:
                continue
            state[event.from_person] = state.get(event.from_person, Fraction(0)) - event.area

        elif event.type == EventType.MUTATION:
            pass  # no state change; reconciliation is R6/R7

        elif event.type in (
            EventType.MORTGAGE,
            EventType.MORTGAGE_RELEASE,
            EventType.POA_GRANT,
            EventType.POA_REVOKE,
        ):
            pass  # non-transferring encumbrance/authorization events; no state change

        elif event.type == EventType.CANCEL:
            err = _validate_cancel(event, events_by_id, cancelled_event_ids)
            if err:
                issues.append(err)
                continue  # skip invalid CANCEL; issue recorded for rule layer
            cancelled_event_ids.add(event.linked_event_id)  # type: ignore[arg-type]
            linked = events_by_id[event.linked_event_id]  # type: ignore[index]
            area = linked.area if linked.area is not None else Fraction(0)
            if linked.from_person:
                state[linked.from_person] = state.get(linked.from_person, Fraction(0)) + area
            if linked.to_person:
                state[linked.to_person]   = state.get(linked.to_person,   Fraction(0)) - area

        elif event.type == EventType.CORRECT:
            if event.source_record_id is None:
                issues.append(
                    f"CORRECT {event.id!r}: source_record_id is required but missing. "
                    f"Dependent rules will return Review Required."
                )
                continue
            if event.from_person is None or event.area is None:
                continue
            # Replace the holder's share entirely.
            # from_person = the holder being corrected; to_person unused.
            state[event.from_person] = Fraction(event.area)

    return state, issues


def replay_up_to(
    events: Sequence[Event],
    baseline_survey_record: SurveyRecord,
    cutoff_date: date,
    cutoff_seq: int,
    exclude_event_id: Optional[str] = None,
) -> tuple[HolderState, list[str]]:
    """
    Compute holder state for events that come BEFORE (cutoff_date, cutoff_seq)
    in sort order, optionally excluding one specific event by ID.

    Used by R1 to get the state immediately before the trigger event:
        replay_up_to(events, baseline,
                     cutoff_date=trigger.event_date,
                     cutoff_seq=trigger.seq,
                     exclude_event_id=trigger.id)

    The comparison is strict (<), so events at exactly (cutoff_date, cutoff_seq)
    are excluded — this matches the trigger-event position in the sorted order.
    """
    filtered = [
        e for e in events
        if e.event_date is not None
        and e.id != exclude_event_id
        and (e.event_date, e.seq) < (cutoff_date, cutoff_seq)
    ]
    return compute_state(filtered, baseline_survey_record)
