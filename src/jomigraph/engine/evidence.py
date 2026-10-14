"""
JomiGraph AI — Minimal Evidence and Impact Lookup
=================================================
SPEC § Minimal Evidence:
  "The engine removes one candidate record at a time and re-runs the rule,
  keeping a record only if removing it makes the violation disappear...
  Deletion order can change the result, so the engine returns all alternative
  minimal sets it finds."

Architecture:
  - Enumerates subsets strictly by size (size 0, 1, 2, ... up to cap of 12).
  - Baseline survey records, CANCEL events (+ linked events), and CORRECT
    events are fixed anchors and are never deletion candidates.
  - Supersets of already-found minimal sets are pruned.
  - Returns all alternative minimal evidence sets.
"""

from __future__ import annotations

from itertools import combinations
from typing import Callable, Sequence

from jomigraph.engine.replay import anchor_ids_for_parcel
from jomigraph.engine.rules import Alert, Status
from jomigraph.models import Event, EventType, SurveyRecord

CANDIDATE_CAP = 12


class MinimalEvidenceResult(list):
    """
    List of minimal evidence set tuples.
    If the number of deletion candidates exceeded candidate_cap, not_minimized is True
    and the result contains the full unminimized candidate set (plus anchors).
    """
    def __init__(self, sets: Sequence[tuple[str, ...]], not_minimized: bool = False):
        super().__init__(sets)
        self.not_minimized = not_minimized


def minimal_evidence(
    eval_fn: Callable[[Sequence[Event]], Alert],
    all_events: Sequence[Event],
    baseline_record: SurveyRecord,
    trigger_event: Event,
    candidate_cap: int = CANDIDATE_CAP,
) -> MinimalEvidenceResult:
    """
    Find all inclusion-minimal evidence sets that establish a Contradiction.

    eval_fn:
        A callable taking a list of events and returning an Alert.
    all_events:
        The full history of events on the parcel.
    baseline_record:
        Baseline SurveyRecord (always a fixed anchor).
    trigger_event:
        The evaluated event (always included).
    candidate_cap:
        Maximum number of deletion candidates to consider (default 12).
        If candidate count exceeds candidate_cap, returns the full candidate
        set with not_minimized=True (never truncates silently).

    Returns:
        MinimalEvidenceResult (list subclass) containing sorted tuples of record/event IDs.
    """
    # Verify baseline contradiction exists
    initial_alert = eval_fn(all_events)
    if initial_alert.status != Status.CONTRADICTION:
        return MinimalEvidenceResult([], not_minimized=False)

    # 1. Identify fixed anchors
    # Baseline survey record, CANCEL events, linked cancelled events, CORRECT events
    raw_anchor_ids = anchor_ids_for_parcel(all_events, trigger_event.parcel_id)
    anchor_event_ids = set(raw_anchor_ids)
    anchor_event_ids.add(trigger_event.id)

    # Partition events into anchors and deletion candidates
    anchor_events = [e for e in all_events if e.id in anchor_event_ids]
    candidate_events = [e for e in all_events if e.id not in anchor_event_ids]

    base_anchor_ids = set(anchor_event_ids)
    base_anchor_ids.add(baseline_record.id)

    # If candidates exceed candidate_cap, return full candidate set with not_minimized=True
    if len(candidate_events) > candidate_cap:
        full_evidence = tuple(sorted(base_anchor_ids | set(e.id for e in candidate_events)))
        return MinimalEvidenceResult([full_evidence], not_minimized=True)

    candidate_ids = [e.id for e in candidate_events]
    candidate_by_id = {e.id: e for e in candidate_events}

    minimal_candidate_subsets: list[set[str]] = []

    # Enumerate subsets by size k = 0, 1, 2, ...
    for k in range(len(candidate_ids) + 1):
        for combo in combinations(candidate_ids, k):
            combo_set = set(combo)

            # Prune if combo_set is a superset of any known minimal subset
            if any(known.issubset(combo_set) for known in minimal_candidate_subsets):
                continue

            # Build event subset: anchors + candidate combo
            subset_events = anchor_events + [candidate_by_id[cid] for cid in combo]

            alert = eval_fn(subset_events)
            if alert.status == Status.CONTRADICTION:
                # Minimality verification: removing any single candidate must make violation disappear
                is_minimal = True
                for remove_id in combo:
                    reduced = [e for e in subset_events if e.id != remove_id]
                    if eval_fn(reduced).status == Status.CONTRADICTION:
                        is_minimal = False
                        break

                if is_minimal:
                    minimal_candidate_subsets.append(combo_set)

    # Format result: each minimal set includes baseline_record.id + anchors + minimal candidate subset
    result: list[tuple[str, ...]] = []

    for c_set in minimal_candidate_subsets:
        full_evidence = sorted(base_anchor_ids | c_set)
        result.append(tuple(full_evidence))

    # If no candidates were needed (anchors alone contradict), return anchors
    if not result and eval_fn(anchor_events).status == Status.CONTRADICTION:
        result.append(tuple(sorted(base_anchor_ids)))

    return MinimalEvidenceResult(result, not_minimized=False)


def impact_lookup(
    event_id: str,
    all_events: Sequence[Event],
) -> list[str]:
    """
    SPEC Additions: "Impact view: list later events that depend on the conflicting event."
    Returns sorted list of event IDs that reference event_id via linked_event_id or source_record_id.
    """
    dependents = [
        e.id for e in all_events
        if e.id != event_id
        and (e.linked_event_id == event_id or e.source_record_id == event_id)
    ]
    return sorted(dependents)


def impact_closure(
    event_id: str,
    all_events: Sequence[Event],
) -> list[str]:
    """
    Compute transitive downstream impact of event_id.
    Includes:
      (a) Events referencing event_id (or any impacted event) via linked_event_id or source_record_id transitively.
      (b) Later events (by seq/date) on the same parcel with the same non-null portion_id.
      (c) Later events on the same parcel whose from_person is the to_person of an impacted event (derived title).
      (d) Cycle-safe and never includes event_id itself.
    """
    root_event = next((e for e in all_events if e.id == event_id), None)
    if root_event is None:
        return []

    def is_later(e_later: Event, e_earlier: Event) -> bool:
        if e_later.event_date and e_earlier.event_date:
            return (e_later.event_date, e_later.seq) > (e_earlier.event_date, e_earlier.seq)
        return e_later.seq > e_earlier.seq

    impacted_ids: set[str] = set()
    queue = [root_event]
    visited_for_queue = {event_id}

    while queue:
        current = queue.pop(0)
        for candidate in all_events:
            if candidate.id == event_id or candidate.id in impacted_ids:
                continue

            is_dependent = False

            # (a) Transitive link via linked_event_id or source_record_id
            if candidate.linked_event_id == current.id or candidate.source_record_id == current.id:
                is_dependent = True

            # (b) Same parcel, same non-null portion_id, later in time
            elif (
                candidate.parcel_id == current.parcel_id
                and current.portion_id is not None
                and candidate.portion_id == current.portion_id
                and is_later(candidate, current)
            ):
                is_dependent = True

            # (c) Derived title: later event on same parcel where from_person == current.to_person
            elif (
                candidate.parcel_id == current.parcel_id
                and current.to_person is not None
                and candidate.from_person == current.to_person
                and is_later(candidate, current)
            ):
                is_dependent = True

            if is_dependent:
                impacted_ids.add(candidate.id)
                if candidate.id not in visited_for_queue:
                    visited_for_queue.add(candidate.id)
                    queue.append(candidate)

    impacted_ids.discard(event_id)
    return sorted(impacted_ids)

