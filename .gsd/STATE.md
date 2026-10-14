# STATE.md — JomiGraph AI

> **Last Updated**: 2026-10-14
> **Current Phase**: Phase 1 — Core Engine
> **Overall Status**: 🟡 In Progress

## What We're Building

A rule-based land-record consistency checker for a Bangladesh hackathon. Synthetic data only. Pure-function engine, FastAPI backend, bilingual HTML/JS frontend.

## Current Focus

Phase 1: Implement data models, event replay, R1–R7 rules, minimal evidence algorithm, pytest tests 1–11 and 14.

## Last Action

Project initialized from full spec. Ready to begin Phase 1 execution.

## Blocking Issues

None.

## Key Decisions Made

- Python 3.11, fractions.Fraction — no floats anywhere in rules.
- Exactly three statuses: Consistent with supplied records / Contradiction Found / Review Required.
- Evaluation order: missing inputs → Review Required FIRST; baseline_complete applied second.
- Minimal evidence: all alternative minimal sets returned.
- Simulation: evaluate() is a pure function, baseline hash verified before and after.

## Environment

- OS: Windows (PowerShell)
- Language: Python 3.11
- Backend: FastAPI
- Frontend: HTML/CSS/JS + Cytoscape.js (CDN)
- Tests: pytest
