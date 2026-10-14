"""
Plan 1.3 Tests — Minimal Evidence and Impact Lookup.
Covers SPEC Test 11 (two alternative minimal sets), SPEC Test 14 (non-empty evidence IDs),
and downstream impact lookup.
"""

from datetime import date
from fractions import Fraction
import pytest

from jomigraph.engine.evidence import impact_closure, impact_lookup, minimal_evidence
from jomigraph.engine.rules import (
    Alert,
    Status,
    check_r1,
    check_r2,
    check_r3,
    check_r4,
    check_r5,
    check_r6,
    check_r7,
    run_rule,
)
from jomigraph.models import (
    Deed,
    Event,
    EventType,
    ParcelHistory,
    SurveyRecord,
)


def make_sr(
    parcel_id: str = "P1",
    survey: str = "BS",
    area: Fraction = Fraction(10),
    holders: tuple = (("H1", Fraction(10)),),
    record_date: date = date(1980, 1, 1),
) -> SurveyRecord:
    return SurveyRecord(
        id=f"SR_{parcel_id}_{survey}",
        parcel_id=parcel_id,
        survey=survey,
        khatian_no="K100",
        record_date=record_date,
        recorded_area=area,
        holders=holders,
    )


def make_history(
    sr: SurveyRecord,
    events: tuple[Event, ...] = (),
    baseline_complete: bool = True,
) -> ParcelHistory:
    return ParcelHistory(
        parcel_id=sr.parcel_id,
        baseline_record_id=sr.id,
        baseline_complete=baseline_complete,
        start_record_id=sr.id,
        end_date=None,
        survey_records=(sr,),
        events=events,
    )


def make_sale(
    eid: str,
    from_p: str,
    to_p: str,
    area: int | Fraction,
    d: date | None,
    seq: int = 1,
    parcel_id: str = "P1",
    deed_id: str | None = None,
    portion_id: str | None = None,
    linked_event_id: str | None = None,
) -> Event:
    return Event(
        id=eid,
        type=EventType.SALE,
        seq=seq,
        event_date=d,
        parcel_id=parcel_id,
        from_person=from_p,
        to_person=to_p,
        area=Fraction(area) if area is not None else None,
        deed_id=deed_id,
        portion_id=portion_id,
        linked_event_id=linked_event_id,
        source_record_id=None,
    )


# ---------------------------------------------------------------------------
# SPEC Test 11: Two Alternative Minimal Evidence Sets
# ---------------------------------------------------------------------------

class TestMinimalEvidence:
    def test_11_two_alternative_minimal_evidence_sets(self):
        """
        SPEC Test 11: A case with two alternative minimal evidence sets reports both.
        Scenario:
          Baseline SR1: H1 has 10 decimals.
          E_A: H1 transfers 4 decimals to P2 on 2000-01-01 (seq=1)
          E_B: H1 transfers 4 decimals to P3 on 2001-01-01 (seq=2)
          E_T: H1 transfers 7 decimals to P4 on 2002-01-01 (seq=3, trigger)

        Full history: prior transfers = 4 + 4 = 8. Available = 2. Transfer = 7 > 2 -> Contradiction.
        Subset {E_A, E_T}: prior = 4. Available = 6. Transfer = 7 > 6 -> Contradiction! (Size 1 minimal)
        Subset {E_B, E_T}: prior = 4. Available = 6. Transfer = 7 > 6 -> Contradiction! (Size 1 minimal)
        Subset {E_T}: prior = 0. Available = 10. Transfer = 7 <= 10 -> Consistent.

        minimal_evidence must return exactly 2 alternative sets:
          {SR1, E_A, E_T} and {SR1, E_B, E_T}.
        """
        sr = make_sr(parcel_id="P1", area=Fraction(10), holders=(("H1", Fraction(10)),))
        e_a = make_sale("E_A", "H1", "P2", 4, date(2000, 1, 1), seq=1)
        e_b = make_sale("E_B", "H1", "P3", 4, date(2001, 1, 1), seq=2)
        e_t = make_sale("E_T", "H1", "P4", 7, date(2002, 1, 1), seq=3)

        all_events = [e_a, e_b, e_t]
        history = make_history(sr, events=tuple(all_events), baseline_complete=True)

        def eval_fn(subset: list[Event]) -> Alert:
            hist = make_history(sr, events=tuple(subset), baseline_complete=True)
            return check_r1(e_t, hist, subset)

        sets = minimal_evidence(
            eval_fn=eval_fn,
            all_events=all_events,
            baseline_record=sr,
            trigger_event=e_t,
        )

        assert len(sets) == 2, f"Expected 2 minimal sets, got: {sets}"

        # Convert to sets of IDs for order-independent comparison
        set_a = set(sets[0])
        set_b = set(sets[1])

        expected_1 = {sr.id, "E_A", "E_T"}
        expected_2 = {sr.id, "E_B", "E_T"}

        assert (set_a == expected_1 and set_b == expected_2) or (
            set_a == expected_2 and set_b == expected_1
        ), f"Sets did not match expected alternative minimal sets: {sets}"

    def test_more_than_12_candidates_returns_not_minimized_full_set(self):
        """
        When candidate count exceeds candidate_cap (12), minimal_evidence returns
        the full candidate set with not_minimized=True; never crashes or truncates silently.
        """
        sr = make_sr(parcel_id="P1", area=Fraction(100), holders=(("H1", Fraction(100)),))
        # Create 14 deletion candidates (sales of 1 decimal each)
        candidates = [
            make_sale(f"E_{i}", "H1", f"BUYER_{i}", 1, date(2000, 1, 1), seq=i)
            for i in range(1, 15)
        ]
        # Trigger event: transfer 90 decimals -> total 14 + 90 = 104 > 100 -> Contradiction!
        e_trigger = make_sale("E_T", "H1", "BUYER_T", 90, date(2001, 1, 1), seq=20)
        all_events = candidates + [e_trigger]

        def eval_fn(subset: list[Event]) -> Alert:
            hist = make_history(sr, events=tuple(subset), baseline_complete=True)
            return check_r1(e_trigger, hist, subset)

        result = minimal_evidence(
            eval_fn=eval_fn,
            all_events=all_events,
            baseline_record=sr,
            trigger_event=e_trigger,
            candidate_cap=12,
        )

        assert result.not_minimized is True
        assert len(result) == 1
        # The single returned evidence set must contain all 14 candidates plus anchors (never truncated)
        returned_set = set(result[0])
        assert sr.id in returned_set
        assert "E_T" in returned_set
        for i in range(1, 15):
            assert f"E_{i}" in returned_set


# ---------------------------------------------------------------------------
# SPEC Test 14: Every Alert Has rule_id and Non-Empty evidence_ids
# ---------------------------------------------------------------------------

class TestAlertInvariants:
    def test_14_every_alert_includes_rule_id_and_non_empty_evidence_ids(self):
        """
        SPEC Test 14: Every alert includes rule_id and non-empty evidence_ids.
        Explicitly verifies both Status.CONSISTENT and non-consistent alerts
        across R1, R2, R3, R4, R5, R6, R7.
        """
        sr = make_sr(area=Fraction(10), holders=(("H1", Fraction(10)),))
        history = make_history(sr, baseline_complete=True)
        deed = Deed(id="D1", deed_no="DEED_1", registration_date=date(2000, 1, 1))

        # R1 CONSISTENT alert
        e_r1 = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1)
        alert_r1 = run_rule(check_r1, e_r1, history, [e_r1])
        assert alert_r1.status == Status.CONSISTENT
        assert alert_r1.rule_id == "R1"
        assert len(alert_r1.evidence_ids) > 0

        # R2 CONSISTENT alert (clean allocation with portion_id and lineage)
        e_r2 = make_sale(
            "E2", "H1", "H2", 5, date(2000, 1, 1), seq=1,
            portion_id="PORT_1", linked_event_id="PARENT"
        )
        alert_r2 = run_rule(check_r2, e_r2, [e_r2], sr)
        assert alert_r2.status == Status.CONSISTENT
        assert alert_r2.rule_id == "R2"
        assert len(alert_r2.evidence_ids) > 0

        # R3 CONSISTENT alert (recorded holder selling)
        e_r3 = make_sale("E3", "H1", "H2", 5, date(2000, 1, 1), seq=1)
        alert_r3 = run_rule(check_r3, e_r3, history, [e_r3])
        assert alert_r3.status == Status.CONSISTENT
        assert alert_r3.rule_id == "R3"
        assert len(alert_r3.evidence_ids) > 0

        # R4 CONSISTENT alert (exact match subdivision)
        e_r4 = Event(
            id="E4", type=EventType.SUBDIVIDE, seq=1,
            event_date=date(2000, 1, 1), parcel_id="P1",
            from_person="H1", to_person=None, area=Fraction(10),
            deed_id=None, portion_id=None, linked_event_id=None, source_record_id=None,
        )
        sr_child = make_sr("P2", area=Fraction(10))
        alert_r4 = run_rule(check_r4, e_r4, [sr_child], [e_r4], sr)
        assert alert_r4.status == Status.CONSISTENT
        assert alert_r4.rule_id == "R4"
        assert len(alert_r4.evidence_ids) > 0

        # R5 CONSISTENT alert (linked successive survey records)
        sr_cs = make_sr("P1", "CS")
        sr_rs = make_sr("P1", "RS")
        e_link = make_sale("E_L", "H1", "H2", 10, date(1950, 1, 1), seq=1)
        alert_r5 = run_rule(check_r5, sr_cs, sr_rs, [e_link], [e_link])
        assert alert_r5.status == Status.CONSISTENT
        assert alert_r5.rule_id == "R5"
        assert len(alert_r5.evidence_ids) > 0

        # R6 CONSISTENT alert (reconciled deed and mutation)
        e_sale = make_sale("E_S", "H1", "H2", 5, date(2000, 1, 1), seq=1, deed_id="D1")
        e_r6 = Event(
            id="E6", type=EventType.MUTATION, seq=2,
            event_date=date(2000, 6, 1), parcel_id="P1",
            from_person=None, to_person="H2", area=Fraction(5),
            deed_id="D1", portion_id=None, linked_event_id="E_S", source_record_id=None,
        )
        alert_r6 = run_rule(check_r6, e_r6, deed, [e_sale, e_r6], sr)
        assert alert_r6.status == Status.CONSISTENT
        assert alert_r6.rule_id == "R6"
        assert len(alert_r6.evidence_ids) > 0

        # R7 CONSISTENT alert (mutation date on/after deed date)
        alert_r7 = run_rule(check_r7, e_r6, deed, [e_r6], sr)
        assert alert_r7.status == Status.CONSISTENT
        assert alert_r7.rule_id == "R7"
        assert len(alert_r7.evidence_ids) > 0


# ---------------------------------------------------------------------------
# Impact Lookup
# ---------------------------------------------------------------------------

class TestImpactLookup:
    def test_impact_lookup_finds_dependents(self):
        """Downstream dependent events referencing an event ID are returned."""
        e1 = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1)
        # E2 references E1 as linked_event_id
        e2 = make_sale(
            "E2", "H2", "H3", 2, date(2001, 1, 1), seq=2,
            linked_event_id="E1"
        )
        # E3 references E1 as source_record_id
        e3 = Event(
            id="E3", type=EventType.CORRECT, seq=3,
            event_date=date(2002, 1, 1), parcel_id="P1",
            from_person="H2", to_person=None, area=Fraction(6),
            deed_id=None, portion_id=None, linked_event_id=None, source_record_id="E1",
        )
        # E4 is independent
        e4 = make_sale("E4", "H5", "H6", 1, date(2003, 1, 1), seq=4)

        dependents = impact_lookup("E1", [e1, e2, e3, e4])
        assert dependents == ["E2", "E3"]


# ---------------------------------------------------------------------------
# Impact Closure (Transitive, Same-Portion, Derived Title, Cycle-Safe)
# ---------------------------------------------------------------------------

class TestImpactClosure:
    def test_impact_closure_chains_transitive(self):
        """Impact closure follows linked_event_id links transitively (chain A -> B -> C)."""
        e1 = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1)
        e2 = make_sale("E2", "H2", "H3", 3, date(2001, 1, 1), seq=2, linked_event_id="E1")
        e3 = make_sale("E3", "H3", "H4", 1, date(2002, 1, 1), seq=3, linked_event_id="E2")
        e_unrelated = make_sale("E_OTHER", "H9", "H10", 2, date(2003, 1, 1), seq=4)

        closure = impact_closure("E1", [e1, e2, e3, e_unrelated])
        assert closure == ["E2", "E3"]

    def test_impact_closure_same_portion(self):
        """Impact closure includes later events on the same non-null portion_id."""
        e1 = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1, portion_id="PORT_X")
        # Later event on same portion
        e2 = make_sale("E2", "H1", "H3", 5, date(2001, 1, 1), seq=2, portion_id="PORT_X")
        # Later event on different portion
        e3 = make_sale("E3", "H1", "H4", 5, date(2002, 1, 1), seq=3, portion_id="PORT_Y")
        # Earlier event on same portion (must not be included)
        e0 = make_sale("E0", "H0", "H1", 5, date(1999, 1, 1), seq=0, portion_id="PORT_X")

        closure = impact_closure("E1", [e0, e1, e2, e3])
        assert closure == ["E2"]

    def test_impact_closure_derived_title(self):
        """Impact closure includes later events where from_person is the conflicting event's to_person."""
        e1 = make_sale("E1", "H1", "BUYER_BOB", 5, date(2000, 1, 1), seq=1)
        # Later sale where Bob resells derived title
        e2 = make_sale("E2", "BUYER_BOB", "BUYER_CHARLIE", 2, date(2001, 1, 1), seq=2)
        # Unrelated sale by someone else
        e3 = make_sale("E3", "H1", "BUYER_DAVE", 1, date(2002, 1, 1), seq=3)

        closure = impact_closure("E1", [e1, e2, e3])
        assert closure == ["E2"]

    def test_impact_closure_cycle_safe_and_never_includes_self(self):
        """Impact closure terminates cleanly on cyclic and self-referencing links, never including root."""
        # 1. Cyclic: E1 -> E2 -> E1
        e1 = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1, linked_event_id="E2")
        e2 = make_sale("E2", "H2", "H3", 5, date(2001, 1, 1), seq=2, linked_event_id="E1")
        closure_e1 = impact_closure("E1", [e1, e2])
        assert closure_e1 == ["E2"]
        assert "E1" not in closure_e1

        # 2. Self-referencing
        e_self = make_sale("E_SELF", "H1", "H2", 5, date(2000, 1, 1), seq=1, linked_event_id="E_SELF")
        closure_self = impact_closure("E_SELF", [e_self])
        assert closure_self == []

    def test_impact_closure_empty_case(self):
        """Impact closure returns empty list when no downstream dependents exist or event is unknown."""
        e1 = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1)
        e2 = make_sale("E2", "H5", "H6", 2, date(2001, 1, 1), seq=2)

        assert impact_closure("E1", [e1, e2]) == []
        assert impact_closure("NON_EXISTENT", [e1, e2]) == []

