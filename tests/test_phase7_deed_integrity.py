"""
Tests for JomiGraph AI v1.1 — Phase 7: Deed Integrity & Identification
======================================================================
Covers:
  1. F13 / R12: Canonical deed content hashing (SHA-256) and deterministic serialization
  2. F13: POST /verify-deed API endpoint (tamper detection, three statuses, role hygiene)
  3. F13: QR generation contract and relative payload format
  4. F14 / R13: Deed-number reuse detection (Review Required semantics, multi-dag support)
  5. F15 / R14: Dummy identity numbers and person disambiguation (search, graph, history)
  6. Offline contract and absence of external network calls
"""

from __future__ import annotations

from datetime import date
from fractions import Fraction
from pathlib import Path
import json
import re
import pytest
from starlette.testclient import TestClient

from jomigraph.api.app import create_app
from jomigraph.engine.deed_hash import (
    build_deed_qr_payload,
    canonical_area_repr,
    canonical_deed_payload,
    hash_deed_content,
)
from jomigraph.engine.rules import (
    Alert,
    Status,
    check_r12,
    check_r13,
    check_r14,
)
from jomigraph.loader import load_dataset
from jomigraph.models import Deed, Event, EventType, Parcel, ParcelHistory, Person, SurveyRecord

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_V11_PATH = PROJECT_ROOT / "data" / "demo_v11.json"


# ===========================================================================
# 1. F13 / R12 Canonical Deed Hashing & Determinism
# ===========================================================================

class TestDeedCanonicalHashing:
    """Tests for deterministic serialization, exact rational areas, and tamper detection."""

    def test_canonical_area_repr_exact_fractions(self):
        assert canonical_area_repr(10) == "10"
        assert canonical_area_repr("10") == "10"
        assert canonical_area_repr(Fraction(10, 1)) == "10"
        assert canonical_area_repr(Fraction(5, 2)) == "5/2"
        assert canonical_area_repr("5/2") == "5/2"
        assert canonical_area_repr(Fraction(7, 3)) == "7/3"

    def test_canonical_payload_normalizes_whitespace(self):
        payload1 = canonical_deed_payload(
            deed_no=" 4021 ",
            registration_date="2020-04-10",
            parcel_id=" PARCEL_101 ",
            seller="  Abdul   Latif  ",
            buyer="Abdul Karim ",
            area=" 10 ",
        )
        payload2 = canonical_deed_payload(
            deed_no="4021",
            registration_date=date(2020, 4, 10),
            parcel_id="PARCEL_101",
            seller="Abdul Latif",
            buyer="Abdul Karim",
            area=Fraction(10, 1),
        )
        assert payload1 == payload2
        assert payload1["seller"] == "Abdul Latif"
        assert payload1["buyer"] == "Abdul Karim"
        assert payload1["area"] == "10"

    def test_hash_deed_content_deterministic(self):
        h1 = hash_deed_content("4021", "2020-04-10", "P101", "Seller A", "Buyer B", "10")
        h2 = hash_deed_content(" 4021 ", date(2020, 4, 10), " P101 ", "Seller  A", "Buyer B ", Fraction(10, 1))
        assert h1 == h2
        assert len(h1) == 64
        assert re.match(r"^[0-9a-f]{64}$", h1)

    def test_hash_changes_on_any_meaningful_tamper(self):
        base_hash = hash_deed_content("4021", "2020-04-10", "P101", "Seller A", "Buyer B", "10")

        # Tamper area: 10 -> 12
        h_area = hash_deed_content("4021", "2020-04-10", "P101", "Seller A", "Buyer B", "12")
        assert h_area != base_hash

        # Tamper seller: Seller A -> Imposter
        h_seller = hash_deed_content("4021", "2020-04-10", "P101", "Imposter", "Buyer B", "10")
        assert h_seller != base_hash

        # Tamper buyer
        h_buyer = hash_deed_content("4021", "2020-04-10", "P101", "Seller A", "Imposter", "10")
        assert h_buyer != base_hash

        # Tamper date
        h_date = hash_deed_content("4021", "2020-04-11", "P101", "Seller A", "Buyer B", "10")
        assert h_date != base_hash

        # Tamper deed_no
        h_deed = hash_deed_content("4022", "2020-04-10", "P101", "Seller A", "Buyer B", "10")
        assert h_deed != base_hash

        # Tamper parcel_id
        h_parcel = hash_deed_content("4021", "2020-04-10", "P102", "Seller A", "Buyer B", "10")
        assert h_parcel != base_hash

    def test_content_hash_field_not_hashed_into_itself(self):
        """Verify content_hash is not part of canonical payload."""
        payload = canonical_deed_payload("4021", "2020-04-10", "P101", "Seller", "Buyer", "5")
        assert "content_hash" not in payload
        assert "id" not in payload

    def test_qr_payload_format(self):
        h = "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0"
        qr = build_deed_qr_payload("4021", h)
        assert qr == "#/verify-deed?deed_no=4021&hash=a1b2c3d4e5f67890"
        assert len(qr.split("hash=")[1]) == 16


# ===========================================================================
# 2. Rule R12 Direct Pure Evaluation
# ===========================================================================

class TestRuleR12Logic:
    """Direct tests for check_r12 rule implementation."""

    def test_r12_consistent_on_matching_fingerprint(self):
        h = hash_deed_content("D-101", date(2020, 1, 1), "PARCEL_1", "P_SELLER", "P_BUYER", Fraction(5, 1))
        deed = Deed(id="D1", deed_no="D-101", registration_date=date(2020, 1, 1), content_hash=h)
        event = Event(
            id="E1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2020, 1, 1),
            parcel_id="PARCEL_1",
            from_person="P_SELLER",
            to_person="P_BUYER",
            area=Fraction(5, 1),
            deed_id="D1",
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        alert = check_r12(deed=deed, trigger_event=event, claimed_hash=h)
        assert alert.status == Status.CONSISTENT
        assert alert.rule_id == "R12"

    def test_r12_contradiction_on_tampered_area(self):
        h = hash_deed_content("D-101", date(2020, 1, 1), "PARCEL_1", "P_SELLER", "P_BUYER", Fraction(5, 1))
        deed = Deed(id="D1", deed_no="D-101", registration_date=date(2020, 1, 1), content_hash=h)
        # Event has tampered area = 7
        event = Event(
            id="E1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2020, 1, 1),
            parcel_id="PARCEL_1",
            from_person="P_SELLER",
            to_person="P_BUYER",
            area=Fraction(7, 1),
            deed_id="D1",
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        alert = check_r12(deed=deed, trigger_event=event)
        assert alert.status == Status.CONTRADICTION
        assert "tamper detected" in alert.calculation

    def test_r12_contradiction_on_mismatched_claimed_hash(self):
        h = hash_deed_content("D-101", date(2020, 1, 1), "PARCEL_1", "P_SELLER", "P_BUYER", Fraction(5, 1))
        deed = Deed(id="D1", deed_no="D-101", registration_date=date(2020, 1, 1), content_hash=h)
        event = Event(
            id="E1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2020, 1, 1),
            parcel_id="PARCEL_1",
            from_person="P_SELLER",
            to_person="P_BUYER",
            area=Fraction(5, 1),
            deed_id="D1",
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        # Provide completely wrong claimed hash
        alert = check_r12(deed=deed, trigger_event=event, claimed_hash="deadbeef" * 8)
        assert alert.status == Status.CONTRADICTION

    def test_r12_consistent_with_16_char_qr_hash_prefix(self):
        h = hash_deed_content("D-101", date(2020, 1, 1), "PARCEL_1", "P_SELLER", "P_BUYER", Fraction(5, 1))
        deed = Deed(id="D1", deed_no="D-101", registration_date=date(2020, 1, 1), content_hash=h)
        event = Event(
            id="E1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2020, 1, 1),
            parcel_id="PARCEL_1",
            from_person="P_SELLER",
            to_person="P_BUYER",
            area=Fraction(5, 1),
            deed_id="D1",
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        # Supply 16-hex char prefix from QR link
        alert = check_r12(deed=deed, trigger_event=event, claimed_hash=h[:16])
        assert alert.status == Status.CONSISTENT

    def test_r12_review_required_when_legacy_deed_has_no_content_hash(self):
        deed = Deed(id="D_LEGACY", deed_no="D-1970-01", registration_date=date(1970, 1, 1), content_hash=None)
        event = Event(
            id="E1",
            type=EventType.SALE,
            seq=1,
            event_date=date(1970, 1, 1),
            parcel_id="PARCEL_1",
            from_person="P_SELLER",
            to_person="P_BUYER",
            area=Fraction(5, 1),
            deed_id="D_LEGACY",
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        alert = check_r12(deed=deed, trigger_event=event)
        assert alert.status == Status.REVIEW
        assert "No registry content fingerprint recorded" in alert.calculation

    def test_r12_review_required_on_missing_input_fields(self):
        event = Event(
            id="E1",
            type=EventType.SALE,
            seq=1,
            event_date=None,
            parcel_id="PARCEL_1",
            from_person=None,
            to_person="P_BUYER",
            area=None,
            deed_id=None,
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        alert = check_r12(deed=None, trigger_event=event)
        assert alert.status == Status.REVIEW


# ===========================================================================
# 3. POST /verify-deed API Endpoint
# ===========================================================================

class TestVerifyDeedAPI:
    """Tests for the /verify-deed endpoint, request validation, and role hygiene."""

    @pytest.fixture
    def client(self):
        ds = load_dataset(DEMO_V11_PATH)
        app = create_app(dataset=ds)
        return TestClient(app)

    def test_verify_deed_match_consistent_reviewer(self, client):
        # Look up clean R12 deed in demo_v11
        payload = {
            "deed_no": "D-V11-1202",
            "registration_date": "2021-06-15",
            "parcel_id": "PARCEL_CLEAN_R12",
            "seller": "P_V11_CLEAN_H1",
            "buyer": "P_V11_CLEAN_H2",
            "area": "4",
            "role": "reviewer",
            "lang": "en",
        }
        # Compute exact hash to provide as claimed_hash
        expected_hash = hash_deed_content("D-V11-1202", "2021-06-15", "PARCEL_CLEAN_R12", "P_V11_CLEAN_H1", "P_V11_CLEAN_H2", "4")
        payload["claimed_hash"] = expected_hash

        resp = client.post("/verify-deed", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status_code"] == "CONSISTENT"
        assert data["rule_id"] == "R12"
        assert data["matches_registry"] is True
        assert data["computed_hash"] == expected_hash
        assert data["recorded_hash"] == expected_hash
        assert data["claimed_hash"] == expected_hash
        assert "#/verify-deed?deed_no=D-V11-1202&hash=" in data["qr_payload"]
        assert "not a legal digital signature" in data["disclaimer"]

    def test_verify_deed_with_16_char_qr_hash_prefix(self, client):
        expected_hash = hash_deed_content("D-V11-1202", "2021-06-15", "PARCEL_CLEAN_R12", "P_V11_CLEAN_H1", "P_V11_CLEAN_H2", "4")
        payload = {
            "deed_no": "D-V11-1202",
            "registration_date": "2021-06-15",
            "parcel_id": "PARCEL_CLEAN_R12",
            "seller": "P_V11_CLEAN_H1",
            "buyer": "P_V11_CLEAN_H2",
            "area": "4",
            "claimed_hash": expected_hash[:16],
            "role": "reviewer",
            "lang": "en",
        }
        resp = client.post("/verify-deed", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status_code"] == "CONSISTENT"
        assert data["matches_registry"] is True

    def test_verify_deed_tamper_detected_contradiction(self, client):
        # Tampered area: 5 instead of recorded 4
        payload = {
            "deed_no": "D-V11-1202",
            "registration_date": "2021-06-15",
            "parcel_id": "PARCEL_CLEAN_R12",
            "seller": "P_V11_CLEAN_H1",
            "buyer": "P_V11_CLEAN_H2",
            "area": "5",
            "role": "reviewer",
            "lang": "en",
        }
        resp = client.post("/verify-deed", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status_code"] == "CONTRADICTION"
        assert data["matches_registry"] is False

    def test_verify_deed_mismatched_claimed_hash_contradiction(self, client):
        payload = {
            "deed_no": "D-V11-1202",
            "registration_date": "2021-06-15",
            "parcel_id": "PARCEL_CLEAN_R12",
            "seller": "P_V11_CLEAN_H1",
            "buyer": "P_V11_CLEAN_H2",
            "area": "4",
            "claimed_hash": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            "role": "reviewer",
            "lang": "en",
        }
        resp = client.post("/verify-deed", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status_code"] == "CONTRADICTION"
        assert data["matches_registry"] is False

    def test_verify_deed_no_claimed_hash_returns_review(self, client):
        # SPEC: "No registry hash on file or no claimed hash -> Review Required"
        payload = {
            "deed_no": "D-V11-1202",
            "registration_date": "2021-06-15",
            "parcel_id": "PARCEL_CLEAN_R12",
            "seller": "P_V11_CLEAN_H1",
            "buyer": "P_V11_CLEAN_H2",
            "area": "4",
            "claimed_hash": None,
            "role": "reviewer",
            "lang": "en",
        }
        resp = client.post("/verify-deed", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status_code"] == "REVIEW"

    def test_verify_deed_unknown_deed_returns_review(self, client):
        payload = {
            "deed_no": "D-UNKNOWN-9999",
            "registration_date": "2021-06-15",
            "parcel_id": "PARCEL_CLEAN_R12",
            "seller": "P_V11_CLEAN_H1",
            "buyer": "P_V11_CLEAN_H2",
            "area": "4",
            "role": "reviewer",
            "lang": "en",
        }
        resp = client.post("/verify-deed", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status_code"] == "REVIEW"
        assert data["recorded_hash"] is None

    def test_verify_deed_role_leak_hygiene_for_citizen(self, client):
        payload = {
            "deed_no": "D-V11-1202",
            "registration_date": "2021-06-15",
            "parcel_id": "PARCEL_CLEAN_R12",
            "seller": "P_V11_CLEAN_H1",
            "buyer": "P_V11_CLEAN_H2",
            "area": "4",
            "role": "citizen",
            "lang": "bn",
        }
        resp = client.post("/verify-deed", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        # Citizen role must NOT receive rule_id
        assert data["rule_id"] is None
        assert "আইনি ডিজিটাল স্বাক্ষর" in data["disclaimer"]

    def test_verify_deed_invalid_inputs_rejected_with_422(self, client):
        # Invalid date format
        resp = client.post("/verify-deed", json={
            "deed_no": "D-101",
            "registration_date": "not-a-date",
            "parcel_id": "P1",
            "seller": "S",
            "buyer": "B",
            "area": "5",
        })
        assert resp.status_code == 422

        # Invalid area
        resp2 = client.post("/verify-deed", json={
            "deed_no": "D-101",
            "registration_date": "2020-01-01",
            "parcel_id": "P1",
            "seller": "S",
            "buyer": "B",
            "area": "-5",
        })
        assert resp2.status_code == 422


# ===========================================================================
# 4. F14 / R13 Deed Number Reuse Detection
# ===========================================================================

class TestRuleR13Reuse:
    """Tests for deed-number reuse detection, clean multi-dag support, and Review Required semantics."""

    def test_r13_single_use_is_consistent(self):
        deed = Deed(id="D1", deed_no="D-UNIQUE-01", registration_date=date(2020, 1, 1))
        event = Event(
            id="E1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2020, 1, 1),
            parcel_id="P1",
            from_person="P_SELLER",
            to_person="P_BUYER",
            area=Fraction(5, 1),
            deed_id="D1",
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        alert = check_r13(deed=deed, trigger_event=event, all_events=[event], all_deeds=[deed])
        assert alert.status == Status.CONSISTENT
        assert alert.rule_id == "R13"
        assert set(alert.evidence_ids) == {"D1", "E1"}

    def test_r13_reused_deed_with_differing_terms_returns_review_required_never_contradiction(self):
        deed1 = Deed(id="D1", deed_no="D-SHARED-01", registration_date=date(2020, 1, 1))
        deed2 = Deed(id="D2", deed_no="D-SHARED-01", registration_date=date(2020, 5, 1))
        event1 = Event(
            id="E1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2020, 1, 1),
            parcel_id="PARCEL_A",
            from_person="P_SELLER_1",
            to_person="P_BUYER_1",
            area=Fraction(5, 1),
            deed_id="D1",
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        event2 = Event(
            id="E2",
            type=EventType.SALE,
            seq=1,
            event_date=date(2020, 5, 1),
            parcel_id="PARCEL_B",
            from_person="P_SELLER_2",
            to_person="P_BUYER_2",
            area=Fraction(8, 1),
            deed_id="D2",
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        all_events = [event1, event2]
        all_deeds = [deed1, deed2]

        alert = check_r13(deed=deed1, trigger_event=event1, all_events=all_events, all_deeds=all_deeds)
        # MUST BE REVIEW REQUIRED, NEVER CONTRADICTION
        assert alert.status == Status.REVIEW
        assert alert.status != Status.CONTRADICTION
        # Evidence must identify all involved events and deeds
        assert "E1" in alert.evidence_ids
        assert "E2" in alert.evidence_ids
        assert "D1" in alert.evidence_ids
        assert "D2" in alert.evidence_ids

    def test_r13_clean_multi_dag_deed_with_identical_terms_is_consistent(self):
        deed = Deed(id="D_MULTI", deed_no="D-MULTI-01", registration_date=date(2020, 1, 1))
        event_dag1 = Event(
            id="E_DAG1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2020, 1, 1),
            parcel_id="PARCEL_101",
            from_person="P_SELLER",
            to_person="P_BUYER",
            area=Fraction(5, 1),
            deed_id="D_MULTI",
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        event_dag2 = Event(
            id="E_DAG2",
            type=EventType.SALE,
            seq=1,
            event_date=date(2020, 1, 1),
            parcel_id="PARCEL_102",
            from_person="P_SELLER",
            to_person="P_BUYER",
            area=Fraction(5, 1),
            deed_id="D_MULTI",
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        all_events = [event_dag1, event_dag2]
        all_deeds = [deed]

        alert = check_r13(deed=deed, trigger_event=event_dag1, all_events=all_events, all_deeds=all_deeds)
        assert alert.status == Status.CONSISTENT
        assert "legitimately covers multiple parcels" in alert.calculation

    def test_r13_missing_deed_returns_review(self):
        event = Event(
            id="E1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2020, 1, 1),
            parcel_id="P1",
            from_person="A",
            to_person="B",
            area=Fraction(5, 1),
            deed_id=None,
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        alert = check_r13(deed=None, trigger_event=event)
        assert alert.status == Status.REVIEW


# ===========================================================================
# 5. F15 / R14 Dummy Identity Numbers & Disambiguation
# ===========================================================================

class TestRuleR14Disambiguation:
    """Tests for dummy identity numbers, name collisions, and disambiguation."""

    def test_r14_distinct_people_with_distinct_names_is_consistent(self):
        sr = SurveyRecord(
            id="SR1",
            parcel_id="P1",
            survey="BS",
            khatian_no="101",
            record_date=date(2010, 1, 1),
            recorded_area=Fraction(10, 1),
            holders=(( "P1", Fraction(10, 1) ),),
        )
        hist = ParcelHistory(
            parcel_id="P1",
            baseline_record_id="SR1",
            baseline_complete=True,
            start_record_id="SR1",
            end_date=date(2020, 1, 1),
            survey_records=(sr,),
            events=(),
        )
        p1 = Person(id="P1", name="Abdul Karim", dummy_id="DUMMY-ID-0001")
        alert = check_r14(hist, all_persons=[p1])
        assert alert.status == Status.CONSISTENT

    def test_r14_same_name_with_distinct_dummy_ids_is_consistent(self):
        """Two people named Abdul Alim, but disambiguated via DUMMY-ID-0001 and DUMMY-ID-0002."""
        sr = SurveyRecord(
            id="SR1",
            parcel_id="P1",
            survey="BS",
            khatian_no="101",
            record_date=date(2010, 1, 1),
            recorded_area=Fraction(10, 1),
            holders=(( "P_ALIM_1", Fraction(10, 1) ),),
        )
        event = Event(
            id="E1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2015, 1, 1),
            parcel_id="P1",
            from_person="P_ALIM_1",
            to_person="P_ALIM_2",
            area=Fraction(5, 1),
            deed_id="D1",
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        hist = ParcelHistory(
            parcel_id="P1",
            baseline_record_id="SR1",
            baseline_complete=True,
            start_record_id="SR1",
            end_date=date(2020, 1, 1),
            survey_records=(sr,),
            events=(event,),
        )
        p1 = Person(id="P_ALIM_1", name="Abdul Alim", dummy_id="DUMMY-ID-0001")
        p2 = Person(id="P_ALIM_2", name="Abdul Alim", dummy_id="DUMMY-ID-0002")

        alert = check_r14(hist, all_persons=[p1, p2])
        assert alert.status == Status.CONSISTENT
        assert "disambiguated with dummy identity numbers" in alert.calculation

    def test_r14_same_name_missing_dummy_id_returns_review_required(self):
        """Two distinct Person entities with identical name where at least one lacks dummy_id."""
        sr = SurveyRecord(
            id="SR1",
            parcel_id="P1",
            survey="BS",
            khatian_no="101",
            record_date=date(2010, 1, 1),
            recorded_area=Fraction(10, 1),
            holders=(( "P_ALIM_1", Fraction(10, 1) ),),
        )
        event = Event(
            id="E1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2015, 1, 1),
            parcel_id="P1",
            from_person="P_ALIM_1",
            to_person="P_ALIM_2",
            area=Fraction(5, 1),
            deed_id="D1",
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        hist = ParcelHistory(
            parcel_id="P1",
            baseline_record_id="SR1",
            baseline_complete=True,
            start_record_id="SR1",
            end_date=date(2020, 1, 1),
            survey_records=(sr,),
            events=(event,),
        )
        p1 = Person(id="P_ALIM_1", name="Abdul Alim", dummy_id=None)
        p2 = Person(id="P_ALIM_2", name="Abdul Alim", dummy_id=None)

        alert = check_r14(hist, all_persons=[p1, p2])
        assert alert.status == Status.REVIEW
        assert "without disambiguating dummy identity numbers" in alert.calculation
        assert "P_ALIM_1" in alert.evidence_ids
        assert "P_ALIM_2" in alert.evidence_ids

    def test_r14_same_dummy_id_different_spelling_returns_review_required(self):
        """Same dummy_id associated with multiple spelling variations of a name."""
        sr = SurveyRecord(
            id="SR1",
            parcel_id="P1",
            survey="BS",
            khatian_no="101",
            record_date=date(2010, 1, 1),
            recorded_area=Fraction(10, 1),
            holders=(( "P1", Fraction(10, 1) ),),
        )
        event = Event(
            id="E1",
            type=EventType.SALE,
            seq=1,
            event_date=date(2015, 1, 1),
            parcel_id="P1",
            from_person="P1",
            to_person="P2",
            area=Fraction(5, 1),
            deed_id="D1",
            portion_id=None,
            linked_event_id=None,
            source_record_id=None,
        )
        hist = ParcelHistory(
            parcel_id="P1",
            baseline_record_id="SR1",
            baseline_complete=True,
            start_record_id="SR1",
            end_date=date(2020, 1, 1),
            survey_records=(sr,),
            events=(event,),
        )
        p1 = Person(id="P1", name="Md. Tariqul Islam", dummy_id="DUMMY-ID-0099")
        p2 = Person(id="P2", name="Tariqul Islam", dummy_id="DUMMY-ID-0099")

        alert = check_r14(hist, all_persons=[p1, p2])
        assert alert.status == Status.REVIEW
        assert "multiple name spellings" in alert.calculation


# ===========================================================================
# 6. Disambiguation in Search and Lineage Graph
# ===========================================================================

class TestSearchAndGraphDisambiguation:
    """Verifies that search and graph presentation distinguish persons with dummy_ids."""

    @pytest.fixture
    def client(self):
        ds = load_dataset(DEMO_V11_PATH)
        app = create_app(dataset=ds)
        return TestClient(app)

    def test_search_disambiguates_holders_by_dummy_id_without_merging(self, client):
        # Search for "Abdul Alim" in demo_v11
        resp = client.get("/search?q=Abdul Alim&lang=en")
        assert resp.status_code == 200
        results = resp.json()

        # Must return entries with dummy_id attached to distinct items
        alim_items = [r for r in results if r.get("holder_name") == "Abdul Alim"]
        assert len(alim_items) >= 2
        # Verify dummy IDs are present in SearchResultItem
        dummy_ids = {item["dummy_id"] for item in alim_items}
        assert "DUMMY-ID-0001" in dummy_ids
        assert "DUMMY-ID-0002" in dummy_ids

        # Labels must show the dummy_id to the user
        for item in alim_items:
            if item["dummy_id"]:
                assert f"[{item['dummy_id']}]" in item["label"]

    def test_graph_node_includes_dummy_id(self, client):
        resp = client.get("/parcel/PARCEL_CLEAN_R14_DISAMBIG?lang=en&role=reviewer")
        assert resp.status_code == 200
        data = resp.json()
        graph_nodes = data["graph"]["nodes"]

        # Find nodes for the two Alims
        alim_nodes = [n for n in graph_nodes if "Abdul Alim" in n["data"]["label"]]
        assert len(alim_nodes) >= 2
        for n in alim_nodes:
            assert "dummy_id" in n["data"]
            assert n["data"]["dummy_id"] in ("DUMMY-ID-0001", "DUMMY-ID-0002")


# ===========================================================================
# 7. Offline Contract and Client-Side QR Vendoring
# ===========================================================================

class TestOfflineContractAndQR:
    """Verifies no external network dependencies and vendor files integrity."""

    def test_vendor_qrcode_js_exists_and_offline(self):
        qr_file = PROJECT_ROOT / "src" / "jomigraph" / "ui" / "vendor" / "qrcode.js"
        assert qr_file.is_file()
        content = qr_file.read_text(encoding="utf-8")
        assert "MIT license" in content or "Kazuhiko Arase" in content
        # Ensure no runtime network calls
        assert "fetch(" not in content
        assert "XMLHttpRequest" not in content
        assert "WebSocket" not in content

    def test_index_html_includes_vendor_qrcode(self):
        index_file = PROJECT_ROOT / "src" / "jomigraph" / "ui" / "index.html"
        content = index_file.read_text(encoding="utf-8")
        assert 'src="/vendor/qrcode.js"' in content or 'src="vendor/qrcode.js"' in content

    def test_verify_deed_screen_elements_in_ui(self):
        extras_file = PROJECT_ROOT / "src" / "jomigraph" / "ui" / "extras.js"
        content = extras_file.read_text(encoding="utf-8")
        assert "verify-deed-form" in content
        assert "vd-deed-no" in content
        assert "vd-reg-date" in content
        assert "vd-parcel-id" in content
        assert "vd-area" in content
        assert "vd-seller" in content
        assert "vd-buyer" in content
        assert "vd-claimed-hash" in content
        assert "verify-result-container" in content
        assert "qrcode" in content
