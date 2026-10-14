"""
JomiGraph AI — FastAPI Endpoint Test Suite
==========================================
Tests all FastAPI endpoints using FastAPI TestClient:
  1. GET  /parcels?lang=bn|en (default lang=bn, label, status_summary, planted/clean)
  2. GET  /parcel/{id}?lang= (survey records, events, graph {nodes, edges}, alerts)
  3. POST /simulate (purity, dataset hash unchanged, simulation result)
  4. POST /simulate float area rejection with HTTP 422
  5. GET  /benchmark (clean false alarms == 0, coverage table, simulation integrity)
"""

from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any
import pytest
from starlette.testclient import TestClient

from jomigraph.api.app import create_app
from jomigraph.engine.simulate import hash_dataset
from jomigraph.loader import load_dataset


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app(dataset_path="data/demo_family.json")
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. GET /parcels Tests
# ---------------------------------------------------------------------------

class TestGetParcelsEndpoint:
    def test_get_parcels_default_bn(self, client: TestClient):
        """GET /parcels defaults to Bengali labels and lists all parcels."""
        response = client.get("/parcels")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 30

        first = data[0]
        assert "id" in first
        assert "label" in first
        assert "status_summary" in first
        assert "planted" in first
        assert "category" in first
        # Bengali default uses "দাগ"
        assert "দাগ" in first["label"]

    def test_get_parcels_english(self, client: TestClient):
        """GET /parcels?lang=en produces English labels."""
        response = client.get("/parcels?lang=en")
        assert response.status_code == 200

        data = response.json()
        first = data[0]
        assert "Dag" in first["label"]

    def test_get_parcels_invalid_lang_returns_422(self, client: TestClient):
        """GET /parcels?lang=invalid returns 422."""
        response = client.get("/parcels?lang=fr")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 2. GET /parcel/{id} Tests
# ---------------------------------------------------------------------------

class TestGetParcelDetailEndpoint:
    def test_get_parcel_story_01_success(self, client: TestClient):
        """GET /parcel/PARCEL_STORY_01 returns complete records, graph, and alerts."""
        response = client.get("/parcel/PARCEL_STORY_01?lang=bn")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == "PARCEL_STORY_01"
        assert data["mouza"] == "Dhanmondi"
        assert data["dag_no"] == "101"

        # Survey records (CS, SA, RS, BS)
        srs = data["survey_records"]
        assert len(srs) == 4
        for sr in srs:
            assert isinstance(sr["recorded_area"], str)
            assert not isinstance(sr["recorded_area"], float)

        # Events timeline (Gifts connecting surveys)
        events = data["events"]
        assert len(events) == 3
        for e in events:
            assert isinstance(e["area"], str)
            assert not isinstance(e["area"], float)

        # Cytoscape graph
        graph = data["graph"]
        assert "nodes" in graph
        assert "edges" in graph
        assert len(graph["nodes"]) > 0
        assert len(graph["edges"]) > 0

        # Node structure verification
        first_node = graph["nodes"][0]
        assert "data" in first_node
        assert "id" in first_node["data"]
        assert "label" in first_node["data"]
        assert "type" in first_node["data"]

        # Alerts (Clean parcel with lang=bn: only Consistent)
        alerts = data["alerts"]
        assert len(alerts) > 0
        for a in alerts:
            assert a["status"] == "সঙ্গতিপূর্ণ"
            assert "evidence_ids" in a
            assert len(a["evidence_ids"]) > 0

    def test_get_planted_parcel_returns_contradiction_alert(self, client: TestClient):
        """GET /parcel/PARCEL_PLANTED_R1 returns R1 Contradiction Found."""
        response = client.get("/parcel/PARCEL_PLANTED_R1?lang=en")
        assert response.status_code == 200

        data = response.json()
        alerts = data["alerts"]
        r1_alerts = [a for a in alerts if a["rule_id"] == "R1" and a["status"] == "Contradiction Found"]
        assert len(r1_alerts) == 1
        assert "excess 2" in r1_alerts[0]["calculation"]

    def test_get_nonexistent_parcel_returns_404(self, client: TestClient):
        """GET /parcel/{id} with unknown ID returns 404."""
        response = client.get("/parcel/NON_EXISTENT_PARCEL")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# 3. POST /simulate Tests (Purity, Invariance, and Rejection)
# ---------------------------------------------------------------------------

class TestSimulateEndpoint:
    def test_simulate_leaves_dataset_hash_unchanged(self, client: TestClient):
        """
        POST /simulate must evaluate counterfactually and leave the dataset hash unchanged.
        Never persists any event to the dataset history.
        """
        app_dataset = client.app.state.dataset  # type: ignore[attr-defined]

        # 1. Compute canonical hash before simulation
        all_events_before = [e for h in app_dataset.histories for e in h.events]
        all_srs_before = [sr for h in app_dataset.histories for sr in h.survey_records]
        hash_before = hash_dataset(all_events_before, all_srs_before)

        events_count_before = len(app_dataset.get_history("PARCEL_LAB_DEMO").events)
        assert events_count_before == 1

        # 2. Simulate 5-decimal sale from H (Tareq) on PARCEL_LAB_DEMO
        payload = {
            "parcel_id": "PARCEL_LAB_DEMO",
            "from_person": "P_G3_TAREQ",
            "to_person": "P_EXT_MONIR",
            "area": "5",
            "date": "1996-05-15",
            "lang": "en",
        }
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["available_before"] == "3"
        assert data["available_after"] == "-2"

        # Check R1 alert
        r1_alerts = [a for a in data["alerts"] if a["rule_id"] == "R1"]
        assert len(r1_alerts) == 1
        assert r1_alerts[0]["status"] == "Contradiction Found"
        assert "requested 5, available 3, excess 2" in r1_alerts[0]["calculation"]

        # 3. Compute canonical hash after simulation -> Must be strictly identical
        all_events_after = [e for h in app_dataset.histories for e in h.events]
        all_srs_after = [sr for h in app_dataset.histories for sr in h.survey_records]
        hash_after = hash_dataset(all_events_after, all_srs_after)

        assert hash_before == hash_after, "Simulation mutated the baseline dataset hash!"
        events_count_after = len(app_dataset.get_history("PARCEL_LAB_DEMO").events)
        assert events_count_after == events_count_before, "Simulation appended events to stored history!"

    def test_simulate_3_decimals_returns_consistent(self, client: TestClient):
        """Simulate sale of 3 decimals from available 3 returns Consistent."""
        payload = {
            "parcel_id": "PARCEL_LAB_DEMO",
            "from_person": "P_G3_TAREQ",
            "to_person": "P_EXT_MONIR",
            "area": "3",
            "date": "1996-05-15",
            "lang": "bn",
        }
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["available_before"] == "3"
        assert data["available_after"] == "0"

        r1_alerts = [a for a in data["alerts"] if a["rule_id"] == "R1"]
        assert len(r1_alerts) == 1
        assert r1_alerts[0]["status"] == "সঙ্গতিপূর্ণ"
        for a in data["alerts"]:
            assert a["status"] == "সঙ্গতিপূর্ণ"

    def test_bn_simulate_response_contains_no_ascii_only_fields(self, client: TestClient):
        """
        Verify that a bn /simulate response contains no ASCII-only
        message, status, or calculation fields. Everything returned for lang=bn
        must be properly localized into Bangla.
        """
        def is_ascii_only(s: str) -> bool:
            has_alpha = any(c.isalpha() for c in s)
            all_ascii = all(ord(c) < 128 for c in s)
            return has_alpha and all_ascii

        # Test with 5-decimal sale (R1 contradiction + R3 consistent)
        res_5 = client.post(
            "/simulate",
            json={
                "parcel_id": "PARCEL_LAB_DEMO",
                "from_person": "H",
                "area": "5",
                "lang": "bn",
            },
        )
        assert res_5.status_code == 200
        data_5 = res_5.json()

        # Top-level calculation
        r1_calc = data_5.get("r1_calculation")
        assert r1_calc is not None
        assert not is_ascii_only(r1_calc), f"r1_calculation is ASCII-only: {r1_calc}"
        assert "অনুরোধকৃত" in r1_calc
        assert "প্রাপ্য" in r1_calc
        assert "অতিরিক্ত" in r1_calc

        # Check every alert
        assert len(data_5["alerts"]) > 0
        for alert in data_5["alerts"]:
            status = alert["status"]
            msg = alert["message"]
            calc = alert["calculation"]
            step = alert["recommended_next_step"]

            assert not is_ascii_only(status), f"Alert status is ASCII-only: {status}"
            assert not is_ascii_only(msg), f"Alert message is ASCII-only: {msg}"
            assert not is_ascii_only(calc), f"Alert calculation is ASCII-only: {calc}"
            assert not is_ascii_only(step), f"Alert next_step is ASCII-only: {step}"

        # Test with 3-decimal sale (consistent case)
        res_3 = client.post(
            "/simulate",
            json={
                "parcel_id": "PARCEL_LAB_DEMO",
                "from_person": "H",
                "area": "3",
                "lang": "bn",
            },
        )
        assert res_3.status_code == 200
        data_3 = res_3.json()
        assert not is_ascii_only(data_3["r1_calculation"])
        for alert in data_3["alerts"]:
            assert not is_ascii_only(alert["status"])
            assert not is_ascii_only(alert["message"])
            assert not is_ascii_only(alert["calculation"])
            assert not is_ascii_only(alert["recommended_next_step"])

    def test_simulate_fraction_string_area_accepted(self, client: TestClient):
        """Exact rational fraction strings e.g. '7/2' are accepted."""
        payload = {
            "parcel_id": "PARCEL_LAB_DEMO",
            "from_person": "P_G3_TAREQ",
            "to_person": "P_EXT_MONIR",
            "area": "5/2",  # 2.5 decimals
            "date": "1996-05-15",
            "lang": "en",
        }
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["available_before"] == "3"
        assert data["available_after"] == "1/2"

    def test_simulate_rejects_float_area_with_422(self, client: TestClient):
        """
        Numeric float literals and decimal float strings in request body
        must be rejected with HTTP 422 Unprocessable Entity.
        """
        # 1. Numeric float literal in JSON: {"area": 5.5}
        payload_float_literal = {
            "parcel_id": "PARCEL_LAB_DEMO",
            "from_person": "P_G3_TAREQ",
            "to_person": "P_EXT_MONIR",
            "area": 5.5,
            "date": "1996-05-15",
        }
        res1 = client.post("/simulate", json=payload_float_literal)
        assert res1.status_code == 422
        assert "Float" in res1.text or "float" in res1.text

        # 2. Decimal float string in JSON: {"area": "5.5"}
        payload_float_str = {
            "parcel_id": "PARCEL_LAB_DEMO",
            "from_person": "P_G3_TAREQ",
            "to_person": "P_EXT_MONIR",
            "area": "5.5",
            "date": "1996-05-15",
        }
        res2 = client.post("/simulate", json=payload_float_str)
        assert res2.status_code == 422
        assert "Float" in res2.text or "forbidden" in res2.text

        # 3. Invalid non-rational string: {"area": "five"}
        payload_bad_str = {
            "parcel_id": "PARCEL_LAB_DEMO",
            "from_person": "P_G3_TAREQ",
            "to_person": "P_EXT_MONIR",
            "area": "five",
            "date": "1996-05-15",
        }
        res3 = client.post("/simulate", json=payload_bad_str)
        assert res3.status_code == 422

    def test_simulate_unknown_parcel_returns_404(self, client: TestClient):
        """Simulate on unknown parcel returns 404."""
        payload = {
            "parcel_id": "UNKNOWN_PARCEL",
            "from_person": "P_G3_TAREQ",
            "to_person": "P_EXT_MONIR",
            "area": "1",
            "date": "1996-05-15",
        }
        response = client.post("/simulate", json=payload)
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# 4. GET /benchmark Tests
# ---------------------------------------------------------------------------

class TestBenchmarkEndpoint:
    def test_get_benchmark_metrics_and_coverage(self, client: TestClient):
        """
        GET /benchmark returns:
          - clean_false_alarm_count == 0
          - coverage table covering R1-R7 (with R1-R5 planted & detected)
          - simulation integrity verification confirming dataset hash is unchanged
        """
        response = client.get("/benchmark")
        assert response.status_code == 200

        data = response.json()
        assert data["clean_false_alarm_count"] == 0

        # Coverage table
        cov = {row["rule_id"]: row for row in data["coverage_table"]}
        assert set(cov.keys()) == {"R1", "R2", "R3", "R4", "R5", "R6", "R7"}

        # Planted cases
        assert cov["R1"]["has_planted_case"] is True
        assert cov["R1"]["detected"] is True
        assert cov["R1"]["status_detected"] == "Contradiction Found"

        assert cov["R2"]["has_planted_case"] is True
        assert cov["R2"]["detected"] is True
        assert cov["R2"]["status_detected"] == "Contradiction Found"

        assert cov["R3"]["has_planted_case"] is True
        assert cov["R3"]["detected"] is True
        assert cov["R3"]["status_detected"] == "Contradiction Found"

        assert cov["R4"]["has_planted_case"] is True
        assert cov["R4"]["detected"] is True
        assert cov["R4"]["status_detected"] == "Contradiction Found"

        assert cov["R5"]["has_planted_case"] is True
        assert cov["R5"]["detected"] is True
        assert cov["R5"]["status_detected"] == "Review Required"

        # Simulation integrity
        sim_int = data["simulation_integrity"]
        assert sim_int["unchanged"] is True
        assert sim_int["dataset_hash_before"] == sim_int["dataset_hash_after"]


# ---------------------------------------------------------------------------
# 5. UI and Static Asset Tests
# ---------------------------------------------------------------------------

class TestUIEndpoints:
    def test_get_root_returns_200_and_serves_html(self, client: TestClient):
        """GET / returns HTTP 200 with HTML application shell."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        text = response.text
        assert "app.js" in text
        assert "style.css" in text
        assert "app-root" in text

    def test_static_assets_are_served(self, client: TestClient):
        """Static assets (/style.css, /app.js) are accessible at root mount."""
        res_css = client.get("/style.css")
        assert res_css.status_code == 200
        assert "Noto Sans Bengali" in res_css.text

        res_js = client.get("/app.js")
        assert res_js.status_code == 200
        assert "ui_strings" in res_js.text

    def test_ui_strings_complete_in_both_bn_and_en(self, client: TestClient):
        """
        Verify that every ui_strings key exists in both bn and en:
          - No key is missing in either language.
          - No string is empty.
          - Neither locale uses forbidden words ('fraud' or 'জালিয়াতি').
        """
        # Test via /ui-strings endpoint
        res = client.get("/ui-strings")
        assert res.status_code == 200
        data = res.json()
        assert "bn" in data
        assert "en" in data

        bn_keys = set(data["bn"].keys())
        en_keys = set(data["en"].keys())

        # Assert 100% key parity
        assert bn_keys == en_keys, f"Keys mismatch! In BN but not EN: {bn_keys - en_keys}; In EN but not BN: {en_keys - bn_keys}"
        assert len(bn_keys) >= 40, "Expected at least 40 UI string keys"

        # Check values are non-empty
        for k in bn_keys:
            bn_val = data["bn"][k]
            en_val = data["en"][k]
            assert isinstance(bn_val, str) and len(bn_val.strip()) > 0, f"BN key '{k}' is empty!"
            assert isinstance(en_val, str) and len(en_val.strip()) > 0, f"EN key '{k}' is empty!"

            # Wording rule: Never use 'fraud' or 'জালিয়াতি'
            assert "fraud" not in bn_val.lower(), f"Forbidden word 'fraud' found in BN key '{k}'"
            assert "fraud" not in en_val.lower(), f"Forbidden word 'fraud' found in EN key '{k}'"
            assert "জালিয়াতি" not in bn_val, f"Forbidden word 'জালিয়াতি' found in BN key '{k}'"
            assert "জালিয়াতি" not in en_val, f"Forbidden word 'জালিয়াতি' found in EN key '{k}'"

        # Also verify app.js itself embeds ui_strings with complete parity
        app_js_path = Path("src/jomigraph/ui/app.js")
        assert app_js_path.is_file()
        js_text = app_js_path.read_text(encoding="utf-8")
        assert "ui_strings" in js_text
        assert "fraud" not in js_text.lower()
        assert "জালিয়াতি" not in js_text

    def test_vendor_assets_accessible_locally(self, client: TestClient):
        """Downloaded vendor assets (cytoscape.min.js and noto-sans-bengali.css) are served locally."""
        res_cy = client.get("/vendor/cytoscape.min.js")
        assert res_cy.status_code == 200
        assert len(res_cy.content) > 100_000

        res_font = client.get("/vendor/noto-sans-bengali.css")
        assert res_font.status_code == 200
        assert "Noto Sans Bengali" in res_font.text


# ---------------------------------------------------------------------------
# 6. GET /search Tests
# ---------------------------------------------------------------------------

class TestSearchEndpoint:
    def test_search_by_parcel_id(self, client: TestClient):
        """Search matches parcel ID case-insensitively."""
        response = client.get("/search?q=parcel_story_01")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        first = data[0]
        assert first["parcel_id"] == "PARCEL_STORY_01"
        assert first["matched_on"] == "parcel_id"

    def test_search_by_dag_no_english_and_bangla(self, client: TestClient):
        """Search by dag number matches both English ('101') and Bangla ('১০১') digits."""
        res_en = client.get("/search?q=101")
        assert res_en.status_code == 200
        data_en = res_en.json()
        assert any(p["parcel_id"] == "PARCEL_STORY_01" and p["matched_on"] == "dag_no" for p in data_en)

        res_bn = client.get("/search?q=১০১")
        assert res_bn.status_code == 200
        data_bn = res_bn.json()
        assert any(p["parcel_id"] == "PARCEL_STORY_01" and p["matched_on"] == "dag_no" for p in data_bn)

    def test_search_by_holder_name_case_insensitive(self, client: TestClient):
        """Search by holder name matches recorded holders case-insensitively."""
        response = client.get("/search?q=abdur")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(p["parcel_id"] == "PARCEL_STORY_01" and p["matched_on"] == "holder_name" for p in data)

    def test_search_by_khatian_no_english_and_bangla(self, client: TestClient):
        """Search by khatian number matches both English and Bangla digits."""
        res_en = client.get("/search?q=1001")
        assert res_en.status_code == 200
        data_en = res_en.json()
        assert any(p["parcel_id"] == "PARCEL_STORY_01" and p["matched_on"] == "khatian_no" for p in data_en)

        res_bn = client.get("/search?q=১০০১")
        assert res_bn.status_code == 200
        data_bn = res_bn.json()
        assert any(p["parcel_id"] == "PARCEL_STORY_01" and p["matched_on"] == "khatian_no" for p in data_bn)

    def test_search_by_deed_no_english_and_bangla(self, client: TestClient):
        """Search by deed number matches both English and Bangla digits."""
        res_en = client.get("/search?q=1948")
        assert res_en.status_code == 200
        data_en = res_en.json()
        assert any(p["parcel_id"] == "PARCEL_STORY_01" and p["matched_on"] == "deed_no" for p in data_en)

        res_bn = client.get("/search?q=১৯৪৮")
        assert res_bn.status_code == 200
        data_bn = res_bn.json()
        assert any(p["parcel_id"] == "PARCEL_STORY_01" and p["matched_on"] == "deed_no" for p in data_bn)

    def test_search_empty_or_one_char_returns_empty_list(self, client: TestClient):
        """Search with an empty string or single character returns an empty list."""
        assert client.get("/search?q=").json() == []
        assert client.get("/search?q=a").json() == []
        assert client.get("/search?q=1").json() == []
        assert client.get("/search?q=১").json() == []
        assert client.get("/search?q=   ").json() == []

    def test_search_no_match_returns_empty_list(self, client: TestClient):
        """Search for a non-matching query returns an empty list."""
        res = client.get("/search?q=nonexistent_query_xyz")
        assert res.status_code == 200
        assert res.json() == []


# ---------------------------------------------------------------------------
# 7. Minimal Evidence and Impact Tests
# ---------------------------------------------------------------------------

class TestMinimalEvidenceAndImpact:
    def test_reviewer_alert_contains_minimal_evidence_and_not_minimized_flag(self, client: TestClient):
        """Reviewer alert on contradiction parcel exposes minimal_evidence_sets and not_minimized."""
        response = client.get("/parcel/PARCEL_PLANTED_R1?role=reviewer&lang=en")
        assert response.status_code == 200
        data = response.json()
        r1_alerts = [a for a in data["alerts"] if a["rule_id"] == "R1" and a["status"] == "Contradiction Found"]
        assert len(r1_alerts) == 1
        r1 = r1_alerts[0]

        assert "minimal_evidence_sets" in r1
        assert isinstance(r1["minimal_evidence_sets"], list)
        assert len(r1["minimal_evidence_sets"]) >= 1
        assert "not_minimized" in r1
        assert r1["not_minimized"] is False
        assert "impact_event_ids" in r1
        assert r1["impact_event_ids"] == ["E_PLANTED_R1_3"]

    def test_impact_lookup_with_cyclic_or_self_referencing_terminates(self):
        """Verify impact_lookup terminates cleanly with self-referencing or cyclic events."""
        from jomigraph.engine.evidence import impact_lookup
        from jomigraph.models import Event, EventType

        # 1. Self-referencing event
        e_self = Event(
            id="E_SELF",
            type=EventType.SALE,
            seq=1,
            event_date=date(2000, 1, 1),
            parcel_id="P1",
            from_person="H1",
            to_person="H2",
            area=Fraction(1),
            deed_id=None,
            portion_id=None,
            linked_event_id="E_SELF",
            source_record_id=None,
        )
        res_self = impact_lookup("E_SELF", [e_self])
        assert res_self == []

        # 2. Cyclic reference: E1 links to E2, E2 links to E1
        e1 = Event(
            id="E1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2000, 1, 1),
            parcel_id="P1",
            from_person="H1",
            to_person="H2",
            area=Fraction(1),
            deed_id=None,
            portion_id=None,
            linked_event_id="E2",
            source_record_id=None,
        )
        e2 = Event(
            id="E2",
            type=EventType.SALE,
            seq=2,
            event_date=date(2001, 1, 1),
            parcel_id="P1",
            from_person="H2",
            to_person="H3",
            area=Fraction(1),
            deed_id=None,
            portion_id=None,
            linked_event_id="E1",
            source_record_id=None,
        )
        res_e1 = impact_lookup("E1", [e1, e2])
        assert res_e1 == ["E2"]
        res_e2 = impact_lookup("E2", [e1, e2])
        assert res_e2 == ["E1"]


# ---------------------------------------------------------------------------
# 8. Role Parameter Tests (Citizen vs. Reviewer)
# ---------------------------------------------------------------------------

class TestRoleParameter:
    FORBIDDEN_CITIZEN_KEYS = {
        "rule_id",
        "calculation",
        "evidence_ids",
        "minimal_evidence_sets",
        "not_minimized",
        "impact_event_ids",
    }

    def _assert_no_forbidden_keys(self, obj: Any):
        """Recursively ensure none of the forbidden reviewer keys appear anywhere."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                assert k not in self.FORBIDDEN_CITIZEN_KEYS, f"Leak: Forbidden key '{k}' found in response!"
                self._assert_no_forbidden_keys(v)
        elif isinstance(obj, list):
            for item in obj:
                self._assert_no_forbidden_keys(item)

    def test_default_role_is_reviewer(self, client: TestClient):
        """When role is omitted, default is 'reviewer' and returns technical fields."""
        response = client.get("/parcel/PARCEL_PLANTED_R1")
        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data
        assert len(data["alerts"]) > 0
        first_alert = data["alerts"][0]
        assert "rule_id" in first_alert
        assert "calculation" in first_alert
        assert "evidence_ids" in first_alert
        assert "minimal_evidence_sets" in first_alert
        assert "not_minimized" in first_alert
        assert "impact_event_ids" in first_alert

    def test_citizen_role_overall_status_and_filtered_alerts(self, client: TestClient):
        """
        Citizen role returns worst status as overall_status and ONLY non-consistent alerts.
        Repeated consistent alerts are excluded.
        """
        # 1. Contradiction planted parcel
        res_p1 = client.get("/parcel/PARCEL_PLANTED_R1?role=citizen&lang=en")
        assert res_p1.status_code == 200
        data_p1 = res_p1.json()
        assert data_p1["overall_status"] == "Contradiction Found"
        # Only 1 non-consistent alert (R1 over-transfer) returned; consistent alerts excluded
        assert len(data_p1["alerts"]) == 1
        assert data_p1["alerts"][0]["status"] == "Contradiction Found"

        # 2. Clean parcel (all consistent) -> 0 non-consistent alerts returned
        res_clean = client.get("/parcel/PARCEL_STORY_01?role=citizen&lang=en")
        assert res_clean.status_code == 200
        data_clean = res_clean.json()
        assert data_clean["overall_status"] == "Consistent with supplied records"
        assert len(data_clean["alerts"]) == 0

    def test_citizen_leak_test_no_reviewer_keys_anywhere(self, client: TestClient):
        """
        Comprehensive leak test asserting that none of the reviewer keys appear
        anywhere in /parcel or /report responses for citizen role.
        """
        res_parcel = client.get("/parcel/PARCEL_PLANTED_R1?role=citizen")
        assert res_parcel.status_code == 200
        self._assert_no_forbidden_keys(res_parcel.json())

        res_report = client.get("/report/PARCEL_PLANTED_R1?role=citizen")
        assert res_report.status_code == 200
        self._assert_no_forbidden_keys(res_report.json())


# ---------------------------------------------------------------------------
# 9. GET /report/{parcel_id} Tests
# ---------------------------------------------------------------------------

class TestReportEndpoint:
    def test_report_citizen_role_structure_and_keys(self, client: TestClient):
        """GET /report/{id}?role=citizen returns structured report with citizen alerts only."""
        response = client.get("/report/PARCEL_STORY_01?role=citizen&lang=bn")
        assert response.status_code == 200
        data = response.json()

        assert data["parcel_id"] == "PARCEL_STORY_01"
        assert data["role"] == "citizen"
        assert data["lang"] == "bn"
        assert data["overall_status"] == "সঙ্গতিপূর্ণ"
        assert "parcel" in data
        assert "records" in data
        assert "survey_records" in data["records"]
        assert "events" in data["records"]
        assert "alerts" in data
        # Clean parcel has zero non-consistent alerts
        assert len(data["alerts"]) == 0
        assert "recommended_next_steps" in data
        assert isinstance(data["recommended_next_steps"], list)
        assert "disclaimer" in data
        assert len(data["disclaimer"]) > 0
        assert "dataset_hash" in data
        assert len(data["dataset_hash"]) == 64  # SHA-256 hex digest

    def test_report_citizen_role_with_contradiction(self, client: TestClient):
        """GET /report/{id}?role=citizen on planted parcel returns overall contradiction and single alert."""
        response = client.get("/report/PARCEL_PLANTED_R1?role=citizen&lang=en")
        assert response.status_code == 200
        data = response.json()
        assert data["overall_status"] == "Contradiction Found"
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["status"] == "Contradiction Found"

    def test_report_reviewer_role_includes_technical_fields(self, client: TestClient):
        """GET /report/{id}?role=reviewer returns rule IDs, calculations, evidence sets, and impact."""
        response = client.get("/report/PARCEL_PLANTED_R1?role=reviewer&lang=en")
        assert response.status_code == 200
        data = response.json()

        assert data["role"] == "reviewer"
        assert data["overall_status"] == "Contradiction Found"
        assert len(data["alerts"]) > 0
        r1_alerts = [a for a in data["alerts"] if a.get("rule_id") == "R1" and a.get("status") == "Contradiction Found"]
        assert len(r1_alerts) == 1
        r1 = r1_alerts[0]
        assert "calculation" in r1
        assert "evidence_ids" in r1
        assert "minimal_evidence_sets" in r1
        assert "not_minimized" in r1
        assert "impact_event_ids" in r1

    def test_report_bilingual_disclaimer(self, client: TestClient):
        """Disclaimer text is provided in both bn and en without forbidden words."""
        res_bn = client.get("/report/PARCEL_STORY_01?lang=bn")
        assert res_bn.status_code == 200
        disc_bn = res_bn.json()["disclaimer"]
        assert "আইনি সিদ্ধান্ত নয়" in disc_bn
        assert "জালিয়াতি" not in disc_bn

        res_en = client.get("/report/PARCEL_STORY_01?lang=en")
        assert res_en.status_code == 200
        disc_en = res_en.json()["disclaimer"]
        assert "not a legal ruling" in disc_en.lower()

    def test_report_nonexistent_parcel_returns_404(self, client: TestClient):
        """GET /report/{id} on non-existent parcel returns 404."""
        response = client.get("/report/NON_EXISTENT_PARCEL")
        assert response.status_code == 404
