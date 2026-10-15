# STATE.md: JomiGraph AI

> **Last Updated**: 2026-10-16
> **Milestone**: v1.0 (LandTech 2026 hackathon, Round 1)
> **Overall Status**: Build complete. Submission items open.

## Current Position
- **Phases 1 to 5**: complete (engine, simulation and data, API, interface, documentation).
- **Tests**: 211 passing (engine, API, dataset, input hardening, UI/API contract).
- **Benchmark**: 0 alerts on the 21 clean parcels, 7 of 7 planted problems detected.
- **Dataset hash**: unchanged before and after simulation (see README).

## Pre-submission fixes (2026-10-16)
- Area input: zero, negative and malformed values are rejected with a specific message. Decimal strings such as 2.5 are accepted and parsed exactly into fractions.
- Lab screen: reads the fields the API actually sends. The date field is sent as `date`.
- Roles: `/simulate` and `/parcels` take a `role` parameter. The citizen response carries no rule IDs, calculations, evidence IDs or staging fields.
- `DEFAULT_DATASET_PATH` is anchored to the repo, so the server starts from any folder.
- Benchmark field renamed to `planted_case_count` (7 rules). The 9 parcels are reported as `planted_parcel_count` in the engine report only.
- Google Fonts links removed. The Bangla font is bundled locally.
- `.gitattributes` added to stop CRLF/LF noise.

## Open items before Round 1 closes (18 October 2026)
1. Concept note (PDF, 3 pages maximum).
2. Demo video (90 seconds maximum).
3. README: scope-of-assistance paragraph and understanding statement, in the authors' own words.
4. Public GitHub repository and the real `<REPO_URL>`.
5. Confirm the licence.
6. Manual checks on a real phone: layout, Bangla print preview, offline reload.

## What We Are Building
A rule-based land-record consistency checker for a Bangladesh hackathon.
Synthetic data only. Pure-function engine, FastAPI backend, bilingual HTML/JS frontend.

## Key Decisions
- Python 3.11, fractions.Fraction. No floats anywhere in the rules.
- Exactly three statuses: Consistent with supplied records / Contradiction Found / Review Required.
- Missing inputs lead to Review Required first. baseline_complete is applied second.
- Minimal evidence: all alternative minimal sets are returned.
- simulate() is a pure function. The dataset hash is checked before and after.
- Roles are demo views, not authentication.

## Blocking Issues
None.

## Environment
- OS: Windows (PowerShell). Also verified on Linux.
- Language: Python 3.11 or newer
- Backend: FastAPI
- Frontend: HTML/CSS/JS with Cytoscape.js (bundled, CDN fallback)
- Tests: pytest
