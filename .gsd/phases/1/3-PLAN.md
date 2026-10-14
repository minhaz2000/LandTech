---
phase: 1
plan: 3
wave: 2
title: Rules R4, R5, R6, R7 and Minimal Evidence
depends_on: "2-PLAN.md"
---

# Plan 1.3: Rules R4, R5, R6, R7 and Minimal Evidence

## Objective
Implement rules R4–R7 and the minimal-evidence algorithm (all alternative
minimal sets). Implement the impact-view dependency lookup. Covers SPEC
tests 7, 8, 9, 10, 11, 14.

## Context
- .gsd/SPEC.md  (§ Rules R4-R7, § Minimal Evidence, § Additions impact view)
- src/jomigraph/engine/rules.py   (from Plan 1.2)
- src/jomigraph/engine/replay.py  (from Plan 1.1)
- src/jomigraph/engine/evidence.py   (to create)
- tests/test_rules_r4_r7.py   (to create)
- tests/test_evidence.py   (to create)

## Files Created This Plan
| Path | Purpose |
|------|---------|
| `src/jomigraph/engine/rules.py` | add R4, R5, R6, R7 (extend existing file) |
| `src/jomigraph/engine/evidence.py` | minimal_evidence(), impact_lookup() |
| `tests/test_rules_r4_r7.py` | SPEC required tests 7, 8, 9, 10 |
| `tests/test_evidence.py` | SPEC required tests 11, 14 |
| `config.py` | tolerance constant (Fraction, named parameter) |

> NOTE: rules.py was created in Plan 1.2 (this phase). No approval
> needed to extend it. config.py is new.

## Tasks

<task type="auto">
  <name>Implement R4, R5, R6, R7 in rules.py</name>
  <files>src/jomigraph/engine/rules.py, src/jomigraph/config.py, tests/test_rules_r4_r7.py</files>
  <action>
    --- config.py ---
    SPEC R4: "The tolerance is a named, explicit parameter in config."
    from fractions import Fraction
    R4_TOLERANCE = Fraction(1, 10)   # 0.1 decimal — adjustable

    --- R4 (SPEC wording exactly) ---
    "All area and share calculations use exact rational arithmetic. An exact
    area match passes. A difference greater than zero and at most the
    declared tolerance returns Review Required. A difference greater than
    the declared tolerance returns Contradiction Found. The tolerance is a
    named, explicit parameter in config."

    def check_r4(subdivide_event, child_survey_records, config) -> Alert:
      Step 1: If subdivide_event.area is None -> Review Required.
              If child_survey_records is empty -> Review Required.
      Step 2: total_child_area = sum(Fraction(sr.recorded_area)
                                     for sr in child_survey_records)
              diff = abs(subdivide_event.area - total_child_area)
              If diff == Fraction(0): return Consistent.
              If Fraction(0) < diff <= config.R4_TOLERANCE: return Review Required.
              If diff > config.R4_TOLERANCE: return Contradiction Found.
              calculation = f"parent {subdivide_event.area}, children {total_child_area}, diff {diff}, tolerance {config.R4_TOLERANCE}"
      evidence_ids = (subdivide_event.id,) + tuple(sr.id for sr in child_survey_records)

    --- R5 (SPEC wording exactly) ---
    "If no documented relationship connects two successive survey records
    for the parcel, return Review Required."
    R5 NEVER returns Contradiction Found.

    def check_r5(earlier_record, later_record, linking_event) -> Alert:
      Step 1: If earlier_record is None or later_record is None -> Review Required.
      Step 2: If linking_event is None -> Review Required.
              Else -> Consistent.
      evidence_ids = (earlier_record.id, later_record.id) +
                     ((linking_event.id,) if linking_event else ())

    --- R6 (SPEC wording exactly) ---
    "If a mutation's linked deed, area or supplied transaction information
    does not reconcile, return Review Required."
    R6 NEVER returns Contradiction Found.

    def check_r6(mutation_event, deed) -> Alert:
      Step 1: If mutation_event.deed_id is None -> Review Required.
              If deed is None -> Review Required.
              If mutation_event.area is None -> Review Required.
      Step 2: Return Review Required. (R6 always returns Review Required;
              reconciliation insufficiency is not a modeled Contradiction.)
      evidence_ids = (mutation_event.id,) + ((deed.id,) if deed else ())

    --- R7 (SPEC wording exactly) ---
    "If the deed-mutation link and both dates are supplied and the mutation
    date precedes the deed registration date, return Contradiction Found.
    If the link or either date is missing, return Review Required."

    def check_r7(mutation_event, deed) -> Alert:
      Step 1: If mutation_event.linked_event_id is None -> Review Required.
              If mutation_event.event_date is None -> Review Required.
              If deed is None -> Review Required.
              If deed.registration_date is None -> Review Required.
      Step 2: If mutation_event.event_date < deed.registration_date:
                return Contradiction Found.
              Else: return Consistent.
      evidence_ids = (mutation_event.id, deed.id)

    --- tests/test_rules_r4_r7.py ---
    Test 7 (SPEC test 7): "A survey gap triggers R5 with Review Required, not Contradiction."
      R5 with linking_event=None returns Status.REVIEW.
      Verify Status is NOT Status.CONTRADICTION.

    Test 8 (SPEC test 8): "R4: exact match passes, difference equal to tolerance
    returns Review Required, difference above tolerance returns Contradiction Found."
      Part A: child areas sum == parent area -> Status.CONSISTENT.
      Part B: diff = R4_TOLERANCE exactly -> Status.REVIEW.
      Part C: diff = R4_TOLERANCE + Fraction(1,100) -> Status.CONTRADICTION.
      All three use Fraction arithmetic — no float.

    Test 9 (SPEC test 9): "R7 returns Contradiction only when the link and both dates
    are present."
      Part A: linked_event_id=None -> Status.REVIEW.
      Part B: mutation_event.event_date=None -> Status.REVIEW.
      Part C: deed=None -> Status.REVIEW.
      Part D: all present, mutation_date < deed_date -> Status.CONTRADICTION.
      Part E: all present, mutation_date > deed_date -> Status.CONSISTENT.

    Test 10 (SPEC test 10): "A cancellation event changes the R1 result and appears
    in the evidence set."
      Setup: holder starts with Fraction(10). Transfer of Fraction(7) (E1).
      Without cancellation: second transfer of Fraction(5) -> Contradiction.
      Add CANCEL event (E2) that cancels E1 (linked_event_id="E1").
      After replay including CANCEL: available returns to Fraction(10).
      R1 for the Fraction(5) transfer now returns Consistent.
      E2 (the CANCEL event) must appear in alert.evidence_ids.
  </action>
  <verify>
    cd src; python -m pytest ../tests/test_rules_r4_r7.py -v 2>&1
  </verify>
  <done>
    - SPEC tests 7, 8, 9, 10 all pass.
    - R5 and R6 never produce Status.CONTRADICTION (assert in test).
    - R4 tolerance is imported from config, not hardcoded in rules.py.
    - CANCEL event appears in evidence_ids for test 10.
  </done>
</task>

<task type="auto">
  <name>Implement minimal_evidence() and impact_lookup()</name>
  <files>src/jomigraph/engine/evidence.py, tests/test_evidence.py</files>
  <action>
    --- SPEC § Minimal Evidence (exact wording) ---
    "The engine removes one candidate record at a time and re-runs the
    rule, keeping a record only if removing it makes the violation
    disappear. For the implemented arithmetic rules, adding unrelated
    records cannot remove an established violation when no relevant
    cancellation, reversal or correction event is present. Such events
    are relevant records and must always be included in the evaluation
    because they can change the modeled state. The procedure returns an
    inclusion-minimal evidence set relative to the implemented rule and
    supplied history, not necessarily the globally smallest. Deletion
    order can change the result, so the engine returns all alternative
    minimal sets it finds."

    Implement:

    def minimal_evidence(
        rule_fn,          # callable: (candidate_events) -> Alert
        candidate_ids,    # list[str] of event/record IDs to try removing
        all_events,       # full list for reference
        *rule_args        # extra positional args forwarded to rule_fn
    ) -> list[tuple[str, ...]]:
      """
      Returns a list of minimal evidence tuples.
      Each tuple is a minimal set: removing any one ID from it causes
      rule_fn to no longer return Status.CONTRADICTION.

      Algorithm:
      1. Start with the full candidate_ids set.
      2. For each permutation order (try each ID as the first to remove):
         a. Walk through candidate_ids in that order.
         b. Tentatively remove the ID from the current set.
         c. Re-run rule_fn with the reduced set.
         d. If the result is still CONTRADICTION, keep the removal.
            If not, restore the ID.
         e. Continue until no more removals are possible.
         f. Record the resulting minimal set.
      3. Deduplicate sets and return all distinct ones.

      Constraint: CANCEL, CORRECT events that affect the result must
      remain in the set (they cannot be removed without changing outcome).
      The algorithm naturally enforces this — removing them changes the
      result, so they stay.
      """

    def impact_lookup(
        event_id: str,
        all_events: list[Event]
    ) -> list[str]:
      """
      SPEC Additions: "Impact view: for any Contradiction or Review result,
      list later events that depend on the conflicting event, so the
      reviewer sees which records may need re-checking."

      Returns IDs of events where:
        - linked_event_id == event_id, OR
        - source_record_id == event_id
      These are candidate downstream dependencies.
      """

    --- tests/test_evidence.py ---
    Test 11 (SPEC test 11): "A case with two alternative minimal evidence sets reports both."
      Construct a scenario where two different CANCEL events can each
      independently resolve the violation:
        E1: transfer Fraction(7) from H1 (event_date=2000-01-01)
        E2: CANCEL of E1 (event_date=2001-01-01)
        E3: CANCEL of E1 (event_date=2001-06-01, alternative path)
        E4: transfer Fraction(5) from H1 (event_date=2002-01-01) -- the trigger
      candidate_ids = ["E1", "E2", "E3"]
      minimal_evidence(...) must return two sets:
        {E1, E2} and {E1, E3}  (or equivalent tuples, order-independent).
      Assert len(result) == 2.
      Assert each set has len == 2.

    Test 14 (SPEC test 14): "Every alert includes rule_id and non-empty evidence_ids."
      Run R1, R2, R3, R4, R5, R6, R7 with inputs designed to trigger
      each status (CONSISTENT, CONTRADICTION, REVIEW) where applicable.
      Assert every returned Alert has:
        alert.rule_id in {"R1","R2","R3","R4","R5","R6","R7"}
        len(alert.evidence_ids) > 0
  </action>
  <verify>
    cd src; python -m pytest ../tests/test_evidence.py -v 2>&1
  </verify>
  <done>
    - SPEC test 11: minimal_evidence returns exactly 2 alternative sets.
    - SPEC test 14: all rule functions return alerts with non-empty evidence_ids.
    - impact_lookup returns downstream event IDs correctly.
    - No float in evidence.py.
  </done>
</task>

## Success Criteria
- [ ] SPEC tests 7, 8, 9, 10, 11, 14 all pass (pytest -v).
- [ ] R5 and R6 never produce Contradiction Found (asserted in tests).
- [ ] minimal_evidence returns all alternative minimal sets, not just one.
- [ ] impact_lookup verified by assertion in test_evidence.py.
- [ ] R4_TOLERANCE is a named Fraction in config.py, not a magic literal.
