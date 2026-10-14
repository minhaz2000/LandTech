"""
JomiGraph AI — Dataset Loader
=============================
Parses raw JSON dataset into immutable typed dataclasses.
All area and share values strictly go through load_fraction().
Floats are strictly rejected.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
from typing import Any, Optional, Sequence

from jomigraph.models import (
    Deed,
    Event,
    EventType,
    Parcel,
    ParcelHistory,
    Person,
    SurveyRecord,
    load_fraction,
)


@dataclass(frozen=True)
class Dataset:
    persons: tuple[Person, ...]
    parcels: tuple[Parcel, ...]
    deeds: tuple[Deed, ...]
    histories: tuple[ParcelHistory, ...]

    def get_parcel(self, parcel_id: str) -> Optional[Parcel]:
        return next((p for p in self.parcels if p.id == parcel_id), None)

    def get_history(self, parcel_id: str) -> Optional[ParcelHistory]:
        return next((h for h in self.histories if h.parcel_id == parcel_id), None)

    def get_deed(self, deed_id: str) -> Optional[Deed]:
        return next((d for d in self.deeds if d.id == deed_id), None)

    def get_person(self, person_id: str) -> Optional[Person]:
        return next((p for p in self.persons if p.id == person_id), None)


def _parse_date(val: Optional[str]) -> Optional[date]:
    if val is None:
        return None
    return date.fromisoformat(val)


def parse_dataset_dict(data: dict[str, Any]) -> Dataset:
    """Parse a dictionary into a validated Dataset instance."""
    # 1. Persons
    persons = tuple(
        Person(id=p["id"], name=p["name"])
        for p in data.get("persons", [])
    )

    # 2. Parcels
    parcels = tuple(
        Parcel(
            id=p["id"],
            dag_no=p["dag_no"],
            mouza=p["mouza"],
            parent_id=p.get("parent_id"),
        )
        for p in data.get("parcels", [])
    )

    # 3. Deeds
    deeds = tuple(
        Deed(
            id=d["id"],
            deed_no=d["deed_no"],
            registration_date=date.fromisoformat(d["registration_date"]),
        )
        for d in data.get("deeds", [])
    )

    # 4. Histories (with survey records and events)
    histories_list: list[ParcelHistory] = []
    for h in data.get("histories", []):
        survey_records = tuple(
            SurveyRecord(
                id=sr["id"],
                parcel_id=sr["parcel_id"],
                survey=sr["survey"],
                khatian_no=sr["khatian_no"],
                record_date=date.fromisoformat(sr["record_date"]),
                recorded_area=load_fraction(sr["recorded_area"]),
                holders=tuple(
                    (holder["person_id"], load_fraction(holder["area"]))
                    for holder in sr["holders"]
                ),
            )
            for sr in h.get("survey_records", [])
        )

        events = tuple(
            Event(
                id=e["id"],
                type=EventType(e["type"]),
                seq=e["seq"],
                event_date=_parse_date(e.get("event_date")),
                parcel_id=e["parcel_id"],
                from_person=e.get("from_person"),
                to_person=e.get("to_person"),
                area=load_fraction(e["area"]) if e.get("area") is not None else None,
                deed_id=e.get("deed_id"),
                portion_id=e.get("portion_id"),
                linked_event_id=e.get("linked_event_id"),
                source_record_id=e.get("source_record_id"),
            )
            for e in h.get("events", [])
        )

        histories_list.append(
            ParcelHistory(
                parcel_id=h["parcel_id"],
                baseline_record_id=h["baseline_record_id"],
                baseline_complete=bool(h.get("baseline_complete", True)),
                start_record_id=h["start_record_id"],
                end_date=_parse_date(h.get("end_date")),
                survey_records=survey_records,
                events=events,
            )
        )

    return Dataset(
        persons=persons,
        parcels=parcels,
        deeds=deeds,
        histories=tuple(histories_list),
    )


def load_dataset(file_path: str | Path) -> Dataset:
    """Load and parse dataset JSON file into Dataset instance."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return parse_dataset_dict(data)


def dataset_to_dict(dataset: Dataset) -> dict[str, Any]:
    """Serialize a Dataset instance into a JSON-compatible dictionary."""
    return {
        "persons": [
            {"id": p.id, "name": p.name}
            for p in dataset.persons
        ],
        "parcels": [
            {
                "id": p.id,
                "dag_no": p.dag_no,
                "mouza": p.mouza,
                "parent_id": p.parent_id,
            }
            for p in dataset.parcels
        ],
        "deeds": [
            {
                "id": d.id,
                "deed_no": d.deed_no,
                "registration_date": d.registration_date.isoformat(),
            }
            for d in dataset.deeds
        ],
        "histories": [
            {
                "parcel_id": h.parcel_id,
                "baseline_record_id": h.baseline_record_id,
                "baseline_complete": h.baseline_complete,
                "start_record_id": h.start_record_id,
                "end_date": h.end_date.isoformat() if h.end_date else None,
                "survey_records": [
                    {
                        "id": sr.id,
                        "parcel_id": sr.parcel_id,
                        "survey": sr.survey,
                        "khatian_no": sr.khatian_no,
                        "record_date": sr.record_date.isoformat(),
                        "recorded_area": str(sr.recorded_area),
                        "holders": [
                            {"person_id": holder[0], "area": str(holder[1])}
                            for holder in sr.holders
                        ],
                    }
                    for sr in h.survey_records
                ],
                "events": [
                    {
                        "id": e.id,
                        "type": e.type.value,
                        "seq": e.seq,
                        "event_date": e.event_date.isoformat() if e.event_date else None,
                        "parcel_id": e.parcel_id,
                        "from_person": e.from_person,
                        "to_person": e.to_person,
                        "area": str(e.area) if e.area is not None else None,
                        "deed_id": e.deed_id,
                        "portion_id": e.portion_id,
                        "linked_event_id": e.linked_event_id,
                        "source_record_id": e.source_record_id,
                    }
                    for e in h.events
                ],
            }
            for h in dataset.histories
        ],
    }


def save_dataset(dataset: Dataset, file_path: str | Path) -> None:
    """Save dataset to formatted JSON file with UTF-8 encoding."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = dataset_to_dict(dataset)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_clean_false_alarms_and_coverage(
    dataset: Dataset,
) -> tuple[int, tuple[Any, ...]]:
    """
    Evaluate dataset and return:
      - clean_case_false_alarm_count (must be 0 on clean cases)
      - coverage_table: tuple of RuleCoverageRow(rule_id, has_planted_case, detected, status_detected)
    """
    from jomigraph.engine.benchmark import evaluate_dataset

    report = evaluate_dataset(dataset)
    return report.clean_false_alarm_count, report.coverage_table

