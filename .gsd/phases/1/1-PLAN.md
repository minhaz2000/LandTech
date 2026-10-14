---
phase: 1
plan: 1
wave: 1
title: Data Models and Event Replay
---

# Plan 1.1: Data Models and Event Replay

## Objective
Define every dataclass from SPEC.md exactly as specified and implement
the chronological event replay function that computes holder state from
a list of events. This is the foundation every rule and test depends on.
No rule logic is written here — only the structures and the replay engine.

## Context
- .gsd/SPEC.md  (§ Data Model, § Evaluation Order, § Hard Constraints)
- src/jomigraph/models.py   (to create)
- src/jomigraph/engine/replay.py   (to create)

## Files Created This Plan
| Path | Purpose |
|------|---------|
| `src/__init__.py` | package marker |
| `src/jomigraph/__init__.py` | package marker |
| `src/jomigraph/models.py` | all dataclasses |
| `src/jomigraph/engine/__init__.py` | package marker |
| `src/jomigraph/engine/replay.py` | chronological replay + state computer |
| `tests/__init__.py` | package marker |
| `tests/test_models.py` | smoke tests for model construction |

## Tasks

<task type="auto">
  <name>Write models.py — all SPEC dataclasses</name>
  <files>src/jomigraph/models.py</files>
  <action>
    Implement these dataclasses exactly as named and typed in SPEC.md
    § Data Model. Use Python 3.11 dataclasses (@dataclass, frozen=True
    where immutability makes sense). Use fractions.Fraction for every
    area and share field — no float anywhere.

    Classes to implement (field names must match SPEC exactly):

      @dataclass
      class Person:
          id: str
          name: str

      @dataclass
      class Parcel:
          id: str
          dag_no: str
          mouza: str
          parent_id: Optional[str]   # None for root parcels

      @dataclass
      class SurveyRecord:
          id: str
          parcel_id: str
          survey: str                # CS | SA | RS | BRS | BS
          khatian_no: str
          record_date: date
          recorded_area: Fraction    # SPEC: fractions.Fraction for ALL area
          holders: tuple[tuple[str, Fraction], ...]   # (person_id, area)

      class EventType(str, Enum):
          SALE = "SALE"
          GIFT = "GIFT"
          SUBDIVIDE = "SUBDIVIDE"
          MUTATION = "MUTATION"
          CANCEL = "CANCEL"
          CORRECT = "CORRECT"

      @dataclass
      class Deed:
          id: str
          deed_no: str
          registration_date: date

      @dataclass
      class Event:
          id: str
          type: EventType
          event_date: Optional[date]    # may be None (triggers Review Required)
          parcel_id: str
          from_person: Optional[str]
          to_person: Optional[str]
          area: Optional[Fraction]
          deed_id: Optional[str]
          portion_id: Optional[str]
          linked_event_id: Optional[str]
          source_record_id: Optional[str]

      @dataclass
      class ParcelHistory:
          parcel_id: str
          baseline_record_id: str
          baseline_complete: bool       # author-declared, explicit assumption
          start_record_id: str
          end_date: Optional[date]
          survey_records: tuple[SurveyRecord, ...]
          events: tuple[Event, ...]

    Constraints:
    - NO float types anywhere.
    - Do NOT add fields not in SPEC. Do not merge or rename fields.
    - All Fraction fields must import from fractions.Fraction.
    - Optional fields use Optional[T], not T | None (compatibility).
  </action>
  <verify>python -c "from jomigraph.models import Person, Parcel, SurveyRecord, Deed, Event, EventType, ParcelHistory; from fractions import Fraction; e = Event(id='E1', type=EventType.SALE, event_date=None, parcel_id='P1', from_person='H1', to_person='H2', area=Fraction(7,1), deed_id=None, portion_id=None, linked_event_id=None, source_record_id=None); print('models ok', e.area)"</verify>
  <done>
    - All seven classes/enums importable from jomigraph.models.
    - Fraction('7') and Fraction(7) accepted without error in area fields.
    - event_date=None accepted without error.
    - No float literals anywhere in the file (grep -n "0\." models.py returns empty).
  </done>
</task>

<task type="auto">
  <name>Write replay.py — chronological state computer</name>
  <files>src/jomigraph/engine/replay.py</files>
  <action>
    Implement compute_state(events, survey_records) -> HolderState.

    HolderState is a dict[str, Fraction] mapping person_id -> available area.

    Algorithm (SPEC § Data Model: "State is always computed by replaying
    events in chronological order on top of the baseline survey record.
    Event dates and record publication dates are separate fields."):

      1. Initialise holder_area from the baseline SurveyRecord holders.
      2. Sort events by event_date ascending. Events with event_date=None
         are NOT replayed — they are skipped by the replay function. The
         rule layer (R1, R7) detects the missing date and returns
         Review Required before ever calling replay.
      3. For each Event in sorted order:
         - SALE / GIFT: subtract area from from_person, add to to_person.
           Fractions only.
         - SUBDIVIDE: subtract area from parent holder; child parcel area
           added by a separate SurveyRecord (handled at rule layer).
         - CANCEL: reverse the linked_event_id effect. Subtract from the
           beneficiary, restore to the originator. The cancelled event
           must be in the supplied event list; if not found, skip (caller
           checks).
         - CORRECT: replace from_person share with the corrected area value
           (area field). Old share is subtracted, new share added.
         - MUTATION: state change recorded; area does not change in replay
           (deed-mutation reconciliation is R6/R7, not replay).
      4. Return the final HolderState dict.

    Also implement get_available_area(holder_state, person_id) -> Fraction
    returning Fraction(0) if person not present.

    Also implement replay_up_to(events, survey_records, cutoff_date) ->
    HolderState that replays only events with event_date <= cutoff_date
    (for point-in-time queries).

    Constraints:
    - All arithmetic uses Fraction. No float, no round().
    - Events with event_date=None are skipped silently; the rule layer
      enforces the missing-date check before calling replay.
    - No side effects; replay is a pure function.
  </action>
  <verify>
    python -c "
from fractions import Fraction
from datetime import date
from jomigraph.models import *
from jomigraph.engine.replay import compute_state, get_available_area
sr = SurveyRecord(id='SR1', parcel_id='P1', survey='BS', khatian_no='K1',
    record_date=date(1980,1,1), recorded_area=Fraction(10),
    holders=(('H1', Fraction(10)),))
e1 = Event(id='E1', type=EventType.SALE, event_date=date(2000,1,1),
    parcel_id='P1', from_person='H1', to_person='H2', area=Fraction(7),
    deed_id=None, portion_id=None, linked_event_id=None, source_record_id=None)
state = compute_state([e1], [sr])
assert get_available_area(state, 'H1') == Fraction(3), state
assert get_available_area(state, 'H2') == Fraction(7), state
print('replay ok')
"
  </verify>
  <done>
    - compute_state([7-decimal transfer]) returns H1=3, H2=7.
    - A CANCEL event restores the transferred area to the originator.
    - replay_up_to with a past cutoff returns state before the event.
    - No float in file (grep -n "0\." replay.py returns empty for numeric literals).
  </done>
</task>

## Success Criteria
- [ ] All seven model classes importable, all Fraction fields verified.
- [ ] compute_state passes the verify command above.
- [ ] CANCEL reversal verified by unit assertion.
- [ ] replay_up_to verified by unit assertion.
- [ ] grep for float literals in models.py and replay.py returns zero hits.
