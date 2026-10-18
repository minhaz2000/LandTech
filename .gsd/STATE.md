# STATE.md: JomiGraph AI

> **Last Updated**: 2026-10-17
> **Milestone**: v1.1 Phase 12 (Final Benchmark, Validation & Documentation)
> **Overall Status**: Phase 12 complete. All 12 phases delivered. 392 Python tests passing, 8 Node.js badge tests passing.

## Current Position
- **Phases 1 to 5 (v1.0)**: Complete.
- **Phase 6 (Foundation)**: Complete.
- **Part 2.5 (All-Upazila Demo Coverage)**: Complete (479 synthetic upazilas + 16 core showcase dags).
- **Phase 7 (Deed Integrity & Identification)**: Complete.
  - F13 / R12: Canonical deed hashing (SHA-256), POST /verify-deed, tamper detection, client-side QR generation, Verify Deed UI screen.
  - F14 / R13: Deed-number reuse detection with Review Required semantics, supporting clean multi-dag deeds.
  - F15 / R14: Dummy identity numbers (`DUMMY-ID-0001`), name disambiguation in search and lineage graph.
- **Phase 8 (Boundary Disambiguation & Share Representation)**: Complete.
  - F16 / R15: Structured boundary duplicate sale detection (identifying identical physical portions under differing portion labels), sub-dag lineage containment (`101/1` vs `101/1-ka`), partial/missing boundary review semantics, non-cancelled transfer filtering.
  - Simulation Lab: Added North, South, East, West descriptor and sub-dag input fields; evaluates proposed transfers pre-registration; frontend contract tests verified.
  - X1 Traditional Land Share: Exact Fraction decomposition (16 ana = 1 whole, 20 ganda, 4 kora, 3 kranti, 20 til = 76,800 til per whole), bilingual display with exact fraction alongside, co-owner quotas breakdown and legal disclaimers.
  - Five-Co-Owner Ejmali Dag: R1 individual quota enforcement verified, ensuring sales exceeding co-owner's own share fail even when sale is less than aggregate dag area.
- **Phase 9 (Encumbrances, POA & Government/Court Locks)**: Complete.
  - Task A (R11 / F17): Government and Court Locks (`is_khas`, `under_acquisition`, `flag_date`, `court_case_no`, `case_status`, `injunction`). Transfers dated after khas/acquisition flag trigger Contradiction Found; pending cases, injunctions, or missing dates trigger Review Required; pre-flag transactions remain Consistent.
  - Task B (R9): Active Mortgage Encumbrance & Release Validation. `MORTGAGE` and `MORTGAGE_RELEASE` replay as non-transferring encumbrances; sale during active unreleased mortgage or second mortgage triggers Contradiction Found; missing release dates or repeated releases trigger Review Required.
  - Task C (R10): Power of Attorney Authority & Revocation. `POA_GRANT` and `POA_REVOKE` replay as non-transferring authority events; sales via revoked POA or unrecorded grant trigger Contradiction Found; tricky clean case verified where sale executed prior to subsequent revocation is Consistent.
  - Integration: Cytoscape purple `#6b21a8` locked parcel styling, locked warning banner, simulation lab blocked warning and `via_poa_id` field.
- **Phase 10 (R8 — Unaccounted Heir Declaration Consistency)**: Complete.
  - Pure documentary consistency check comparing recorded `ParcelHistory.heir_declaration` against subsequent survey records and deeds.
  - Does NOT calculate religious inheritance shares under Farayez or statutory inheritance law; does not evaluate legal authenticity of certificates; does not infer heirs from names.
  - Checks for registered deeds executed by omitted heirs documenting sale, gift, or release/না-দাবি (`EventType.RELEASE`).
  - Contradiction Found strictly when declaration and baseline are complete, all dates present, documentary chain is explicit, and no recorded deed accounts for omitted heir.
  - Review Required when declaration flag is incomplete, baseline is incomplete, or dates/records are missing/ambiguous.
  - Consistent with supplied records when all heirs are recorded, or omitted heir transferred/released their interest by recorded deed (tricky clean case), or no declaration is present.
- **Phase 11 (Decision Support & User Experience)**: Complete.
  - F18 Deterministic Attention Score: 0–100 integer score from configured rule weights in `config.py` and fired alerts. Completely clean parcels score strictly 0 with green traffic light. Score never overrides or alters headline three-status evaluation result. Citizen interface shows score, traffic light indicator, and plain-language sentence only; Reviewer interface shows score, traffic light indicator, and contributing factors breakdown. Forbidden words eliminated.
  - X2 Offline Bangla Voice: "ফলাফল শুনুন" control using browser `speechSynthesis`. Prioritizes `bn-BD`, then `bn-IN`. Gracefully falls back to readable on-screen text when speech API or voices are unavailable. Repeated clicks cleanly cancel prior speech. Zero network/cloud speech dependencies. Accessible labels provided.
  - X3 Rule-Specific Next-Step Guide: Actionable documentary checks for all covered rules (R1 through R15 + HYGIENE) in English and Bengali. Law mentor review disclaimer included. Graceful fallback on unknown rules.
  - X4 USSD / Feature-Phone Simulator: Explicitly simulated text-only interaction via invented demo code `*123*45#`. Disclosed as demonstration simulator. Phone-frame UI with interactive keypad and flow: language selection -> mouza -> dag -> result. Strict <= 160 characters limit enforced. Backed by `/ussd` API endpoint.
  - X5 Digital Vetting Certificate: Printable advisory report via browser print dialog. Structured certificate layout with parcel summary, unaltered three-status result, attention score & explanation, relevant record hash (`report.dataset_hash`), offline client-side QR code SVG using vendored `qrcode.js` linking to `#/verify-deed`, standard non-judicial disclaimer. `@media print` CSS cleanly excludes navigation, headers, buttons, and forms.
- **Phase 12 (Final Benchmark, Validation & Documentation)**: Complete.
  - Extended Benchmark: Additive `extended` response block on `GET /benchmark` covering R8–R15 detection (100% detection rate, 8/8 planted rules detected), Phase 10 validation, Phase 11 feature verification, simulation purity, and backward compatibility. Baseline dataset false alarm rate remains strictly 0% (0/21 clean false alarms).
  - README.md: Fully updated with LandTech 2026 problem P3 context, full R1–R15 rules catalogue, Phase 11 features, architecture file map, setup/run/benchmark instructions, actual executed benchmark metrics, third-party asset licenses table (MIT qrcode.js, three.min.js, OrbitControls.js), while preserving authors' own-words placeholders verbatim.
  - `docs/NEW_FEATURES_EXPLAINED.md`: Plain-language walkthrough of v1.1 features + 15 technically accurate judge questions and answers for student presenters.
  - `docs/demo_script_v11.md`: Exact 90-second video demo walkthrough script with realistic timings, two student roles, clean parcel, planted contradiction, evidence breakdown, Phase 11 feature showcase, and advisory disclaimer.
  - Deployment Readiness: Static validation of `Dockerfile`, `render.yaml` (`healthCheckPath: /ui-strings`), `.dockerignore`, and dependency manifests. Docker CLI absence noted.
  - Full Regression & Invariants: 392 Python tests passing, 8 Node.js badge tests passing, 100% locales parity, 100% UI strings parity, zero forbidden words across all copy, baseline hash strictly invariant (`b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01`).
- **Tests**: 392 passing pytest tests (11 new Phase 12 tests) + 8 node badge tests.
- **Benchmark**: 0 false alarms on clean parcels (0.0%), planted problems detected (100.0% on baseline R1–R7; 100.0% on extended R8–R15).
- **Dataset hash**: `b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01` (strictly invariant).
- **Zero Forbidden Words**: Verified 100% clean across all locales, strings, UI text, and documentation.


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
