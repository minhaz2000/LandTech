---
phase: 1
plan: 2
wave: 1
title: Rules R1, R2, R3 and Alert Structure
depends_on: "1-PLAN.md"
---

# Plan 1.2: Rules R1, R2, R3 and Alert Structure

## Objective
Implement the Alert dataclass (with recommended_next_step and
impact_event_ids) and rules R1, R2, R3 with exact SPEC wording for
evaluation order: missing-inputs check first, baseline_complete second.
Covers tests 1, 2, 3, 4, 5, 6.

## Context
- .gsd/SPEC.md  (§ Rules, § Evaluation Order, § Minimal Evidence, § Additions)
- src/jomigraph/models.py   (from Plan 1.1)
- src/jomigraph/engine/replay.py   (from Plan 1.1)
- src/jomigraph/engine/rules.py   (to create)
- src/jomigraph/i18n.py   (to create — stub keys only)
- tests/test_rules_r1_r2_r3.py   (to create)

## Files Created This Plan
| Path | Purpose |
|------|---------|
| `src/jomigraph/engine/rules.py` | Alert dataclass + R1, R2, R3 |
| `src/jomigraph/i18n.py` | key constants + stub resolver |
| `tests/test_rules_r1_r2_r3.py` | required tests 1–6 |

## Tasks

<task type="auto">
  <name>Write Alert dataclass and i18n stub</name>
  <files>src/jomigraph/engine/rules.py, src/jomigraph/i18n.py</files>
  <action>
    --- i18n.py ---
    Create a module-level dict NEXT_STEP_KEYS mapping rule_id strings
    ("R1"..."R7") to a dict {"bn": str, "en": str} containing
    recommended next-step text keys (not final UI strings — those come
    in Phase 4 JSON files). For Phase 1 these are placeholder strings
    that clearly name the right verification action per rule, e.g.:

      "R1": {
        "bn": "বিক্রেতার পূর্ববর্তী দলিল ও রেকর্ড যাচাই করুন",
        "en": "Verify seller prior deeds and earlier transfer records"
      }
      "R2": {
        "bn": "পোর্শন আইডি এবং বংশলতিকা লিঙ্ক যাচাই করুন",
        "en": "Verify portion_id lineage link and supporting documents"
      }
      "R3": {
        "bn": "বিক্রেতার রেকর্ডকৃত স্বার্থ এবং পরবর্তী সংশোধনী যাচাই করুন",
        "en": "Verify seller recorded interest and any later corrections or cancellations"
      }
      "R4": {
        "bn": "উপ-বিভাগ রেকর্ড এবং মোট জমির পরিমাণ যাচাই করুন",
        "en": "Check subdivision records and total area reconciliation"
      }
      "R5": {
        "bn": "পরপর সার্ভে রেকর্ডের মধ্যে সংযোগ দলিল যাচাই করুন",
        "en": "Verify documented link between successive survey records"
      }
      "R6": {
        "bn": "দলিল ও মিউটেশন তথ্য পুনরায় মিলিয়ে নিন",
        "en": "Reconcile deed and mutation information"
      }
      "R7": {
        "bn": "দলিল নিবন্ধন তারিখ এবং মিউটেশন তারিখ যাচাই করুন",
        "en": "Verify deed registration date and mutation date order"
      }

    --- Alert dataclass (in rules.py) ---
    SPEC § Additions: "Every alert includes a recommended_next_step."
    SPEC § Minimal Evidence: "Each rule returns the event and record IDs
    used to establish its result."
    SPEC Impact view: "list later events that depend on the conflicting event."

    @dataclass(frozen=True)
    class Status(str, Enum):
        CONSISTENT   = "Consistent with supplied records"
        CONTRADICTION = "Contradiction Found"
        REVIEW        = "Review Required"

    @dataclass(frozen=True)
    class Alert:
        rule_id: str                         # e.g. "R1"
        status: Status
        message_key: str                     # key into translation JSON
        evidence_ids: tuple[str, ...]        # event/record IDs used
        calculation: str                     # human-readable arithmetic
        recommended_next_step: dict          # {"bn": ..., "en": ...}
        impact_event_ids: tuple[str, ...]    # downstream events (may be empty)

    Note: SPEC test 14 requires "every alert includes rule_id and
    non-empty evidence_ids". Enforce in run_rule() wrapper (see next task).
  </action>
  <verify>
    python -c "
from jomigraph.engine.rules import Alert, Status
from jomigraph.i18n import NEXT_STEP_KEYS
a = Alert(rule_id='R1', status=Status.CONTRADICTION,
    message_key='r1.excess', evidence_ids=('E1','E2'),
    calculation='requested 5, available 3, excess 2',
    recommended_next_step=NEXT_STEP_KEYS['R1'],
    impact_event_ids=())
assert a.evidence_ids == ('E1','E2')
assert 'bn' in a.recommended_next_step
assert 'en' in a.recommended_next_step
print('Alert ok')
"
  </verify>
  <done>
    - Alert importable; frozen dataclass.
    - All seven rules have NEXT_STEP_KEYS entries with bn and en keys.
    - Status enum has exactly three members matching SPEC verbatim.
  </done>
</task>

<task type="auto">
  <name>Implement R1, R2, R3 with evaluation order from SPEC</name>
  <files>src/jomigraph/engine/rules.py, tests/test_rules_r1_r2_r3.py</files>
  <action>
    Implement three rule functions. Each follows SPEC § Evaluation Order:
      Step 1 — Check required inputs; if missing/ambiguous return Review Required.
      Step 2 — Apply baseline_complete and the rule logic.
    baseline_complete must NEVER override a missing or ambiguous input.

    --- R1 (SPEC wording exactly) ---
    "If baseline_complete is true for the relevant interval and a transfer
    exceeds the seller's modeled available share at the event date, return
    Contradiction Found. Otherwise return Review Required."

    def check_r1(event, parcel_history, all_events) -> Alert:
      Step 1: If event.event_date is None -> Review Required.
              If event.from_person is None -> Review Required.
              If event.area is None -> Review Required.
      Step 2: Replay all_events up to event.event_date (exclusive of this
              event) to get available area. Use replay.replay_up_to().
              available = get_available_area(state, event.from_person)
              excess = event.area - available
              If parcel_history.baseline_complete is True:
                If excess > Fraction(0): return Contradiction Found.
                  calculation = f"requested {event.area}, available {available}, excess {excess}"
                Else: return Consistent.
              Else: return Review Required.
      evidence_ids = (event.id,) + tuple of any CANCEL/CORRECT event IDs
                     that affected from_person's share.

    --- R2 (SPEC wording exactly) ---
    "Incompatible transfers allocate the same identified portion.
    Contradiction Found if overlap is established through portion_id and
    lineage; otherwise Review Required. Never match on dag number or deed
    number alone."

    def check_r2(event, all_events) -> Alert:
      Step 1: If event.portion_id is None -> Review Required.
              If event.linked_event_id is None -> Review Required.
      Step 2: Collect all events where portion_id == event.portion_id
              AND type in {SALE, GIFT} AND id != event.id.
              If any such event exists -> Contradiction Found.
              Else -> Review Required (cannot establish overlap).
      evidence_ids = (event.id,) + tuple of conflicting event IDs.
      IMPORTANT: do NOT look at deed_id or dag_no to establish duplication.

    --- R3 (SPEC wording exactly) ---
    "If baseline_complete is true for the relevant interval and complete
    supplied evidence disproves the seller's modeled interest at the event
    date, return Contradiction Found. If the interest cannot be established
    because evidence is missing or ambiguous, return Review Required."

    def check_r3(event, parcel_history, all_events) -> Alert:
      Step 1: If event.event_date is None -> Review Required.
              If event.from_person is None -> Review Required.
              If event.source_record_id is None -> Review Required.
      Step 2: Replay to get available. If baseline_complete is True:
              If available == Fraction(0) and event.area > Fraction(0):
                return Contradiction Found.
              Else return Consistent.
              Else return Review Required.

    --- run_rule() wrapper ---
    All three rule functions are called through:
      run_rule(fn, *args) -> Alert
    which asserts alert.rule_id is set and len(alert.evidence_ids) > 0
    before returning, raising AssertionError otherwise (enforces test 14).

    --- tests/test_rules_r1_r2_r3.py ---
    Write the following tests (SPEC required tests 1-6):

    Test 1 (SPEC test 1): "A 7-decimal transfer from a 10-decimal holding passes."
      baseline_complete=True, holder has Fraction(10), transfer Fraction(7).
      R1 returns Status.CONSISTENT.

    Test 2 (SPEC test 2): "A following 5-decimal transfer fails R1 with excess exactly 2."
      Same holder. After the 7-decimal transfer, available=3.
      Transfer of Fraction(5) returns Status.CONTRADICTION.
      alert.calculation must contain "requested 5" and "excess 2".

    Test 3 (SPEC test 3): "The same events with reversed dates are replayed
    chronologically and give the correct outcome."
      Swap the two event dates. The 5-decimal transfer now comes first
      (available=10, passes). The 7-decimal transfer then succeeds too.
      Both return Status.CONSISTENT. Demonstrates pure chronological replay.

    Test 4 (SPEC test 4): "R1 with baseline_complete false returns Review Required."
      Same over-transfer scenario, baseline_complete=False.
      R1 returns Status.REVIEW.

    Test 5 (SPEC test 5): "R1 with baseline_complete true but a missing event date
    returns Review Required."
      event.event_date=None. R1 must return Status.REVIEW (evaluation order
      step 1 fires before step 2; baseline_complete is irrelevant).

    Test 6 (SPEC test 6): "The same portion_id sold twice triggers R2.
    The same deed_no with different portion_ids does not."
      Part A: two events with identical portion_id + linked_event_id ->
        R2 returns Status.CONTRADICTION.
      Part B: two events with same deed_id but DIFFERENT portion_ids ->
        R2 returns Status.REVIEW (not Contradiction).
  </action>
  <verify>
    cd src; python -m pytest ../tests/test_rules_r1_r2_r3.py -v 2>&1
  </verify>
  <done>
    - All 6 tests pass (SPEC tests 1-6 satisfied).
    - run_rule() raises AssertionError if evidence_ids is empty.
    - grep for "float" and "0\." in rules.py returns zero hits for numeric literals.
  </done>
</task>

## Success Criteria
- [ ] SPEC tests 1, 2, 3, 4, 5, 6 all pass (pytest -v).
- [ ] Status enum values match SPEC verbatim.
- [ ] Alert has recommended_next_step with bn+en keys.
- [ ] Alert has impact_event_ids field.
- [ ] R2 does NOT use dag_no or deed_no to establish Contradiction.
- [ ] run_rule() enforces non-empty evidence_ids (test 14 partial).
