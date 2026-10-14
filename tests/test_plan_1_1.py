"""
Plan 1.1 smoke tests — models and replay engine.
These tests verify the foundation that all rules depend on.
No rule logic is exercised here.
"""
import pytest
from datetime import date
from fractions import Fraction

from jomigraph.models import (
    Person, Parcel, SurveyRecord, Deed,
    Event, EventType, ParcelHistory,
    load_fraction,
)
from jomigraph.engine.replay import (
    compute_state,
    replay_up_to,
    get_available_area,
    has_undated_events,
    anchor_ids_for_parcel,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_sr(parcel_id="P1", holders=None, area=Fraction(10)):
    """Helper: create a SurveyRecord with given holders (defaults to H1=area)."""
    if holders is None:
        holders = (("H1", area),)
    return SurveyRecord(
        id="SR1", parcel_id=parcel_id, survey="BS",
        khatian_no="K1", record_date=date(1980, 1, 1),
        recorded_area=area, holders=holders,
    )


def make_sale(eid, from_p, to_p, area, d, seq):
    return Event(
        id=eid, type=EventType.SALE, seq=seq,
        event_date=d, parcel_id="P1",
        from_person=from_p, to_person=to_p,
        area=Fraction(area), deed_id=None,
        portion_id=None, linked_event_id=None, source_record_id=None,
    )


def make_cancel(eid, linked_id, d, seq, area=None):
    return Event(
        id=eid, type=EventType.CANCEL, seq=seq,
        event_date=d, parcel_id="P1",
        from_person=None, to_person=None,
        area=Fraction(area) if area is not None else None,
        deed_id=None, portion_id=None,
        linked_event_id=linked_id, source_record_id=None,
    )


def make_correct(eid, holder, new_area, d, seq, source="SR1"):
    return Event(
        id=eid, type=EventType.CORRECT, seq=seq,
        event_date=d, parcel_id="P1",
        from_person=holder, to_person=None,
        area=Fraction(new_area), deed_id=None,
        portion_id=None, linked_event_id=None, source_record_id=source,
    )


# ---------------------------------------------------------------------------
# load_fraction
# ---------------------------------------------------------------------------

class TestLoadFraction:
    def test_rejects_float(self):
        with pytest.raises(TypeError, match="float values are not permitted"):
            load_fraction(7.0)

    def test_rejects_float_zero(self):
        with pytest.raises(TypeError):
            load_fraction(0.5)

    def test_accepts_int(self):
        assert load_fraction(7) == Fraction(7)

    def test_accepts_str_integer(self):
        assert load_fraction("7") == Fraction(7)

    def test_accepts_str_fraction(self):
        assert load_fraction("7/2") == Fraction(7, 2)

    def test_accepts_fraction(self):
        f = Fraction(3, 4)
        assert load_fraction(f) == Fraction(3, 4)


# ---------------------------------------------------------------------------
# Model construction
# ---------------------------------------------------------------------------

class TestModelConstruction:
    def test_person(self):
        p = Person(id="P1", name="রহিম")
        assert p.id == "P1"

    def test_parcel_optional_parent(self):
        p = Parcel(id="PAR1", dag_no="D1", mouza="M1")
        assert p.parent_id is None
        p2 = Parcel(id="PAR2", dag_no="D2", mouza="M1", parent_id="PAR1")
        assert p2.parent_id == "PAR1"

    def test_survey_record_fraction_area(self):
        sr = make_sr(area=Fraction(10))
        assert sr.recorded_area == Fraction(10)
        assert isinstance(sr.recorded_area, Fraction)

    def test_survey_record_fraction_holders(self):
        sr = make_sr(holders=(("H1", Fraction(7)), ("H2", Fraction(3))))
        assert sr.holders[0][1] == Fraction(7)
        assert isinstance(sr.holders[0][1], Fraction)

    def test_event_date_none_accepted(self):
        e = make_sale("E1", "H1", "H2", 7, None, seq=1)
        assert e.event_date is None

    def test_event_seq_required(self):
        e = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=3)
        assert e.seq == 3

    def test_parcel_history_baseline_complete_flag(self):
        ph = ParcelHistory(
            parcel_id="P1", baseline_record_id="SR1",
            baseline_complete=True, start_record_id="SR1",
            end_date=None, survey_records=(make_sr(),), events=(),
        )
        assert ph.baseline_complete is True


# ---------------------------------------------------------------------------
# has_undated_events
# ---------------------------------------------------------------------------

class TestHasUndatedEvents:
    def test_no_undated(self):
        events = [make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1)]
        assert has_undated_events(events) is False

    def test_one_undated(self):
        events = [
            make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1),
            make_sale("E2", "H2", "H3", 2, None, seq=2),
        ]
        assert has_undated_events(events) is True

    def test_empty_list(self):
        assert has_undated_events([]) is False


# ---------------------------------------------------------------------------
# Replay — basic sale
# ---------------------------------------------------------------------------

class TestReplayBasicSale:
    def test_7_decimal_transfer_from_10(self):
        """A 7-decimal transfer from a 10-decimal holding."""
        sr = make_sr(area=Fraction(10))
        e1 = make_sale("E1", "H1", "H2", 7, date(2000, 1, 1), seq=1)
        state, issues = compute_state([e1], sr)
        assert issues == []
        assert get_available_area(state, "H1") == Fraction(3)
        assert get_available_area(state, "H2") == Fraction(7)

    def test_sequential_transfers(self):
        """Two sequential transfers reduce the holder correctly."""
        sr = make_sr(area=Fraction(10))
        e1 = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1)
        e2 = make_sale("E2", "H1", "H3", 5, date(2001, 1, 1), seq=2)
        state, issues = compute_state([e1, e2], sr)
        assert issues == []
        assert get_available_area(state, "H1") == Fraction(0)

    def test_no_clamp_negative(self):
        """Replay does NOT clamp negative shares — over-allocation is stored as-is."""
        sr = make_sr(area=Fraction(10))
        e1 = make_sale("E1", "H1", "H2", 8, date(2000, 1, 1), seq=1)
        e2 = make_sale("E2", "H1", "H3", 8, date(2001, 1, 1), seq=2)
        state, issues = compute_state([e1, e2], sr)
        assert issues == []
        assert get_available_area(state, "H1") == Fraction(-6)

    def test_undated_event_skipped_by_replay(self):
        """Replay skips events with event_date=None."""
        sr = make_sr(area=Fraction(10))
        e1 = make_sale("E1", "H1", "H2", 7, None, seq=1)  # undated
        state, issues = compute_state([e1], sr)
        # H1 still has 10 because E1 was skipped
        assert get_available_area(state, "H1") == Fraction(10)


# ---------------------------------------------------------------------------
# Replay — sort order and tie-break
# ---------------------------------------------------------------------------

class TestSortOrder:
    def test_sort_by_date_not_id(self):
        """Events are ordered by (date, seq), not by event ID lexicography."""
        sr = make_sr(area=Fraction(10))
        # E_LATE has a lexicographically smaller ID but a later date
        e_late  = make_sale("E_AA", "H1", "H2", 7, date(2001, 1, 1), seq=2)
        e_early = make_sale("E_ZZ", "H1", "H2", 3, date(2000, 1, 1), seq=1)
        state, _ = compute_state([e_late, e_early], sr)
        # Both transfers deduct from H1: 10 - 3 - 7 = 0
        assert get_available_area(state, "H1") == Fraction(0)

    def test_same_date_tiebreak_by_seq(self):
        """Same-date events are ordered by seq."""
        sr = make_sr(area=Fraction(10))
        # E1 (seq=1) transfers 7, E2 (seq=2) transfers 2; both same date
        e1 = make_sale("E1", "H1", "H2", 7, date(2000, 1, 1), seq=1)
        e2 = make_sale("E2", "H2", "H3", 2, date(2000, 1, 1), seq=2)
        state, _ = compute_state([e2, e1], sr)  # intentionally reversed input
        # H2 received 7 then sent 2, so H2=5
        assert get_available_area(state, "H2") == Fraction(5)
        assert get_available_area(state, "H3") == Fraction(2)


# ---------------------------------------------------------------------------
# Replay — CANCEL
# ---------------------------------------------------------------------------

class TestReplayCancel:
    def test_cancel_reverses_sale(self):
        """A valid CANCEL restores the transferred area."""
        sr = make_sr(area=Fraction(10))
        e1 = make_sale("E1",  "H1", "H2", 7, date(2000, 1, 1), seq=1)
        e2 = make_cancel("E2", "E1",       date(2001, 1, 1), seq=2)
        state, issues = compute_state([e1, e2], sr)
        assert issues == []
        assert get_available_area(state, "H1") == Fraction(10)
        assert get_available_area(state, "H2") == Fraction(0)

    def test_cancel_missing_linked_event_adds_issue(self):
        """CANCEL with unknown linked_event_id is not silently skipped."""
        sr = make_sr(area=Fraction(10))
        e_bad = make_cancel("EC", "NONEXISTENT", date(2001, 1, 1), seq=1)
        state, issues = compute_state([e_bad], sr)
        assert len(issues) == 1
        assert "not found" in issues[0]

    def test_double_cancel_rejected(self):
        """A second CANCEL of the same event is rejected and flagged."""
        sr = make_sr(area=Fraction(10))
        e1   = make_sale("E1",  "H1", "H2", 7, date(2000, 1, 1), seq=1)
        ec1  = make_cancel("EC1", "E1",      date(2001, 1, 1), seq=2)
        ec2  = make_cancel("EC2", "E1",      date(2002, 1, 1), seq=3)
        state, issues = compute_state([e1, ec1, ec2], sr)
        # ec1 is valid; ec2 is a double-cancel -> one issue
        assert len(issues) == 1
        assert "already cancelled" in issues[0].lower() or "double-cancel" in issues[0].lower()

    def test_cancel_dated_before_linked_event_adds_issue(self):
        """Cannot cancel a future event."""
        sr = make_sr(area=Fraction(10))
        e1  = make_sale("E1",  "H1", "H2", 7, date(2002, 1, 1), seq=2)
        ec  = make_cancel("EC", "E1",          date(2001, 1, 1), seq=1)
        state, issues = compute_state([e1, ec], sr)
        assert len(issues) == 1
        assert "after the cancel date" in issues[0]

    def test_cancel_of_non_sale_gift_adds_issue(self):
        """Cannot cancel a MUTATION."""
        sr = make_sr(area=Fraction(10))
        e_mut = Event(
            id="EM", type=EventType.MUTATION, seq=1,
            event_date=date(2000, 1, 1), parcel_id="P1",
            from_person=None, to_person=None, area=None,
            deed_id=None, portion_id=None, linked_event_id=None, source_record_id=None,
        )
        ec = make_cancel("EC", "EM", date(2001, 1, 1), seq=2)
        state, issues = compute_state([e_mut, ec], sr)
        assert len(issues) == 1
        assert "SALE or GIFT" in issues[0]


# ---------------------------------------------------------------------------
# Replay — CORRECT
# ---------------------------------------------------------------------------

class TestReplayCorrect:
    def test_correct_replaces_share(self):
        """CORRECT with source_record_id replaces the holder's share."""
        sr = make_sr(area=Fraction(10))
        e1 = make_sale("E1", "H1", "H2", 3, date(2000, 1, 1), seq=1)
        ec = make_correct("EC", "H1", Fraction(4), date(2001, 1, 1), seq=2)
        state, issues = compute_state([e1, ec], sr)
        assert issues == []
        assert get_available_area(state, "H1") == Fraction(4)

    def test_correct_without_source_record_adds_issue(self):
        """CORRECT missing source_record_id is not applied and issues are raised."""
        sr = make_sr(area=Fraction(10))
        ec = make_correct("EC", "H1", Fraction(4), date(2001, 1, 1), seq=1, source=None)
        state, issues = compute_state([ec], sr)
        assert len(issues) == 1
        assert "source_record_id" in issues[0]
        # Share must not have been changed
        assert get_available_area(state, "H1") == Fraction(10)


# ---------------------------------------------------------------------------
# replay_up_to
# ---------------------------------------------------------------------------

class TestReplayUpTo:
    def test_excludes_trigger_event(self):
        """replay_up_to with exclude_event_id removes the trigger from state."""
        sr = make_sr(area=Fraction(10))
        e1 = make_sale("E1", "H1", "H2", 7, date(2000, 1, 1), seq=1)
        e2 = make_sale("E2", "H1", "H3", 3, date(2001, 1, 1), seq=2)
        # Exclude E2 (the trigger); cutoff is E2's position
        state, issues = replay_up_to(
            [e1, e2], sr,
            cutoff_date=date(2001, 1, 1),
            cutoff_seq=2,
            exclude_event_id="E2",
        )
        assert issues == []
        # Only E1 was replayed: H1=3, H2=7
        assert get_available_area(state, "H1") == Fraction(3)
        assert get_available_area(state, "H2") == Fraction(7)

    def test_excludes_same_date_higher_seq(self):
        """Events at (cutoff_date, seq >= cutoff_seq) are excluded."""
        sr = make_sr(area=Fraction(10))
        e1 = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1)
        e2 = make_sale("E2", "H1", "H3", 5, date(2000, 1, 1), seq=2)  # same date, later seq
        # cutoff = E2's position; E1 comes before, E2 is the trigger
        state, _ = replay_up_to(
            [e1, e2], sr,
            cutoff_date=date(2000, 1, 1),
            cutoff_seq=2,
            exclude_event_id="E2",
        )
        assert get_available_area(state, "H1") == Fraction(5)  # only E1 applied


# ---------------------------------------------------------------------------
# anchor_ids_for_parcel
# ---------------------------------------------------------------------------

class TestAnchorIds:
    def test_cancel_and_linked_event_are_anchors(self):
        sr = make_sr()
        e1  = make_sale("E1",  "H1", "H2", 5, date(2000, 1, 1), seq=1)
        ec  = make_cancel("EC", "E1",          date(2001, 1, 1), seq=2)
        anchors = anchor_ids_for_parcel([e1, ec], parcel_id="P1")
        assert "EC" in anchors   # the CANCEL itself
        assert "E1" in anchors   # the linked (cancelled) event

    def test_correct_is_anchor(self):
        ec = make_correct("EC", "H1", Fraction(4), date(2001, 1, 1), seq=1)
        anchors = anchor_ids_for_parcel([ec], parcel_id="P1")
        assert "EC" in anchors

    def test_plain_sale_is_not_anchor(self):
        e1 = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1)
        anchors = anchor_ids_for_parcel([e1], parcel_id="P1")
        assert "E1" not in anchors

    def test_different_parcel_not_included(self):
        """Events on a different parcel do not contribute anchors."""
        ec = Event(
            id="EC", type=EventType.CANCEL, seq=1,
            event_date=date(2001, 1, 1), parcel_id="P2",  # different parcel
            from_person=None, to_person=None, area=None,
            deed_id=None, portion_id=None, linked_event_id="E1", source_record_id=None,
        )
        anchors = anchor_ids_for_parcel([ec], parcel_id="P1")
        assert "EC" not in anchors
        assert "E1" not in anchors


# ---------------------------------------------------------------------------
# Replay — SUBDIVIDE, GIFT, MUTATION
# ---------------------------------------------------------------------------

class TestReplaySubdivide:
    def test_subdivide_reduces_parent_share(self):
        """SUBDIVIDE deducts area from parent holder on parent parcel."""
        sr = make_sr(area=Fraction(10))
        e_sub = Event(
            id="ES1", type=EventType.SUBDIVIDE, seq=1,
            event_date=date(2000, 1, 1), parcel_id="P1",
            from_person="H1", to_person=None, area=Fraction(4),
            deed_id=None, portion_id=None, linked_event_id=None, source_record_id=None,
        )
        state, issues = compute_state([e_sub], sr)
        assert issues == []
        assert get_available_area(state, "H1") == Fraction(6)

    def test_child_parcel_state_isolated_from_parent(self):
        """
        Child parcel state is computed from child's own SurveyRecord.
        The parent's reduced share is not used for child sales.
        """
        # Parent parcel P1 has 10 decimals, subdivided 4 decimals
        sr_parent = make_sr(area=Fraction(10))
        e_sub = Event(
            id="ES1", type=EventType.SUBDIVIDE, seq=1,
            event_date=date(2000, 1, 1), parcel_id="P1",
            from_person="H1", to_person=None, area=Fraction(4),
            deed_id=None, portion_id=None, linked_event_id=None, source_record_id=None,
        )
        parent_state, _ = compute_state([e_sub], sr_parent)
        assert get_available_area(parent_state, "H1") == Fraction(6)

        # Child parcel P2 (parent_id="P1") has baseline SurveyRecord of 4 decimals
        sr_child = SurveyRecord(
            id="SR_CHILD", parcel_id="P2", survey="BS", khatian_no="K2",
            record_date=date(2000, 6, 1), recorded_area=Fraction(4),
            holders=(("H1", Fraction(4)),),
        )
        # Sale on child parcel P2 transfers 4 decimals
        e_child_sale = make_sale("E_CS1", "H1", "H2", 4, date(2001, 1, 1), seq=1)
        child_state, child_issues = compute_state([e_child_sale], sr_child)
        assert child_issues == []
        assert get_available_area(child_state, "H1") == Fraction(0)
        assert get_available_area(child_state, "H2") == Fraction(4)
        # Parent's share remains 6, completely independent
        assert get_available_area(parent_state, "H1") == Fraction(6)


class TestReplayGift:
    def test_gift_transfers_area(self):
        """GIFT event transfers area from from_person to to_person."""
        sr = make_sr(area=Fraction(10))
        e_gift = Event(
            id="EG1", type=EventType.GIFT, seq=1,
            event_date=date(2000, 1, 1), parcel_id="P1",
            from_person="H1", to_person="H2", area=Fraction(3),
            deed_id=None, portion_id=None, linked_event_id=None, source_record_id=None,
        )
        state, issues = compute_state([e_gift], sr)
        assert issues == []
        assert get_available_area(state, "H1") == Fraction(7)
        assert get_available_area(state, "H2") == Fraction(3)


class TestReplayMutation:
    def test_mutation_does_not_alter_holder_state(self):
        """MUTATION does not alter holder areas during replay."""
        sr = make_sr(area=Fraction(10))
        e_mut = Event(
            id="EM1", type=EventType.MUTATION, seq=1,
            event_date=date(2000, 1, 1), parcel_id="P1",
            from_person="H1", to_person="H2", area=Fraction(5),
            deed_id="D1", portion_id=None, linked_event_id=None, source_record_id=None,
        )
        state, issues = compute_state([e_mut], sr)
        assert issues == []
        # Area unchanged; H1 still has full 10, H2 has 0
        assert get_available_area(state, "H1") == Fraction(10)
        assert get_available_area(state, "H2") == Fraction(0)

