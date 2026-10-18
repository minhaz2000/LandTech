"""
Extra routes: Bangladesh geography, fictional regional demo parcels, and
POST /check-my-land (a customer types their own plot; nothing is stored).
The main demo dataset and its hash are never touched.
"""
from __future__ import annotations

import json
import re
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from jomigraph.area_input import AreaInputError, MESSAGES as AREA_MESSAGES, parse_area
from jomigraph.engine.assistant import process_assistant_query
from jomigraph.engine.benchmark import evaluate_history
from jomigraph.engine.rules import Status
from jomigraph.i18n import translate
from jomigraph.loader import Dataset, load_dataset
from jomigraph.models import Deed, Event, EventType, Parcel, ParcelHistory, Person, SurveyRecord

DATA = Path(__file__).resolve().parents[3] / "data"
BN_DIG = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
# Existing demo mouzas sit in Dhaka; this is the demo-area entry added to the Dhaka district.
DHAKA_DEMO_UPAZILA = "Dhaka city thanas (demo area)"


def dataset_for(app: FastAPI, parcel_id: str) -> Dataset:
    """Main dataset, or the regional / all-upazila dataset when the parcel lives there."""
    main: Dataset = app.state.dataset
    if main.get_parcel(parcel_id) is not None:
        return main
    if hasattr(app.state, "regions") and app.state.regions.get_parcel(parcel_id) is not None:
        return app.state.regions
    if hasattr(app.state, "upazilas") and app.state.upazilas.get_parcel(parcel_id) is not None:
        return app.state.upazilas
    return main


def _status_code(alerts) -> str:
    if any(a.status == Status.CONTRADICTION for a in alerts):
        return "CONTRADICTION"
    if any(a.status == Status.REVIEW for a in alerts):
        return "REVIEW"
    return "CONSISTENT"


def _fmt(fr: Fraction) -> str:
    if fr.denominator == 1:
        return str(fr.numerator)
    return f"{float(fr):.2f}".rstrip("0").rstrip(".")


def _iso(text: Optional[str], lang: str, label: str) -> Optional[date]:
    if text is None or not str(text).strip():
        return None
    try:
        return date.fromisoformat(str(text).strip().translate(BN_DIG))
    except ValueError:
        raise HTTPException(422, detail=(f"{label}: তারিখ YYYY-MM-DD আকারে দিন" if lang == "bn" else f"{label}: use a YYYY-MM-DD date"))


class MyHolder(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    area: str = Field(min_length=1, max_length=40)


class MyDeed(BaseModel):
    seller: str = Field(min_length=1, max_length=80)
    buyer: str = Field(min_length=1, max_length=80)
    area: str = Field(min_length=1, max_length=40)
    date: str = Field(min_length=1, max_length=20)
    deed_no: Optional[str] = Field(default=None, max_length=40)
    mutation_area: Optional[str] = Field(default=None, max_length=40)
    mutation_date: Optional[str] = Field(default=None, max_length=20)


class MyLandRequest(BaseModel):
    division: Optional[str] = Field(default=None, max_length=60)
    district: Optional[str] = Field(default=None, max_length=60)
    upazila: Optional[str] = Field(default=None, max_length=80)
    mouza: str = Field(min_length=1, max_length=80)
    dag_no: str = Field(min_length=1, max_length=20)
    khatian_no: Optional[str] = Field(default=None, max_length=20)
    survey_date: str = Field(min_length=1, max_length=20)
    holders: list[MyHolder] = Field(min_length=1, max_length=20)
    deeds: list[MyDeed] = Field(default_factory=list, max_length=30)
    baseline_complete: bool = True
    lang: str = Field(default="bn", pattern="^(bn|en)$")


class AssistantRequest(BaseModel):
    question: str = Field(default="", max_length=300)
    parcel_id: Optional[str] = Field(default=None, max_length=80)


def register_extras(
    app: FastAPI,
    regions_path: Optional[Path] = None,
    upazilas_path: Optional[Path] = None,
) -> None:
    regions_file = Path(regions_path or DATA / "demo_regions.json")
    app.state.regions = load_dataset(regions_file) if regions_file.is_file() else Dataset((), (), (), ())
    upazilas_file = Path(upazilas_path or DATA / "demo_upazilas.json")
    app.state.upazilas = load_dataset(upazilas_file) if upazilas_file.is_file() else Dataset((), (), (), ())
    places_file = DATA / "demo_places.json"
    regional_places = json.loads(places_file.read_text(encoding="utf-8")) if places_file.is_file() else {}
    geo = json.loads((DATA / "bd_geo.json").read_text(encoding="utf-8"))

    def place_of(p: Parcel) -> dict[str, str]:
        if p.id in regional_places:
            return regional_places[p.id]
        return {"division": "Dhaka", "district": "Dhaka", "upazila": DHAKA_DEMO_UPAZILA}

    @app.get("/geo/tree")
    def geo_tree() -> dict:
        return geo

    @app.get("/geo/parcels")
    def geo_parcels(
        division: Optional[str] = None,
        district: Optional[str] = None,
        upazila: Optional[str] = None,
        lang: str = Query("bn", pattern="^(bn|en)$"),
    ) -> dict[str, Any]:
        """Demo parcels (main, fictional regional, and all-upazila synthetic) under a place, with status counts."""
        out = []
        datasets = [app.state.dataset, app.state.regions]
        if hasattr(app.state, "upazilas") and app.state.upazilas:
            datasets.append(app.state.upazilas)

        seen_ids = set()
        for ds in datasets:
            for p in ds.parcels:
                if p.id in seen_ids:
                    continue
                pl = place_of(p)
                if division and pl.get("division") != division:
                    continue
                if district and pl.get("district") != district:
                    continue
                if upazila and pl.get("upazila") != upazila:
                    continue
                seen_ids.add(p.id)
                h = ds.get_history(p.id)
                code = _status_code(evaluate_history(h, ds.parcels, ds.deeds, ds.histories)) if h else "CONSISTENT"
                label = f"{p.mouza} দাগ {p.dag_no}" if lang == "bn" else f"{p.mouza} Dag {p.dag_no}"
                is_demo = bool(pl.get("is_synthetic_demo", p.id.startswith("PARCEL_REG_") or p.id.startswith("PARCEL_UPA_")))
                out.append({"id": p.id, "label": label, "status_code": code, "is_synthetic_demo": is_demo, **pl})
        counts = {c: sum(1 for x in out if x["status_code"] == c) for c in ("CONTRADICTION", "REVIEW", "CONSISTENT")}
        disclaimer = (
            "সিন্থেটিক ডেমো ডেটা: এই রেকর্ডগুলো পরীক্ষামূলক প্রদর্শনের জন্য কৃত্রিমভাবে তৈরি। কোনো সরকারি সনদ বা মালিকানার প্রমাণ নয়।"
            if lang == "bn"
            else "Synthetic Demo Data: These records are synthetically generated for demonstration. Not official government records or proof of ownership."
        )
        return {"parcels": out, "counts": counts, "total": len(out), "disclaimer": disclaimer}

    @app.post("/check-my-land")
    def check_my_land(req: MyLandRequest) -> dict[str, Any]:
        lang = req.lang

        def area(v: str, label: str) -> Fraction:
            try:
                return parse_area(v)
            except AreaInputError as e:
                raise HTTPException(422, detail=f"{label}: {AREA_MESSAGES[e.code]}")

        survey_date = _iso(req.survey_date, lang, "survey_date")
        if survey_date is None:
            raise HTTPException(422, detail="survey_date is required")

        ids: dict[str, str] = {}
        persons: list[Person] = []

        def pid(name: str) -> str:
            key = re.sub(r"\s+", " ", name.strip()).casefold()
            if key not in ids:
                ids[key] = f"P_USER_{len(ids) + 1}"
                persons.append(Person(id=ids[key], name=re.sub(r"\s+", " ", name.strip())))
            return ids[key]

        holders = tuple((pid(h.name), area(h.area, h.name)) for h in req.holders)
        total = sum((a for _, a in holders), Fraction(0))
        parcel = Parcel(id="PARCEL_USER", dag_no=req.dag_no.strip(), mouza=req.mouza.strip())
        baseline = SurveyRecord(id="SR_USER", parcel_id=parcel.id, survey="BS", khatian_no=(req.khatian_no or "-").strip(),
                                record_date=survey_date, recorded_area=total, holders=holders)

        events: list[Event] = []
        deeds: list[Deed] = []
        dated = []
        for i, d in enumerate(req.deeds, start=1):
            label = f"deed {i}"
            dt = _iso(d.date, lang, label)
            if dt is None:
                raise HTTPException(422, detail=f"{label}: date is required")
            dated.append((dt, i, d))
        dated.sort(key=lambda x: (x[0], x[1]))
        seq = 0
        for dt, i, d in dated:
            deed = Deed(id=f"DEED_USER_{i}", deed_no=(d.deed_no or f"D-{i}").strip(), registration_date=dt)
            deeds.append(deed)
            seq += 1
            sale_id = f"E_USER_SALE_{i}"
            events.append(Event(id=sale_id, type=EventType.SALE, seq=seq, event_date=dt, parcel_id=parcel.id,
                                from_person=pid(d.seller), to_person=pid(d.buyer), area=area(d.area, f"deed {i}"),
                                deed_id=deed.id, portion_id=None, linked_event_id=None, source_record_id=None))
            if d.mutation_area and d.mutation_area.strip():
                mdt = _iso(d.mutation_date, lang, f"deed {i} mutation")
                if mdt is None:
                    raise HTTPException(422, detail=(f"দলিল {i}: নামজারির তারিখ দিন" if lang == "bn" else f"Deed {i}: enter the mutation date"))
                seq += 1
                events.append(Event(id=f"E_USER_MUT_{i}", type=EventType.MUTATION, seq=seq, event_date=mdt, parcel_id=parcel.id,
                                    from_person=pid(d.seller), to_person=pid(d.buyer), area=area(d.mutation_area, f"deed {i} mutation"),
                                    deed_id=deed.id, portion_id=None, linked_event_id=sale_id, source_record_id=None))

        history = ParcelHistory(parcel_id=parcel.id, baseline_record_id=baseline.id, baseline_complete=req.baseline_complete,
                                start_record_id=baseline.id, end_date=None, survey_records=(baseline,), events=tuple(events))
        alerts = evaluate_history(history, (parcel,), tuple(deeds), (history,))
        code = _status_code(alerts)

        # Paper arithmetic only: who holds how much after each deed, in date order. Not a statement of ownership.
        bal: dict[str, Fraction] = {pid_: a for pid_, a in holders}
        for e in events:
            if e.type == EventType.SALE:
                bal[e.from_person] = bal.get(e.from_person, Fraction(0)) - e.area
                bal[e.to_person] = bal.get(e.to_person, Fraction(0)) + e.area
        names = {p.id: p.name for p in persons}
        after = [{"name": names[k], "area": _fmt(v), "negative": v < 0} for k, v in bal.items() if v != 0]

        problems = [a for a in alerts if a.status != Status.CONSISTENT]
        return {
            "status_code": code,
            "alerts": [{"status_code": a.status.name, "message": translate(a.message_key, lang=lang),
                        "recommended_next_step": translate(a.recommended_next_step, lang=lang)} for a in problems],
            "checks_passed": sum(1 for a in alerts if a.status == Status.CONSISTENT),
            "checks_total": len(alerts),
            "paper_balance": after,
            "survey_total": _fmt(total),
            "disclaimer": ("ডেমো হিসাব, আইনি সিদ্ধান্ত বা মালিকানার সনদ নয়। আপনার দেওয়া তথ্য সংরক্ষণ করা হয় না।" if lang == "bn"
                           else "Demo arithmetic, not a legal ruling or proof of ownership. The details you typed are not stored."),
        }

    @app.post("/assistant")
    def assistant_endpoint(
        req: AssistantRequest,
        lang: str = Query("bn", pattern="^(bn|en)$"),
        role: str = Query("citizen", pattern="^(citizen|reviewer)$"),
    ) -> dict[str, Any]:
        """Offline, rule-based bilingual assistant for explaining results, rules, and workflows."""
        ds = dataset_for(app, req.parcel_id) if req.parcel_id else app.state.dataset
        res = process_assistant_query(
            query_text=req.question,
            dataset=ds,
            parcel_id=req.parcel_id,
            lang=lang,
            role=role,
        )
        return {
            "intent": res.intent,
            "answer": res.answer,
            "suggestions": res.suggestions,
            "status": res.status,
        }
