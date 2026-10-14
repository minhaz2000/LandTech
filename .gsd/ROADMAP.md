# ROADMAP.md — JomiGraph AI

> **Current Phase**: Phase 1 — Core Engine
> **Milestone**: v1.0 (Hackathon Demo)

## Must-Haves

- [ ] Pure-function evaluation engine with rules R1–R7
- [ ] fractions.Fraction arithmetic throughout (no floats)
- [ ] Three statuses only: Consistent / Contradiction Found / Review Required
- [ ] Minimal evidence sets (all alternatives)
- [ ] Pure simulate() that never mutates the baseline
- [ ] Synthetic dataset with planted + clean cases
- [ ] FastAPI backend (parcel, alerts, simulate endpoints)
- [ ] Bilingual UI (Bangla default, English toggle)
- [ ] 15 pytest tests all passing
- [ ] Zero Contradiction alerts on clean synthetic cases
- [ ] README + benchmark.md + demo script

---

## Phase 1: Core Engine
**Status**: 🟡 In Progress
**Objective**: Data models, event replay, rules R1–R7, minimal evidence algorithm. Tests 1–11 and 14.

### Tasks
- [ ] Define dataclasses: Person, Parcel, SurveyRecord, Deed, Event, ParcelHistory
- [ ] Implement chronological event replay (state computer)
- [ ] Implement R1 — Excess transfer
- [ ] Implement R2 — Duplicate allocation (portion_id + lineage only)
- [ ] Implement R3 — Seller's recorded interest
- [ ] Implement R4 — Subdivision reconciliation (Fraction, tolerance param)
- [ ] Implement R5 — Survey continuity (Review Required only)
- [ ] Implement R6 — Deed-mutation reconciliation (Review Required only)
- [ ] Implement R7 — Chronological consistency
- [ ] Minimal evidence algorithm (all alternative minimal sets)
- [ ] recommended_next_step field in every alert (EN + BN keys)
- [ ] Impact view: downstream events per conflicting event
- [ ] pytest tests 1–11 and 14
- [ ] Run tests, show results, stop

**Deliverable**: All engine logic tested; no UI, no API, no data generator yet.

---

## Phase 2: Simulation and Data
**Status**: ⬜ Not Started
**Objective**: evaluate() pure function, counterfactual simulate(), synthetic data generator, tests 12, 13, 15.

### Tasks
- [ ] evaluate(events, parcel_history) → (state, alerts) pure function
- [ ] simulate(baseline, proposed_event) → (state, alerts) never-mutating wrapper
- [ ] Canonical serialization + hash for simulation integrity
- [ ] Synthetic data generator (fixed seed, 8–10 parcels, 4 generations)
  - Planted: over-transfer, duplicate portion, survey gap, mutation-before-deed
  - ~20 clean cases (zero expected Contradiction)
  - One case with two alternative minimal evidence sets
- [ ] pytest tests 12, 13, 15
- [ ] Run tests, show results, stop

**Deliverable**: Full engine + synthetic dataset verified.

---

## Phase 3: API
**Status**: ⬜ Not Started
**Objective**: FastAPI endpoints for parcel, alerts, simulate, search, report.

### Tasks
- [ ] GET /parcels/{parcel_id} — parcel + history
- [ ] GET /parcels/{parcel_id}/alerts — all alerts with evidence + impact
- [ ] POST /simulate — evaluate proposed event, return (state, alerts)
- [ ] GET /search?q=... — search by parcel ID, holder name, khatian no, deed no
- [ ] GET /report/{parcel_id}?lang=bn|en — printable case summary
- [ ] Pydantic response schemas
- [ ] pytest smoke tests for API
- [ ] Run tests, show results, stop

**Deliverable**: Backend API fully operational.

---

## Phase 4: Interface
**Status**: ⬜ Not Started
**Objective**: Bilingual HTML/CSS/JS frontend — Citizen view, Reviewer view, graph, timeline, simulation form.

### Tasks
- [ ] Two JSON translation files (bn.json, en.json) — all user-facing strings
- [ ] Language toggle (Bangla ↔ English), Noto Sans Bengali font
- [ ] Fictional-data banner on every screen
- [ ] Citizen view: plain-language result, recommended_next_step, three starting actions
- [ ] Reviewer view: rule ID, dates, exact arithmetic, source IDs, downstream impact, evidence graph
- [ ] Cytoscape.js evidence graph (CDN)
- [ ] Timeline of events
- [ ] Simulation form: proposed sale input → live result
- [ ] Search bar (parcel ID / holder / khatian / deed)
- [ ] Printable report page (Bangla or English)
- [ ] Mobile-friendly, large tap targets, status as text + icon (never color alone)
- [ ] End-to-end demo case in both languages
- [ ] Run tests, show results, stop

**Deliverable**: Full working UI, demo ready.

---

## Phase 5: Documentation
**Status**: ⬜ Not Started
**Objective**: README, benchmark.md, demo script — all honest, all complete.

### Tasks
- [ ] README.md: setup, modeling assumptions, limits, AI-tool disclosure
- [ ] docs/benchmark.md: rule coverage, clean-case false-alarm rate, evidence traceability, simulation integrity, deterministic replay, uncertainty handling
- [ ] docs/demo_script.md: step-by-step walkthrough for presentation
- [ ] Final check: all 15 tests pass, zero clean-case Contradictions, hashes match
- [ ] Run tests, show results, stop

**Deliverable**: Project fully documented and presentation-ready.
