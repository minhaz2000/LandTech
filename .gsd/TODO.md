# TODO.md: JomiGraph AI

## Before submission (Round 1 closes 18 October 2026)

- [ ] Concept note, PDF, 3 pages maximum
- [ ] Demo video, 90 seconds maximum
- [ ] README: scope-of-assistance paragraph and understanding statement, in the authors' own words
- [ ] Public GitHub repository, then replace `<REPO_URL>` in the README
- [ ] Confirm the LICENSE (MIT is in the repo as the default)
- [ ] Check on a real phone: layout at about 375 px, Bangla and English print preview, offline reload
- [ ] Run the quickstart once on a clean machine

## Optional polish

- [ ] Add an HTML-escape helper for the `innerHTML` calls in `app.js`. Nothing user-typed is echoed today, so this is hardening only.
- [ ] Write `docs/benchmark.md` and `docs/demo_script.md` if there is time (the README already covers the benchmark and the walkthrough).

## Done

- [x] Phase 1: models, replay, rules R1 to R7, minimal evidence
- [x] Phase 2: simulate(), synthetic dataset generator, integrity hash
- [x] Phase 3: FastAPI endpoints, schemas, search, report
- [x] Phase 4: bilingual UI, role views, lineage graph, simulation lab, print report
- [x] Phase 5: README with quickstart, limits and third-party table
- [x] Pre-submission fixes: input validation, decimals, role-aware responses, path anchoring, field rename, font links, line endings
