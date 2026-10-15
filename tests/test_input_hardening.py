"""
Input hardening, role-aware responses and path anchoring.

Covers the pre-submission fixes:
  - zero, negative and malformed areas are rejected with a clear code
  - decimal strings are accepted exactly (no float is ever created)
  - /simulate and /parcels drop staging detail for the citizen role
  - the dataset path does not depend on the working directory
"""

from __future__ import annotations

import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from jomigraph.api.app import DEFAULT_DATASET_PATH, create_app
from jomigraph.area_input import AreaInputError, parse_area

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


def sim(client: TestClient, area, **extra):
    body = {"parcel_id": "PARCEL_LAB_DEMO", "from_person": "H", "area": area, "lang": "en"}
    body.update(extra)
    query = extra.pop("_query", "") if "_query" in extra else ""
    return client.post("/simulate" + query, json=body)


# ---------------------------------------------------------------------------
# parse_area
# ---------------------------------------------------------------------------

class TestParseArea:
    @pytest.mark.parametrize("text,expected", [
        ("5", Fraction(5)),
        ("2.5", Fraction(5, 2)),
        ("0.75", Fraction(3, 4)),
        ("5/2", Fraction(5, 2)),
        (" 5 / 2 ", Fraction(5, 2)),
        ("২.৫", Fraction(5, 2)),
        ("১০", Fraction(10)),
        (7, Fraction(7)),
    ])
    def test_valid_inputs_are_exact(self, text, expected):
        result = parse_area(text)
        assert isinstance(result, Fraction)
        assert result == expected

    @pytest.mark.parametrize("text,code", [
        ("0", "AREA_NOT_POSITIVE"),
        ("0.0", "AREA_NOT_POSITIVE"),
        ("0/5", "AREA_NOT_POSITIVE"),
        ("-1", "AREA_NOT_POSITIVE"),
        ("-2.5", "AREA_NOT_POSITIVE"),
        ("", "AREA_EMPTY"),
        ("   ", "AREA_EMPTY"),
        ("abc", "AREA_FORMAT"),
        ("1e3", "AREA_FORMAT"),
        ("nan", "AREA_FORMAT"),
        ("inf", "AREA_FORMAT"),
        ("5/0", "AREA_FORMAT"),
        ("1.2.3", "AREA_FORMAT"),
        ("1,5", "AREA_FORMAT"),
        ("99999999999", "AREA_TOO_LARGE"),
        ("9" * 60, "AREA_TOO_LARGE"),
        (2.5, "AREA_FLOAT_TYPE"),
        (True, "AREA_FLOAT_TYPE"),
        (0, "AREA_NOT_POSITIVE"),
        (-3, "AREA_NOT_POSITIVE"),
        (None, "AREA_FORMAT"),
        ([5], "AREA_FORMAT"),
    ])
    def test_invalid_inputs_carry_a_code(self, text, code):
        with pytest.raises(AreaInputError) as exc:
            parse_area(text)
        assert exc.value.code == code


# ---------------------------------------------------------------------------
# POST /simulate
# ---------------------------------------------------------------------------

class TestSimulateValidation:
    @pytest.mark.parametrize("area", ["0", "0.0", "-1", "-0.5", 0, -1])
    def test_zero_and_negative_are_rejected(self, client, area):
        res = sim(client, area)
        assert res.status_code == 422
        assert "AREA_" in res.text

    def test_zero_message_is_specific(self, client):
        res = sim(client, "0")
        assert "greater than zero" in res.text

    @pytest.mark.parametrize("area", ["abc", "", "1e3", "5/0", "nan"])
    def test_malformed_is_rejected(self, client, area):
        assert sim(client, area).status_code == 422

    def test_json_float_is_rejected(self, client):
        res = sim(client, 2.5)
        assert res.status_code == 422
        assert "AREA_FLOAT_TYPE" in res.text

    def test_decimal_string_matches_fraction_string(self, client):
        a = sim(client, "2.5").json()
        b = sim(client, "5/2").json()
        assert a["requested_area"] == b["requested_area"] == "5/2"
        assert a["overall_status_code"] == b["overall_status_code"] == "CONSISTENT"

    def test_three_is_consistent_and_five_contradicts(self, client):
        ok = sim(client, "3").json()
        assert ok["overall_status_code"] == "CONSISTENT"
        assert ok["excess"] == "0"
        bad = sim(client, "5").json()
        assert bad["overall_status_code"] == "CONTRADICTION"
        assert bad["requested_area"] == "5"
        assert bad["seller_available_before"] == "3"
        assert bad["excess"] == "2"

    def test_decimal_excess_is_exact(self, client):
        data = sim(client, "3.1").json()
        assert data["overall_status_code"] == "CONTRADICTION"
        assert data["excess"] == "1/10"

    def test_date_field_is_honoured(self, client):
        data = sim(client, "3", date="2001-02-03").json()
        assert data["proposed_event"]["event_date"] == "2001-02-03"

    def test_null_and_blank_date_use_the_default(self, client):
        for value in (None, "", "  "):
            res = sim(client, "3", date=value)
            assert res.status_code == 200, value

    def test_bad_date_is_rejected(self, client):
        assert sim(client, "3", date="not-a-date").status_code == 422

    def test_unknown_parcel_is_404(self, client):
        res = client.post("/simulate", json={"parcel_id": "NOPE", "from_person": "H", "area": "1"})
        assert res.status_code == 404

    def test_invalid_role_is_422(self, client):
        res = client.post("/simulate?role=admin", json={
            "parcel_id": "PARCEL_LAB_DEMO", "from_person": "H", "area": "1"})
        assert res.status_code == 422

    def test_simulation_leaves_dataset_unchanged(self, client):
        before = client.get("/benchmark").json()["simulation_integrity"]
        sim(client, "5")
        sim(client, "5", **{"_query": ""})
        after = client.get("/benchmark").json()["simulation_integrity"]
        assert before["dataset_hash_before"] == after["dataset_hash_after"]
        assert after["unchanged"] is True


# ---------------------------------------------------------------------------
# Role-aware responses
# ---------------------------------------------------------------------------

STAGED_KEYS = {"rule_id", "calculation", "evidence_ids", "minimal_evidence_sets",
               "impact_event_ids", "not_minimized", "r1_calculation", "proposed_event"}


def keys_anywhere(obj, found=None):
    found = set() if found is None else found
    if isinstance(obj, dict):
        for k, v in obj.items():
            found.add(k)
            keys_anywhere(v, found)
    elif isinstance(obj, list):
        for item in obj:
            keys_anywhere(item, found)
    return found


class TestRoleAwareSimulate:
    def body(self, area="5"):
        return {"parcel_id": "PARCEL_LAB_DEMO", "from_person": "H", "area": area, "lang": "en"}

    def test_citizen_response_has_no_staged_fields(self, client):
        data = client.post("/simulate?role=citizen", json=self.body()).json()
        assert not (keys_anywhere(data) & STAGED_KEYS)
        text = str(data)
        assert "R1" not in text and "PROPOSED_EVENT" not in text and "SR_LAB" not in text

    def test_citizen_response_still_has_what_the_screen_needs(self, client):
        data = client.post("/simulate?role=citizen", json=self.body()).json()
        assert data["overall_status_code"] == "CONTRADICTION"
        assert data["requested_area"] == "5"
        assert data["seller_available_before"] == "3"
        assert data["excess"] == "2"
        assert data["alerts"]
        for a in data["alerts"]:
            assert set(a) == {"status", "status_code", "message", "recommended_next_step"}

    def test_reviewer_response_keeps_full_detail(self, client):
        data = client.post("/simulate?role=reviewer", json=self.body()).json()
        assert {"rule_id", "calculation", "evidence_ids"} <= keys_anywhere(data)
        assert data["r1_calculation"] == "requested 5, available 3, excess 2"

    def test_default_role_is_reviewer(self, client):
        data = client.post("/simulate", json=self.body()).json()
        assert "r1_calculation" in data


class TestRoleAwareParcels:
    def test_citizen_list_has_no_planted_or_category(self, client):
        data = client.get("/parcels?role=citizen&lang=en").json()
        assert len(data) == 30
        for item in data:
            assert "planted" not in item and "category" not in item

    def test_reviewer_list_keeps_staging_fields(self, client):
        data = client.get("/parcels?role=reviewer&lang=en").json()
        assert all("planted" in i and "category" in i for i in data)
        assert sum(1 for i in data if i["planted"]) == 9

    def test_invalid_role_is_422(self, client):
        assert client.get("/parcels?role=root").status_code == 422


# ---------------------------------------------------------------------------
# Benchmark naming
# ---------------------------------------------------------------------------

def test_benchmark_counts_cases_not_parcels(client):
    data = client.get("/benchmark").json()
    assert data["planted_case_count"] == 7
    assert data["planted_detected_count"] == 7
    assert "planted_parcel_count" not in data
    assert data["clean_false_alarm_count"] == 0


# ---------------------------------------------------------------------------
# Dataset path
# ---------------------------------------------------------------------------

def test_default_dataset_path_is_absolute_and_exists():
    assert DEFAULT_DATASET_PATH.is_absolute()
    assert DEFAULT_DATASET_PATH.is_file()
    assert DEFAULT_DATASET_PATH == REPO_ROOT / "data" / "demo_family.json"


def test_app_starts_from_a_different_working_directory(tmp_path):
    code = (
        "import sys; sys.path.insert(0, r'%s'); "
        "from jomigraph.api.app import create_app; "
        "app = create_app(); print(len(app.state.dataset.parcels))"
    ) % (REPO_ROOT / "src")
    env_cwd = tmp_path
    out = subprocess.run([sys.executable, "-c", code], cwd=env_cwd,
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "30"
