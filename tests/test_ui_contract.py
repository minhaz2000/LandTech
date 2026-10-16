"""
Static checks that keep the UI and the API in step.

These would have caught three real bugs: the lab reading response fields the
API never sent, the lab sending `event_date` while the API reads `date`, and a
Google Fonts request left in the page after the font was bundled locally.
"""

from __future__ import annotations

import re
from pathlib import Path

from jomigraph.api.schemas import CitizenSimulateResponse, SimulateRequest, SimulateResponse

UI = Path(__file__).resolve().parents[1] / "src" / "jomigraph" / "ui"


def read(name: str) -> str:
    return (UI / name).read_text(encoding="utf-8")


def test_index_makes_no_external_font_requests():
    html = read("index.html")
    assert "fonts.googleapis.com" not in html
    assert "fonts.gstatic.com" not in html


def test_index_cdn_fallback_script_tag_is_closed_correctly():
    html = read("index.html")
    assert "<\\/script>" in html
    assert "<\\\\/script>" not in html


def test_lab_reads_only_fields_the_api_sends():
    js = read("app.js")
    used = set(re.findall(r"\bsimRes\.([A-Za-z0-9_]+)", js))
    sent = set(SimulateResponse.model_fields) | set(CitizenSimulateResponse.model_fields)
    assert used, "expected the lab handler to read simRes fields"
    assert used <= sent, f"UI reads fields the API does not send: {sorted(used - sent)}"


def test_lab_citizen_fields_exist_in_citizen_response():
    js = read("app.js")
    # Fields used inside the citizen branch must exist on the citizen response.
    start = js.index("if (isCitizen) {", js.index("function attachLabFormHandler"))
    end = js.index("} else {", start)
    used = set(re.findall(r"\bsimRes\.([A-Za-z0-9_]+)", js[start:end]))
    assert used <= set(CitizenSimulateResponse.model_fields), sorted(used)


def test_lab_payload_keys_match_the_request_model():
    js = read("app.js")
    block = js[js.index("const payload = {", js.index("function attachLabFormHandler")):]
    block = block[: block.index("};")]
    keys = set(re.findall(r"^\s*([a-z_]+):", block, re.M))
    assert keys <= set(SimulateRequest.model_fields), sorted(keys - set(SimulateRequest.model_fields))
    assert "date" in keys and "event_date" not in keys


def test_lab_requests_the_active_role():
    js = read("app.js")
    assert "/simulate?lang=${currentLang}&role=${role}" in js
    assert "/parcels?lang=${currentLang}&role=" in js


def test_every_ui_string_key_used_in_lab_exists():
    import json
    strings = json.loads(read("strings.json"))
    for key in ("error_area_not_positive", "error_area_format", "error_area_too_large",
                "error_server_unreachable", "lab_area_placeholder", "error_empty_fields"):
        for locale in ("bn", "en"):
            assert strings[locale].get(key), (locale, key)


def test_graph_code_unwraps_the_cytoscape_data_wrapper():
    """The API sends {data: {...}} elements; reading n.id directly gave dots with no labels or edges."""
    js = read("app.js")
    start = js.index("function initializeCytoscape")
    body = js[start:]
    assert "n.data || n" in body and "e.data || e" in body
