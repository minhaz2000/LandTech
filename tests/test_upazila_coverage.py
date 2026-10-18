"""
JomiGraph AI — Upazila Demo Data Coverage Test Suite
====================================================
Verifies that:
1. The authoritative geographic dataset contains the expected upazila hierarchy.
2. Every upazila has at least one usable demo parcel.
3. No generated parcel references an unknown upazila.
4. Division and district mappings are consistent (including homonymous upazilas).
5. Generated IDs are unique and do not collide with existing records.
6. Repeated generation produces identical output (deterministic).
7. The generated records can be loaded by the real loader and evaluate cleanly.
8. Existing hand-crafted demonstration scenarios remain available.
9. The v1.0 baseline dataset hash remains unchanged.
10. Existing API, search, and simulation work seamlessly with generated parcels.
"""

from __future__ import annotations

import json
from datetime import date
from fractions import Fraction
from pathlib import Path
import pytest
from starlette.testclient import TestClient

from data.upazila_generator import generate_all_upazila_dataset
from jomigraph.api.app import create_app
from jomigraph.engine.benchmark import evaluate_history
from jomigraph.engine.simulate import hash_dataset, simulate
from jomigraph.loader import load_dataset
from jomigraph.models import Event, EventType

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
BASELINE_HASH = "b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01"


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app(dataset_path=str(DATA_DIR / "demo_family.json"))
    return TestClient(app)


def get_authoritative_hierarchy() -> tuple[dict, set[tuple[str, str, str]]]:
    geo = json.loads((DATA_DIR / "bd_geo.json").read_text(encoding="utf-8"))
    tuples = set()
    for d in geo.get("divisions", []):
        div_en = d.get("en", "")
        for dist in d.get("districts", []):
            dist_en = dist.get("en", "")
            for u in dist.get("upazilas", []):
                u_en = u.get("en", "") if isinstance(u, dict) else str(u)
                tuples.add((div_en, dist_en, u_en))
    return geo, tuples


# ---------------------------------------------------------------------------
# 1. Authoritative geographic dataset contains expected upazila hierarchy
# ---------------------------------------------------------------------------
def test_authoritative_hierarchy():
    geo, up_tuples = get_authoritative_hierarchy()
    divisions = geo.get("divisions", [])
    assert len(divisions) == 8, f"Expected 8 divisions, found {len(divisions)}"
    total_districts = sum(len(d.get("districts", [])) for d in divisions)
    assert total_districts == 64, f"Expected 64 districts, found {total_districts}"
    # In bd_geo.json, there are 494 unique (div, dist, upazila) tuples
    # (Companiganj in Sylhet and Sunamganj Sadar in Sunamganj appear twice consecutively)
    assert len(up_tuples) == 494, f"Expected 494 unique upazila tuples, found {len(up_tuples)}"


# ---------------------------------------------------------------------------
# 2. Every upazila has at least one usable demo parcel
# ---------------------------------------------------------------------------
def test_every_upazila_has_at_least_one_usable_demo_parcel(client: TestClient):
    _, authoritative_tuples = get_authoritative_hierarchy()

    # Load actual datasets through real loader
    ds_main = load_dataset(DATA_DIR / "demo_family.json")
    ds_regions = load_dataset(DATA_DIR / "demo_regions.json")
    ds_upazilas = load_dataset(DATA_DIR / "demo_upazilas.json")

    places = json.loads((DATA_DIR / "demo_places.json").read_text(encoding="utf-8"))

    # Track covered tuples
    covered_tuples = set()

    # Regional and all-upazila datasets
    for ds in (ds_regions, ds_upazilas):
        for p in ds.parcels:
            pl = places.get(p.id)
            assert pl is not None, f"Parcel {p.id} missing in demo_places.json"
            key = (pl["division"], pl["district"], pl["upazila"])
            covered_tuples.add(key)

    # Baseline main dataset covers Dhaka city demo area
    assert len(ds_main.parcels) > 0
    covered_tuples.add(("Dhaka", "Dhaka", "Dhaka city thanas (demo area)"))

    missing_tuples = authoritative_tuples - covered_tuples
    assert len(missing_tuples) == 0, f"Uncovered upazilas ({len(missing_tuples)}): {missing_tuples}"
    assert len(covered_tuples) == 494, f"Expected 494 covered upazilas, got {len(covered_tuples)}"


# ---------------------------------------------------------------------------
# 3. No generated parcel references an unknown upazila
# ---------------------------------------------------------------------------
def test_no_parcel_references_unknown_upazila():
    _, authoritative_tuples = get_authoritative_hierarchy()
    places = json.loads((DATA_DIR / "demo_places.json").read_text(encoding="utf-8"))

    for pid, loc in places.items():
        key = (loc["division"], loc["district"], loc["upazila"])
        assert key in authoritative_tuples, f"Parcel {pid} references unknown location {key}"


# ---------------------------------------------------------------------------
# 4. Division and district mappings are consistent (including homonyms)
# ---------------------------------------------------------------------------
def test_division_and_district_mappings_consistent():
    geo, authoritative_tuples = get_authoritative_hierarchy()
    dist_to_div: dict[str, str] = {}
    for d in geo["divisions"]:
        for dist in d["districts"]:
            dist_to_div[dist["en"]] = d["en"]

    places = json.loads((DATA_DIR / "demo_places.json").read_text(encoding="utf-8"))
    for pid, loc in places.items():
        # District belongs to division
        assert dist_to_div[loc["district"]] == loc["division"], (
            f"District {loc['district']} mismatch with division {loc['division']} in parcel {pid}"
        )

    # Verify homonymous upazilas (e.g. Kaliganj in 4 districts) receive distinct parcels
    kaliganj_parcels = [
        (pid, loc["district"]) for pid, loc in places.items() if loc.get("upazila") == "Kaliganj"
    ]
    kaliganj_districts = {dist for _, dist in kaliganj_parcels}
    assert len(kaliganj_districts) == 4, f"Expected Kaliganj in 4 districts, got {kaliganj_districts}"
    assert len(kaliganj_parcels) == 4, f"Expected 4 distinct Kaliganj parcels, got {len(kaliganj_parcels)}"


# ---------------------------------------------------------------------------
# 5. Generated IDs are unique and do not collide with existing records
# ---------------------------------------------------------------------------
def test_generated_ids_unique_and_no_collision():
    ds_main = load_dataset(DATA_DIR / "demo_family.json")
    ds_regions = load_dataset(DATA_DIR / "demo_regions.json")
    ds_upazilas = load_dataset(DATA_DIR / "demo_upazilas.json")

    datasets = [("main", ds_main), ("regions", ds_regions), ("upazilas", ds_upazilas)]

    all_parcel_ids = []
    all_person_ids = []
    all_deed_ids = []
    all_sr_ids = []
    all_event_ids = []

    for name, ds in datasets:
        all_parcel_ids.extend([p.id for p in ds.parcels])
        all_person_ids.extend([p.id for p in ds.persons])
        all_deed_ids.extend([d.id for d in ds.deeds])
        for h in ds.histories:
            all_sr_ids.extend([sr.id for sr in h.survey_records])
            all_event_ids.extend([e.id for e in h.events])

    assert len(all_parcel_ids) == len(set(all_parcel_ids)), "Duplicate parcel IDs found"
    assert len(all_person_ids) == len(set(all_person_ids)), "Duplicate person IDs found"
    assert len(all_deed_ids) == len(set(all_deed_ids)), "Duplicate deed IDs found"
    assert len(all_sr_ids) == len(set(all_sr_ids)), "Duplicate survey record IDs found"
    assert len(all_event_ids) == len(set(all_event_ids)), "Duplicate event IDs found"


# ---------------------------------------------------------------------------
# 6. Repeated generation produces identical output (deterministic)
# ---------------------------------------------------------------------------
def test_repeated_generation_is_deterministic(tmp_path):
    out_upa = tmp_path / "demo_upazilas_test.json"
    out_places = tmp_path / "demo_places_test.json"

    ds1, pl1 = generate_all_upazila_dataset(
        output_upazilas_path=out_upa,
        output_places_path=out_places,
    )

    out_upa2 = tmp_path / "demo_upazilas_test2.json"
    out_places2 = tmp_path / "demo_places_test2.json"

    ds2, pl2 = generate_all_upazila_dataset(
        output_upazilas_path=out_upa2,
        output_places_path=out_places2,
    )

    assert out_upa.read_bytes() == out_upa2.read_bytes(), "Repeated generation produced different bytes!"
    assert out_places.read_bytes() == out_places2.read_bytes(), "Repeated places output differs!"


# ---------------------------------------------------------------------------
# 7. The generated records can be loaded by the real loader and evaluate cleanly
# ---------------------------------------------------------------------------
def test_generated_records_load_and_evaluate_cleanly():
    ds = load_dataset(DATA_DIR / "demo_upazilas.json")
    assert len(ds.parcels) == 479
    assert len(ds.histories) == 479

    # Verify zero rule false alarms
    for h in ds.histories:
        alerts = evaluate_history(h, ds.parcels, ds.deeds, ds.histories)
        assert all(a.status.name == "CONSISTENT" for a in alerts), (
            f"Parcel {h.parcel_id} produced unexpected non-consistent alerts"
        )


# ---------------------------------------------------------------------------
# 8. Existing hand-crafted demonstration scenarios remain available
# ---------------------------------------------------------------------------
def test_handcrafted_demonstration_scenarios_available(client: TestClient):
    # Verify regional showcase parcels
    for syl_id in ("PARCEL_REG_SYL_01", "PARCEL_REG_SYL_02", "PARCEL_REG_SYL_03"):
        r = client.get(f"/parcel/{syl_id}?role=reviewer")
        assert r.status_code == 200, f"Failed to retrieve regional showcase parcel {syl_id}"

    # Verify baseline planted parcels in Dhaka demo area
    r_planted = client.get("/parcel/PARCEL_PLANTED_R1?role=reviewer")
    assert r_planted.status_code == 200
    assert r_planted.json()["overall_status_code"] == "CONTRADICTION"


# ---------------------------------------------------------------------------
# 9. Baseline v1.0 dataset hash remains unchanged
# ---------------------------------------------------------------------------
def test_v10_baseline_dataset_hash_unchanged():
    ds = load_dataset(DATA_DIR / "demo_family.json")
    events = [e for h in ds.histories for e in h.events]
    srs = [s for h in ds.histories for s in h.survey_records]
    current_hash = hash_dataset(events, srs)
    assert current_hash == BASELINE_HASH, f"Baseline hash changed! Expected {BASELINE_HASH}, got {current_hash}"


# ---------------------------------------------------------------------------
# 10. Existing API, search, and simulation work seamlessly with generated parcels
# ---------------------------------------------------------------------------
def test_api_search_and_simulation_with_generated_parcels(client: TestClient):
    # 1. Select specific upazila via /geo/parcels
    r_geo = client.get("/geo/parcels?division=Barishal&district=Barguna&upazila=Betagi")
    assert r_geo.status_code == 200
    data_geo = r_geo.json()
    assert data_geo["total"] >= 1
    sample_p = data_geo["parcels"][0]
    pid = sample_p["id"]
    assert pid.startswith("PARCEL_UPA_")
    assert sample_p["is_synthetic_demo"] is True

    # 2. Get parcel details via /parcel/{id}
    r_detail = client.get(f"/parcel/{pid}?role=citizen")
    assert r_detail.status_code == 200
    detail = r_detail.json()
    assert detail["id"] == pid
    assert detail["overall_status_code"] == "CONSISTENT"

    # 3. Search parcel by ID
    r_search = client.get(f"/search?q={pid}")
    assert r_search.status_code == 200
    search_results = r_search.json()
    assert any(x["parcel_id"] == pid for x in search_results)

    # 4. Search parcel by holder name
    holder_name = "Fictional Holder A (Betagi)"
    r_search_holder = client.get(f"/search?q={holder_name}")
    assert r_search_holder.status_code == 200
    assert any(x["parcel_id"] == pid for x in r_search_holder.json())

    # 5. Get structured report via /report/{id}
    r_report = client.get(f"/report/{pid}?role=citizen")
    assert r_report.status_code == 200
    report_data = r_report.json()
    assert report_data["parcel_id"] == pid

    # 6. Counterfactual simulation on generated parcel via /simulate
    sim_payload = {
        "parcel_id": pid,
        "from_person": "P_UPA_BAR_BARGUNA_BETAGI_A",
        "to_person": "P_UPA_BAR_BARGUNA_BETAGI_B",
        "area": "5",
        "date": "2020-01-01",
    }
    r_sim = client.post("/simulate", json=sim_payload)
    assert r_sim.status_code == 200
    sim_data = r_sim.json()
    assert sim_data["available_before"] == "10"
    assert sim_data["available_after"] == "5"
    assert sim_data["requested_area"] == "5"
