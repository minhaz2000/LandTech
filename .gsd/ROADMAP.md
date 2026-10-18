# ROADMAP.md — JomiGraph AI

> **Current Phase**: Complete. Submission items remain (see STATE.md and TODO.md).
> **Milestone**: v1.0 (Hackathon Demo)

## Must-Haves

- [x] Pure-function evaluation engine with rules R1–R7
- [x] fractions.Fraction arithmetic throughout (no floats)
- [x] Three statuses only: Consistent / Contradiction Found / Review Required
- [x] Minimal evidence sets (all alternatives)
- [x] Pure simulate() that never mutates the baseline
- [x] Synthetic dataset with planted + clean cases
- [x] FastAPI backend (parcel, alerts, simulate endpoints)
- [x] Bilingual UI (Bangla default, English toggle)
- [x] pytest suite passing (211 tests)
- [x] Zero Contradiction alerts on clean synthetic cases
- [x] README with benchmark and demo walkthrough (separate benchmark.md and demo_script.md are optional)

---

## Phase 1: Core Engine
**Status**: Complete
**Objective**: Data models, event replay, rules R1–R7, minimal evidence algorithm. Tests 1–11 and 14.

### Tasks
- [x] Define dataclasses: Person, Parcel, SurveyRecord, Deed, Event, ParcelHistory
- [x] Implement chronological event replay (state computer)
- [x] Implement R1 — Excess transfer
- [x] Implement R2 — Duplicate allocation (portion_id + lineage only)
- [x] Implement R3 — Seller's recorded interest
- [x] Implement R4 — Subdivision reconciliation (Fraction, tolerance param)
- [x] Implement R5 — Survey continuity (Review Required only)
- [x] Implement R6 — Deed-mutation reconciliation (Review Required only)
- [x] Implement R7 — Chronological consistency
- [x] Minimal evidence algorithm (all alternative minimal sets)
- [x] recommended_next_step field in every alert (EN + BN keys)
- [x] Impact view: downstream events per conflicting event
- [x] pytest tests 1–11 and 14
- [x] Run tests, show results, stop

**Deliverable**: All engine logic tested; no UI, no API, no data generator yet.

---

## Phase 2: Simulation and Data
**Status**: Complete
**Objective**: evaluate() pure function, counterfactual simulate(), synthetic data generator, tests 12, 13, 15.

### Tasks
- [x] evaluate(events, parcel_history) → (state, alerts) pure function
- [x] simulate(baseline, proposed_event) → (state, alerts) never-mutating wrapper
- [x] Canonical serialization + hash for simulation integrity
- [x] Synthetic data generator (fixed seed, 8–10 parcels, 4 generations)
  - Planted: over-transfer, duplicate portion, survey gap, mutation-before-deed
  - ~20 clean cases (zero expected Contradiction)
  - One case with two alternative minimal evidence sets
- [x] pytest tests 12, 13, 15
- [x] Run tests, show results, stop

**Deliverable**: Full engine + synthetic dataset verified.

---

## Phase 3: API
**Status**: Complete
**Objective**: FastAPI endpoints for parcel, alerts, simulate, search, report.

### Tasks
- [x] GET /parcels/{parcel_id} — parcel + history
- [x] GET /parcels/{parcel_id}/alerts — all alerts with evidence + impact
- [x] POST /simulate — evaluate proposed event, return (state, alerts)
- [x] GET /search?q=... — search by parcel ID, holder name, khatian no, deed no
- [x] GET /report/{parcel_id}?lang=bn|en — printable case summary
- [x] Pydantic response schemas
- [x] pytest smoke tests for API
- [x] Run tests, show results, stop

**Deliverable**: Backend API fully operational.

---

## Phase 4: Interface
**Status**: Complete
**Objective**: Bilingual HTML/CSS/JS frontend — Citizen view, Reviewer view, graph, timeline, simulation form.

### Tasks
- [x] Two JSON translation files (bn.json, en.json) — all user-facing strings
- [x] Language toggle (Bangla ↔ English), Noto Sans Bengali font
- [x] Fictional-data banner on every screen
- [x] Citizen view: plain-language result, recommended_next_step, three starting actions
- [x] Reviewer view: rule ID, dates, exact arithmetic, source IDs, downstream impact, evidence graph
- [x] Cytoscape.js evidence graph (bundled, CDN fallback)
- [x] Timeline of events
- [x] Simulation form: proposed sale input → live result
- [x] Search bar (parcel ID / holder / khatian / deed)
- [x] Printable report page (Bangla or English)
- [x] Mobile-friendly, large tap targets, status as text + icon (never color alone)
- [x] End-to-end demo case in both languages
- [x] Run tests, show results, stop

**Deliverable**: Full working UI, demo ready.

---

## Phase 5: Documentation
**Status**: Complete
**Objective**: README, benchmark.md, demo script — all honest, all complete.

### Tasks
- [x] README.md: setup, modeling assumptions, limits, AI-tool disclosure
- [ ] docs/benchmark.md (optional, README covers it)
- [ ] docs/demo_script.md (optional, README covers the walkthrough)
- [x] Final check: all 15 tests pass, zero clean-case Contradictions, hashes match
- [x] Run tests, show results, stop

**Deliverable**: Project fully documented and presentation-ready.

---

## Verified Prior v1.1 Work (Recovery Audit)
- [x] Offline rule-based bilingual assistant (`POST /assistant`, `assistant.py`, `assistant.js`, `assistant.css`, 10 tests)
- [x] Procedural 3D Mouza Cadastral Map & 3D lineage spline curves (`extras.js`, `theme.css`, Three.js r147)
- [x] Accessible 3D transitions & camera fly-to (`transitions3d.js`, `transitions3d.css`, 7 tests)
- [x] Motion & Accessibility foundation (`motion.js`, `motion.css`, `:focus-visible`, skip link, ARIA live region)
- [x] Regional administrative navigation & Check My Land form (`extras.py`, `myland.js`, `bd_geo.json`, 7 tests)
- [x] Dockerfile and render.yaml deployment configuration

---

## Phase 6: Core Foundation (v1.1)
**Status**: Complete
**Objective**: Shared rule dispatcher, extended data models & loader, config weights, v1.1 demo dataset foundation.

### Tasks
- [x] SPEC.md and ROADMAP.md planning lock update
- [x] Refactor evaluate() and evaluate_history() to single shared rule dispatcher in engine/rules.py
- [x] Extend data models in models.py (Deed.content_hash, Person.dummy_id, Event.portion/boundary/via_poa_id, Parcel lock fields, new EventTypes, ParcelHistory.heir_declaration)
- [x] Extend dataset loader in loader.py and non-transferring replay in replay.py
- [x] Add Attention Score weights table in config.py
- [x] Implement data/generator_v11.py and generate data/demo_v11.json
- [x] Verify baseline hash unchanged and run regression tests

**Deliverable**: Zero regressions on v1.0 suite, shared dispatcher operational, data foundation ready.

---

## Phase 7: Deed Integrity & Identification (v1.1)
**Status**: Complete
**Objective**: F13 (R12 deed content hash + POST /verify-deed + QR + verify screen), F14 (R13 deed number reuse), F15 (R14 dummy ID disambiguation).

### Tasks
- [x] F13 / R12: Canonical deed hashing (SHA-256), POST /verify-deed, tamper detection, client-side QR generation, Verify Deed UI screen
- [x] F14 / R13: Deed-number reuse detection with Review Required semantics, supporting clean multi-dag deeds
- [x] F15 / R14: Dummy identity numbers (`DUMMY-ID-0001`), name disambiguation in search and lineage graph

---

## Phase 8: Boundary Disambiguation & Share Representation (v1.1)
**Status**: Complete
**Objective**: F16 (R15 structured boundary / portion sold twice), simulation-lab boundary fields, X1 (traditional ana-ganda-kora-kranti-til display helper and Ejmali dag tests).

---

## Phase 9: Encumbrances, POA & Lockouts (v1.1)
**Status**: Complete
**Objective**: F17 (R11 government/court lock + UI lock state), R9 (active mortgage check), R10 (power of attorney check).

### Tasks
- [x] Implement R11 / F17: Government and Court Locks (`is_khas`, `under_acquisition`, `flag_date`, `court_case_no`, `case_status`, `injunction`)
- [x] Implement R9: Mortgage and Release (`MORTGAGE`, `MORTGAGE_RELEASE`, non-transferring replay, double-mortgage check, release chronology)
- [x] Implement R10: Power of Attorney (`POA_GRANT`, `POA_REVOKE`, `via_poa_id`, non-transferring replay, revocation chronology, tricky clean case)
- [x] Extend API schemas, Cytoscape `#6b21a8` locked parcel styling, UI locked warning banner, and simulation lab `via_poa_id` input
- [x] Update generator and create deterministic synthetic demo scenarios (`PARCEL_PLANTED_R9`, `PARCEL_CLEAN_R9_TRICKY`, `PARCEL_PLANTED_R10`, `PARCEL_CLEAN_R10_TRICKY`, `PARCEL_PLANTED_R11`, `PARCEL_CLEAN_R11`)
- [x] Add 27 focused Phase 9 tests covering rules, simulation, API, hash invariance, and parity
- [x] Verify full pytest suite (337 passed), Node badge suite (8/8 passed), and zero forbidden words

---

## Phase 10: Heir Declaration (v1.1)
**Status**: Complete
**Objective**: R8 (unaccounted heir declaration consistency check).

### Tasks
- [x] Implement R8 pure documentary consistency check (`ParcelHistory.heir_declaration`, documentary verification against subsequent survey records and deeds)
- [x] Add `EventType.RELEASE` and handle non-transferring release replay in `replay.py`
- [x] Wire R8 into shared history evaluation dispatcher (`rules.py`) and simulation engine (`simulate.py`)
- [x] Add bilingual localization keys, recommended next-step guides, and calculation localizations (zero forbidden words)
- [x] Add deterministic synthetic demonstration parcels (`PARCEL_PLANTED_R8`, `PARCEL_CLEAN_R8`, `PARCEL_CLEAN_R8_TRICKY`) to generator and demo_v11.json
- [x] Add 22 focused Phase 10 tests covering contradiction, review required, clean, tricky clean (sale/gift/release), replay non-transfer, simulation, API, role leak, hash invariance, and forbidden words
- [x] Verify full test suite passing (359 python tests, 8 node badge tests), 0 clean false alarms, baseline hash preserved

---

## Phase 11: Decision Support & User Experience (v1.1)
**Status**: Complete
**Objective**: F18 (Attention Score 0–100 + traffic light), X3 (concrete next-step guides), X2 (Bangla voice synthesis), X4 (USSD phone simulator), X5 (Digital Vetting Certificate).

### Tasks
- [x] F18 Deterministic Attention Score: 0–100 integer score from configured rule weights in `config.py` and fired alerts; clean parcels score strictly 0 with green traffic light; headline status preserved; Reviewer sees factors and score; Citizen sees plain sentence and traffic light; forbidden words removed
- [x] X2 Offline Bangla Voice: browser `speechSynthesis` control "ফলাফল শুনুন" prioritizing `bn-BD` then `bn-IN`, graceful fallback to on-screen text, clean repeated clicks cancellation, zero external cloud dependencies, accessible ARIA labels
- [x] X3 Rule-Specific Next-Step Guide: 2–4 concrete actionable checks for rules R1 through R15 + HYGIENE in English and Bengali, Law mentor review disclaimer, fallback for unknown rules
- [x] X4 USSD / Feature-Phone Simulator: dedicated demonstration simulator phone frame UI, code `*123*45#`, flow (language -> mouza -> dag -> result), strict <= 160 characters length limit, backed by `/ussd` endpoint
- [x] X5 Digital Vetting Certificate: printable advisory report via browser print dialog, structured certificate layout, unaltered three-status result, attention score & explanation, relevant hash (`report.dataset_hash`), offline QR SVG via `qrcode.js` linking to `#/verify-deed`, standard non-judicial disclaimer, clean print CSS excluding screen controls
- [x] Add 22 focused Phase 11 tests covering all checkpoints, API contracts, parity, and baseline invariance
- [x] Full suite verified: 381 Python tests passing, 8 Node.js badge tests passing, baseline hash strictly invariant, zero forbidden words

**Deliverable**: Decision support scoring, offline voice assistance, actionable rule guides, feature-phone simulator, and advisory vetting certificate fully operational and verified.

---

## Phase 12: Benchmark, Validation & Final Documentation (v1.1)
**Status**: Complete
**Objective**: Extended additive /benchmark table, comprehensive README updates, NEW_FEATURES_EXPLAINED.md, demo_script_v11.md, Docker/Render verification, full regression and invariant checks.

### Tasks
- [x] Checkpoint 1 (Extended Benchmark): Additive `/benchmark` extension returning an `extended` block reporting R8–R15 rule detections and Phase 10/11 features while preserving v1.0 response fields and 0 false alarms on baseline data.
- [x] Checkpoint 2 (README.md): Updated with LandTech 2026 problem P3 context, R1–R15 rules inventory, Phase 11 decision support/UX features, architecture, setup/run commands, actual executed benchmark metrics, third-party asset/license inventory (MIT qrcode.js, three.min.js, OrbitControls.js), while preserving authors' own-words placeholders.
- [x] Checkpoint 3 (docs/NEW_FEATURES_EXPLAINED.md): Plain-language walkthrough of v1.1 features + 15 technically accurate judge questions and answers for student presenters.
- [x] Checkpoint 4 (docs/demo_script_v11.md): Exact 90-second video demo walkthrough script with realistic timings, two student presenter roles, clean parcel, planted contradiction, evidence breakdown, Phase 11 feature showcase, and advisory disclaimer.
- [x] Checkpoint 5 (Deployment Readiness): Static validation of Dockerfile, render.yaml (healthCheckPath: /ui-strings), .dockerignore, and dependency manifests. Noted that live local Docker container verification was unverified due to Docker CLI not being installed in Windows environment.
- [x] Checkpoint 6 (Full Regression & Invariants): 392 Python tests passing, 8 Node.js badge tests passing, 100% locales key parity (72 keys), 100% UI strings parity (220 keys in bn and en), zero forbidden words across all copy, baseline hash strictly invariant (`b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01`).

**Deliverable**: Final extended benchmark, comprehensive technical & plain-language documentation, 90-second presentation script, deployment validation, and complete regression audit verified.


