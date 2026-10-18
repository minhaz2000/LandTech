"""
Unit & Integration Tests for 3D Map Enhancements and Accessible Transitions (Phases 14, 15)
============================================================================================
Tests static asset integrity, offline zero-network compliance, reduced-motion rules,
bilingual disclaimers, lineage configuration, and 3D transition contracts.
"""

from __future__ import annotations

import re
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from jomigraph.api.app import create_app

UI_DIR = Path(__file__).resolve().parents[1] / "src" / "jomigraph" / "ui"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app(dataset_path="data/demo_family.json"))


def test_no_external_urls_in_new_ui_assets():
    """Verify that all newly created CSS/JS files make ZERO external network/CDN calls."""
    new_files = ["motion.css", "assistant.css", "transitions3d.css", "motion.js", "assistant.js", "transitions3d.js", "extras.js"]
    for fname in new_files:
        fpath = UI_DIR / fname
        assert fpath.is_file(), f"File {fname} must exist"
        content = fpath.read_text(encoding="utf-8")
        assert "http://" not in content, f"External http link found in {fname}"
        assert "https://" not in content, f"External https link found in {fname}"
        assert "googleapis" not in content, f"Google API reference found in {fname}"


def test_bilingual_map_disclaimer_present():
    """Verify that the synthetic fictional cadastral disclaimer exists in both BN and EN in extras.js."""
    extras_code = (UI_DIR / "extras.js").read_text(encoding="utf-8")
    assert "কাল্পনিক ডেমো মৌজা নকশা — বাস্তব ভৌগোলিক সীমানা নয়" in extras_code
    assert "Fictional demo cadastral layout — Not real geographic boundaries" in extras_code


def test_prefers_reduced_motion_in_motion_and_transitions():
    """Verify that @media (prefers-reduced-motion: reduce) is implemented across stylesheets."""
    motion_css = (UI_DIR / "motion.css").read_text(encoding="utf-8")
    transitions_css = (UI_DIR / "transitions3d.css").read_text(encoding="utf-8")

    assert "prefers-reduced-motion: reduce" in motion_css
    assert "prefers-reduced-motion: reduce" in transitions_css
    assert "reduce-motion" in motion_css
    assert "reduce-motion" in transitions_css


def test_go3d_interface_and_safe_fallback():
    """Verify go3d function signature, fallback handling, and deadlock guard in transitions3d.js."""
    trans_js = (UI_DIR / "transitions3d.js").read_text(encoding="utf-8")
    assert "window.go3d = function" in trans_js
    assert "isReducedMotion" in trans_js
    assert "setTimeout(cleanup" in trans_js or "timer" in trans_js, "Must have safety timeout"
    assert "focusHeading" in trans_js, "Must transfer keyboard focus"


def test_lineage_group_and_subdivision_curves_in_extras():
    """Verify that lineage curves connect parent PARCEL_PLANTED_R4 to its children R4_A and R4_B."""
    extras_js = (UI_DIR / "extras.js").read_text(encoding="utf-8")
    assert "PARCEL_PLANTED_R4" in extras_js
    assert "PARCEL_PLANTED_R4_A" in extras_js
    assert "PARCEL_PLANTED_R4_B" in extras_js
    assert "QuadraticBezierCurve3" in extras_js
    assert "TubeGeometry" in extras_js or "Line" in extras_js


def test_procedural_canvas_textures_and_tone_mapping_in_extras():
    """Verify procedural canvas textures and ACESFilmic tone mapping are used without remote textures."""
    extras_js = (UI_DIR / "extras.js").read_text(encoding="utf-8")
    assert "CanvasTexture" in extras_js
    assert "ACESFilmicToneMapping" in extras_js
    assert "stopMap = () =>" in extras_js
    assert "ctl.dispose()" in extras_js
    assert "ren.dispose()" in extras_js


def test_skip_link_and_live_region_in_index():
    """Verify accessibility landmarks: skip-link and aria live status in index.html."""
    html = (UI_DIR / "index.html").read_text(encoding="utf-8")
    assert 'id="skip-link"' in html
    assert 'id="a11y-status"' in html
    assert 'role="status"' in html
    assert 'aria-live="polite"' in html
    assert 'id="motion-toggle-btn"' in html
