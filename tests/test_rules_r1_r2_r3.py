"""
Plan 1.2 Tests — Rules R1, R2, R3, R6 and Alert Structure.
Covers SPEC Tests 1, 2, 3, 4, 5, 6, plus R3/R6 clean/review cases,
mutual exclusivity of R1 vs R3, history hygiene, and i18n key resolution.
"""

from datetime import date
from fractions import Fraction
import pytest

from jomigraph.engine.rules import (
    Alert,
    Status,
    check_r1,
    check_r2,
    check_r3,
    check_r6,
    run_rule,
)
from jomigraph.i18n import (
    MSG_CONSISTENT,
    MSG_R1_CONTRADICTION,
    MSG_R1_REVIEW_INCOMPLETE_BASELINE,
    MSG_R2_CONTRADICTION,
    MSG_R2_REVIEW_UNESTABLISHED,
    MSG_R3_CONTRADICTION,
    MSG_R3_REVIEW_INCOMPLETE_BASELINE,
    MSG_R6_CONSISTENT,
    MSG_R6_REVIEW_MISMATCH,
    MSG_REVIEW_UNDATED_HISTORY,
    MSG_REVIEW_UNSUPPORTED_HISTORY,
    translate,
)
from jomigraph.models import (
    Deed,
    Event,
    EventType,
    ParcelHistory,
    SurveyRecord,
)


# ---------------------------------------------------------------------------
# Test Helpers
# ---------------------------------------------------------------------------

def make_sr(
    parcel_id: str = "P1",
    area: Fraction = Fraction(10),
    holders: tuple = (("H1", Fraction(10)),),
    record_date: date = date(1980, 1, 1),
) -> SurveyRecord:
    return SurveyRecord(
        id=f"SR_{parcel_id}",
        parcel_id=parcel_id,
        survey="BS",
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
# SPEC Test 1 to 5: Rule R1
# ---------------------------------------------------------------------------

class TestRuleR1:
    def test_1_7_decimal_from_10_passes(self):
        """SPEC Test 1: A 7-decimal transfer from a 10-decimal holding passes."""
        sr = make_sr(area=Fraction(10), holders=(("H1", Fraction(10)),))
        e1 = make_sale("E1", "H1", "H2", 7, date(2000, 1, 1), seq=1)
        history = make_history(sr, events=(e1,), baseline_complete=True)

        alert = run_rule(check_r1, e1, history, [e1])

        assert alert.rule_id == "R1"
        assert alert.status == Status.CONSISTENT
        assert alert.message_key == MSG_CONSISTENT
        assert "E1" in alert.evidence_ids
        assert len(alert.evidence_ids) > 0

    def test_2_following_5_decimal_fails_r1_with_excess_2(self):
        """SPEC Test 2: A following 5-decimal transfer fails R1 with excess exactly 2."""
        sr = make_sr(area=Fraction(10), holders=(("H1", Fraction(10)),))
        e1 = make_sale("E1", "H1", "H2", 7, date(2000, 1, 1), seq=1)
        e2 = make_sale("E2", "H1", "H3", 5, date(2001, 1, 1), seq=2)
        history = make_history(sr, events=(e1, e2), baseline_complete=True)

        alert = run_rule(check_r1, e2, history, [e1, e2])

        assert alert.rule_id == "R1"
        assert alert.status == Status.CONTRADICTION
        assert alert.message_key == MSG_R1_CONTRADICTION
        assert "requested 5" in alert.calculation
        assert "available 3" in alert.calculation
        assert "excess 2" in alert.calculation
        assert "E2" in alert.evidence_ids
        assert "E1" in alert.evidence_ids

    def test_3_reversed_dates_replayed_chronologically(self):
        """
        SPEC Test 3: The same events with reversed dates are replayed
        chronologically and give the correct outcome.
        E1: H1 transfers 7 to H2.
        E2: H2 transfers 5 to H3.
        If E1 is on 2000-01-01 and E2 on 2001-01-01, H2 has 7 when selling 5 -> passes.
        """
        sr = make_sr(area=Fraction(10), holders=(("H1", Fraction(10)),))
        e1 = make_sale("E1", "H1", "H2", 7, date(2000, 1, 1), seq=1)
        e2 = make_sale("E2", "H2", "H3", 5, date(2001, 1, 1), seq=2)
        history = make_history(sr, events=(e1, e2), baseline_complete=True)

        # Input given in reverse chronological order [e2, e1]
        alert_e1 = run_rule(check_r1, e1, history, [e2, e1])
        alert_e2 = run_rule(check_r1, e2, history, [e2, e1])

        assert alert_e1.status == Status.CONSISTENT
        assert alert_e2.status == Status.CONSISTENT

    def test_4_r1_baseline_complete_false_returns_review(self):
        """SPEC Test 4: R1 with baseline_complete false returns Review Required."""
        sr = make_sr(area=Fraction(10), holders=(("H1", Fraction(10)),))
        e1 = make_sale("E1", "H1", "H2", 7, date(2000, 1, 1), seq=1)
        e2 = make_sale("E2", "H1", "H3", 5, date(2001, 1, 1), seq=2)
        # baseline_complete is False
        history = make_history(sr, events=(e1, e2), baseline_complete=False)

        alert = run_rule(check_r1, e2, history, [e1, e2])

        assert alert.rule_id == "R1"
        assert alert.status == Status.REVIEW
        assert alert.message_key == MSG_R1_REVIEW_INCOMPLETE_BASELINE
        assert "excess 2" in alert.calculation

    def test_5_r1_missing_event_date_returns_review(self):
        """SPEC Test 5: R1 with baseline_complete true but missing event date returns Review Required."""
        sr = make_sr(area=Fraction(10), holders=(("H1", Fraction(10)),))
        e_undated = make_sale("E1", "H1", "H2", 7, None, seq=1)
        history = make_history(sr, events=(e_undated,), baseline_complete=True)

        alert = run_rule(check_r1, e_undated, history, [e_undated])

        assert alert.rule_id == "R1"
        assert alert.status == Status.REVIEW
        assert len(alert.evidence_ids) > 0


# ---------------------------------------------------------------------------
# SPEC Test 6: Rule R2
# ---------------------------------------------------------------------------

class TestRuleR2:
    def test_6_part_a_duplicate_portion_triggers_contradiction(self):
        """
        SPEC Test 6 Part A: The same portion_id sold twice via lineage triggers R2.
        """
        sr = make_sr()
        e1 = make_sale(
            "E1", "H1", "H2", 5, date(2000, 1, 1), seq=1,
            portion_id="PORTION_NORTH", linked_event_id="PARENT_DEED_1"
        )
        e2 = make_sale(
            "E2", "H1", "H3", 5, date(2001, 1, 1), seq=2,
            portion_id="PORTION_NORTH", linked_event_id="PARENT_DEED_1"
        )

        alert = run_rule(check_r2, e2, [e1, e2], sr)

        assert alert.rule_id == "R2"
        assert alert.status == Status.CONTRADICTION
        assert alert.message_key == MSG_R2_CONTRADICTION
        assert "E2" in alert.evidence_ids
        assert "E1" in alert.evidence_ids

    def test_6_part_b_same_deed_different_portions_does_not_trigger_contradiction(self):
        """
        SPEC Test 6 Part B: The same deed_no with different portion_ids does not trigger Contradiction.
        Must never match on dag/deed number alone.
        """
        sr = make_sr()
        # Same deed_id "DEED_99", but different portion_id
        e1 = make_sale(
            "E1", "H1", "H2", 3, date(2000, 1, 1), seq=1,
            deed_id="DEED_99", portion_id="PORTION_NORTH", linked_event_id="PARENT_DEED_1"
        )
        e2 = make_sale(
            "E2", "H1", "H3", 3, date(2001, 1, 1), seq=2,
            deed_id="DEED_99", portion_id="PORTION_SOUTH", linked_event_id="PARENT_DEED_1"
        )

        alert = run_rule(check_r2, e2, [e1, e2], sr)

        assert alert.rule_id == "R2"
        assert alert.status == Status.REVIEW
        assert alert.message_key == MSG_R2_REVIEW_UNESTABLISHED


# ---------------------------------------------------------------------------
# Rule R3 Tests (Clean, Review, Contradiction, and Mutual Exclusivity with R1)
# ---------------------------------------------------------------------------

class TestRuleR3:
    def test_r3_clean_recorded_holder(self):
        """R3 Clean: Seller is a recorded holder in baseline. Returns CONSISTENT."""
        sr = make_sr(holders=(("H1", Fraction(10)),))
        e1 = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1)
        history = make_history(sr, events=(e1,), baseline_complete=True)

        alert = run_rule(check_r3, e1, history, [e1])

        assert alert.rule_id == "R3"
        assert alert.status == Status.CONSISTENT
        assert alert.message_key == MSG_CONSISTENT

    def test_r3_review_incomplete_baseline(self):
        """R3 Review: Seller is unrecorded, but baseline is incomplete. Returns REVIEW."""
        sr = make_sr(holders=(("H1", Fraction(10)),))
        # H_STRANGER is not in baseline
        e1 = make_sale("E1", "H_STRANGER", "H2", 5, date(2000, 1, 1), seq=1)
        history = make_history(sr, events=(e1,), baseline_complete=False)

        alert = run_rule(check_r3, e1, history, [e1])

        assert alert.rule_id == "R3"
        assert alert.status == Status.REVIEW
        assert alert.message_key == MSG_R3_REVIEW_INCOMPLETE_BASELINE

    def test_r3_contradiction_complete_baseline(self):
        """R3 Contradiction: Seller is unrecorded, baseline is complete. Returns CONTRADICTION."""
        sr = make_sr(holders=(("H1", Fraction(10)),))
        e1 = make_sale("E1", "H_STRANGER", "H2", 5, date(2000, 1, 1), seq=1)
        history = make_history(sr, events=(e1,), baseline_complete=True)

        alert = run_rule(check_r3, e1, history, [e1])

        assert alert.rule_id == "R3"
        assert alert.status == Status.CONTRADICTION
        assert alert.message_key == MSG_R3_CONTRADICTION

    def test_r1_vs_r3_mutual_exclusivity(self):
        """
        One case must not give both alerts:
          - Unrecorded seller: R3 gives CONTRADICTION, R1 does NOT contradict.
          - Recorded seller with excess: R1 gives CONTRADICTION, R3 gives CONSISTENT.
        """
        sr = make_sr(area=Fraction(10), holders=(("H1", Fraction(10)),))

        # Case A: Unrecorded seller H_STRANGER
        e_stranger = make_sale("E_S", "H_STRANGER", "H2", 5, date(2000, 1, 1), seq=1)
        hist_a = make_history(sr, events=(e_stranger,), baseline_complete=True)
        r3_a = run_rule(check_r3, e_stranger, hist_a, [e_stranger])
        r1_a = run_rule(check_r1, e_stranger, hist_a, [e_stranger])
        assert r3_a.status == Status.CONTRADICTION
        assert r1_a.status != Status.CONTRADICTION  # R1 does not fire

        # Case B: Recorded seller H1 selling 15 from 10
        e_excess = make_sale("E_X", "H1", "H2", 15, date(2000, 1, 1), seq=1)
        hist_b = make_history(sr, events=(e_excess,), baseline_complete=True)
        r3_b = run_rule(check_r3, e_excess, hist_b, [e_excess])
        r1_b = run_rule(check_r1, e_excess, hist_b, [e_excess])
        assert r3_b.status == Status.CONSISTENT      # R3 confirms recorded interest
        assert r1_b.status == Status.CONTRADICTION  # R1 flags excess share


# ---------------------------------------------------------------------------
# Rule R6 Tests (Clean, Review Mismatch, Review Missing Deed)
# ---------------------------------------------------------------------------

class TestRuleR6:
    def test_r6_clean_mutation_reconciles_with_deed(self):
        """R6 Clean: Mutation area and details match the deed sale. Returns CONSISTENT."""
        sr = make_sr()
        deed = Deed(id="D1", deed_no="DEED_101", registration_date=date(2000, 1, 1))
        e_sale = make_sale("E_S1", "H1", "H2", 5, date(2000, 1, 1), seq=1, deed_id="D1")
        e_mut = Event(
            id="E_M1", type=EventType.MUTATION, seq=2,
            event_date=date(2000, 6, 1), parcel_id="P1",
            from_person=None, to_person="H2", area=Fraction(5),
            deed_id="D1", portion_id=None, linked_event_id="E_S1", source_record_id=None,
        )

        alert = run_rule(check_r6, e_mut, deed, [e_sale, e_mut], sr)

        assert alert.rule_id == "R6"
        assert alert.status == Status.CONSISTENT
        assert alert.message_key == MSG_R6_CONSISTENT
        assert "E_M1" in alert.evidence_ids
        assert "D1" in alert.evidence_ids

    def test_r6_review_mutation_area_mismatch(self):
        """R6 Review: Mutation area does not match deed sale area. Returns REVIEW."""
        sr = make_sr()
        deed = Deed(id="D1", deed_no="DEED_101", registration_date=date(2000, 1, 1))
        e_sale = make_sale("E_S1", "H1", "H2", 5, date(2000, 1, 1), seq=1, deed_id="D1")
        # Mutation claims 6 decimals instead of 5
        e_mut = Event(
            id="E_M1", type=EventType.MUTATION, seq=2,
            event_date=date(2000, 6, 1), parcel_id="P1",
            from_person=None, to_person="H2", area=Fraction(6),
            deed_id="D1", portion_id=None, linked_event_id="E_S1", source_record_id=None,
        )

        alert = run_rule(check_r6, e_mut, deed, [e_sale, e_mut], sr)

        assert alert.rule_id == "R6"
        assert alert.status == Status.REVIEW
        assert alert.message_key == MSG_R6_REVIEW_MISMATCH

    def test_r6_review_missing_deed(self):
        """R6 Review: Deed is not supplied. Returns REVIEW."""
        sr = make_sr()
        e_mut = Event(
            id="E_M1", type=EventType.MUTATION, seq=1,
            event_date=date(2000, 6, 1), parcel_id="P1",
            from_person=None, to_person="H2", area=Fraction(5),
            deed_id=None, portion_id=None, linked_event_id=None, source_record_id=None,
        )

        alert = run_rule(check_r6, e_mut, None, [e_mut], sr)

        assert alert.rule_id == "R6"
        assert alert.status == Status.REVIEW


# ---------------------------------------------------------------------------
# History Hygiene and i18n Verification
# ---------------------------------------------------------------------------

class TestHistoryHygieneAndI18n:
    def test_undated_event_in_history_forces_review_on_all_rules(self):
        """If ANY event in history is undated, dependent rules return Review Required."""
        sr = make_sr(holders=(("H1", Fraction(10)),))
        e_valid = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1)
        e_undated = make_sale("E2", "H2", "H3", 2, None, seq=2)
        history = make_history(sr, events=(e_valid, e_undated), baseline_complete=True)

        alert_r1 = run_rule(check_r1, e_valid, history, [e_valid, e_undated])
        alert_r3 = run_rule(check_r3, e_valid, history, [e_valid, e_undated])

        assert alert_r1.status == Status.REVIEW
        assert alert_r1.message_key == MSG_REVIEW_UNDATED_HISTORY
        assert alert_r3.status == Status.REVIEW
        assert alert_r3.message_key == MSG_REVIEW_UNDATED_HISTORY

    def test_unsupported_cancel_in_history_forces_review(self):
        """If history contains an invalid CANCEL, dependent rules return Review Required."""
        sr = make_sr(holders=(("H1", Fraction(10)),))
        e_valid = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1)
        e_bad_cancel = Event(
            id="EC_BAD", type=EventType.CANCEL, seq=2,
            event_date=date(2001, 1, 1), parcel_id="P1",
            from_person=None, to_person=None, area=None,
            deed_id=None, portion_id=None, linked_event_id="NONEXISTENT", source_record_id=None,
        )
        history = make_history(sr, events=(e_valid, e_bad_cancel), baseline_complete=True)

        alert = run_rule(check_r1, e_valid, history, [e_valid, e_bad_cancel])
        assert alert.status == Status.REVIEW
        assert alert.message_key == MSG_REVIEW_UNSUPPORTED_HISTORY

    def test_all_message_and_next_step_keys_translate_in_both_locales(self):
        """Ensure all Alert keys exist and resolve in bn.json and en.json."""
        sr = make_sr()
        e1 = make_sale("E1", "H1", "H2", 5, date(2000, 1, 1), seq=1)
        history = make_history(sr, events=(e1,), baseline_complete=True)

        alert = run_rule(check_r1, e1, history, [e1])

        # Message key translation
        assert translate(alert.message_key, "en") != alert.message_key
        assert translate(alert.message_key, "bn") != alert.message_key

        # Recommended next step translation
        assert translate(alert.recommended_next_step, "en") != alert.recommended_next_step
        assert translate(alert.recommended_next_step, "bn") != alert.recommended_next_step
