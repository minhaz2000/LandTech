"""
JomiGraph AI — All-Upazila Synthetic Demo Data Generator
========================================================
Generates deterministic, synthetic demonstration land-record data for all
upazilas in Bangladesh that do not already have demo parcels in demo_regions.json
or demo_family.json.

Safety & Integrity Invariants:
1. Preserves existing hand-crafted demo scenarios (demo_family.json, demo_regions.json).
2. Never modifies demo_family.json or its baseline integrity hash.
3. Every uncovered upazila receives at least one valid synthetic parcel.
4. Generated IDs are stable, unique, and collision-free (prefixed with PARCEL_UPA_, P_UPA_, etc.).
5. Internal geography is consistent: references exact upazila, district, and division.
6. Zero rule false alarms in generated records (all clean valid chains).
7. Clearly labeled as synthetic demonstration records.
8. Deterministic output: repeated runs produce identical bytes.
"""

from __future__ import annotations

import json
import re
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

DIV_TAGS = {
    "Barishal": "BAR",
    "Chattogram": "CTG",
    "Dhaka": "DHA",
    "Khulna": "KHL",
    "Mymensingh": "MYM",
    "Rajshahi": "RAJ",
    "Rangpur": "RNG",
    "Sylhet": "SYL",
}


def slugify(text: str) -> str:
    """Convert text to uppercase alphanumeric slug with underscores."""
    return re.sub(r"[^A-Z0-9]+", "_", text.upper()).strip("_")


def generate_all_upazila_dataset(
    geo_path: Path = HERE / "bd_geo.json",
    places_path: Path = HERE / "demo_places.json",
    output_upazilas_path: Path = HERE / "demo_upazilas.json",
    output_places_path: Path = HERE / "demo_places.json",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Generate synthetic parcels for all uncovered upazilas.
    Returns (upazilas_dict, places_dict).
    """
    geo_data = json.loads(geo_path.read_text(encoding="utf-8"))

    # Load regions to identify pre-existing regional showcase parcels
    regions_path = HERE / "demo_regions.json"
    covered_keys = set()
    existing_places: dict[str, dict[str, Any]] = {}
    
    if places_path.is_file():
        raw_places = json.loads(places_path.read_text(encoding="utf-8"))
        # Retain only pre-existing regional showcase parcels (PARCEL_REG_*) in existing_places
        for pid, loc in raw_places.items():
            if not pid.startswith("PARCEL_UPA_"):
                existing_places[pid] = loc
                if isinstance(loc, dict) and "division" in loc and "district" in loc and "upazila" in loc:
                    covered_keys.add((loc["division"], loc["district"], loc["upazila"]))

    # Dhaka city demo area is covered by demo_family.json
    covered_keys.add(("Dhaka", "Dhaka", "Dhaka city thanas (demo area)"))

    # Enumerate all authoritative upazilas in deterministic order
    all_upazila_tuples: list[tuple[str, str, str, str]] = []
    seen_tuples: set[tuple[str, str, str]] = set()

    for div in sorted(geo_data.get("divisions", []), key=lambda d: d.get("en", "")):
        div_en = div.get("en", "")
        for dist in sorted(div.get("districts", []), key=lambda d: d.get("en", "")):
            dist_en = dist.get("en", "")
            for u in dist.get("upazilas", []):
                u_en = u.get("en", "") if isinstance(u, dict) else str(u)
                u_bn = u.get("bn", "") if isinstance(u, dict) else u_en
                tup_key = (div_en, dist_en, u_en)
                if tup_key not in seen_tuples:
                    seen_tuples.add(tup_key)
                    all_upazila_tuples.append((div_en, dist_en, u_en, u_bn))

    uncovered = [t for t in all_upazila_tuples if (t[0], t[1], t[2]) not in covered_keys]

    persons: list[dict[str, Any]] = []
    parcels: list[dict[str, Any]] = []
    deeds: list[dict[str, Any]] = []
    histories: list[dict[str, Any]] = []
    updated_places = dict(existing_places)

    for idx, (div_en, dist_en, up_en, up_bn) in enumerate(uncovered, start=1):
        div_tag = DIV_TAGS.get(div_en, div_en[:3].upper())
        dist_slug = slugify(dist_en)
        up_slug = slugify(up_en)
        tag = f"{div_tag}_{dist_slug}_{up_slug}"

        pid = f"PARCEL_UPA_{tag}"
        pa_id = f"P_UPA_{tag}_A"
        pb_id = f"P_UPA_{tag}_B"
        sr_id = f"SR_UPA_{tag}_1"
        deed_id = f"DEED_UPA_{tag}_1"
        event_id = f"E_UPA_{tag}_1"

        dag_no = str(100 + (idx % 800))
        khatian_no = f"{dag_no}01"
        deed_no = f"SYN-{div_tag}-{dist_slug[:3]}-{dag_no}"

        # Synthetic names clearly indicating demo nature
        pa_name = f"Fictional Holder A ({up_en})"
        pb_name = f"Fictional Buyer B ({up_en})"

        persons.append({
            "id": pa_id,
            "name": pa_name,
            "dummy_id": f"SYN-NID-{idx:04d}-A",
        })
        persons.append({
            "id": pb_id,
            "name": pb_name,
            "dummy_id": f"SYN-NID-{idx:04d}-B",
        })

        parcels.append({
            "id": pid,
            "dag_no": dag_no,
            "mouza": f"Demo Mouza ({up_en})",
            "parent_id": None,
        })

        deeds.append({
            "id": deed_id,
            "deed_no": deed_no,
            "registration_date": "2010-06-01",
        })

        histories.append({
            "parcel_id": pid,
            "baseline_record_id": sr_id,
            "baseline_complete": True,
            "start_record_id": sr_id,
            "end_date": "2025-12-31",
            "survey_records": [
                {
                    "id": sr_id,
                    "parcel_id": pid,
                    "survey": "BS",
                    "khatian_no": khatian_no,
                    "record_date": "2000-01-10",
                    "recorded_area": "20",
                    "holders": [{"person_id": pa_id, "area": "20"}],
                }
            ],
            "events": [
                {
                    "id": event_id,
                    "type": "SALE",
                    "seq": 1,
                    "event_date": "2010-06-01",
                    "parcel_id": pid,
                    "from_person": pa_id,
                    "to_person": pb_id,
                    "area": "10",
                    "deed_id": deed_id,
                    "portion_id": None,
                    "linked_event_id": None,
                    "source_record_id": None,
                }
            ],
        })

        updated_places[pid] = {
            "division": div_en,
            "district": dist_en,
            "upazila": up_en,
            "upazila_bn": up_bn,
            "is_synthetic_demo": True,
        }

    dataset_dict = {
        "metadata": {
            "title": "JomiGraph AI — All-Upazila Synthetic Demo Dataset",
            "description": "Deterministic synthetic land records providing complete geographic coverage across all Bangladesh upazilas.",
            "disclaimer": "SYNTHETIC DEMO DATA ONLY. All records, names, deeds, khatians, and parcels are fictional. Does not represent authentic government records or actual land ownership.",
            "uncovered_upazilas_generated": len(uncovered),
            "total_parcels": len(parcels),
        },
        "persons": persons,
        "parcels": parcels,
        "deeds": deeds,
        "histories": histories,
    }

    output_upazilas_path.write_text(
        json.dumps(dataset_dict, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )

    output_places_path.write_text(
        json.dumps(updated_places, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )

    return dataset_dict, updated_places


if __name__ == "__main__":
    ds, pl = generate_all_upazila_dataset()
    print(f"Generated {len(ds['parcels'])} synthetic parcels for all uncovered upazilas.")
    print(f"Total entries in demo_places.json: {len(pl)}")
