"""
Plan 1.3 Tests — Rules R4, R5, R7, and R2 Cancellation semantics.
Covers SPEC Tests 7, 8, 9, 10, and user addition for R2 cancelled sales.
"""

from datetime import date
from fractions import Fraction
import pytest

from jomigraph.config import R4_TOLERANCE
from jomigraph.engine.rules import (
    Alert,
    Status,
    check_r1,
    check_r2,
    check_r4,
    check_r5,
    check_r7,
    run_rule,
)
from jomigraph.i18n import (
    MSG_CONSISTENT,
    MSG_R4_CONTRADICTION,
    MSG_R4_REVIEW_TOLERANCE,
    MSG_R5_CONSISTENT,
    MSG_R5_REVIEW_NO_LINK,
    MSG_R7_CONTRADICTION,
    MSG_R7_CONSISTENT,
    MSG_R7_REVIEW_MISSING_LINK_OR_DATE,
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


def make_cancel(
    eid: str,
    linked_eid: str,
    d: date,
    seq: int = 2,
    parcel_id: str = "P1",
) -> Event:
    return Event(
        id=eid,
        type=EventType.CANCEL,
        seq=seq,
        event_date=d,
        parcel_id=parcel_id,
        from_person=None,
        to_person=None,
        area=None,
        deed_id=None,
        portion_id=None,
        linked_event_id=linked_eid,
        source_record_id=None,
    )


# ---------------------------------------------------------------------------
# SPEC Test 8: Rule R4 Subdivision Reconciliation
# ---------------------------------------------------------------------------

class TestRuleR4:
    def test_r4_exact_match_passes(self):
        """Exact subdivision area match passes (CONSISTENT)."""
        sr_parent = make_sr("P1", area=Fraction(10))
        e_sub = Event(
            id="E_SUB", type=EventType.SUBDIVIDE, seq=1,
            event_date=date(2000, 1, 1), parcel_id="P1",
            from_person="H1", to_person=None, area=Fraction(10),
            deed_id=None, portion_id=None, linked_event_id=None, source_record_id=None,
        )
        # Two child parcels summing exactly to 10
        sr_c1 = make_sr("P2", "BS", area=Fraction(6))
        sr_c2 = make_sr("P3", "BS", area=Fraction(4))

        alert = run_rule(check_r4, e_sub, [sr_c1, sr_c2], [e_sub], sr_parent)

        assert alert.rule_id == "R4"
        assert alert.status == Status.CONSISTENT
        assert alert.message_key == MSG_CONSISTENT
        assert "E_SUB" in alert.evidence_ids

    def test_r4_difference_within_tolerance_returns_review(self):
        """Difference in (0, tolerance] returns Review Required."""
        sr_parent = make_sr("P1", area=Fraction(10))
        e_sub = Event(
            id="E_SUB", type=EventType.SUBDIVIDE, seq=1,
            event_date=date(2000, 1, 1), parcel_id="P1",
            from_person="H1", to_person=None, area=Fraction(10),
            deed_id=None, portion_id=None, linked_event_id=None, source_record_id=None,
        )
        # Children sum to 9.95 -> diff is 0.05 (Fraction(1, 20)), which is <= R4_TOLERANCE (0.1)
        sr_c1 = make_sr("P2", "BS", area=Fraction(995, 100))

        alert = run_rule(check_r4, e_sub, [sr_c1], [e_sub], sr_parent, tolerance=R4_TOLERANCE)

        assert alert.rule_id == "R4"
        assert alert.status == Status.REVIEW
        assert alert.message_key == MSG_R4_REVIEW_TOLERANCE

    def test_r4_difference_greater_than_tolerance_returns_contradiction(self):
        """Difference > tolerance returns Contradiction Found."""
        sr_parent = make_sr("P1", area=Fraction(10))
        e_sub = Event(
            id="E_SUB", type=EventType.SUBDIVIDE, seq=1,
            event_date=date(2000, 1, 1), parcel_id="P1",
            from_person="H1", to_person=None, area=Fraction(10),
            deed_id=None, portion_id=None, linked_event_id=None, source_record_id=None,
        )
        # Children sum to 9.5 -> diff is 0.5 (Fraction(1, 2)), which is > R4_TOLERANCE (0.1)
        sr_c1 = make_sr("P2", "BS", area=Fraction(95, 10))

        alert = run_rule(check_r4, e_sub, [sr_c1], [e_sub], sr_parent, tolerance=R4_TOLERANCE)

        assert alert.rule_id == "R4"
        assert alert.status == Status.CONTRADICTION
        assert alert.message_key == MSG_R4_CONTRADICTION


# ---------------------------------------------------------------------------
# SPEC Test 7: Rule R5 Survey Continuity
# ---------------------------------------------------------------------------

class TestRuleR5:
    def test_r5_unlinked_records_returns_review(self):
        """SPEC Test 7: No documented link between successive survey records returns Review Required."""
        sr_cs = make_sr("P1", "CS", area=Fraction(10), record_date=date(1920, 1, 1))
        sr_rs = make_sr("P1", "RS", area=Fraction(10), record_date=date(1960, 1, 1))

        # No linking events supplied
        alert = run_rule(check_r5, sr_cs, sr_rs, [], [])

        assert alert.rule_id == "R5"
        assert alert.status == Status.REVIEW
        assert alert.message_key == MSG_R5_REVIEW_NO_LINK
        assert sr_cs.id in alert.evidence_ids
        assert sr_rs.id in alert.evidence_ids

    def test_r5_linked_records_returns_consistent(self):
        """Documented link between successive survey records returns Consistent."""
        sr_cs = make_sr("P1", "CS", area=Fraction(10), record_date=date(1920, 1, 1))
        sr_rs = make_sr("P1", "RS", area=Fraction(10), record_date=date(1960, 1, 1))
        e_link = make_sale("E_LINK", "H1", "H2", 10, date(1940, 1, 1), seq=1)

        alert = run_rule(check_r5, sr_cs, sr_rs, [e_link], [e_link])

        assert alert.rule_id == "R5"
        assert alert.status == Status.CONSISTENT
        assert alert.message_key == MSG_R5_CONSISTENT
        assert "E_LINK" in alert.evidence_ids

    def test_r5_never_returns_contradiction(self):
        """SPEC: R5 never produces Contradiction Found."""
        sr1 = make_sr("P1", "CS")
        sr2 = make_sr("P1", "RS")
        alert = run_rule(check_r5, sr1, sr2, [], [])
        assert alert.status != Status.CONTRADICTION


# ---------------------------------------------------------------------------
# SPEC Test 9: Rule R7 Chronological Consistency
# ---------------------------------------------------------------------------

class TestRuleR7:
    def test_r7_mutation_precedes_deed_returns_contradiction(self):
        """SPEC Test 9: Mutation date precedes deed registration date -> Contradiction Found."""
        sr = make_sr()
        deed = Deed(id="D1", deed_no="DEED_200", registration_date=date(2005, 6, 1))
        # Mutation date 2005-01-01 is BEFORE deed registration date 2005-06-01
        e_mut = Event(
            id="EM", type=EventType.MUTATION, seq=1,
            event_date=date(2005, 1, 1), parcel_id="P1",
            from_person=None, to_person="H2", area=Fraction(5),
            deed_id="D1", portion_id=None, linked_event_id="ES1", source_record_id=None,
        )

        alert = run_rule(check_r7, e_mut, deed, [e_mut], sr)

        assert alert.rule_id == "R7"
        assert alert.status == Status.CONTRADICTION
        assert alert.message_key == MSG_R7_CONTRADICTION
        assert "precedes" in alert.calculation

    def test_r7_mutation_after_deed_returns_consistent(self):
        """Mutation on or after deed registration date -> Consistent."""
        sr = make_sr()
        deed = Deed(id="D1", deed_no="DEED_200", registration_date=date(2005, 1, 1))
        e_mut = Event(
            id="EM", type=EventType.MUTATION, seq=1,
            event_date=date(2005, 6, 1), parcel_id="P1",
            from_person=None, to_person="H2", area=Fraction(5),
            deed_id="D1", portion_id=None, linked_event_id="ES1", source_record_id=None,
        )

        alert = run_rule(check_r7, e_mut, deed, [e_mut], sr)

        assert alert.rule_id == "R7"
        assert alert.status == Status.CONSISTENT
        assert alert.message_key == MSG_R7_CONSISTENT

    def test_r7_missing_link_or_date_returns_review(self):
        """Missing deed or missing registration date -> Review Required."""
        sr = make_sr()
        e_mut = Event(
            id="EM", type=EventType.MUTATION, seq=1,
            event_date=date(2005, 1, 1), parcel_id="P1",
            from_person=None, to_person="H2", area=Fraction(5),
            deed_id=None, portion_id=None, linked_event_id=None, source_record_id=None,
        )

        alert = run_rule(check_r7, e_mut, None, [e_mut], sr)

        assert alert.rule_id == "R7"
        assert alert.status == Status.REVIEW
        assert alert.message_key == MSG_R7_REVIEW_MISSING_LINK_OR_DATE


# ---------------------------------------------------------------------------
# SPEC Test 10: Cancellation changes R1 and appears in evidence
# ---------------------------------------------------------------------------

class TestRuleR1WithCancellation:
    def test_10_cancellation_restores_share_and_appears_in_evidence(self):
        """
        SPEC Test 10: A cancellation changes R1 outcome from Contradiction
        to Consistent and the CANCEL event appears in evidence_ids.
        """
        sr = make_sr(area=Fraction(10), holders=(("H1", Fraction(10)),))
        e1 = make_sale("E1", "H1", "H2", 7, date(2000, 1, 1), seq=1)
        ec = make_cancel("EC", "E1", date(2001, 1, 1), seq=2)
        # Following sale of 5 decimals by H1
        e3 = make_sale("E3", "H1", "H3", 5, date(2002, 1, 1), seq=3)

        # Without EC: H1 has 10 - 7 = 3 available; selling 5 fails R1 with excess 2
        hist_without_cancel = make_history(sr, events=(e1, e3), baseline_complete=True)
        alert_fail = run_rule(check_r1, e3, hist_without_cancel, [e1, e3])
        assert alert_fail.status == Status.CONTRADICTION

        # With EC: EC restores 7 decimals to H1 -> available is 10; selling 5 passes R1
        hist_with_cancel = make_history(sr, events=(e1, ec, e3), baseline_complete=True)
        alert_pass = run_rule(check_r1, e3, hist_with_cancel, [e1, ec, e3])
        assert alert_pass.status == Status.CONSISTENT
        # CANCEL event must appear in evidence_ids
        assert "EC" in alert_pass.evidence_ids


# ---------------------------------------------------------------------------
# Addition 1: R2 Cancelled Sale Excluded from Duplicate Portion
# ---------------------------------------------------------------------------

class TestRuleR2WithCancellation:
    def test_portion_sold_cancelled_and_resold_has_no_r2_contradiction(self):
        """
        Portion sold (E1), cancelled (EC), sold again to a different buyer (E2).
        The cancelled sale must not trigger an R2 contradiction.
        """
        sr = make_sr()
        e1 = make_sale(
            "E1", "H1", "H2", 5, date(2000, 1, 1), seq=1,
            portion_id="PORTION_A", linked_event_id="PARENT_DEED"
        )
        ec = make_cancel("EC", "E1", date(2001, 1, 1), seq=2)
        e2 = make_sale(
            "E2", "H1", "H3", 5, date(2002, 1, 1), seq=3,
            portion_id="PORTION_A", linked_event_id="PARENT_DEED"
        )

        all_events = [e1, ec, e2]
        alert = run_rule(check_r2, e2, all_events, sr)

        # No contradiction because E1 was cancelled; clean resale returns CONSISTENT
        assert alert.status == Status.CONSISTENT
        assert alert.message_key == MSG_CONSISTENT
