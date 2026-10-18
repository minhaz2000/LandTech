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

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware

from jomigraph.api.extras import dataset_for, register_extras
from jomigraph.api.graph import build_parcel_graph
from jomigraph.api.schemas import (
    AlertDetail,
    BenchmarkResponse,
    CitizenAlertDetail,
    CitizenParcelDetailResponse,
    CitizenReportResponse,
    CitizenSimulateResponse,
    CoownerQuotaDetail,
    CoverageRowItem,
    EventDetail,
    ExtendedBenchmarkResponse,
    HolderDetail,
    ParcelDetailResponse,
    ParcelListItem,
    Phase10BenchmarkDetail,
    Phase11FeaturesBenchmarkDetail,
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
    USSDRequest,
    USSDResponse,
    VerifyDeedRequest,
    VerifyDeedResponse,
)
from jomigraph.traditional_share import (
    TRADITIONAL_SHARE_DISCLAIMER_BN,
    TRADITIONAL_SHARE_DISCLAIMER_EN,
    calculate_coowner_quotas,
    format_traditional_share,
)
from jomigraph.engine.benchmark import evaluate_dataset, evaluate_extended_dataset, evaluate_history
from jomigraph.engine.deed_hash import build_deed_qr_payload, hash_deed_content
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
from jomigraph.engine.next_steps import get_rule_next_steps
from jomigraph.engine.scoring import compute_attention_score
from jomigraph.engine.simulate import hash_dataset, simulate
from jomigraph.engine.ussd import process_ussd_step
from jomigraph.area_input import parse_area
from jomigraph.i18n import (
    MSG_R12_CONTRADICTION,
    MSG_R12_CONSISTENT,
    MSG_R12_REVIEW_NO_HASH,
    NEXT_STEP_R12,
    translate,
)
from jomigraph.loader import Dataset, get_clean_false_alarms_and_coverage, load_dataset
from jomigraph.models import Event, EventType, ParcelHistory, SurveyRecord, load_fraction


# Anchored to this file, not the working directory, so the server starts
# correctly from any folder. Layout: <repo>/src/jomigraph/api/app.py
DEFAULT_DATASET_PATH = Path(__file__).resolve().parents[3] / "data" / "demo_family.json"

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


def to_status_code(val: Any) -> str:
    """Convert any Status enum or status string into a stable uppercase status_code."""
    if isinstance(val, Status):
        return val.name
    if isinstance(val, str):
        val_upper = val.strip().upper()
        if "CONTRADICTION" in val_upper or "অসঙ্গতি" in val:
            return "CONTRADICTION"
        if "REVIEW" in val_upper or "পর্যালোচনা" in val:
            return "REVIEW"
        if "CONSISTENT" in val_upper or "সঙ্গতিপূর্ণ" in val:
            return "CONSISTENT"
        try:
            return Status(val).name
        except Exception:
            pass
    return "UNKNOWN"


def compute_overall_status(alerts: Sequence[Alert], lang: str = "bn") -> tuple[str, str]:
    """Return (localized_status, status_code)."""
    if any(a.status == Status.CONTRADICTION for a in alerts):
        code = "CONTRADICTION"
        raw = Status.CONTRADICTION.value
    elif any(a.status == Status.REVIEW for a in alerts):
        code = "REVIEW"
        raw = Status.REVIEW.value
    else:
        code = "CONSISTENT"
        raw = Status.CONSISTENT.value
    return localize_status(raw, lang=lang), code


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
    if trigger_event is not None and a.status in (Status.CONTRADICTION, Status.REVIEW):
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

    if "Portion boundary descriptors are missing, partial, or ambiguous" in calc:
        return "খণ্ডের সীমানার বিবরণ অসম্পূর্ণ, আংশিক বা অস্পষ্ট; পৃথক ভূখণ্ড যাচাই করা সম্ভব হয়নি।"

    if "conflicts with prior recorded transfer" in calc:
        return f"দাগ/সীমানার বিবরণ পূর্ববর্তী হস্তান্তরের সাথে সংঘর্ষপূর্ণ: {to_bangla_digits(calc)}"

    if "are distinct and non-overlapping with recorded transfers" in calc:
        return "উক্ত খণ্ডের সীমানা রেকর্ডকৃত পূর্ববর্তী দলিলের সাথে কোনো দ্বৈত বা সংঘর্ষ তৈরি করে না (স্বতন্ত্র)।"

    # Phase 9 calculations (R9, R10, R11)
    if "is recorded after government flag date" in calc:
        return f"সরকারি খাস/অধিগ্রহণ ঘোষণার তারিখের পর উক্ত হস্তান্তর দলিল সম্পাদিত হয়েছে: {to_bangla_digits(calc)}"

    if "has government khas or acquisition flag" in calc and "flag_date is missing" in calc:
        return "উক্ত দাগে সরকারি খাস বা অধিগ্রহণ ফ্ল্যাগ রয়েছে কিন্তু কার্যকরের তারিখ অনুপস্থিত; পর্যালোচনা প্রয়োজন।"

    if "is subject to an active court injunction" in calc:
        return "উক্ত দাগটি আদালতের সক্রিয় নিষেধাজ্ঞা বা ইনজাংশনের অধীন; আদালতের নিষ্পত্তি ব্যতিরেকে হস্তান্তর পর্যালোচনা প্রয়োজন।"

    if "is subject to pending court case" in calc:
        return f"উক্ত দাগটি আদালতে বিচারাধীন মামলার বিষয়বস্তু: {to_bangla_digits(calc)}"

    if "No active government acquisition, khas declaration, or court injunction" in calc:
        return "উক্ত দাগে সরকারি খাস, অধিগ্রহণ বা আদালতের কোনো সক্রিয় নিষেধাজ্ঞা নেই।"

    if "remains unreleased" in calc or "occurred before prior mortgage" in calc:
        return f"উক্ত দাগ বা অংশের ওপর পূর্বে গৃহীত বন্ধক বা দায় অপরিশোধিত রয়েছে: {to_bangla_digits(calc)}"

    if "Second mortgage on portion" in calc and "unreleased" in calc:
        return f"একই দাগ/অংশের ওপর পূর্বে গৃহীত বন্ধক অপরিশোধিত অবস্থায় নতুন বন্ধক রেকর্ড করা হয়েছে: {to_bangla_digits(calc)}"

    if "lacks an event date" in calc or "has no explicit release" in calc:
        return f"বন্ধক বা বন্ধক মুক্তির নথিতে গ্রহণযোগ্য তারিখ বা মূল বন্ধকের রেফারেন্স অসম্পূর্ণ: {to_bangla_digits(calc)}"

    if "All prior mortgages on parcel/portion were released" in calc or "No active unreleased mortgage" in calc:
        return "কোনো সক্রিয় অপরিশোধিত বন্ধক নেই বা পূর্ববর্তী বন্ধক বিধিসম্মতভাবে অবমুক্ত হয়েছে।"

    if "is recorded under revoked power of attorney" in calc:
        return f"আমমোক্তারনামা বাতিলের পর উক্ত ক্ষমতা ব্যবহার করে লেনদেনের চেষ্টা করা হয়েছে: {to_bangla_digits(calc)}"

    if "dated prior to power of attorney grant" in calc:
        return f"আমমোক্তারনামা কার্যকরের তারিখের পূর্বে লেনদেন সম্পন্ন করার চেষ্টা করা হয়েছে: {to_bangla_digits(calc)}"

    if "Power of attorney grant event" in calc and "not found" in calc:
        return f"আমমোক্তারনামার সনদ বা মঞ্জুরির নথি পাওয়া যায়নি: {to_bangla_digits(calc)}"

    if "POA scope or authority is ambiguous" in calc or "lacks an event date" in calc:
        return f"আমমোক্তারনামার সীমা বা কর্তৃত্ব অস্পষ্ট; পর্যালোচনা প্রয়োজন: {to_bangla_digits(calc)}"

    if "Direct conveyance by recorded owner" in calc or "Validly executed under active power of attorney" in calc:
        return "রেকর্ডকৃত মালিক কর্তৃক সরাসরি হস্তান্তর বা সক্রিয় আমমোক্তারনামার অধীনে সম্পাদিত।"

    # R8 Heir declaration calculation templates
    if "No heir declarations recorded in parcel history." in calc:
        return "খতিয়ান বা ইতিহাসে কোনো ওয়ারিশ ঘোষণার রেকর্ড নেই।"

    if "is omitted from subsequent record" in calc and "without any recorded deed" in calc:
        return f"ঘোষিত ওয়ারিশ পরবর্তী রেকর্ডে কোনো হস্তান্তর বা না-দাবি দলিল ছাড়াই বাদ পড়েছেন: {to_bangla_digits(calc)}"

    if "is accounted for by recorded deed" in calc:
        return f"ঘোষিত ওয়ারিশ খতিয়ানে অনুপস্থিত থাকলেও রেজিস্ট্রিকৃত দলিলের মাধ্যমে স্বার্থ নিষ্পত্তি রয়েছে: {to_bangla_digits(calc)}"

    if "All declared heirs under declaration" in calc:
        return f"ঘোষিত সকল ওয়ারিশ পরবর্তী খতিয়ানে যথাযথভাবে অন্তর্ভুক্ত বা নিষ্পত্তি রয়েছে: {to_bangla_digits(calc)}"

    if "Declared heir" in calc and "and review is required" in calc:
        return f"ঘোষিত ওয়ারিশের তথ্য পরবর্তী রেকর্ডের সাথে অসম্পূর্ণ বা অস্পষ্ট; পর্যালোচনা প্রয়োজন: {to_bangla_digits(calc)}"

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
    register_extras(app)

    # -----------------------------------------------------------------------
    # GET /parcels?lang=bn|en
    # -----------------------------------------------------------------------
    @app.get("/parcels", response_model=list[ParcelListItem], response_model_exclude_none=True)
    def get_parcels(
        lang: str = Query("bn", pattern="^(bn|en)$"),
        role: str = Query("reviewer", pattern="^(citizen|reviewer)$"),
    ) -> list[ParcelListItem]:
        """
        List all parcels with label and status summary.
        The reviewer role also gets the staging fields (planted, category).
        The citizen role never receives them. Demo role, not authentication.
        """
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
                alerts = evaluate_history(
                    history,
                    all_parcels=ds.parcels,
                    all_deeds=ds.deeds,
                    all_histories=ds.histories,
                    all_persons=ds.persons,
                )
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

            is_locked = bool(
                p.is_khas
                or p.under_acquisition
                or p.injunction
                or (p.court_case_no and p.case_status == "pending")
            )

            items.append(
                ParcelListItem(
                    id=p.id,
                    label=label,
                    status_summary=status_summary,
                    status_summary_code=status_summary,
                    status_code=status_summary,
                    planted=is_planted if role == "reviewer" else None,
                    category=category if role == "reviewer" else None,
                    is_khas=p.is_khas if p.is_khas else None,
                    under_acquisition=p.under_acquisition if p.under_acquisition else None,
                    court_case_no=p.court_case_no if p.court_case_no else None,
                    injunction=p.injunction if p.injunction else None,
                    is_locked=is_locked if is_locked else None,
                )
            )

        return items

    # -----------------------------------------------------------------------
    # GET /parcel/{id}?lang=bn|en&role=citizen|reviewer
    # -----------------------------------------------------------------------
    @app.get("/parcel/{parcel_id}")
    def get_parcel(
        parcel_id: str,
        response: Response,
        lang: str = Query("bn", pattern="^(bn|en)$"),
        role: str = Query("reviewer", pattern="^(citizen|reviewer)$"),
    ) -> ParcelDetailResponse | CitizenParcelDetailResponse:
        """
        Get parcel details, survey records, events timeline, Cytoscape graph, and evaluated alerts.
        # This is a demo role, not authentication.
        """
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        ds: Dataset = dataset_for(app, parcel_id)
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
                trad_share = None
                share_frac_str = None
                if sr.recorded_area and sr.recorded_area > 0:
                    frac = area / sr.recorded_area
                    share_frac_str = f"{frac.numerator}/{frac.denominator}" if frac.denominator != 1 else str(frac.numerator)
                    trad_share = format_traditional_share(frac, lang=lang, include_fraction=True)
                holders.append(
                    HolderDetail(
                        person_id=pid,
                        person_name=person.name if person else pid,
                        area=str(area),
                        share_fraction=share_frac_str,
                        traditional_share=trad_share,
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
                    via_poa_id=e.via_poa_id,
                )
            )

        # 3. Cytoscape graph
        graph_data = build_parcel_graph(history, ds, lang=lang)

        # 4. Evaluated alerts
        raw_alerts = evaluate_history(
            history,
            all_parcels=ds.parcels,
            all_deeds=ds.deeds,
            all_histories=ds.histories,
            all_persons=ds.persons,
        )
        overall_status, overall_status_code = compute_overall_status(raw_alerts, lang=lang)

        is_locked = bool(
            parcel
            and (
                parcel.is_khas
                or parcel.under_acquisition
                or parcel.injunction
                or (parcel.court_case_no and parcel.case_status == "pending")
            )
        )

        # Co-owner quota breakdown for Ejmali parcels
        coowner_quotas: Optional[list[CoownerQuotaDetail]] = None
        trad_disclaimer: Optional[str] = None
        if history.survey_records:
            latest_sr = history.survey_records[-1]
            if len(latest_sr.holders) > 1 and latest_sr.recorded_area > 0:
                raw_quotas = calculate_coowner_quotas(latest_sr.holders, latest_sr.recorded_area, lang=lang)
                coowner_quotas = []
                for q in raw_quotas:
                    p = ds.get_person(q["person_id"])
                    p_name = p.name if p else q["person_id"]
                    coowner_quotas.append(
                        CoownerQuotaDetail(
                            person_id=q["person_id"],
                            person_name=p_name,
                            recorded_area=str(q["recorded_area"]),
                            quota_limit=str(q["quota_limit"]),
                            share_fraction=str(q["share_fraction"]),
                            traditional_share=q["traditional_share"],
                        )
                    )
                trad_disclaimer = (
                    TRADITIONAL_SHARE_DISCLAIMER_BN if lang == "bn" else TRADITIONAL_SHARE_DISCLAIMER_EN
                )

        # Attention Score (F18)
        score_data = compute_attention_score(raw_alerts, lang=lang)

        if role == "citizen":
            non_consistent = [a for a in raw_alerts if a.status != Status.CONSISTENT]
            citizen_alerts = [
                CitizenAlertDetail(
                    status=localize_status(a.status.value, lang=lang),
                    status_code=a.status.name,
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
                overall_status_code=overall_status_code,
                survey_records=srs,
                events=events,
                graph=graph_data,  # type: ignore[arg-type]
                alerts=citizen_alerts,
                coowner_quotas=coowner_quotas,
                traditional_share_disclaimer=trad_disclaimer,
                is_khas=parcel.is_khas,
                under_acquisition=parcel.under_acquisition,
                flag_date=parcel.flag_date.isoformat() if parcel.flag_date else None,
                court_case_no=parcel.court_case_no,
                case_status=parcel.case_status,
                injunction=parcel.injunction,
                is_locked=is_locked,
                attention_score=score_data["score"],
                traffic_light=score_data["traffic_light"],
                score_summary=score_data["summary"],
                score_disclaimer=score_data["disclaimer"],
            )
        else:  # reviewer
            reviewer_alerts: list[ReviewerAlertDetail] = []
            for a in raw_alerts:
                min_sets, not_min, impacts = build_minimal_evidence_and_impact(a, history, ds)
                reviewer_alerts.append(
                    ReviewerAlertDetail(
                        rule_id=a.rule_id,
                        status=localize_status(a.status.value, lang=lang),
                        status_code=a.status.name,
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
                overall_status_code=overall_status_code,
                survey_records=srs,
                events=events,
                graph=graph_data,  # type: ignore[arg-type]
                alerts=reviewer_alerts,
                coowner_quotas=coowner_quotas,
                traditional_share_disclaimer=trad_disclaimer,
                is_khas=parcel.is_khas,
                under_acquisition=parcel.under_acquisition,
                flag_date=parcel.flag_date.isoformat() if parcel.flag_date else None,
                court_case_no=parcel.court_case_no,
                case_status=parcel.case_status,
                injunction=parcel.injunction,
                is_locked=is_locked,
                attention_score=score_data["score"],
                traffic_light=score_data["traffic_light"],
                score_factors=score_data["factors"],
                score_disclaimer=score_data["disclaimer"],
            )

    # -----------------------------------------------------------------------
    # POST /simulate
    # -----------------------------------------------------------------------
    @app.post("/simulate", response_model=None)
    def post_simulate(
        payload: SimulateRequest,
        lang: Optional[str] = Query(None, pattern="^(bn|en)$"),
        role: str = Query("reviewer", pattern="^(citizen|reviewer)$"),
    ) -> SimulateResponse | CitizenSimulateResponse:
        """
        Counterfactual simulation of a proposed transaction.
        Never mutates or persists any data in the dataset.
        The citizen role gets a response without rule IDs, calculations or
        evidence IDs. This is a demo role, not authentication.
        """
        ds: Dataset = dataset_for(app, payload.parcel_id)
        history = ds.get_history(payload.parcel_id)
        if history is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parcel history for '{payload.parcel_id}' not found.",
            )

        # Build proposed Event with exact Fraction area
        prop_area = parse_area(payload.area)
        
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

        # Resolve structured boundary and sub-dag if provided
        b_dict = None
        if any([payload.boundary_north, payload.boundary_south, payload.boundary_east, payload.boundary_west]):
            b_dict = {}
            if payload.boundary_north and payload.boundary_north.strip():
                b_dict["north"] = payload.boundary_north.strip()
            if payload.boundary_south and payload.boundary_south.strip():
                b_dict["south"] = payload.boundary_south.strip()
            if payload.boundary_east and payload.boundary_east.strip():
                b_dict["east"] = payload.boundary_east.strip()
            if payload.boundary_west and payload.boundary_west.strip():
                b_dict["west"] = payload.boundary_west.strip()

        resolved_boundary = (
            payload.boundary
            if payload.boundary is not None
            else (b_dict if b_dict is not None else (payload.sub_dag.strip() if payload.sub_dag and payload.sub_dag.strip() else None))
        )

        portion_dict = dict(payload.portion) if isinstance(payload.portion, dict) else {}
        if payload.portion_id:
            portion_dict["portion_id"] = payload.portion_id
        if payload.sub_dag and payload.sub_dag.strip():
            portion_dict["sub_dag"] = payload.sub_dag.strip()
        if resolved_boundary:
            portion_dict["boundary"] = resolved_boundary
        if payload.portion_area:
            portion_dict["portion_area"] = payload.portion_area

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
            portion=portion_dict if portion_dict else None,
            boundary=resolved_boundary,
            via_poa_id=payload.via_poa_id,
        )

        parcel = ds.get_parcel(payload.parcel_id)

        # Pure counterfactual simulation
        sim_res = simulate(
            events=history.events,
            proposed=proposed_event,
            parcel_history=history,
            deeds=ds.deeds,
            parcel=parcel,
        )

        active_lang = lang if lang is not None else (payload.lang or "bn")

        # Format alerts with localization
        formatted_alerts = [
            AlertDetail(
                rule_id=a.rule_id,
                status=localize_status(a.status.value, lang=active_lang),
                status_code=a.status.name,
                message=translate(a.message_key, lang=active_lang),
                recommended_next_step=translate(a.recommended_next_step, lang=active_lang),
                evidence_ids=list(a.evidence_ids),
                calculation=localize_calculation(a.calculation, a.rule_id, lang=active_lang),
            )
            for a in sim_res.alerts
        ]

        _, sim_status_code = compute_overall_status(sim_res.alerts, lang=active_lang)

        requested = sim_res.proposed_event.area
        seller_before = sim_res.available_before
        excess = max(Fraction(0), requested - seller_before)

        # Attention Score (F18)
        sim_score_data = compute_attention_score(sim_res.alerts, lang=active_lang)

        if role == "citizen":
            citizen_alerts = [
                CitizenAlertDetail(
                    status=a.status,
                    status_code=a.status_code,
                    message=a.message,
                    recommended_next_step=a.recommended_next_step,
                )
                for a in formatted_alerts
            ]
            return CitizenSimulateResponse(
                requested_area=str(requested),
                seller_available_before=str(seller_before),
                seller_available_after=str(sim_res.available_after),
                excess=str(excess),
                alerts=citizen_alerts,
                status_code=sim_status_code,
                overall_status_code=sim_status_code,
                attention_score=sim_score_data["score"],
                traffic_light=sim_score_data["traffic_light"],
                score_summary=sim_score_data["summary"],
                score_disclaimer=sim_score_data["disclaimer"],
            )

        r1_calc_out = (
            localize_calculation(sim_res.r1_calculation, "R1", lang=active_lang)
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
                boundary=sim_res.proposed_event.boundary,
                portion=sim_res.proposed_event.portion,
                via_poa_id=sim_res.proposed_event.via_poa_id,
            ),
            available_before=str(sim_res.available_before),
            available_after=str(sim_res.available_after),
            requested_area=str(requested),
            seller_available_before=str(seller_before),
            seller_available_after=str(sim_res.available_after),
            excess=str(excess),
            r1_calculation=r1_calc_out,
            alerts=formatted_alerts,
            status_code=sim_status_code,
            overall_status_code=sim_status_code,
            attention_score=sim_score_data["score"],
            traffic_light=sim_score_data["traffic_light"],
            score_factors=sim_score_data["factors"],
            score_disclaimer=sim_score_data["disclaimer"],
        )

    # -----------------------------------------------------------------------
    # POST /verify-deed
    # -----------------------------------------------------------------------
    @app.post("/verify-deed", response_model=VerifyDeedResponse)
    def verify_deed(
        req: VerifyDeedRequest,
        role: str = Query("reviewer", pattern="^(citizen|reviewer)$"),
    ) -> VerifyDeedResponse:
        """
        Verify cryptographic content integrity of presented deed copy (F13 / R12).
        Computes SHA-256 fingerprint over canonical deed fields (deed_no, registration_date,
        parcel_id, seller, buyer, area) and compares with registry record.
        """
        active_role = req.role if req.role in ("citizen", "reviewer") else role

        # 1. Compute canonical fingerprint
        computed_hash = hash_deed_content(
            deed_no=req.deed_no,
            registration_date=req.registration_date,
            parcel_id=req.parcel_id,
            seller=req.seller,
            buyer=req.buyer,
            area=req.area,
        )
        qr_payload = build_deed_qr_payload(req.deed_no, computed_hash)

        # 2. Look up recorded deed across all loaded datasets
        datasets = [app.state.dataset]
        if hasattr(app.state, "regions") and app.state.regions:
            datasets.append(app.state.regions)
        if hasattr(app.state, "upazilas") and app.state.upazilas:
            datasets.append(app.state.upazilas)

        clean_deed_no = req.deed_no.strip()
        recorded_deed = next(
            (d for ds in datasets for d in ds.deeds if d.deed_no == clean_deed_no or d.id == clean_deed_no),
            None,
        )
        recorded_hash = recorded_deed.content_hash.strip().lower() if recorded_deed and recorded_deed.content_hash else None
        clean_claimed = req.claimed_hash.strip().lower() if req.claimed_hash else None

        # 3. Determine status and message
        if recorded_hash is None:
            status_obj = Status.REVIEW
            message_key = MSG_R12_REVIEW_NO_HASH
            matches_registry = False
        else:
            claimed_matches_recorded = (
                clean_claimed is not None
                and (clean_claimed == recorded_hash or (len(clean_claimed) >= 16 and recorded_hash.startswith(clean_claimed)))
            )
            if computed_hash != recorded_hash:
                status_obj = Status.CONTRADICTION
                message_key = MSG_R12_CONTRADICTION
                matches_registry = False
            elif clean_claimed is not None and not claimed_matches_recorded:
                status_obj = Status.CONTRADICTION
                message_key = MSG_R12_CONTRADICTION
                matches_registry = False
            elif clean_claimed is None:
                # SPEC: "No registry hash on file or no claimed hash -> Review Required"
                status_obj = Status.REVIEW
                message_key = MSG_R12_REVIEW_NO_HASH
                matches_registry = True
            else:
                status_obj = Status.CONSISTENT
                message_key = MSG_R12_CONSISTENT
                matches_registry = True

        status_code = to_status_code(status_obj)
        localized_st = localize_status(status_obj.value, lang=req.lang)
        msg = translate(message_key, lang=req.lang)
        rec_step = translate(NEXT_STEP_R12, lang=req.lang)

        disclaimer = (
            "এই গাণিতিক হ্যাশ যাচাইকরণ সংরক্ষিত রেজিস্ট্রি ফিঙ্গারপ্রিন্টের সাথে দলিলের তথ্যের গাণিতিক অভিন্নতা পরীক্ষা করে। এটি কোনো আইনি ডিজিটাল স্বাক্ষর বা সরকারি নিবন্ধন সনদ নয়।"
            if req.lang == "bn"
            else "This mathematical hash comparison verifies cryptographic integrity of supplied deed fields against the recorded registry fingerprint. It is not a legal digital signature or government title guarantee."
        )

        return VerifyDeedResponse(
            status=localized_st,
            status_code=status_code,
            rule_id="R12" if active_role == "reviewer" else None,
            computed_hash=computed_hash,
            recorded_hash=recorded_hash,
            claimed_hash=clean_claimed,
            matches_registry=matches_registry,
            message=msg,
            recommended_next_step=rec_step,
            qr_payload=qr_payload,
            disclaimer=disclaimer,
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

        planted_rows = [r for r in coverage_table if r.has_planted_case]
        planted_detected = [r for r in planted_rows if r.detected]

        # Build extended benchmark if demo_v11.json exists or ds contains v11 parcels
        extended_resp: Optional[ExtendedBenchmarkResponse] = None
        v11_path = Path("data/demo_v11.json")
        v11_ds: Optional[Dataset] = None
        if v11_path.is_file():
            v11_ds = load_dataset(v11_path)
        elif any("V11" in h.parcel_id or "R8" in h.parcel_id for h in ds.histories):
            v11_ds = ds

        if v11_ds is not None:
            ext_report = evaluate_extended_dataset(v11_ds)
            extended_resp = ExtendedBenchmarkResponse(
                dataset_name=ext_report.dataset_name,
                total_parcels=ext_report.total_parcels,
                clean_parcel_count=ext_report.clean_parcel_count,
                clean_false_alarm_count=ext_report.clean_false_alarm_count,
                planted_parcel_count=ext_report.planted_parcel_count,
                planted_case_count=ext_report.planted_case_count,
                planted_detected_count=ext_report.planted_detected_count,
                coverage_table=[
                    CoverageRowItem(
                        rule_id=row.rule_id,
                        has_planted_case=row.has_planted_case,
                        detected=row.detected,
                        status_detected=row.status_detected,
                        status_code=to_status_code(row.status_detected) if row.status_detected else None,
                    )
                    for row in ext_report.coverage_table
                ],
                phase10_heir_declaration=Phase10BenchmarkDetail(
                    rule_id=ext_report.phase10_heir_declaration.rule_id,
                    planted_detected=ext_report.phase10_heir_declaration.planted_detected,
                    clean_passed=ext_report.phase10_heir_declaration.clean_passed,
                    tricky_clean_passed=ext_report.phase10_heir_declaration.tricky_clean_passed,
                ),
                phase11_features=Phase11FeaturesBenchmarkDetail(
                    attention_scoring_verified=ext_report.phase11_features.attention_scoring_verified,
                    bangla_voice_verified=ext_report.phase11_features.bangla_voice_verified,
                    next_step_guide_verified=ext_report.phase11_features.next_step_guide_verified,
                    ussd_simulator_verified=ext_report.phase11_features.ussd_simulator_verified,
                    vetting_certificate_verified=ext_report.phase11_features.vetting_certificate_verified,
                ),
                simulation_integrity=SimulationIntegrityResult(
                    dataset_hash_before=ext_report.simulation_integrity["dataset_hash_before"],
                    dataset_hash_after=ext_report.simulation_integrity["dataset_hash_after"],
                    unchanged=ext_report.simulation_integrity["unchanged"],
                ),
                disclaimer=ext_report.disclaimer,
            )

        return BenchmarkResponse(
            clean_false_alarm_count=clean_false_alarms,
            coverage_table=[
                CoverageRowItem(
                    rule_id=row.rule_id,
                    has_planted_case=row.has_planted_case,
                    detected=row.detected,
                    status_detected=row.status_detected,
                    status_code=to_status_code(row.status_detected) if row.status_detected else None,
                )
                for row in coverage_table
            ],
            simulation_integrity=SimulationIntegrityResult(
                dataset_hash_before=hash_before,
                dataset_hash_after=hash_after,
                unchanged=(hash_before == hash_after),
            ),
            total_parcels=len(ds.histories),
            planted_case_count=len(planted_rows),
            planted_detected_count=len(planted_detected),
            extended=extended_resp,
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
        datasets = [app.state.dataset]
        if hasattr(app.state, "regions") and app.state.regions:
            datasets.append(app.state.regions)
        if hasattr(app.state, "upazilas") and app.state.upazilas:
            datasets.append(app.state.upazilas)

        results: list[SearchResultItem] = []
        seen_pids: set[str] = set()

        for ds in datasets:
            for p in ds.parcels:
                history = ds.get_history(p.id)
                matched_field = None

                # 1. Direct parcel attributes
                if q_norm in normalize_for_search(p.id):
                    matched_field = "parcel_id"
                elif q_norm in normalize_for_search(p.dag_no):
                    matched_field = "dag_no"
                elif history:
                    for sr in history.survey_records:
                        if q_norm in normalize_for_search(sr.khatian_no):
                            matched_field = "khatian_no"
                            break
                    if not matched_field:
                        for e in history.events:
                            if e.deed_id:
                                deed = ds.get_deed(e.deed_id)
                                if deed and (
                                    q_norm in normalize_for_search(deed.deed_no)
                                    or q_norm in normalize_for_search(deed.id)
                                ):
                                    matched_field = "deed_no"
                                    break

                if matched_field and p.id not in seen_pids:
                    seen_pids.add(p.id)
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

                # 2. Holder / person disambiguation (F15 / R14)
                if history:
                    matching_persons: list[Person] = []
                    checked_pids: set[str] = set()

                    # Check survey record holders
                    for sr in history.survey_records:
                        for pid, _ in sr.holders:
                            if pid not in checked_pids:
                                checked_pids.add(pid)
                                person = ds.get_person(pid)
                                if person:
                                    name_matches = q_norm in normalize_for_search(person.name)
                                    dummy_matches = bool(person.dummy_id and q_norm in normalize_for_search(person.dummy_id))
                                    if name_matches or dummy_matches:
                                        matching_persons.append(person)

                    # Check event parties
                    for e in history.events:
                        for party_id in (e.from_person, e.to_person):
                            if party_id and party_id not in checked_pids:
                                checked_pids.add(party_id)
                                person = ds.get_person(party_id)
                                if person:
                                    name_matches = q_norm in normalize_for_search(person.name)
                                    dummy_matches = bool(person.dummy_id and q_norm in normalize_for_search(person.dummy_id))
                                    if name_matches or dummy_matches:
                                        matching_persons.append(person)

                    for person in matching_persons:
                        item_id = f"{p.id}_{person.id}"
                        if item_id in seen_pids:
                            continue
                        seen_pids.add(item_id)
                        if person.dummy_id:
                            label = (
                                f"{p.mouza} দাগ {p.dag_no} — {person.name} [{person.dummy_id}]"
                                if lang == "bn"
                                else f"{p.mouza} Dag {p.dag_no} — {person.name} [{person.dummy_id}]"
                            )
                        else:
                            label = (
                                f"{p.mouza} দাগ {p.dag_no} — {person.name}"
                                if lang == "bn"
                                else f"{p.mouza} Dag {p.dag_no} — {person.name}"
                            )
                        results.append(
                            SearchResultItem(
                                id=item_id,
                                parcel_id=p.id,
                                dag_no=p.dag_no,
                                mouza=p.mouza,
                                label=label,
                                matched_on="holder_name",
                                holder_name=person.name,
                                dummy_id=person.dummy_id,
                                person_id=person.id,
                            )
                        )

        return results

    # -----------------------------------------------------------------------
    # GET /report/{parcel_id}?lang=bn|en&role=citizen|reviewer
    # -----------------------------------------------------------------------
    @app.get("/report/{parcel_id}")
    def get_report(
        parcel_id: str,
        response: Response,
        lang: str = Query("bn", pattern="^(bn|en)$"),
        role: str = Query("citizen", pattern="^(citizen|reviewer)$"),
    ) -> ReviewerReportResponse | CitizenReportResponse:
        """
        Return structured case summary report for the parcel.
        # This is a demo role, not authentication.
        """
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        ds: Dataset = dataset_for(app, parcel_id)
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

        raw_alerts = evaluate_history(
            history,
            all_parcels=ds.parcels,
            all_deeds=ds.deeds,
            all_histories=ds.histories,
            all_persons=ds.persons,
        )
        overall_status, overall_status_code = compute_overall_status(raw_alerts, lang=lang)

        # Attention Score (F18)
        report_score_data = compute_attention_score(raw_alerts, lang=lang)

        # Supported verification workflow QR payload (F13 / R12 / X5)
        parcel_deed_ids = {e.deed_id for e in history.events if e.deed_id}
        deed_with_hash = next((d for d in ds.deeds if d.id in parcel_deed_ids and d.content_hash), None)
        if deed_with_hash:
            cert_qr = build_deed_qr_payload(deed_with_hash.deed_no, deed_with_hash.content_hash)
        else:
            cert_qr = f"#/verify-deed?parcel_id={parcel.id}&hash={ds_hash[:16]}"

        if role == "citizen":
            non_consistent = [a for a in raw_alerts if a.status != Status.CONSISTENT]
            citizen_alerts = [
                CitizenAlertDetail(
                    status=localize_status(a.status.value, lang=lang),
                    status_code=a.status.name,
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
                overall_status_code=overall_status_code,
                records=records_info,
                alerts=citizen_alerts,
                recommended_next_steps=next_steps,
                disclaimer=disclaimer,
                dataset_hash=ds_hash,
                attention_score=report_score_data["score"],
                traffic_light=report_score_data["traffic_light"],
                score_summary=report_score_data["summary"],
                score_disclaimer=report_score_data["disclaimer"],
                certificate_qr_payload=cert_qr,
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
                        status_code=a.status.name,
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
                overall_status_code=overall_status_code,
                records=records_info,
                alerts=reviewer_alerts,
                recommended_next_steps=next_steps,
                disclaimer=disclaimer,
                dataset_hash=ds_hash,
                attention_score=report_score_data["score"],
                traffic_light=report_score_data["traffic_light"],
                score_factors=report_score_data["factors"],
                score_disclaimer=report_score_data["disclaimer"],
                certificate_qr_payload=cert_qr,
            )

    # -----------------------------------------------------------------------
    # GET /next-steps/{rule_id}?lang=bn|en
    # -----------------------------------------------------------------------
    @app.get("/next-steps/{rule_id}")
    def get_next_steps_endpoint(
        rule_id: str,
        lang: str = Query("bn", pattern="^(bn|en)$"),
    ) -> dict[str, Any]:
        """
        Return 2-4 concrete documentary checks and legal mentor disclaimer for a rule (X3).
        """
        return get_rule_next_steps(rule_id, lang=lang)

    # -----------------------------------------------------------------------
    # POST /ussd (X4: Feature-Phone Simulator)
    # -----------------------------------------------------------------------
    @app.post("/ussd", response_model=USSDResponse)
    def post_ussd(req: USSDRequest) -> USSDResponse:
        """
        Feature-phone text-only USSD simulation endpoint (*123*45#) (X4).
        Enforces strict 160-character output limit.
        """
        ds: Dataset = app.state.dataset
        res = process_ussd_step(
            text=req.text,
            dataset=ds,
            session_id=req.session_id or "USSD_SESSION_01",
        )
        return USSDResponse(**res)

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
