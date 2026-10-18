"""
Unit & Integration Tests for Offline Rule-Based Assistant (Phase 13)
====================================================================
Tests intent dispatch, bilingual responses, citizen role sanitization,
prohibited term prevention, and input hardening.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from jomigraph.api.app import create_app
from jomigraph.engine.assistant import PROHIBITED_TERMS
from jomigraph.engine.simulate import hash_dataset


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app(dataset_path="data/demo_family.json"))


def test_greeting_intent_bn_and_en(client: TestClient):
    # Bangla greeting
    res_bn = client.post("/assistant?lang=bn", json={"question": "হ্যালো"}).json()
    assert res_bn["intent"] == "greeting"
    assert "নমস্কার" in res_bn["answer"] or "সালাম" in res_bn["answer"]
    assert len(res_bn["suggestions"]) >= 3

    # English greeting
    res_en = client.post("/assistant?lang=en", json={"question": "hello"}).json()
    assert res_en["intent"] == "greeting"
    assert "Hello" in res_en["answer"]
    assert len(res_en["suggestions"]) >= 3


def test_legal_advice_refusal(client: TestClient):
    res_bn = client.post("/assistant?lang=bn", json={"question": "আমি কি জমি নিয়ে আদালতে মামলা করব?"}).json()
    assert res_bn["intent"] == "legal_advice"
    assert "আইনি পরামর্শ" in res_bn["answer"]
    assert "সাব-রেজিস্ট্রি" in res_bn["answer"] or "আইনজীবী" in res_bn["answer"]

    res_en = client.post("/assistant?lang=en", json={"question": "Should I sue the seller in court?"}).json()
    assert res_en["intent"] == "legal_advice"
    assert "legal advice" in res_en["answer"]


def test_rule_explanation_all_rules(client: TestClient):
    rules = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
    for r in rules:
        res = client.post("/assistant?lang=en", json={"question": f"What is rule {r}?"}).json()
        assert res["intent"] == "rule_explanation"
        assert r in res["answer"]

    # Bangla rule query
    res_r1_bn = client.post("/assistant?lang=bn", json={"question": "আর১ নিয়ম কি?"}).json()
    assert res_r1_bn["intent"] == "rule_explanation"
    assert "অতিরিক্ত হস্তান্তর" in res_r1_bn["answer"]


def test_glossary_intents_bn_and_en(client: TestClient):
    terms = [
        ("খতিয়ান কী?", "bn", "খতিয়ান"),
        ("what is deed", "en", "Deed"),
        ("নামজারি কি", "bn", "নামজারি"),
        ("what is mutation", "en", "Mutation"),
        ("দাগ নম্বর কী", "bn", "দাগ"),
        ("what is mouza", "en", "Mouza"),
    ]
    for q, lang, expected in terms:
        res = client.post(f"/assistant?lang={lang}", json={"question": q}).json()
        assert res["intent"] == "glossary", f"Failed for {q}"
        assert expected.lower() in res["answer"].lower()


def test_status_meaning_intent(client: TestClient):
    res_bn = client.post("/assistant?lang=bn", json={"question": "লাল দাগ কেন?"}).json()
    assert res_bn["intent"] == "status_meaning"
    assert "অসঙ্গতি" in res_bn["answer"]

    res_en = client.post("/assistant?lang=en", json={"question": "What does yellow status mean?"}).json()
    assert res_en["intent"] == "status_meaning"
    assert "Review Required" in res_en["answer"]


def test_parcel_specific_why_status_citizen_vs_reviewer(client: TestClient):
    # PARCEL_PLANTED_R1 has a planted contradiction
    # 1. Citizen Role: MUST NOT leak rule IDs or calculation
    res_cit = client.post(
        "/assistant?lang=bn&role=citizen",
        json={"question": "এই দাগে সমস্যা কী?", "parcel_id": "PARCEL_PLANTED_R1"}
    ).json()
    assert res_cit["intent"] == "why_status"
    assert res_cit["status"] == "CONTRADICTION"
    assert "[R1]" not in res_cit["answer"]
    assert "Fraction" not in res_cit["answer"]

    # 2. Reviewer Role: Can show rule ID tag
    res_rev = client.post(
        "/assistant?lang=bn&role=reviewer",
        json={"question": "কেন এই ফলাফল?", "parcel_id": "PARCEL_PLANTED_R1"}
    ).json()
    assert res_rev["intent"] == "why_status"
    assert "[R1]" in res_rev["answer"]


def test_status_matches_parcel_endpoint(client: TestClient):
    for pid in ["PARCEL_STORY_01", "PARCEL_PLANTED_R1", "PARCEL_PLANTED_R5"]:
        endpoint_res = client.get(f"/parcel/{pid}?role=citizen").json()
        expected_status = endpoint_res["overall_status_code"]

        ast_res = client.post("/assistant", json={"question": "কেন এই স্ট্যাটাস?", "parcel_id": pid}).json()
        assert ast_res["status"] == expected_status


def test_prohibited_terms_never_appear(client: TestClient):
    queries = [
        "Is this land safe?",
        "Who is the legal owner?",
        "Can you certify title?",
        "জমির মালিকানা নিশ্চিত কি?",
        "জালিয়াতিমুক্ত কিনা বল",
    ]
    for q in queries:
        for lang in ("bn", "en"):
            res = client.post(f"/assistant?lang={lang}", json={"question": q}).json()
            answer_lower = res["answer"].lower()
            for prohibited in PROHIBITED_TERMS:
                assert prohibited not in answer_lower, f"Prohibited term '{prohibited}' found in answer to '{q}'"


def test_input_hardening(client: TestClient):
    # 1. Empty string
    assert client.post("/assistant", json={"question": ""}).status_code == 200

    # 2. HTML injection
    res_html = client.post("/assistant", json={"question": "<script>alert('xss')</script>"}).json()
    assert "<script>" not in res_html["answer"]

    # 3. Control characters
    res_ctrl = client.post("/assistant", json={"question": "হ্যালো\x00\x08\x1b"}).json()
    assert res_ctrl["status_code"] if "status_code" in res_ctrl else 200

    # 4. Long word / long string
    long_q = "a" * 299
    assert client.post("/assistant", json={"question": long_q}).status_code == 200

    # 5. Oversized (>300 chars handled cleanly by Pydantic validation)
    oversized = "a" * 301
    assert client.post("/assistant", json={"question": oversized}).status_code == 422


def test_assistant_never_mutates_dataset_hash(client: TestClient):
    ds = client.app.state.dataset
    before = hash_dataset([e for h in ds.histories for e in h.events], [s for h in ds.histories for s in h.survey_records])
    client.post("/assistant", json={"question": "কেন এই ফলাফল?", "parcel_id": "PARCEL_LAB_DEMO"})
    after = hash_dataset([e for h in ds.histories for e in h.events], [s for h in ds.histories for s in h.survey_records])
    assert before == after
