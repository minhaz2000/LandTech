# STATE.md — JomiGraph AI

> **Last Updated**: 2026-10-14
> **Current Phase**: Phase 1 — Core Engine
> **Overall Status**: 🟡 Planning Complete — Ready for Execution

## Current Position
- **Phase**: 1 Complete + Simulation Engine (79 tests passing)
- **Task**: Plans 1.1-1.3, R2 cancellation fix, minimal_evidence cap handling, and simulate.py completed
- **Status**: Ready for Phase 2 (Synthetic Dataset Generation and API endpoints)

## Next Steps
1. Phase 2: Synthetic dataset generation and integration tests (tests 12, 13, 15)

## What We Are Building
A rule-based land-record consistency checker for a Bangladesh hackathon.
Synthetic data only. Pure-function engine, FastAPI backend, bilingual HTML/JS frontend.

## Phase 1 Plans

| Plan | Wave | Title | Tests Covered |
|------|------|-------|---------------|
| 1.1 | 1 | Data Models and Event Replay | (foundation for all) |
| 1.2 | 1 | Rules R1, R2, R3 + Alert Structure | 1, 2, 3, 4, 5, 6 |
| 1.3 | 2 | Rules R4-R7 + Minimal Evidence | 7, 8, 9, 10, 11, 14 |

## Key Decisions Made

- Python 3.11, fractions.Fraction — no floats anywhere in rules.
- Exactly three statuses: Consistent with supplied records / Contradiction Found / Review Required.
- Evaluation order: missing inputs -> Review Required FIRST; baseline_complete applied second.
- Minimal evidence: all alternative minimal sets returned.
- simulate() is a pure function; baseline hash verified before and after.
- recommended_next_step in every Alert (bn + en keys).
- impact_event_ids in every Alert for downstream dependency view.
- R4_TOLERANCE is a named Fraction in config.py.

## Blocking Issues
None.

## Environment
- OS: Windows (PowerShell)
- Language: Python 3.11
- Backend: FastAPI
- Frontend: HTML/CSS/JS + Cytoscape.js (CDN)
- Tests: pytest
