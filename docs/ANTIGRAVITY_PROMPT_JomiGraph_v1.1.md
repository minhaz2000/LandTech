# JomiGraph AI v1.1 — Antigravity master prompt

Paste everything below the line into Antigravity (Planning mode, Gemini Pro / Claude). Repo root: `LandTech/`.

---

## 0. Who you are working for, and the deadline

You are extending **JomiGraph AI**, a rule-based land-record consistency checker built by two DIU students for **LandTech 2026** (problem P3, Round 1 closes **18 Oct 2026**). Judges read the rulebook's "Think about who will actually use your software" line, so v1.1 adds features that serve real users: village citizens, urban flat buyers, banks, sub-registry offices, AC Land offices, courts and lawyers. The students must be able to **explain every line**, so prefer small, readable functions over clever ones.

Time is short. Work in the phases in section 6, in order. **Every phase must end with all tests green and the app runnable**, so we can stop after any phase and still submit. Do not stop between phases to ask permission (see 1.3), but do stop after 3 failed attempts on the same problem (GSD rule) and write a state dump.

## 1. Process (GSD, already set up in this repo)

1. Read first, in this order: `.gemini/GEMINI.md`, `PROJECT_RULES.md`, `.gsd/SPEC.md`, `.gsd/STATE.md`, `.gsd/ROADMAP.md`, `README.md`. Search before reading big files (`rules.py`, `app.py`, `app.js`).
2. **Planning Lock:** before any code, amend `.gsd/SPEC.md` with a new section "v1.1 Additions" (new rules R8–R15, new fields, new endpoints, the invariants in section 2), set Status back to `FINALIZED`, then add Phases 6–12 to `.gsd/ROADMAP.md` and write a `PLAN.md` per phase under `.gsd/phases/`.
3. **Approval is granted in advance** for editing these existing files, because SPEC says to ask: `models.py, loader.py, config.py, i18n.py, engine/rules.py, engine/simulate.py, engine/benchmark.py, engine/evidence.py, api/app.py, api/schemas.py, api/extras.py, ui/*.js, ui/*.html, ui/*.css, ui/strings.json, locales/*.json, README.md, .gsd/*`. Do **not** weaken or delete any existing test assertion. New tests go in new files.
4. One task = one commit, message `type(scope): description`. After each task update `.gsd/STATE.md`. Proof is required: paste the pytest output, curl output, or a screenshot path for every phase (see PROJECT_RULES.md).
5. Environment is Windows PowerShell plus Linux (Render/Docker). Keep paths portable; use `pathlib`.

## 2. Non-negotiable invariants (a violation = revert the change)

- **Fractions only** for any area or share. No float in rules or in new fields (`load_fraction` stays the boundary).
- **Exactly three statuses**: `Consistent with supplied records`, `Contradiction Found`, `Review Required`. Never output "safe", "valid", "legal", "verified owner", "fraud", "forged", "scam" or "you will be cheated" in any user-visible string, Bangla or English. Use "records conflict", "needs checking", "সরবরাহকৃত রেকর্ডে অসঙ্গতি", "দেখা দরকার".
- **Missing or ambiguous input -> Review Required first.** Only then apply `baseline_complete` and the rule logic. A new rule returns Contradiction only when the SPEC-style condition is explicit and all inputs are present.
- Every `Alert` has non-empty `evidence_ids` (the `run_rule` wrapper enforces it). Every alert has bilingual `message_key` and `recommended_next_step` keys in **both** `locales/bn.json` and `locales/en.json`.
- **Synthetic data only.** No real names, NID numbers, phone numbers, bank names or case numbers. Use fictional ones ("Demo Bank Ltd", `DEMO-CASE-0001`, `DUMMY-ID-0001`). Dummy IDs must visibly look fake and must not match any real Bangladesh NID length or format.
- **No new network calls at runtime, no ML, no blockchain, no scraping, no external API.** Any new library must be MIT/Apache/BSD, vendored into `ui/vendor/` (or `requirements.txt` with a pinned version for Python), and added to the README third-party table. The app must still work offline.
- **Back-compat:** all existing data loads unchanged. New model fields are optional with defaults. Existing JSON keys and values in API responses are unchanged; new data is added under new keys. The 211 existing tests, the benchmark (21 clean parcels with 0 alerts, 7 of 7 planted detected) and the dataset hash before/after simulation must remain true. If `hash_dataset` has to include a new field, include it only when present so the original dataset hash does not change, and prove that with a test.
- **Roles:** the citizen response must still contain no rule IDs, calculations, evidence IDs or staging fields. Reviewer sees everything. Add a test per new endpoint for this.
- `simulate()` stays pure. New rules must also run inside `evaluate()`, `evaluate_history()` and the simulation lab. These two functions currently duplicate the rule dispatch; as the very first code commit, extract one shared dispatcher with **no behaviour change** and prove it with the unchanged test suite.

## 3. What is already built (do not rebuild)

R1–R7 replay engine with exact Fractions, minimal evidence sets, downstream impact, simulation lab with SHA-256 integrity, 21 clean + 7 planted benchmark, three-status UI, citizen/reviewer views, lineage graph (Cytoscape), 3D mouza map and division/district/upazila filter, "check my land" form (`/check-my-land`), bilingual UI, one-page print report with hash, input hardening, 13 test files, Render deploy.

Note: **R1 already enforces the seller's own share per holder** (it compares the sale against the seller's modeled share, not the whole dag). So the "Ejmali / co-owner quota" idea needs only a display helper and extra tests (item X1), not a new rule.

## 4. Features to add (grouped by the user's list 13–18 plus the extra ideas)

Rule IDs continue from R7. Each rule is a pure function in `engine/rules.py` with the same shape as `check_r1..r7`, wired into the single dispatcher.

**F13 · R12 Deed integrity (rulebook P2: fake or changed copies)**
- Add optional `content_hash` on `Deed`: SHA-256 over a canonical serialisation of the deed's registry-recorded fields (deed_no, registration_date, parcel_id, seller, buyer, area) using the same canonical JSON style as `simulate.hash_dataset`.
- New endpoint `POST /verify-deed` (body: the fields on the presented copy + optional claimed hash). Recompute and compare. Mismatch -> **Contradiction Found** ("presented copy differs from the registry-recorded fingerprint"). No registry hash on file or no claimed hash -> **Review Required**. Match -> Consistent.
- **QR:** each deed/parcel gets a QR whose payload is a relative verify link containing deed_no and the first 16 hex chars of the hash. Generate the QR **client-side** with a vendored MIT library (e.g. `qrcode-generator` or Nayuki's QR code generator) in `ui/vendor/`. Add a "Verify deed" screen: type or paste deed fields, see the result in three-status form. State on screen that this is a hash comparison, not a legal digital signature.

**F14 · R13 Deed number reused (P3)**
- Same `deed_no` on more than one parcel or event with a different registration date, seller, buyer or area -> **Review Required only**. Never Contradiction, and never claim double sale: one deed can legitimately cover several dags (existing R2 rule says "never match on dag/deed number alone"; keep that). Show all parcels sharing the number in the evidence.

**F15 · R14 Dummy identity numbers (P3: two different people with one name)**
- Add optional `dummy_id` on `Person` (format `DUMMY-ID-0001`). Same name + different `dummy_id` = different people everywhere (search, graph, evidence, report). Same `dummy_id` + different spelling of name = **Review Required** (possible same person, needs checking). Missing `dummy_id` on a name that exists twice in a parcel history = **Review Required**.
- Search by name must show a disambiguation list with the dummy ID, never merge people by name.

**F16 · R15 Same portion sold twice, boundary / portion marks (P3 core)**
- Add optional structured `portion` on `Event`: `portion_id` (already exists), `boundary` (north/south/east/west descriptors as short strings or a named sub-dag such as `101/1-ka`), `portion_area` (Fraction). Two non-cancelled transfers whose structured boundary descriptors are identical or one contains the other, via lineage -> **Contradiction Found**. If boundaries are missing or only partly given -> **Review Required**. R2 keeps its current behaviour; R15 catches the same physical piece under two different `portion_id`s.
- Add the boundary fields to the simulation lab form so a judge can type a proposed sale and watch R15 fire before registration.

**F17 + text R11 · Government / court lock (P5)**
- Optional parcel metadata: `is_khas` (bool), `under_acquisition` (bool) with `flag_date`, `court_case_no` (string, fictional) with `case_status` (`pending` | `disposed`) and `injunction` (bool).
- A SALE/GIFT dated after a khas or acquisition flag -> **Contradiction Found** (records conflict with the recorded flag). A pending case or injunction -> **Review Required** (a case alone does not prove the sale is invalid). Flag missing a date -> Review Required.
- UI: locked parcels get a distinct purple/dark node in the lineage graph and 3D map, a lock icon, and "new transactions are shown as blocked". Add `is_khas`/`under_acquisition`/`court_case_no` as filters in the area filter.

**Text R9 · Mortgage active at sale (banks, "same land mortgaged twice")**
- New event types `MORTGAGE` and `MORTGAGE_RELEASE` (fictional lender id). A SALE/GIFT by the mortgagor while a mortgage on that portion is unreleased -> **Contradiction Found**; a second MORTGAGE on a portion with an unreleased one -> Contradiction Found; release date missing or unclear -> Review Required. Replay must treat these types as non-transferring (they must not change holder areas).

**Text R10 · Power of attorney (urban developer sales)**
- New event types `POA_GRANT` and `POA_REVOKE`, plus optional `via_poa_id` on SALE. A sale by an agent needs a grant from the owner that covers the parcel (and the portion if scoped) and no revocation dated before the sale -> otherwise **Contradiction Found** (revoked or missing grant when all dates are present), **Review Required** when dates or scope are missing.

**Text R8 · Unaccounted heir (inheritance, village use case)**
- SPEC non-goal still stands: **do not calculate inheritance shares by law.** R8 only checks consistency of what the records declare: an optional `heir_declaration` (deceased id, list of declared heirs with relation, `complete` flag, source record id). When the next khatian or deed after the death does not list a declared heir and there is no release, gift or sale document by that heir -> **Review Required**; **Contradiction Found** only if `complete=true`, all dates are present and the document set is explicit. Never judge whether a sanad is genuine.
- Put this phase **last** among rules; if time is short it is the first thing to cut.

**F18 · Attention score and explanation**
- Deterministic integer **attention score 0–100** per parcel and per simulated sale, computed from fired alerts using a weights table in `config.py` (e.g. Contradiction weight > Review weight; per-rule weights). Return `score` plus `factors` (list of rule, status, points). Reviewer sees the factors; citizen sees the score, the traffic light and plain sentences only.
- The **status stays the headline**. The score never overrides it and is never a probability of fraud. A parcel with all-Consistent alerts must score 0. Label: "Attention score" / "মনোযোগ স্কোর", with the line "0 means no flags in the supplied records, not that the land is safe."
- Traffic light derived from status first: Contradiction = red, Review Required = yellow, Consistent = green. Green text must say "সরবরাহকৃত রেকর্ডের সাথে সামঞ্জস্যপূর্ণ" / "Consistent with supplied records", never "safe".

**Extras from the notes**
- **X1 Share display:** helper converting a Fraction share into traditional units for display only (16 ana = 1 whole; 1 ana = 20 ganda; 1 ganda = 4 kora; 1 kora = 3 kranti; 1 kranti = 20 til), e.g. 1/4 = 4 ana. Show the exact Fraction as well. Add a note that the conversion table should be confirmed with the Law mentor. Show each co-owner's share and limit in the Reviewer view, with tests for R1 on a 5-co-owner (Ejmali) dag.
- **X2 Bangla voice:** "ফলাফল শুনুন" button using the browser's built-in `speechSynthesis` (no external API). Feature-detect, try `bn-BD` then `bn-IN`, and if no Bangla voice exists show "এই ডিভাইসে বাংলা ভয়েস নেই" and keep the text visible. The spoken sentence is built from the same citizen-safe translated strings (no rule IDs, no accusations), e.g. "সতর্কতা: সরবরাহকৃত রেকর্ডে অসঙ্গতি পাওয়া গেছে। কেনার আগে সাব-রেজিস্ট্রি অফিসে যাচাই করুন।"
- **X3 Next-step guide:** extend `recommended_next_step` for every rule (old and new) into 2–4 concrete "what to check or ask" steps in Bangla and English (ask for a certified deed copy, check mutation/নামজারি status at the land office, ask the bank for a lien/mortgage statement, consult a lawyer). Frame them as checks, not legal advice; add the disclaimer line "to be reviewed by the Law mentor". Do not invent specific legal procedures or office names you are not sure of.
- **X4 USSD / feature-phone simulator:** a phone-frame screen in the UI that walks a text-only flow (choose language -> mouza -> dag number -> result in <=160 characters per screen) over the existing citizen API. Use an **invented** short code such as `*123*45#` and label it "সিমুলেটর, কোনো আসল টেলিকম সংযোগ নয়". Do not use any real government hotline or short code.
- **X5 Vetting certificate:** extend the existing print report into a "Digital Vetting Certificate": parcel, three-status result, attention score, chain summary, SHA-256 of the evaluated records, QR to the verify link, timestamp placeholder, and the standard disclaimer. Use the browser print dialog for PDF (no new PDF library). Bangla and English.

## 5. Data and benchmark

- Do not edit existing `demo_family.json`, `demo_regions.json` or their generators. Create `data/demo_v11.json` with a seeded `data/generator_v11.py` (fixed seed).
- For every new rule: at least **1 planted positive** and **2 clean parcels**. Add one deliberately tricky clean case per rule (e.g. same deed number covering two dags legitimately; two people with one name and different dummy IDs; mortgage released before the sale; POA revoked after the sale; heir who sold their share by deed).
- Extend `/benchmark` **additively** (new `extended` block with the same coverage-table shape). Targets: 0 alerts on every clean parcel, every planted case detected, and the original block unchanged. Report honest counts in the README; do not inflate.
- Add to `/ui-strings` and `locales/*.json` every new string in both languages. Add a test that fails if any key exists in one language and not the other, and a test that scans all citizen-visible strings for the forbidden words in section 2.

## 6. Phases (each ends green and committed)

| Phase | Content | Done when |
|---|---|---|
| 6 | SPEC/ROADMAP amend, shared dispatcher refactor (no behaviour change), optional model/loader fields, `config.py` weights, i18n scaffolding, `demo_v11.json` skeleton | 211 tests green, hash unchanged |
| 7 | F13 R12 + QR + `/verify-deed` + Verify screen; F14 R13; F15 R14 + name disambiguation | new tests green, curl proof, screenshot |
| 8 | F16 R15 + simulation-lab boundary fields + X1 share display + Ejmali tests | planted case fires in lab, clean cases silent |
| 9 | F17 R11 lock + UI lock state; R9 mortgage; R10 POA | all three with planted + clean + tricky cases |
| 10 | R8 heir declaration (cut if short on time) | same |
| 11 | F18 score + traffic light; X3 next-step guide; X2 voice; X4 USSD simulator; X5 certificate; wire all into citizen and reviewer views and the "check my land" flow | UI contract tests updated additively; screenshots at 375 px and desktop |
| 12 | Benchmark extended, README (new features, honest limits, new third-party libs, AI tools used, "what changed since Round 1"), `docs/NEW_FEATURES_EXPLAINED.md` (plain-language walkthrough and 15 likely judge questions with answers for the two students), `docs/demo_script_v11.md` (90-second video script), Docker/Render smoke test, final full regression | everything green, `STATE.md` updated |

**Cut line if time runs out:** ship after Phase 9 plus the score/traffic-light part of Phase 11. Never leave a phase half-merged.

## 7. Final checklist (paste the evidence in your last message)

1. Full `pytest` output: old 211 plus new tests, 0 failures. Node badge test if Node exists.
2. Benchmark JSON: original block unchanged, extended block with counts.
3. Dataset hash before and after simulation, original dataset and `demo_v11`.
4. A role-leak test result: citizen responses for every new endpoint contain no rule IDs, calculations or evidence IDs.
5. Forbidden-word scan result on all user-visible strings, Bangla and English.
6. Screenshots: verify screen, lock state, score card with traffic light, USSD simulator, certificate print preview.
7. `git log --oneline` showing one commit per task.
8. List of anything you could not finish or were unsure about, and every new third-party file with its licence.

Do not touch: the concept note, the demo video, the GitHub URL, or the authors' own-words README paragraphs (scope of assistance, understanding statement). Leave those for the students.
