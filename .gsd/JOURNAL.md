# JOURNAL.md — JomiGraph AI

## 2026-10-14 — Project Initialized

- Received full project specification from team.
- GSD already installed (.agent, .agents, .gemini, .gsd, adapters, scripts, PROJECT_RULES.md, GSD-STYLE.md).
- Created SPEC.md, ROADMAP.md, STATE.md, DECISIONS.md, TODO.md.
- Ready to begin Phase 1 execution.

## 2026-10-16: Pre-submission review fixes

- Fixed area validation (zero, negative, decimals, malformed) and made the lab read the real API fields.
- Added role-aware `/simulate` and `/parcels`, anchored the dataset path, renamed `planted_parcel_count` to `planted_case_count`.
- Removed the Google Fonts links and added `.gitattributes`.
- Added UI/API contract tests so a field mismatch between the screen and the API fails the test run.
- Tests: 141 to 211.
