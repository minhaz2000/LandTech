# JomiGraph AI (জমিগ্রাফ এআই) v1.1

A rule-based land transaction consistency and decision-support engine developed for **LandTech 2026** (Problem P3: *Catch Fraud and Double-Selling*, Round 1 deadline: 18 October 2026). JomiGraph AI evaluates chronological chains of land records—survey khatians (CS, SA, RS, BS), registered conveyance deeds, mutations, mortgages, power of attorney grants, and inheritance declarations—against 15 deterministic consistency rules (R1–R15). It pinpoints documentary contradictions, generates minimal evidence sets, visualizes downstream impacts, and enables counterfactual transfer simulation without modifying stored records.

> **Advisory Scope & Synthetic Data Disclosure**  
> All data in this repository is synthetic and fictional. Fictitious names, parcel numbers, dummy identification numbers (`DUMMY-ID-0001`), and sample case references are generated deterministically. JomiGraph AI is an advisory decision-support tool. It does not provide legal rulings, does not certify official title ownership, does not replace the Sub-Registry or AC Land office, and does not establish legal guilt or intent.

---

## What It Does

- **Chronological Replay:** Replays each parcel's history from baseline survey (CS/SA/RS/BS) through conveyance events in strict date/sequence order.
- **15 Mathematical & Chronological Rules (R1–R15):** Evaluates recorded ownership, area constraints, boundary overlap, encumbrances, and succession declarations.
- **Three Deterministic Statuses:** Every evaluation resolves strictly to one of three statuses:
  - `Consistent with supplied records` (সব রেকর্ড সামঞ্জস্যপূর্ণ)
  - `Contradiction Found` (রেকর্ডে অসঙ্গতি পাওয়া গেছে)
  - `Review Required` (পর্যালোচনা প্রয়োজন)
- **Zero Forbidden Words:** Strict enforcement across English and Bengali interfaces. The system never outputs ambiguous or legally fraught terms (`safe`, `valid`, `legal`, `verified owner`, `fraud`, `forged`, `scam`, `you will be cheated`, `জালিয়াতি`, `আইনগত`, `বৈধ`).
- **Counterfactual Simulation Lab:** Test proposed sales and transfers prior to deed execution. The engine evaluates rules on-the-fly and guarantees dataset immutability via canonical SHA-256 hashing.
- **Two Distinct Perspectives:**
  - **Citizen View (নাগরিক ভিউ):** Plain-language status, attention score with traffic-light indicator, actionable verification next steps, and ownership timeline. Internal rule IDs, mathematical calculations, and raw evidence IDs are suppressed.
  - **Reviewer View (পর্যালোচক ভিউ):** Full technical transparency with rule IDs, exact rational calculations (`fractions.Fraction`), minimal evidence sets, downstream impact propagation, and interactive lineage graphs.

---

## Rules Inventory (R1–R15)

All area and quota arithmetic uses Python's exact `fractions.Fraction`—strictly avoiding floating-point rounding errors.

| Rule | Name | Target Problem | Resolution Logic |
| :--- | :--- | :--- | :--- |
| **R1** | Excess Transfer | Overselling / co-owner quota breach | Contradiction if cumulative sales exceed seller's modeled share under complete baseline; Review Required if baseline incomplete. |
| **R2** | Duplicate Allocation | Double-selling identified sub-plot | Contradiction if uncancelled transfers allocate the same `portion_id` through identical lineage; Review Required if overlap unestablished. |
| **R3** | Seller's Recorded Interest | Bogus seller without title | Contradiction if seller is not a recorded survey holder or prior deed grantee under complete baseline; Review Required if baseline incomplete. |
| **R4** | Subdivision Reconciliation | Area inflation upon partition | Contradiction if child parcel sum exceeds parent area by more than tolerance (`R4_TOLERANCE` = 0.1 decimal); Review Required if within tolerance. |
| **R5** | Survey Continuity | Unlinked gaps between CS, SA, RS, BS | Review Required if successive survey records lack documentary deeds or mutation bridges. Never Contradiction. |
| **R6** | Deed-Mutation Reconciliation | Mutation differs from registered deed | Review Required if mutated area or beneficiary conflicts with linked deed. |
| **R7** | Chronological Consistency | Post-dated deed or pre-dated mutation | Contradiction if mutation order date precedes deed registration date; Review Required if dates missing. |
| **R8** | Unaccounted Heir Declaration | Village inheritance omission | Contradiction if complete heir declaration omits declared heirs in subsequent khatian without release/sale; Review Required if declaration incomplete. |
| **R9** | Active Mortgage Encumbrance | Mortgaged land sold or re-pledged | Contradiction if land sold or re-mortgaged while an unreleased mortgage remains active; Review Required if release date unclear. |
| **R10** | Power of Attorney | Unauthorized developer sale | Contradiction if sale executed under revoked or missing power of attorney grant; Review Required if POA scope/date missing. |
| **R11** | Government & Court Locks | Khas land, acquisition, injunctions | Contradiction if transfer dated after recorded khas or acquisition flag; Review Required if pending court case or injunction exists. |
| **R12** | Deed Content Fingerprint | Altered or counterfeit deed copy | Contradiction if presented deed copy fields do not match canonical SHA-256 fingerprint on file; Review Required if hash unrecorded. |
| **R13** | Reused Deed Number | Same deed volume reused on other plots | Review Required if same deed number appears across multiple parcels with different dates, parties, or areas. Never Contradiction. |
| **R14** | Identity Disambiguation | Name collisions across different persons | Review Required if identical name appears with distinct dummy IDs (`DUMMY-ID-0001`) or without disambiguating identifiers. |
| **R15** | Physical Boundary Duplicate Sale | Duplicate sale under different sub-plot labels | Contradiction if structured boundary descriptors (North, South, East, West) or sub-dag allocations match an uncancelled prior sale. |

---

## Decision Support & User Experience (v1.1 Features)

- **Deterministic Attention Score (F18):** Integer score (0–100) calculated deterministically from active alerts and weighted severity in `config.py`. Status remains the primary headline; a score of 0 indicates zero documentary flags in supplied records, never a guarantee of legal safety. Paired with high-contrast traffic lights: Green (`Consistent`), Yellow (`Review Required`), Red (`Contradiction Found`).
- **Traditional Share Display (X1):** Converts exact fractional shares into traditional Bengali land accounting units (16 Ana = 1 Whole; 1 Ana = 20 Ganda; 1 Ganda = 4 Kora; 1 Kora = 3 Kranti; 1 Kranti = 20 Til) alongside exact rational fractions.
- **Offline Bangla Speech Synthesis (X2):** Browser-native speech announcement ("ফলাফল শুনুন") utilizing `window.speechSynthesis` (`bn-BD` / `bn-IN`) with graceful offline fallback if speech engines are unavailable.
- **Actionable Next-Step Guidance (X3):** 2–4 concrete, documentary verification steps for each rule in both Bangla and English (e.g., inspecting volume records at the Sub-Registry office, obtaining certified khatian copies from the AC Land office, consulting counsel).
- **USSD / Feature-Phone Simulator (X4):** Text-only feature-phone simulation accessible via demo code `*123*45#` (`POST /ussd`). Strictly enforces the 160-character GSM screen limit across multi-step session navigation (Language -> Mouza -> Dag -> Result).
- **Digital Vetting Certificate (X5):** Formal printable summary report featuring parcel details, three-status outcome, attention score, chain summary, canonical SHA-256 dataset hash, client-side QR verification link, timestamp placeholder, and advisory disclaimer.

---

## Quickstart & Installation

Requires Python 3.11 or newer. Node.js is optional (used for client-side badge formatting tests).

### Windows (PowerShell)

```powershell
git clone https://github.com/minhaz2000/LandTech
cd LandTech

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Run full regression suite
python -m pytest

# Start local server
python -m uvicorn jomigraph.api.app:create_app --factory --app-dir src --host 127.0.0.1 --port 8000
```

### Linux / macOS

```bash
git clone https://github.com/minhaz2000/LandTech
cd LandTech

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

# Run full regression suite
python -m pytest

# Start local server
python -m uvicorn jomigraph.api.app:create_app --factory --app-dir src --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` in any modern web browser.

---

## Running the Benchmark

JomiGraph AI includes a reproducible, deterministic benchmark endpoint:

```bash
curl http://127.0.0.1:8000/benchmark
```

### Executed Benchmark Results

- **Baseline Dataset (`data/demo_family.json`):**
  - Total Parcels: 30
  - Clean Parcels: 21 (0 false alarms; 0.0% false alarm rate)
  - Planted Cases: 7 (R1 to R7)
  - Planted Cases Detected: 7 of 7 (100.0% detection rate)
  - Simulation Integrity: Hash unchanged (`b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01`)
- **Extended v1.1 Dataset (`data/demo_v11.json`):**
  - Total Parcels: 18
  - Clean Parcels: 9
  - Planted Cases: 8 (R8 to R15)
  - Planted Cases Detected: 8 of 8 (100.0% detection rate: R8, R9, R10, R11, R12, R13, R14, R15)
  - Phase 10 Heir Declaration: Planted detected, Clean passed, Tricky clean passed
  - Phase 11 Features: Attention score, Voice, Next steps, USSD simulator, and Certificate verified
  - Simulation Integrity: Hash unchanged (`e336674f02ce50d5b79f635837981f82002f45d8c8b11701f93add8a3ec074b7`)

---

## Architecture & Important File Locations

```
LandTech/
├── src/jomigraph/
│   ├── config.py                 # Tolerance values and attention score weights
│   ├── models.py                 # Core domain models (Parcel, SurveyRecord, Event, Deed, Person)
│   ├── loader.py                 # JSON dataset parsing and validation
│   ├── i18n.py                   # Bilingual translation resolver
│   ├── traditional_share.py      # Ana-Ganda-Kora-Kranti-Til traditional share converter
│   ├── engine/
│   │   ├── rules.py              # Pure rule functions R1–R15 & shared dispatchers
│   │   ├── replay.py             # Chronological state replay engine
│   │   ├── simulate.py           # Pure counterfactual transfer simulation
│   │   ├── benchmark.py          # Benchmark runner and coverage reporter
│   │   ├── evidence.py           # Minimal evidence sets and impact closure
│   │   ├── scoring.py            # Attention score (0–100) computation
│   │   ├── deed_hash.py          # Canonical deed SHA-256 fingerprinting & QR payload
│   │   ├── next_steps.py         # Concrete 2–4 actionable steps per rule
│   │   └── ussd.py               # Feature-phone USSD session state machine
│   ├── api/
│   │   ├── app.py                # FastAPI routes and application factory
│   │   ├── schemas.py            # Pydantic request and response schemas
│   │   ├── extras.py             # Endpoints for deed verification, USSD, and assistant
│   │   └── graph.py              # Cytoscape graph serialization
│   └── ui/
│       ├── index.html            # Main web interface entry point
│       ├── app.js                # Frontend controllers and state management
│       ├── style.css             # Base stylesheet
│       ├── theme.css             # High-contrast accessible design tokens
│       ├── strings.json          # UI localized strings
│       └── vendor/               # Offline vendored third-party libraries
├── data/
│   ├── demo_family.json          # Primary baseline synthetic family dataset
│   ├── demo_v11.json             # Extended synthetic demonstration dataset (R8–R15)
│   ├── demo_regions.json         # Regional demo parcels across 8 divisions
│   └── bd_geo.json               # Divisions, districts, and upazilas metadata
├── locales/
│   ├── bn.json                   # Bengali alert messages and next steps
│   └── en.json                   # English alert messages and next steps
├── tests/                        # Full automated test suite (Pytest & Node)
├── docs/
│   ├── ANTIGRAVITY_PROMPT_JomiGraph_v1.1.md # Master specification
│   ├── NEW_FEATURES_EXPLAINED.md           # Plain-language guide and 15 judge Q&As
│   └── demo_script_v11.md                  # 90-second video walkthrough script
├── Dockerfile                    # Container configuration for local and cloud deployment
└── render.yaml                   # Infrastructure-as-code manifest for Render
```

---

## Limitations

- **Synthetic Records Only:** All datasets represent synthetic models designed to validate rule correctness under controlled test conditions. Real-world records exhibit physical handwriting variations, unrecorded oral partitions, and local registry customs not represented here.
- **Decision Support, Not Legal Adjudication:** JomiGraph AI does not give legal rulings, does not certify ownership, and does not prove fraud. It highlights documentary inconsistencies to assist human review.
- **No Document OCR or Signature Verification:** The system evaluates structured data. It cannot authenticate physical ink signatures, stamped paper watermarks, or detect physically altered deed documents without a pre-registered digital fingerprint.
- **Inheritance Law Boundary:** R8 evaluates whether declared heirs are consistently accounted for across subsequent documentation. It deliberately avoids calculating statutory or religious shares under Muslim Farayez or Hindu succession laws.
- **Demo Role Views:** Citizen and Reviewer modes are presentation views designed for demonstration and usability; they do not constitute role-based access control (RBAC) or cryptographic authentication.

---

## AI Tools Disclosure

- **Antigravity IDE** (with GSD workflows) served as the primary agentic pair-programming assistant for implementing rules, endpoints, and test suites.
- **Claude & Gemini Pro** models assisted in architectural planning, invariant verification, edge-case analysis, and drafting documentation.
- All rules, data models, domain constraints, and presentation flows were designed and verified against the hackathon problem specification.

**Team roles and AI disclosure.** The code (rules engine, API, UI, tests and demo datasets) was written by Al Mahmud, working with AI coding assistants (Antigravity with the GSD workflow, Claude and Gemini, as listed above). Minhaz handled deployment, the GitHub repository, the submission materials, the demo video and the pitch. Al Mahmud can explain the code in detail; Minhaz presents the problem, the features and how the rules work at a functional level.

---

## Third-Party Assets & Licences

All third-party libraries and assets are permissively licensed (MIT, BSD-3-Clause, or SIL OFL 1.1) and operate strictly offline:

| Library / Asset | Version / Location | Licence | Provenance / Purpose |
| :--- | :--- | :--- | :--- |
| **FastAPI** | `requirements.txt` | MIT | Python ASGI REST framework |
| **Uvicorn** | `requirements.txt` | BSD-3-Clause | Production ASGI web server |
| **Pydantic** | `requirements.txt` | MIT | Data validation and settings management |
| **pytest** | `requirements.txt` | MIT | Python test framework |
| **HTTPX** | `requirements.txt` | BSD-3-Clause | Test client for FastAPI endpoints |
| **Cytoscape.js** | 3.30.2 (`ui/vendor/cytoscape.min.js`) | MIT | Lineage graph visualization |
| **qrcode.js** | Kazuhiko Arase (`ui/vendor/qrcode.js`) | MIT | Client-side QR code generator |
| **Three.js** | r147 (`ui/vendor/three.min.js`) | MIT | 3D Cadastral canvas visualization |
| **OrbitControls** | Three.js (`ui/vendor/OrbitControls.js`) | MIT | 3D camera mouse and touch controls |
| **Noto Sans Bengali** | (`ui/vendor/fonts/`) | SIL OFL 1.1 | Localized typography for Bengali script |
| **bangladesh-districts-upazilas**| `data/bd_geo.json` | MIT | Division, district, and upazila names |

---

## Licence

MIT License. See `LICENSE` file for details.
