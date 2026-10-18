"""Tests for geography, regional demo parcels and POST /check-my-land."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from jomigraph.api.app import create_app
from jomigraph.engine.simulate import hash_dataset


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app(dataset_path="data/demo_family.json"))


BASE = {"mouza": "Demo", "dag_no": "9", "survey_date": "2000-01-10", "holders": [{"name": "Rahim", "area": "10"}], "lang": "en"}


def test_geo_tree_has_8_divisions_and_64_districts(client):
    tree = client.get("/geo/tree").json()
    assert len(tree["divisions"]) == 8
    assert sum(len(d["districts"]) for d in tree["divisions"]) == 64


def test_every_non_dhaka_division_has_one_of_each_colour(client):
    for div in ("Barishal", "Chattogram", "Khulna", "Mymensingh", "Rajshahi", "Rangpur", "Sylhet"):
        counts = client.get(f"/geo/parcels?division={div}").json()["counts"]
        assert counts["CONTRADICTION"] >= 1 and counts["REVIEW"] >= 1 and counts["CONSISTENT"] >= 1, div


def test_regional_parcel_detail_is_served_and_main_list_is_unchanged(client):
    assert client.get("/parcel/PARCEL_REG_SYL_03?role=citizen").status_code == 200
    assert len(client.get("/parcels").json()) == 30


def test_check_my_land_consistent_and_oversell(client):
    ok = client.post("/check-my-land", json={**BASE, "deeds": [{"seller": "Rahim", "buyer": "Karim", "area": "4", "date": "2010-01-01"}]}).json()
    assert ok["status_code"] == "CONSISTENT" and ok["alerts"] == []
    bad = client.post("/check-my-land", json={**BASE, "deeds": [{"seller": "Rahim", "buyer": "Karim", "area": "15", "date": "2010-01-01"}]}).json()
    assert bad["status_code"] == "CONTRADICTION"
    assert any(b["negative"] for b in bad["paper_balance"])


def test_check_my_land_mutation_before_deed_is_contradiction(client):
    deed = {"seller": "Rahim", "buyer": "Karim", "area": "4", "date": "2010-01-01", "mutation_area": "4", "mutation_date": "2009-01-01"}
    assert client.post("/check-my-land", json={**BASE, "deeds": [deed]}).json()["status_code"] == "CONTRADICTION"


def test_check_my_land_rejects_bad_input(client):
    assert client.post("/check-my-land", json={**BASE, "holders": [{"name": "A", "area": "abc"}]}).status_code == 422
    assert client.post("/check-my-land", json={**BASE, "deeds": [{"seller": "Rahim", "buyer": "K", "area": "1", "date": "01/01/2010"}]}).status_code == 422
    assert client.post("/check-my-land", json={**BASE, "holders": []}).status_code == 422


def test_check_my_land_never_changes_main_dataset(client):
    ds = client.app.state.dataset
    before = hash_dataset([e for h in ds.histories for e in h.events], [s for h in ds.histories for s in h.survey_records])
    client.post("/check-my-land", json={**BASE, "deeds": [{"seller": "Rahim", "buyer": "Karim", "area": "15", "date": "2010-01-01"}]})
    after = hash_dataset([e for h in ds.histories for e in h.events], [s for h in ds.histories for s in h.survey_records])
    assert before == after
