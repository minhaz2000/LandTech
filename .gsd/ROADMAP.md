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
