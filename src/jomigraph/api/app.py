"""
JomiGraph AI — FastAPI Application
==================================
Routes:
  - GET  /parcels?lang=bn|en
  - GET  /parcel/{id}?lang=bn|en
  - POST /simulate
  - GET  /benchmark
"""

from __future__ import annotations

from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any, Optional, Sequence

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from jomigraph.api.graph import build_parcel_graph
from jomigraph.api.schemas import (
    AlertDetail,
    BenchmarkResponse,
    CitizenAlertDetail,
    CitizenParcelDetailResponse,
    CitizenReportResponse,
    CoverageRowItem,
    EventDetail,
    HolderDetail,
    ParcelDetailResponse,
    ParcelListItem,
    ProposedEventDetail,
    ReportParcelItem,
    ReportRecordsDetail,
    ReviewerAlertDetail,
    ReviewerReportResponse,
    SearchResultItem,
    SimulateRequest,
    SimulateResponse,
    SimulationIntegrityResult,
    SurveyRecordDetail,
)
from jomigraph.engine.benchmark import evaluate_dataset, evaluate_history
from jomigraph.engine.evidence import MinimalEvidenceResult, impact_closure, impact_lookup, minimal_evidence
from jomigraph.engine.rules import (
    Alert,
    Status,
    check_r1,
    check_r2,
    check_r3,
    check_r4,
    check_r7,
)
from jomigraph.engine.simulate import hash_dataset, simulate
from jomigraph.i18n import translate
from jomigraph.loader import Dataset, get_clean_false_alarms_and_coverage, load_dataset
from jomigraph.models import Event, EventType, ParcelHistory, SurveyRecord, load_fraction


DEFAULT_DATASET_PATH = Path("data/demo_family.json")

EN_TO_BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
BN_TO_EN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def to_bangla_digits(val: Any) -> str:
    """Convert ASCII digits in a number/string to Bangla digits."""
    return str(val).translate(EN_TO_BN_DIGITS)


def normalize_for_search(val: Any) -> str:
    """Normalize text for search by converting Bengali digits to ASCII, lowercasing, and stripping."""
    if val is None:
        return ""
    return str(val).translate(BN_TO_EN_DIGITS).lower().strip()


def compute_overall_status(alerts: Sequence[Alert], lang: str = "bn") -> str:
    """Return worst status across alerts, localized."""
    if any(a.status == Status.CONTRADICTION for a in alerts):
        raw = Status.CONTRADICTION.value
    elif any(a.status == Status.REVIEW for a in alerts):
        raw = Status.REVIEW.value
    else:
        raw = Status.CONSISTENT.value
    return localize_status(raw, lang=lang)


def build_minimal_evidence_and_impact(
    a: Alert,
    history: ParcelHistory,
    ds: Dataset,
) -> tuple[list[list[str]], bool, list[str]]:
    """
    Reuse minimal_evidence() and impact_closure() from engine/evidence.py.
    Returns (minimal_evidence_sets, not_minimized, impact_event_ids).
    """
    event_by_id = {e.id: e for e in history.events}
    trigger_event = event_by_id.get(a.evidence_ids[0]) if a.evidence_ids else None
    if trigger_event is None:
        trigger_event = next((e for e in history.events if e.id in a.evidence_ids), None)
    impact_ids: list[str] = []
    if trigger_event is not None:
        impact_ids = impact_closure(trigger_event.id, history.events)

    if a.status != Status.CONTRADICTION or trigger_event is None:
        return [], False, impact_ids

    baseline = history.survey_records[0]

    # Build rule-specific eval_fn
    if a.rule_id == "R1":
        def eval_fn(subset: Sequence[Event]) -> Alert:
            sub_hist = ParcelHistory(
                parcel_id=history.parcel_id,
                baseline_record_id=history.baseline_record_id,
                baseline_complete=history.baseline_complete,
                start_record_id=history.start_record_id,
                end_date=history.end_date,
                survey_records=history.survey_records,
                events=tuple(subset),
            )
            return check_r1(trigger_event, sub_hist, subset)
    elif a.rule_id == "R2":
        def eval_fn(subset: Sequence[Event]) -> Alert:
            return check_r2(trigger_event, subset, baseline)
    elif a.rule_id == "R3":
        def eval_fn(subset: Sequence[Event]) -> Alert:
            sub_hist = ParcelHistory(
                parcel_id=history.parcel_id,
                baseline_record_id=history.baseline_record_id,
                baseline_complete=history.baseline_complete,
                start_record_id=history.start_record_id,
                end_date=history.end_date,
                survey_records=history.survey_records,
                events=tuple(subset),
            )
            return check_r3(trigger_event, sub_hist, subset)
    elif a.rule_id == "R4":
        child_parcel_ids = {p.id for p in ds.parcels if p.parent_id == history.parcel_id}
        child_srs = [sr for h in ds.histories if h.parcel_id in child_parcel_ids for sr in h.survey_records]
        def eval_fn(subset: Sequence[Event]) -> Alert:
            return check_r4(trigger_event, child_srs, subset, baseline)
    elif a.rule_id == "R7":
        deed = ds.get_deed(trigger_event.deed_id) if trigger_event.deed_id else None
        def eval_fn(subset: Sequence[Event]) -> Alert:
            return check_r7(trigger_event, deed, subset, baseline)
    else:
        return [list(a.evidence_ids)], False, impact_ids

    res: MinimalEvidenceResult = minimal_evidence(
        eval_fn=eval_fn,
        all_events=history.events,
        baseline_record=baseline,
        trigger_event=trigger_event,
    )

    min_sets = [list(s) for s in res] if res else [list(a.evidence_ids)]
    return min_sets, res.not_minimized, impact_ids


STATUS_TRANSLATIONS = {
    "bn": {
        "Consistent with supplied records": "সঙ্গতিপূর্ণ",
        "Review Required": "পর্যালোচনা প্রয়োজন",
        "Contradiction Found": "অসঙ্গতি পাওয়া গেছে",
        "CONSISTENT": "সঙ্গতিপূর্ণ",
        "REVIEW": "পর্যালোচনা প্রয়োজন",
        "CONTRADICTION": "অসঙ্গতি পাওয়া গেছে",
    },
    "en": {
        "Consistent with supplied records": "Consistent with supplied records",
        "Review Required": "Review Required",
        "Contradiction Found": "Contradiction Found",
        "CONSISTENT": "Consistent with supplied records",
        "REVIEW": "Review Required",
        "CONTRADICTION": "Contradiction Found",
    },
}


def localize_status(status_val: str, lang: str = "bn") -> str:
    """Return localized status string for the given language."""
    return STATUS_TRANSLATIONS.get(lang, {}).get(status_val, status_val)


def localize_calculation(calc: str, rule_id: str, lang: str = "bn") -> str:
    """
    Localize calculation string for Bangla when lang == 'bn'.
    Translates templates, numbers into Bangla digits, and explanations.
    """
    if lang != "bn" or not calc:
        return calc

    import re

    # R1 calculation templates
    m_r1_excess = re.match(
        r"requested\s+([0-9/.]+),\s+available\s+([0-9/.\-]+),\s+excess\s+([0-9/.]+)(?:,\s+baseline incomplete)?",
        calc,
    )
    if m_r1_excess:
        req, avail, excess = m_r1_excess.groups()
        bn_str = f"অনুরোধকৃত {to_bangla_digits(req)}, প্রাপ্য {to_bangla_digits(avail)}, অতিরিক্ত {to_bangla_digits(excess)}"
        if "baseline incomplete" in calc:
            bn_str += ", ভিত্তি জরিপ অসম্পূর্ণ"
        return bn_str

    m_r1_ok = re.match(r"requested\s+([0-9/.]+),\s+available\s+([0-9/.\-]+)", calc)
    if m_r1_ok:
        req, avail = m_r1_ok.groups()
        return f"অনুরোধকৃত {to_bangla_digits(req)}, প্রাপ্য {to_bangla_digits(avail)}"

    if "is not a recorded holder; evaluated under R3" in calc:
        m = re.search(r"Seller '([^']+)'", calc)
        seller = m.group(1) if m else ""
        return f"বিক্রেতা '{seller}' রেকর্ডভুক্ত অংশীদার নন; নিয়ম ৩ এর অধীনে মূল্যায়িত।"

    if "Event date, seller, or transfer area is missing" in calc:
        return "তারিখ, বিক্রেতা বা হস্তান্তরিত জমির পরিমাণ অনুপস্থিত।"

    # R3 calculation templates
    if "has documented recorded interest in parcel history" in calc:
        m = re.search(r"Seller '([^']+)'", calc)
        seller = m.group(1) if m else ""
        return f"বিক্রেতা '{seller}' এর খতিয়ান বা ইতিহাসে রেকর্ডকৃত স্বার্থ রয়েছে।"

    if "is not a recorded holder and baseline is complete" in calc:
        m = re.search(r"Seller '([^']+)'", calc)
        seller = m.group(1) if m else ""
        return f"বিক্রেতা '{seller}' কোনো রেকর্ডভুক্ত অংশীদার নন এবং ভিত্তি জরিপ সম্পূর্ণ।"

    if "has no recorded interest, but baseline is incomplete" in calc:
        m = re.search(r"Seller '([^']+)'", calc)
        seller = m.group(1) if m else ""
        return f"বিক্রেতা '{seller}' রেকর্ডভুক্ত নন এবং ভিত্তি জরিপ অসম্পূর্ণ।"

    if "Event date or seller information is missing" in calc:
        return "তারিখ বা বিক্রেতার তথ্য অনুপস্থিত।"

    # R2 calculation templates
    if "allocated in" in calc:
        m = re.search(r"Portion '([^']+)'", calc)
        p = m.group(1) if m else ""
        return f"পোর্শন '{p}' ইতিপূর্বে অন্য হস্তান্তরে বরাদ্দ রয়েছে (দ্বৈত বণ্টন চিহ্নিত)।"

    if "No duplicate allocation for portion" in calc:
        m = re.search(r"Portion '([^']+)'", calc)
        p = m.group(1) if m else ""
        return f"পোর্শন '{p}' এর কোনো দ্বৈত বণ্টন পাওয়া যায়নি (সঙ্গতিপূর্ণ)।"

    if "Same deed" in calc:
        return "একই দলিল একাধিক ভিন্ন পোর্শনে ব্যবহৃত হয়েছে; পর্যালোচনা প্রয়োজন।"

    if "Portion ID or lineage link is missing" in calc:
        return "পোর্শন আইডি বা বংশলতিকা তথ্য অনুপস্থিত।"

    # R4 calculation templates
    if "Children total" in calc:
        m = re.search(r"differs from parent.*?by\s+([0-9/.]+)", calc)
        diff = m.group(1) if m else ""
        return f"উপ-বিভাগে খণ্ডিত প্লটের মোট জমির সাথে মূল দাগের অমিল রয়েছে (পার্থক্য: {to_bangla_digits(diff)} শতক)।"

    if "All subdivide children survey records reconcile exactly" in calc:
        return "উপ-বিভাগের সকল খণ্ডিত প্লটের জরিপের মোট পরিমাণ মূল দাগের সমান।"

    # R5, R6, R7 calculation templates
    if "Adjacent survey records linked by event" in calc:
        return "পরপর জরিপ রেকর্ডের মধ্যে সংযোগকারী দলিল বা ইভেন্ট বিদ্যমান।"

    if "No linking event or deed found between adjacent survey records" in calc:
        return "পরপর দুটি জরিপ রেকর্ডের মধ্যে কোনো সংযোগ দলিল বা প্রমাণ নেই।"

    if "Deed and mutation reconcile exactly" in calc:
        return "দলিল ও নামজারির (মিউটেশন) তথ্য সম্পূর্ণভাবে সামঞ্জস্যপূর্ণ।"

    if "Mutation area" in calc and "differs from deed" in calc:
        return "নামজারির জমির পরিমাণ দলিলের সাথে মেলেনি।"

    if "Deed registration date" in calc:
        return "দলিল ও নামজারির তারিখের ধারাবাহিকতা পরীক্ষা করা হয়েছে।"

    if "History contains undated event" in calc:
        return "দাগের ইতিহাসে তারিখবিহীন ঘটনা রয়েছে; পর্যালোচনা প্রয়োজন।"

    if "History contains unsupported" in calc:
        return "ইতিহাসে অসংগত বা ভিত্তিহীন বাতিল/সংশোধন ঘটনা রয়েছে।"

    return to_bangla_digits(calc)


def create_app(dataset: Optional[Dataset] = None, dataset_path: Optional[Path | str] = None) -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="JomiGraph AI",
        description="Rule-based land transaction consistency and simulation engine.",
        version="0.1.0",
    )

    # CORS configuration for web frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Load and cache dataset
    if dataset is not None:
        loaded_dataset = dataset
    else:
        path = Path(dataset_path or DEFAULT_DATASET_PATH)
        if not path.is_file():
            # Generate dataset if missing
            from data.generator import generate_and_save
            generate_and_save(path, seed=42)
        loaded_dataset = load_dataset(path)

    app.state.dataset = loaded_dataset

    # -----------------------------------------------------------------------
    # GET /parcels?lang=bn|en
    # -----------------------------------------------------------------------
    @app.get("/parcels", response_model=list[ParcelListItem])
    def get_parcels(lang: str = Query("bn", pattern="^(bn|en)$")) -> list[ParcelListItem]:
        """List all parcels with label, status summary, and planted/clean category."""
        ds: Dataset = app.state.dataset
        items: list[ParcelListItem] = []

        for p in ds.parcels:
            history = ds.get_history(p.id)
            is_planted = "PLANTED" in p.id.upper()
            category = "planted" if is_planted else "clean"

            # Compute label
            if lang == "bn":
                label = f"{p.mouza} দাগ {p.dag_no}"
            else:
                label = f"{p.mouza} Dag {p.dag_no}"

            # Compute status summary
            if history is not None:
                alerts = evaluate_history(history, ds.parcels, ds.deeds, ds.histories)
                has_contradiction = any(a.status == Status.CONTRADICTION for a in alerts)
                has_review = any(a.status == Status.REVIEW for a in alerts)

                if has_contradiction:
                    status_summary = "CONTRADICTION"
                elif has_review:
                    status_summary = "REVIEW"
                else:
                    status_summary = "CONSISTENT"
            else:
                status_summary = "CONSISTENT"

            items.append(
                ParcelListItem(
                    id=p.id,
                    label=label,
                    status_summary=status_summary,
                    planted=is_planted,
                    category=category,
                )
            )

        return items

    # -----------------------------------------------------------------------
    # GET /parcel/{id}?lang=bn|en&role=citizen|reviewer
    # -----------------------------------------------------------------------
    @app.get("/parcel/{parcel_id}")
    def get_parcel(
        parcel_id: str,
        lang: str = Query("bn", pattern="^(bn|en)$"),
        role: str = Query("reviewer", pattern="^(citizen|reviewer)$"),
    ) -> ParcelDetailResponse | CitizenParcelDetailResponse:
        """
        Get parcel details, survey records, events timeline, Cytoscape graph, and evaluated alerts.
        # This is a demo role, not authentication.
        """
        ds: Dataset = app.state.dataset
        parcel = ds.get_parcel(parcel_id)
        if parcel is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parcel '{parcel_id}' not found.",
            )

        history = ds.get_history(parcel_id)
        if history is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"History for parcel '{parcel_id}' not found.",
            )

        # 1. Survey records
        srs: list[SurveyRecordDetail] = []
        for sr in history.survey_records:
            holders: list[HolderDetail] = []
            for pid, area in sr.holders:
                person = ds.get_person(pid)
                holders.append(
                    HolderDetail(
                        person_id=pid,
                        person_name=person.name if person else pid,
                        area=str(area),
                    )
                )
            srs.append(
                SurveyRecordDetail(
                    id=sr.id,
                    parcel_id=sr.parcel_id,
                    survey=sr.survey,
                    khatian_no=sr.khatian_no,
                    record_date=sr.record_date.isoformat(),
                    recorded_area=str(sr.recorded_area),
                    holders=holders,
                )
            )

        # 2. Events timeline
        events: list[EventDetail] = []
        for e in history.events:
            from_name = ds.get_person(e.from_person).name if e.from_person and ds.get_person(e.from_person) else None
            to_name = ds.get_person(e.to_person).name if e.to_person and ds.get_person(e.to_person) else None
            events.append(
                EventDetail(
                    id=e.id,
                    type=e.type.value,
                    seq=e.seq,
                    event_date=e.event_date.isoformat() if e.event_date else None,
                    parcel_id=e.parcel_id,
                    from_person=e.from_person,
                    from_person_name=from_name,
                    to_person=e.to_person,
                    to_person_name=to_name,
                    area=str(e.area) if e.area is not None else None,
                    deed_id=e.deed_id,
                    portion_id=e.portion_id,
                    linked_event_id=e.linked_event_id,
                    source_record_id=e.source_record_id,
                )
            )

        # 3. Cytoscape graph
        graph_data = build_parcel_graph(history, ds, lang=lang)

        # 4. Evaluated alerts
        raw_alerts = evaluate_history(history, ds.parcels, ds.deeds, ds.histories)
        overall_status = compute_overall_status(raw_alerts, lang=lang)

        if role == "citizen":
            non_consistent = [a for a in raw_alerts if a.status != Status.CONSISTENT]
            citizen_alerts = [
                CitizenAlertDetail(
                    status=localize_status(a.status.value, lang=lang),
                    message=translate(a.message_key, lang=lang),
                    recommended_next_step=translate(a.recommended_next_step, lang=lang),
                )
                for a in non_consistent
            ]
            return CitizenParcelDetailResponse(
                id=parcel.id,
                dag_no=parcel.dag_no,
                mouza=parcel.mouza,
                parent_id=parcel.parent_id,
                overall_status=overall_status,
                survey_records=srs,
                events=events,
                graph=graph_data,  # type: ignore[arg-type]
                alerts=citizen_alerts,
            )
        else:  # reviewer
            reviewer_alerts: list[ReviewerAlertDetail] = []
            for a in raw_alerts:
                min_sets, not_min, impacts = build_minimal_evidence_and_impact(a, history, ds)
                reviewer_alerts.append(
                    ReviewerAlertDetail(
                        rule_id=a.rule_id,
                        status=localize_status(a.status.value, lang=lang),
                        message=translate(a.message_key, lang=lang),
                        recommended_next_step=translate(a.recommended_next_step, lang=lang),
                        evidence_ids=list(a.evidence_ids),
                        calculation=localize_calculation(a.calculation, a.rule_id, lang=lang),
                        minimal_evidence_sets=min_sets,
                        not_minimized=not_min,
                        impact_event_ids=impacts,
                    )
                )

            return ParcelDetailResponse(
                id=parcel.id,
                dag_no=parcel.dag_no,
                mouza=parcel.mouza,
                parent_id=parcel.parent_id,
                overall_status=overall_status,
                survey_records=srs,
                events=events,
                graph=graph_data,  # type: ignore[arg-type]
                alerts=reviewer_alerts,
            )

    # -----------------------------------------------------------------------
    # POST /simulate
    # -----------------------------------------------------------------------
    @app.post("/simulate", response_model=SimulateResponse)
    def post_simulate(payload: SimulateRequest) -> SimulateResponse:
        """
        Counterfactual simulation of a proposed transaction.
        Never mutates or persists any data in the dataset.
        """
        ds: Dataset = app.state.dataset
        history = ds.get_history(payload.parcel_id)
        if history is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parcel history for '{payload.parcel_id}' not found.",
            )

        # Build proposed Event with exact Fraction area
        prop_area = load_fraction(payload.area)
        
        # Determine from_person (support 'H' alias for holder in lab demo/parcels)
        from_person_id = payload.from_person
        if from_person_id.upper() == "H" and history.survey_records:
            from_person_id = history.survey_records[0].holders[0][0]

        # Determine date: default to parcel's latest event date (or later), never an arbitrary date
        if payload.date and payload.date.strip():
            prop_date = date.fromisoformat(payload.date.strip())
        else:
            dated_events = [e for e in history.events if e.event_date is not None]
            if dated_events:
                prop_date = max(e.event_date for e in dated_events)
            elif history.survey_records:
                prop_date = max(sr.record_date for sr in history.survey_records)
            else:
                prop_date = date.today()

        to_person_id = payload.to_person or "P_BUYER_SIM"

        proposed_event = Event(
            id="PROPOSED_EVENT",
            type=EventType.SALE,
            seq=0,  # simulate() assigns max_seq + 1
            event_date=prop_date,
            parcel_id=payload.parcel_id,
            from_person=from_person_id,
            to_person=to_person_id,
            area=prop_area,
            deed_id=payload.deed_id,
            portion_id=payload.portion_id,
            linked_event_id=None,
            source_record_id=None,
        )

        # Pure counterfactual simulation
        sim_res = simulate(
            events=history.events,
            proposed=proposed_event,
            parcel_history=history,
            deeds=ds.deeds,
        )

        lang = payload.lang

        # Format alerts with localization
        formatted_alerts = [
            AlertDetail(
                rule_id=a.rule_id,
                status=localize_status(a.status.value, lang=lang),
                message=translate(a.message_key, lang=lang),
                recommended_next_step=translate(a.recommended_next_step, lang=lang),
                evidence_ids=list(a.evidence_ids),
                calculation=localize_calculation(a.calculation, a.rule_id, lang=lang),
            )
            for a in sim_res.alerts
        ]

        r1_calc_out = (
            localize_calculation(sim_res.r1_calculation, "R1", lang=lang)
            if sim_res.r1_calculation
            else None
        )

        return SimulateResponse(
            proposed_event=ProposedEventDetail(
                id=sim_res.proposed_event.id,
                type=sim_res.proposed_event.type.value,
                seq=sim_res.proposed_event.seq,
                event_date=sim_res.proposed_event.event_date.isoformat() if sim_res.proposed_event.event_date else None,
                parcel_id=sim_res.proposed_event.parcel_id,
                from_person=sim_res.proposed_event.from_person,
                to_person=sim_res.proposed_event.to_person,
                area=str(sim_res.proposed_event.area),
                deed_id=sim_res.proposed_event.deed_id,
                portion_id=sim_res.proposed_event.portion_id,
            ),
            available_before=str(sim_res.available_before),
            available_after=str(sim_res.available_after),
            r1_calculation=r1_calc_out,
            alerts=formatted_alerts,
        )

    # -----------------------------------------------------------------------
    # GET /benchmark
    # -----------------------------------------------------------------------
    @app.get("/benchmark", response_model=BenchmarkResponse)
    def get_benchmark() -> BenchmarkResponse:
        """
        Evaluate dataset benchmark metrics:
          - Clean false-alarm count (must be 0)
          - Coverage table for R1-R7
          - Simulation integrity test (hash verification before and after)
        """
        ds: Dataset = app.state.dataset
        clean_false_alarms, coverage_table = get_clean_false_alarms_and_coverage(ds)

        # Compute dataset canonical hash before simulation
        all_events = [e for h in ds.histories for e in h.events]
        all_srs = [sr for h in ds.histories for sr in h.survey_records]
        hash_before = hash_dataset(all_events, all_srs)

        # Run a sample counterfactual simulation on the first parcel
        target_history = ds.histories[0]
        sample_proposed = Event(
            id="BENCHMARK_PROBE",
            type=EventType.SALE,
            seq=0,
            event_date=date(2020, 1, 1),
            parcel_id=target_history.parcel_id,
            from_person=target_history.survey_records[0].holders[0][0],
            to_person="P_BENCHMARK_PROBE",
            area=Fraction(1),
            deed_id=None,
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        _ = simulate(target_history.events, sample_proposed, target_history, ds.deeds)

        # Compute dataset canonical hash after simulation
        all_events_after = [e for h in ds.histories for e in h.events]
        all_srs_after = [sr for h in ds.histories for sr in h.survey_records]
        hash_after = hash_dataset(all_events_after, all_srs_after)

        return BenchmarkResponse(
            clean_false_alarm_count=clean_false_alarms,
            coverage_table=[
                CoverageRowItem(
                    rule_id=row.rule_id,
                    has_planted_case=row.has_planted_case,
                    detected=row.detected,
                    status_detected=row.status_detected,
                )
                for row in coverage_table
            ],
            simulation_integrity=SimulationIntegrityResult(
                dataset_hash_before=hash_before,
                dataset_hash_after=hash_after,
                unchanged=(hash_before == hash_after),
            ),
        )

    # -----------------------------------------------------------------------
    # GET /search?q=...&lang=bn|en
    # -----------------------------------------------------------------------
    @app.get("/search", response_model=list[SearchResultItem])
    def search_parcels(
        q: str = Query("", description="Search query string"),
        lang: str = Query("bn", pattern="^(bn|en)$"),
    ) -> list[SearchResultItem]:
        """
        Search parcels across ID, dag number, holder name, khatian number, and deed number.
        Case-insensitive and accepts both Bangla and English digits.
        Empty or single-character queries return an empty list.
        """
        if not q or len(q.strip()) <= 1:
            return []

        q_norm = normalize_for_search(q)
        ds: Dataset = app.state.dataset
        results: list[SearchResultItem] = []

        for p in ds.parcels:
            history = ds.get_history(p.id)
            matched_field = None

            if q_norm in normalize_for_search(p.id):
                matched_field = "parcel_id"
            elif q_norm in normalize_for_search(p.dag_no):
                matched_field = "dag_no"
            elif history:
                for sr in history.survey_records:
                    for pid, _ in sr.holders:
                        person = ds.get_person(pid)
                        if person and q_norm in normalize_for_search(person.name):
                            matched_field = "holder_name"
                            break
                    if matched_field:
                        break

            if not matched_field and history:
                for sr in history.survey_records:
                    if q_norm in normalize_for_search(sr.khatian_no):
                        matched_field = "khatian_no"
                        break

            if not matched_field and history:
                for e in history.events:
                    if e.deed_id:
                        deed = ds.get_deed(e.deed_id)
                        if deed and (
                            q_norm in normalize_for_search(deed.deed_no)
                            or q_norm in normalize_for_search(deed.id)
                        ):
                            matched_field = "deed_no"
                            break

            if matched_field:
                label = f"{p.mouza} দাগ {p.dag_no}" if lang == "bn" else f"{p.mouza} Dag {p.dag_no}"
                results.append(
                    SearchResultItem(
                        id=p.id,
                        parcel_id=p.id,
                        dag_no=p.dag_no,
                        mouza=p.mouza,
                        label=label,
                        matched_on=matched_field,
                    )
                )

        return results

    # -----------------------------------------------------------------------
    # GET /report/{parcel_id}?lang=bn|en&role=citizen|reviewer
    # -----------------------------------------------------------------------
    @app.get("/report/{parcel_id}")
    def get_report(
        parcel_id: str,
        lang: str = Query("bn", pattern="^(bn|en)$"),
        role: str = Query("citizen", pattern="^(citizen|reviewer)$"),
    ) -> ReviewerReportResponse | CitizenReportResponse:
        """
        Return structured case summary report for the parcel.
        # This is a demo role, not authentication.
        """
        ds: Dataset = app.state.dataset
        parcel = ds.get_parcel(parcel_id)
        if parcel is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parcel '{parcel_id}' not found.",
            )

        history = ds.get_history(parcel_id)
        if history is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"History for parcel '{parcel_id}' not found.",
            )

        # 1. Survey records
        srs: list[SurveyRecordDetail] = []
        for sr in history.survey_records:
            holders: list[HolderDetail] = []
            for pid, area in sr.holders:
                person = ds.get_person(pid)
                holders.append(
                    HolderDetail(
                        person_id=pid,
                        person_name=person.name if person else pid,
                        area=str(area),
                    )
                )
            srs.append(
                SurveyRecordDetail(
                    id=sr.id,
                    parcel_id=sr.parcel_id,
                    survey=sr.survey,
                    khatian_no=sr.khatian_no,
                    record_date=sr.record_date.isoformat(),
                    recorded_area=str(sr.recorded_area),
                    holders=holders,
                )
            )

        # 2. Events timeline
        events: list[EventDetail] = []
        for e in history.events:
            from_name = ds.get_person(e.from_person).name if e.from_person and ds.get_person(e.from_person) else None
            to_name = ds.get_person(e.to_person).name if e.to_person and ds.get_person(e.to_person) else None
            events.append(
                EventDetail(
                    id=e.id,
                    type=e.type.value,
                    seq=e.seq,
                    event_date=e.event_date.isoformat() if e.event_date else None,
                    parcel_id=e.parcel_id,
                    from_person=e.from_person,
                    from_person_name=from_name,
                    to_person=e.to_person,
                    to_person_name=to_name,
                    area=str(e.area) if e.area is not None else None,
                    deed_id=e.deed_id,
                    portion_id=e.portion_id,
                    linked_event_id=e.linked_event_id,
                    source_record_id=e.source_record_id,
                )
            )

        label = f"{parcel.mouza} দাগ {parcel.dag_no}" if lang == "bn" else f"{parcel.mouza} Dag {parcel.dag_no}"
        parcel_info = ReportParcelItem(
            id=parcel.id,
            dag_no=parcel.dag_no,
            mouza=parcel.mouza,
            parent_id=parcel.parent_id,
            label=label,
        )

        records_info = ReportRecordsDetail(
            survey_records=srs,
            events=events,
        )

        # Canonical dataset hash
        all_events = [e for h in ds.histories for e in h.events]
        all_srs = [sr for h in ds.histories for sr in h.survey_records]
        ds_hash = hash_dataset(all_events, all_srs)

        # Localized disclaimer (no forbidden words)
        if lang == "bn":
            disclaimer = "ডেমো, কাল্পনিক তথ্য, আইনি সিদ্ধান্ত নয়। এটি একটি নিয়মভিত্তিক সিদ্ধান্ত-সহায়ক প্রোটোটাইপ, যা কোনো আইনি রায় প্রদান করে না।"
        else:
            disclaimer = "Demo, fictional data, not a legal ruling. JomiGraph AI is a rule-based decision-support prototype; it never certifies legal ownership."

        raw_alerts = evaluate_history(history, ds.parcels, ds.deeds, ds.histories)
        overall_status = compute_overall_status(raw_alerts, lang=lang)

        if role == "citizen":
            non_consistent = [a for a in raw_alerts if a.status != Status.CONSISTENT]
            citizen_alerts = [
                CitizenAlertDetail(
                    status=localize_status(a.status.value, lang=lang),
                    message=translate(a.message_key, lang=lang),
                    recommended_next_step=translate(a.recommended_next_step, lang=lang),
                )
                for a in non_consistent
            ]
            target_for_steps = non_consistent if non_consistent else raw_alerts
            next_steps = list(dict.fromkeys(translate(a.recommended_next_step, lang=lang) for a in target_for_steps))
            return CitizenReportResponse(
                parcel_id=parcel.id,
                parcel=parcel_info,
                role=role,
                lang=lang,
                overall_status=overall_status,
                records=records_info,
                alerts=citizen_alerts,
                recommended_next_steps=next_steps,
                disclaimer=disclaimer,
                dataset_hash=ds_hash,
            )
        else:  # reviewer
            next_steps = list(dict.fromkeys(translate(a.recommended_next_step, lang=lang) for a in raw_alerts))
            reviewer_alerts: list[ReviewerAlertDetail] = []
            for a in raw_alerts:
                min_sets, not_min, impacts = build_minimal_evidence_and_impact(a, history, ds)
                reviewer_alerts.append(
                    ReviewerAlertDetail(
                        rule_id=a.rule_id,
                        status=localize_status(a.status.value, lang=lang),
                        message=translate(a.message_key, lang=lang),
                        recommended_next_step=translate(a.recommended_next_step, lang=lang),
                        evidence_ids=list(a.evidence_ids),
                        calculation=localize_calculation(a.calculation, a.rule_id, lang=lang),
                        minimal_evidence_sets=min_sets,
                        not_minimized=not_min,
                        impact_event_ids=impacts,
                    )
                )

            return ReviewerReportResponse(
                parcel_id=parcel.id,
                parcel=parcel_info,
                role=role,
                lang=lang,
                overall_status=overall_status,
                records=records_info,
                alerts=reviewer_alerts,
                recommended_next_steps=next_steps,
                disclaimer=disclaimer,
                dataset_hash=ds_hash,
            )

    # -----------------------------------------------------------------------
    # Static UI Files & Root Route
    # -----------------------------------------------------------------------
    ui_dir = Path(__file__).resolve().parent.parent / "ui"

    @app.get("/ui-strings")
    def get_ui_strings() -> dict:
        """Expose ui_strings for client inspection and automated tests."""
        strings_file = ui_dir / "strings.json"
        if strings_file.is_file():
            import json
            with open(strings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    if ui_dir.is_dir():
        from fastapi.responses import FileResponse
        from starlette.staticfiles import StaticFiles

        @app.get("/", response_class=FileResponse)
        def serve_index() -> FileResponse:
            """Serve the single-page application entry point."""
            return FileResponse(ui_dir / "index.html")

        app.mount("/", StaticFiles(directory=str(ui_dir), html=True), name="ui")

    return app


# Default application instance
app = create_app()
