# JomiGraph AI (জমিগ্রাফ এআই)

A decision-support prototype that checks whether a land record history hangs together. It replays survey records and deed transactions in date order, tests them against seven rules, and shows exactly which records conflict and why. It can also test a proposed sale before anything is registered.

All data in this project is synthetic. JomiGraph AI does not give legal rulings, does not certify ownership, and does not prove fraud.

Built for the LandTech 2026 hackathon, problem P3: Catch Fraud and Double-Selling.

---

## What it does

- Replays each parcel's history (CS, SA, RS and BS survey records plus sales, mutations and subdivisions) in chronological order.
- Checks the history against seven rules, R1 to R7, and reports one of three statuses.
- For a contradiction, shows the exact arithmetic, the records involved, a minimal set of records that reproduces the conflict, and the later transactions that depend on the disputed one.
- Lets a user test a proposed sale in the simulation lab. The stored records are never changed, and the dataset hash is shown before and after to prove it.
- Works in Bangla (default) and English, and prints a one-page case report.

### Two views

- **Citizen view (নাগরিক):** plain-language status, a recommended next step, and the ownership timeline. Rule IDs, calculations, evidence IDs and internal IDs are not shown.
- **Reviewer view (পর্যালোচক):** everything above plus rule IDs, exact calculations, evidence sets, the downstream impact list and an interactive lineage graph.

The two roles are demo views. They are not authentication and have no passwords or access control.

---

## Quickstart

You need Python 3.11 or newer. Node.js is optional: one test checks the status-badge code with Node and skips itself if Node is not installed.

### Windows (PowerShell)

```powershell
git clone https://github.com/alm03806-dev/LandTech
cd LandTech

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

python -m pytest

python -m uvicorn jomigraph.api.app:create_app --factory --app-dir src --host 127.0.0.1 --port 8000
```

### Linux / macOS

```bash
git clone https://github.com/alm03806-dev/LandTech
cd LandTech

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python -m pytest

python -m uvicorn jomigraph.api.app:create_app --factory --app-dir src --host 127.0.0.1 --port 8000
```

Then open http://127.0.0.1:8000 in a browser. `pip install -e .` also works but is not needed.

---

## Demo walkthrough: the Tareq story

The demo data includes a four-generation family in Dhanmondi mouza: Abdur Rahim (CS survey, 1920), Khorshed Alam (SA, 1958), Tareq Mahmud (RS, 1982) and Farhan Mahmud (BS, 2015).

1. Open the app and choose **Citizen (নাগরিক)**.
2. Open `PARCEL_STORY_01` (Dhanmondi, Dag 101). It shows a consistent history across all four surveys, with the ownership timeline.
3. Open `PARCEL_LAB_DEMO` (Dhanmondi, Dag 401). The RS survey of 1982 records Tareq Mahmud with 10 decimals. In 1995 he sold 7 decimals, so 3 decimals remain.
4. Scroll to the simulation lab (**সিমুলেশন ল্যাব: প্রস্তাবিত হস্তান্তর যাচাই**). Enter `3` (decimals such as `2.5` and fractions such as `5/2` also work, and zero or negative values are rejected) and press **Simulate Transfer (হস্তান্তর যাচাই করুন)**. The result is Consistent.
5. Change the area to `5` and press the button again. The result is Contradiction Found: requested 5, available 3, excess 2. The "records unchanged" badge confirms nothing was modified.
6. Press **Switch Role (ভূমিকা পরিবর্তন)** and choose **Reviewer (পর্যালোচক)**. On the planted parcel `PARCEL_PLANTED_R1` (Mirpur, Dag 301) you can see the rule ID, the calculation, the evidence IDs, the minimal evidence set, the lineage graph, and the later resale that depends on the disputed transfer.
7. Press **Print Report (প্রতিবেদন প্রিন্ট করুন)** to get the printable report with the disclaimer and the dataset hash.

---

## Rules and statuses

All areas and shares use Python `fractions.Fraction`, so there is no floating-point rounding.

### Statuses

- **Consistent with supplied records (সঙ্গতিপূর্ণ):** the checks pass on the records provided. This does not mean the title is legally valid.
- **Contradiction Found (অসঙ্গতি পাওয়া গেছে):** the records break a mathematical or date constraint.
- **Review Required (পর্যালোচনা প্রয়োজন):** something is missing or ambiguous, so the engine will not call it a contradiction.

### Rules

- **R1, excess transfer:** a recorded holder transfers more than they have left at that date. If the history is declared incomplete, the result is Review Required instead.
- **R2, duplicate allocation:** two incompatible transfers of the same portion (`portion_id`) through the same lineage. Cancelled sales are ignored. A matching dag or deed number alone is never enough.
- **R3, seller's recorded interest:** the seller had no recorded interest before selling. Contradiction if the history is declared complete, otherwise Review Required.
- **R4, subdivision reconciliation:** child parcel areas should add up to the parent. A difference above 0 and up to `R4_TOLERANCE` (1/10 decimal, set in `config.py`) gives Review Required. A larger difference gives Contradiction Found.
- **R5, survey continuity:** successive surveys (CS, SA, RS, BS) need a documented link. A missing link gives Review Required, never Contradiction.
- **R6, deed and mutation reconciliation:** a mutation's area and beneficiary should match its linked deed and sale. Differences give Review Required.
- **R7, chronology:** a mutation dated before its deed's registration date is a Contradiction. If a date or the link is missing, the result is Review Required.

Before any rule runs, the engine checks for undated events and unsupported event types. If that check fails, it returns Review Required and makes no assumptions.

---

## Data and benchmark

The demo data is generated by `data/generator.py` with a fixed seed (`random.Random(42)`). You can regenerate it at any time.

- 30 parcels in total.
- 21 clean parcels: 10 family-story parcels (`PARCEL_STORY_01` to `10`), 10 clean validation parcels (`PARCEL_CLEAN_01` to `10`) and the simulation demo parcel (`PARCEL_LAB_DEMO`).
- 9 parcels carrying 7 planted problems, one for each rule R1 to R7. The R4 problem uses a parent parcel and two child parcels, which is why 7 problems take 9 parcels. All planted parcels are in Mirpur mouza:

| Parcel | Dag | Planted problem | Result |
| :--- | :--- | :--- | :--- |
| `PARCEL_PLANTED_R1` | 301 | R1 excess transfer | Contradiction Found |
| `PARCEL_PLANTED_R2` | 302 | R2 duplicate allocation | Contradiction Found |
| `PARCEL_PLANTED_R3` | 303 | R3 seller has no recorded interest | Contradiction Found |
| `PARCEL_PLANTED_R4`, `_R4_A`, `_R4_B` | 304, 304/A, 304/B | R4 child areas do not match the parent | Contradiction Found |
| `PARCEL_PLANTED_R5` | 305 | R5 unlinked survey gap | Review Required |
| `PARCEL_PLANTED_R6` | 306 | R6 mutation area differs from the deed | Review Required |
| `PARCEL_PLANTED_R7` | 307 | R7 mutation dated before the deed | Contradiction Found |

- The benchmark (`GET /benchmark` and the Reviewer view) reports 0 alerts on the 21 clean parcels and 7 of 7 planted problems detected.
- Simulation integrity: the dataset's SHA-256 hash is the same before and after a simulation. The current hash is `b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01`. It will change if the data is regenerated with different content.
- The data contains invented names only. It has no NIDs or phone numbers. No data was scraped or downloaded from government websites.

---

## Licence

MIT, see `LICENSE`.

## Limitations

- All data is synthetic. The benchmark shows how the rules behave on 30 invented parcels that we built ourselves. It says nothing about accuracy on real land records.
- This is a decision-support prototype. It does not issue legal rulings, certify ownership or prove fraud, and it does not replace the sub-registry or AC Land office.
- The Citizen and Reviewer roles are demo views, not authentication.
- Whether a parcel's history is complete (`baseline_complete`) is declared by whoever prepares the data. When it is marked incomplete, the engine returns Review Required instead of a contradiction.
- Rule R2 can only detect double allocation of land that carries a `portion_id` label. That label is part of our data model, not something a real register provides today.
- The minimal-evidence search considers at most 12 candidate records. Above that, the result is flagged as not minimized.
- The engine reads structured records. It does not read scanned documents, and it uses no OCR, machine learning or blockchain.
- It does not calculate inheritance shares. Missing inheritance or partition evidence leads to Review Required.
- The seven rules cover a modelled subset of what can go wrong with land records. They are not a complete fraud check.

---

## AI tools used

- **Antigravity** (with the workflow files in `.gsd`, `.agent`, `.agents` and `adapters`) was the main build tool for the engine, API and interface.
- **Claude** was used for planning, code review and drafting prompts. In the final review round it also fixed input validation, the simulation lab, the role-aware API responses and the tests, and it wrote the contract tests that compare the screen with the API.
- The seven rules, the data model and the demo story were specified by the authors. All data is synthetic.

<!-- TODO for the authors: add one or two sentences, in your own words, saying which parts you wrote yourselves and that you can explain every part of the code. Do not submit without this. -->

## Third-party material

Package versions are pinned in `requirements.txt`.

| Library or asset | Details | Licence |
| :--- | :--- | :--- |
| FastAPI | REST API | MIT |
| Uvicorn | ASGI server | BSD-3-Clause |
| Pydantic | Request and response validation | MIT |
| pytest | Test runner | MIT |
| HTTPX | Test client | BSD-3-Clause |
| Cytoscape.js 3.30.2 | Lineage graph. Bundled in `src/jomigraph/ui/vendor/`, with a CDN fallback to the same version | MIT |
| Noto Sans Bengali | Bangla font. Bundled in `src/jomigraph/ui/vendor/fonts/` | SIL Open Font License 1.1 |

---

## Changes since Round 1

*(Nothing yet. Updates for the final round will be listed here.)*
