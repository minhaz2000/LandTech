"""
Tests for simulate.py — Pure-Function Simulation Engine.
Covers:
  - Dataset hash unchanged before and after simulation
  - Two runs give identical alerts (determinism)
  - 7 from 10 passes, then a second proposal of 5 fails R1 with excess 2
  - Parametrized mix of valid and invalid proposals covering R1, R2, R3
  - Rejected simulation leaves stored events unchanged
"""

from datetime import date
from fractions import Fraction
import pytest

from jomigraph.engine.rules import Status
from jomigraph.engine.simulate import (
    SimulationResult,
    evaluate,
    hash_dataset,
    simulate,
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


class TestSimulationPurityAndInvariance:
    def test_dataset_hash_unchanged_after_simulation(self):
        """Simulation never mutates stored dataset; canonical SHA256 matches exactly."""
        sr = make_sr(area=Fraction(10))
        e1 = make_sale("E1", "H1", "H2", 3, date(2000, 1, 1), seq=1)
        events = [e1]
        history = make_history(sr, events=tuple(events), baseline_complete=True)

        # Baseline hash before simulation
        hash_before = hash_dataset(events, [sr])

        # Proposed event
        proposed = make_sale("E_PROP", "H1", "H3", 4, date(2001, 1, 1), seq=0)

        # Run simulation
        result = simulate(events, proposed, history)

        # Hash after simulation
        hash_after = hash_dataset(events, [sr])

        assert hash_before == hash_after
        assert len(events) == 1
        assert events[0] is e1
        assert proposed.seq == 0  # original proposed object sequence unchanged

    def test_two_simulation_runs_give_identical_alerts(self):
        """Pure simulation is deterministic; two runs produce identical results."""
        sr = make_sr(area=Fraction(10))
        e1 = make_sale("E1", "H1", "H2", 7, date(2000, 1, 1), seq=1)
        events = [e1]
        history = make_history(sr, events=tuple(events), baseline_complete=True)

        proposed = make_sale("E_PROP", "H1", "H3", 5, date(2001, 1, 1), seq=0)

        res1 = simulate(events, proposed, history)
        res2 = simulate(events, proposed, history)

        assert res1.proposed_event == res2.proposed_event
        assert res1.available_before == res2.available_before
        assert res1.available_after == res2.available_after
        assert res1.alerts == res2.alerts
        assert res1.r1_calculation == res2.r1_calculation

    def test_rejected_simulation_leaves_stored_events_unchanged(self):
        """When simulation detects contradiction, underlying history is completely unmutated."""
        sr = make_sr(area=Fraction(10))
        e1 = make_sale("E1", "H1", "H2", 8, date(2000, 1, 1), seq=1)
        events = [e1]
        history = make_history(sr, events=tuple(events), baseline_complete=True)

        # Propose transfer of 5 decimals when only 2 remain -> Contradiction!
        proposed_invalid = make_sale("E_INVALID", "H1", "H3", 5, date(2001, 1, 1), seq=0)

        result = simulate(events, proposed_invalid, history)

        # Contradiction flagged in alerts
        r1_alert = next((a for a in result.alerts if a.rule_id == "R1"), None)
        assert r1_alert is not None
        assert r1_alert.status == Status.CONTRADICTION

        # Underlying events list is unchanged
        assert len(events) == 1
        assert events[0].id == "E1"
        assert result.available_before == Fraction(2)
        assert result.available_after == Fraction(-3)  # counterfactual state computed


class TestSimulationCalculations:
    def test_7_from_10_passes_then_second_proposal_of_5_fails_r1(self):
        """
        Sequence of simulations:
        1. H1 has 10. Proposed sale of 7 passes with available_before=10, after=3.
        2. Proposing a further sale of 5 from state after E1 fails with excess 2.
        """
        sr = make_sr(area=Fraction(10))
        history_init = make_history(sr, events=(), baseline_complete=True)

        # Simulation 1: H1 proposes 7 from 10
        prop_1 = make_sale("E_P1", "H1", "H2", 7, date(2000, 1, 1), seq=0)
        res_1 = simulate([], prop_1, history_init)

        assert res_1.proposed_event.seq == 1
        assert res_1.available_before == Fraction(10)
        assert res_1.available_after == Fraction(3)
        r1_alert_1 = next(a for a in res_1.alerts if a.rule_id == "R1")
        assert r1_alert_1.status == Status.CONSISTENT

        # Simulation 2: Now assume E_P1 occurred (now in baseline events)
        e1_accepted = res_1.proposed_event
        events_stage2 = [e1_accepted]
        history_stage2 = make_history(sr, events=(e1_accepted,), baseline_complete=True)

        prop_2 = make_sale("E_P2", "H1", "H3", 5, date(2001, 1, 1), seq=0)
        res_2 = simulate(events_stage2, prop_2, history_stage2)

        assert res_2.proposed_event.seq == 2
        assert res_2.available_before == Fraction(3)
        assert res_2.available_after == Fraction(-2)
        r1_alert_2 = next(a for a in res_2.alerts if a.rule_id == "R1")
        assert r1_alert_2.status == Status.CONTRADICTION
        assert "requested 5" in res_2.r1_calculation
        assert "available 3" in res_2.r1_calculation
        assert "excess 2" in res_2.r1_calculation


class TestSimulationParametrizedRules:
    @pytest.mark.parametrize(
        "from_p, area, portion_id, linked_id, expected_rule, expected_status",
        [
            # Valid R1 & R3: H1 has 10, sells 4 -> CONSISTENT
            ("H1", 4, None, None, "R1", Status.CONSISTENT),
            # Invalid R1: H1 has 10, sells 12 -> CONTRADICTION
            ("H1", 12, None, None, "R1", Status.CONTRADICTION),
            # Invalid R3: Unrecorded stranger sells 2 -> CONTRADICTION on R3
            ("H_STRANGER", 2, None, None, "R3", Status.CONTRADICTION),
            # Invalid R2: Duplicate portion allocation
            ("H1", 2, "PORTION_ALPHA", "PARENT_DEED", "R2", Status.CONTRADICTION),
        ],
    )
    def test_parametrized_proposals(
        self, from_p, area, portion_id, linked_id, expected_rule, expected_status
    ):
        """Parametrized verification of valid and invalid proposals covering R1, R2, R3."""
        sr = make_sr(area=Fraction(10), holders=(("H1", Fraction(10)),))
        # Prior event that allocated PORTION_ALPHA
        e_prior = make_sale(
            "E_PRIOR", "H1", "H2", 2, date(2000, 1, 1), seq=1,
            portion_id="PORTION_ALPHA", linked_event_id="PARENT_DEED"
        )
        events = [e_prior]
        history = make_history(sr, events=tuple(events), baseline_complete=True)

        proposed = make_sale(
            "E_PROP", from_p, "H_BUYER", area, date(2001, 1, 1), seq=0,
            portion_id=portion_id, linked_event_id=linked_id
        )

        result = simulate(events, proposed, history)

        matching_alert = next((a for a in result.alerts if a.rule_id == expected_rule), None)
        assert matching_alert is not None, f"Alert for {expected_rule} was not generated: {result.alerts}"
        assert matching_alert.status == expected_status
