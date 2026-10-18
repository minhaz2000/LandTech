# SPEC.md — JomiGraph AI

> **Status**: `FINALIZED`

## Vision

JomiGraph AI is a rule-based, decision-support prototype for a Bangladesh land-technology hackathon. It tests a proposed land transaction against a parcel's recorded history, shows exactly which records conflict, and changes none of those records while doing so. It uses only synthetic, invented data and never claims to give a legal ruling or detect fraud. It is designed to be small, readable, fully explainable, and defensible by two students.

## Goals

1. Implement a pure-function evaluation engine (rules R1–R7) that replays synthetic land-record events in chronological order and returns one of three statuses: *Consistent with supplied records*, *Contradiction Found*, or *Review Required*.
2. Provide a counterfactual simulation lab: `evaluate(events, parcel_history)` is a pure function; simulations never mutate the baseline.
3. Deliver a bilingual (Bangla default / English) web interface with a Citizen view and a Reviewer view, Cytoscape.js graph, and a printable case-summary report.
4. Achieve 100% test coverage for the 15 required pytest tests and zero false-alarm Contradiction alerts on clean synthetic cases.
5. Produce honest, self-contained documentation (README, benchmark.md, demo script) that states all assumptions and limits.

## Non-Goals (Out of Scope)

- Inheritance calculation — missing inheritance or partition evidence returns *Review Required*.
- OCR, ML models, blockchain, web scraping, or any external data source.
- Real land records, real people, real government portals.
- Claiming legal ownership, proving fraud, or certifying any real-world state.
- Features outside this brief.

## Users

- **Citizen view**: Plain-language result with recommended next steps, mobile-friendly, large tap targets.
- **Reviewer view**: Full rule ID, exact arithmetic, source record IDs, evidence graph, downstream impact, printable report.
- **Hackathon judges**: Two students must present, explain and defend every line of code.

## Hard Constraints

- Python 3.11, fractions.Fraction for ALL area/share arithmetic — no floats in rules.
- FastAPI backend, pytest for tests, plain HTML/CSS/JavaScript frontend, Cytoscape.js (CDN) for graph.
- No OCR, ML, blockchain, scraping, external APIs.
- Synthetic data only, invented names only, fixed random seed for generator.
- Work one GSD phase at a time; run tests, show results, stop.
- Before modifying any file not created in the current phase, request approval.

## Data Model

- Person(id, name)
- Parcel(id, dag_no, mouza, parent_id)
- SurveyRecord(id, parcel_id, survey, khatian_no, record_date, recorded_area, holders[(person_id, area)])
- Deed(id, deed_no, registration_date)
- Event(id, type in {SALE,GIFT,SUBDIVIDE,MUTATION,CANCEL,CORRECT}, event_date, parcel_id, from_person, to_person, area, deed_id, portion_id, linked_event_id, source_record_id)
- ParcelHistory(baseline_complete: bool, start_record_id, end_date)

portion_id is a modeled label, not proof of physical identity. baseline_complete is an explicit author-declared assumption. Nothing stores "current owner" — state is always computed by replaying events chronologically.

## Rules

R1 Excess transfer: Contradiction Found if baseline_complete=true and transfer exceeds modeled share; else Review Required.
R2 Duplicate allocation: Contradiction Found if same portion_id sold twice via lineage; else Review Required. Never match on dag/deed number alone.
R3 Seller's recorded interest: Contradiction Found if baseline_complete=true and evidence disproves seller's interest; else Review Required.
R4 Subdivision reconciliation: Exact match passes. Difference in (0, tolerance] = Review Required. Difference > tolerance = Contradiction Found.
R5 Survey continuity: No documented link between successive survey records = Review Required (never Contradiction).
R6 Deed-mutation reconciliation: Mutation's deed/area/info doesn't reconcile = Review Required.
R7 Chronological consistency: Contradiction Found only when link+both dates present and mutation precedes deed. Else Review Required.

## Statuses (exactly three)

- Consistent with supplied records: all checks pass. Never "safe", "valid" or "legal".
- Contradiction Found: complete, relevant evidence violates an explicit modeled constraint.
- Review Required: evidence missing, ambiguous or insufficient.

None certifies legal ownership or proves fraud.

## Evaluation Order (inside every rule)

1. Check required inputs; if missing/ambiguous return Review Required.
2. Apply baseline_complete and rule logic. baseline_complete must never override a missing or ambiguous input.

## Minimal Evidence

Engine removes one candidate record at a time, re-runs rule, keeps record only if its removal makes the violation disappear. Returns all alternative minimal sets found.

## Simulation Integrity

evaluate(events, parcel_history) is a pure function returning (state, alerts). Simulation calls evaluate(events + [proposed]) on a new list and never mutates the original data. Canonical serialization hash of baseline must match before and after every simulation.

## Additions (in scope)

- recommended_next_step in every alert (Bangla + English).
- Impact view: downstream events depending on the conflicting event.
- Search: by parcel ID, holder name, khatian number, deed number.
- Report: printable case summary (Bangla or English) as a page.

## Synthetic Dataset

Fixed random seed, one main story family across 4 generations (CS, SA, RS, BS), 8-10 parcels, one subdivision. Planted: over-transfer, duplicate portion sale, survey gap, mutation before deed. ~20 clean cases with zero expected Contradiction alerts. One case with two alternative minimal evidence sets.

## Success Criteria

- All 15 pytest tests pass.
- Zero Contradiction alerts on clean synthetic cases.
- Demo case works end-to-end in Bangla and English.
- Simulations never mutate the baseline (hash verification).
- README states all assumptions and limits honestly.
- benchmark.md covers all required evaluation dimensions.

---

## v1.1 Additions

### Invariants (Non-negotiable)
- **Fractions only** for any area or share. No float in rules or in new fields (`load_fraction` stays the boundary).
- **Exactly three statuses**: `Consistent with supplied records`, `Contradiction Found`, `Review Required`. Never output "safe", "valid", "legal", "verified owner", "fraud", "forged", "scam" or "you will be cheated" in any user-visible string.
- **Missing or ambiguous input -> Review Required first.** Only then apply `baseline_complete` and rule logic. A new rule returns Contradiction only when the condition is explicit and all inputs are present.
- **Every Alert has non-empty evidence_ids**; every alert has bilingual `message_key` and `recommended_next_step` keys in both `locales/bn.json` and `locales/en.json`.
- **Synthetic data only.** No real names, NIDs, phone numbers, bank names or case numbers. Fictional dummy IDs (`DUMMY-ID-0001`, `DEMO-CASE-0001`).
- **No new network calls at runtime, no ML, no blockchain, no scraping, no external API.** Pure offline capability.
- **Back-compat:** All existing v1.0 data loads unchanged. New model fields are optional with defaults. Existing API schemas and dataset SHA-256 hashes remain identical.
- **Role separation:** Citizen response contains no rule IDs, calculations, evidence IDs or staging fields; Reviewer sees complete audit evidence.
- **Pure simulation & Shared dispatch:** `simulate()` stays pure. All rules evaluate through a single shared rule dispatcher across `evaluate()`, `evaluate_history()`, and simulation.

### Rules R8–R15
- **R8 Unaccounted heir declaration:** Consistency check of declared heirs in `heir_declaration`. When next khatian or deed lacks declared heir without release/gift/sale deed -> Review Required; Contradiction Found only if complete=true and dates/docs explicit.
- **R9 Mortgage active at sale:** Event types `MORTGAGE` and `MORTGAGE_RELEASE`. Sale/gift during active mortgage -> Contradiction Found; second mortgage on same portion -> Contradiction Found; ambiguous release -> Review Required. Replay treats as non-transferring.
- **R10 Power of attorney:** Event types `POA_GRANT` and `POA_REVOKE`. Sale via POA (`via_poa_id`) requires valid grant and no prior revocation -> Contradiction Found if revoked/missing; Review Required if dates/scope ambiguous. Replay treats as non-transferring.
- **R11 Government / court lock:** Parcel flags `is_khas`, `under_acquisition`, `court_case_no`, `injunction`. Sale after flag date -> Contradiction Found; pending case or injunction -> Review Required.
- **R12 Deed integrity:** Canonical SHA-256 `content_hash` on Deed. Verification endpoint `POST /verify-deed`. Mismatch -> Contradiction Found; missing on file/claimed -> Review Required; match -> Consistent. Client-side QR code.
- **R13 Deed number reused:** Same `deed_no` on multiple parcels/events with different parties/dates/area -> Review Required only (never Contradiction).
- **R14 Dummy identity numbers:** Optional `dummy_id` on Person (`DUMMY-ID-0001`). Disambiguates persons with identical names in search, graph, and evidence.
- **R15 Structured boundary / portion sold twice:** Structured `portion` and `boundary` descriptors on Event. Overlapping or duplicate physical boundary via lineage -> Contradiction Found.

### Extended Model Fields & Types
- `Deed.content_hash: Optional[str] = None`
- `Person.dummy_id: Optional[str] = None`
- `Event.portion: Optional[dict] = None`
- `Event.boundary: Optional[str | dict] = None`
- `Event.via_poa_id: Optional[str] = None`
- `Parcel.is_khas: bool = False`
- `Parcel.under_acquisition: bool = False`
- `Parcel.flag_date: Optional[date] = None`
- `Parcel.court_case_no: Optional[str] = None`
- `Parcel.case_status: Optional[str] = None`
- `Parcel.injunction: bool = False`
- `EventType`: `MORTGAGE`, `MORTGAGE_RELEASE`, `POA_GRANT`, `POA_REVOKE`
- `ParcelHistory.heir_declaration: Optional[dict | list] = None`

### Endpoints (v1.1)
- `POST /verify-deed`
- `POST /assistant` (Offline deterministic guidance)
- `GET /geo/tree`, `GET /geo/parcels`, `POST /check-my-land` (Administrative navigation and citizen check)
- `GET /benchmark` (Extended additive coverage)

