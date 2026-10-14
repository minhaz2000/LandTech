"""
JomiGraph AI — Data Models
==========================
All area and share fields use fractions.Fraction.  Floats are rejected at
the boundary by load_fraction().  No float literal appears in this file.

MODELING NOTE (SPEC § Modeling Assumption):
    Each survey record is a time-specific claim about a parcel, not automatic
    proof of current ownership.  Nothing here stores "current owner"; state is
    always computed by replaying events in chronological order.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from fractions import Fraction
from typing import Optional


# ---------------------------------------------------------------------------
# Boundary helper
# ---------------------------------------------------------------------------

def load_fraction(value) -> Fraction:
    """
    Parse *value* into a Fraction.

    Raises TypeError if *value* is a float.  Floats are rejected because
    IEEE-754 precision loss can corrupt exact-arithmetic land-area calculations.
    Accepted types: int, str (e.g. "7", "7/2", "3.5"), Fraction.
    """
    if isinstance(value, float):
        raise TypeError(
            "float values are not permitted in area/share fields — "
            f"pass int, str, or Fraction instead.  Got: {value!r}"
        )
    return Fraction(value)


# ---------------------------------------------------------------------------
# Core entities
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Person:
    id: str
    name: str


@dataclass(frozen=True)
class Parcel:
    id: str
    dag_no: str
    mouza: str
    parent_id: Optional[str] = None   # None for root parcels


@dataclass(frozen=True)
class SurveyRecord:
    """
    A time-specific claim about a parcel (CS, SA, RS, BRS, BS).
    Not automatic proof of current ownership.

    holders: tuple of (person_id: str, area: Fraction) pairs.
             All area values must be Fraction — never float.
    """
    id: str
    parcel_id: str
    survey: str           # CS | SA | RS | BRS | BS
    khatian_no: str
    record_date: date
    recorded_area: Fraction
    holders: tuple[tuple[str, Fraction], ...]


class EventType(str, Enum):
    SALE      = "SALE"
    GIFT      = "GIFT"
    SUBDIVIDE = "SUBDIVIDE"
    MUTATION  = "MUTATION"
    CANCEL    = "CANCEL"
    CORRECT   = "CORRECT"


@dataclass(frozen=True)
class Deed:
    id: str
    deed_no: str
    registration_date: date


@dataclass(frozen=True)
class Event:
    """
    A recorded land-transaction event.

    seq : int
        Explicit integer sequence number, assigned at dataset creation time
        (use a monotonically increasing counter, zero-padded in string IDs if
        needed).  The replay sort key is (event_date, seq) — deterministic
        regardless of event ID format or string comparison order.

    event_date : Optional[date]
        None means the date is unknown.  The rule layer must call
        has_undated_events() and return Review Required for the whole
        parcel history if any event lacks a date.  Replay skips undated
        events but does not surface this ambiguity itself.

    from_person : Optional[str]
        SALE / GIFT:    the transferring holder.
        SUBDIVIDE:      the holder on the parent parcel whose share is reduced.
        CORRECT:        the holder whose share is being corrected.
                        to_person is unused for CORRECT and should be None.
        CANCEL:         unused (effect is determined from the linked event).

    source_record_id : Optional[str]
        Required for CORRECT events.  If None, dependent rules return
        Review Required — a correction without documented evidence is
        ambiguous.
    """
    id: str
    type: EventType
    seq: int                      # explicit integer for deterministic tie-break
    event_date: Optional[date]    # None → Review Required in rule layer
    parcel_id: str
    from_person: Optional[str]
    to_person: Optional[str]      # unused (and ignored) for CORRECT events
    area: Optional[Fraction]
    deed_id: Optional[str]
    portion_id: Optional[str]
    linked_event_id: Optional[str]   # CANCEL: event being reversed
    source_record_id: Optional[str]  # CORRECT: required documentary evidence


@dataclass(frozen=True)
class ParcelHistory:
    """
    The declared history of one parcel.

    baseline_complete : bool
        Author-declared assumption that the supplied event history covers
        the interval from start_record_id through the event being evaluated.
        This is an EXPLICIT COMPLETENESS ASSUMPTION, not proof of completeness.

        Evaluation order (SPEC § Evaluation Order):
          1. Check required inputs first; if missing/ambiguous → Review Required.
          2. Only then apply baseline_complete and the rule logic.
        baseline_complete must NEVER override a missing or ambiguous input.
    """
    parcel_id: str
    baseline_record_id: str
    baseline_complete: bool
    start_record_id: str
    end_date: Optional[date]
    survey_records: tuple[SurveyRecord, ...]
    events: tuple[Event, ...]
