# JomiGraph AI (জমিগ্রাফ এআই)

> **Rule-Based Land Record Continuity & Verification Engine**  
> *Decision-support prototype for a Bangladesh land-technology hackathon.*  
> *Developed using synthetic, invented data. Not a legal ruling; does not certify legal ownership or prove fraud.*

---

## Overview

**JomiGraph AI** is a pure-function, rule-based verification and counterfactual simulation engine designed to evaluate land record continuity across historical surveys (CS, SA, RS, BS) and private deed transactions in Bangladesh.

The engine replays land-record events chronologically, evaluates them against 7 explicit land continuity rules (R1–R7), isolates minimal conflicting evidence sets, maps downstream transaction impacts, and enables interactive "what-if" transaction simulations without ever altering baseline data.

### Key Capabilities
- **Dual Perspective UI**:
  - **Citizen View (নাগরিক)**: Plain-language status, recommended next steps, and clean ownership timeline. Technical internals (rule IDs, calculations, evidence sets, entity IDs) are strictly omitted.
  - **Reviewer View (পর্যালোচক)**: Complete audit trail, rule IDs, exact arithmetic calculations, minimal evidence sets (with unminimized warnings), interactive Cytoscape.js lineage graph, and downstream impact tracking.
- **Counterfactual Simulation Lab**: Pure-function transaction simulation with SHA-256 database hash verification before and after every run.
- **Bilingual by Design**: Full Bangla (বাংলা) default with complete English toggle across all labels, alerts, next steps, and reports.
- **Printable Case Reports**: Single-page A4 print stylesheet formatting audit findings, timeline tables, legal disclaimers, and canonical hashes.

---

## Verified Quickstart

Follow these exact verified steps to set up and run JomiGraph AI.

### Prerequisites
- **Python >= 3.11** installed on your system.
- *(Optional)* **Node.js**: Only required if running the supplementary badge formatting unit test; tests automatically skip if Node.js is absent.

---

### Windows (PowerShell)

```powershell
# 1. Open PowerShell and navigate to the project root
cd d:\hackathon\LandTech

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# (Optional: install the package in editable mode)
# pip install -e .

# 5. Run the test suite
python -m pytest

# 6. Start the application server
python -m uvicorn jomigraph.api.app:create_app --factory --app-dir src --host 127.0.0.1 --port 8000

# 7. Open in your browser
# Navigate to: http://127.0.0.1:8000
```

---

### Linux / macOS (bash / zsh)

```bash
# 1. Open a terminal and navigate to the project directory
cd LandTech

# 2. Create a virtual environment
python3 -m venv .venv

# 3. Activate the virtual environment
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# (Optional: install the package in editable mode)
# pip install -e .

# 5. Run the test suite
python -m pytest

# 6. Start the application server
python -m uvicorn jomigraph.api.app:create_app --factory --app-dir src --host 127.0.0.1 --port 8000

# 7. Open in your browser
# Navigate to: http://127.0.0.1:8000
```

---

## System Architecture

```
LandTech/
├── src/jomigraph/
│   ├── models.py          # Person, Parcel, SurveyRecord, Deed, Event models (exact Fraction area)
│   ├── config.py          # Named Fraction constants (e.g., R4_TOLERANCE = 1/2 decimal)
│   ├── loader.py          # Dataset deserialization & canonical dataset hashing
│   ├── i18n.py            # Bilingual dictionary and string translation helpers
│   ├── engine/
│   │   ├── replay.py      # Chronological event replay & share balance calculation
│   │   ├── rules.py       # Core evaluation rules (R1 to R7)
│   │   ├── simulate.py    # Counterfactual simulation engine (pure function)
│   │   ├── evidence.py    # Minimal evidence set isolation & downstream impact closure
│   │   └── benchmark.py   # Dataset benchmark metrics & coverage table
│   ├── api/
│   │   ├── app.py         # FastAPI application factory & REST endpoints
│   │   ├── schemas.py     # Pydantic request/response validation schemas
│   │   └── graph.py       # Cytoscape.js graph serialization
│   └── ui/                # Plain HTML, CSS & Vanilla JavaScript frontend
│       ├── index.html     # Application shell
│       ├── app.js         # Single-page application router and view renderers
│       ├── style.css      # Design system, accessible components, and @media print
│       └── strings.json   # Bilingual UI string dictionary
├── data/                  # Synthetic land record datasets
├── tests/                 # Automated test suite (141 tests)
├── pyproject.toml         # PEP 517/660 build configuration (setuptools.build_meta)
├── requirements.txt       # Direct pinned dependencies
└── README.md              # Project documentation
```

---

## Core Rules & Status Hierarchy

### The Three Statuses
1. **Consistent with supplied records (সঙ্গতিপূর্ণ)**: All modeled continuity checks pass based on the records provided. *Never claims "legal", "valid", or "safe".*
2. **Contradiction Found (অসঙ্গতি পাওয়া গেছে)**: Relevant records explicitly violate a modeled mathematical constraint (e.g., over-transfer, duplicate portion sale, chronological inversion).
3. **Review Required (পর্যালোচনা প্রয়োজন)**: Inputs are missing, records are ambiguous, surveys lack linkage, or author-declared baseline is incomplete.

### Rule Definitions
- **R1 — Excess Transfer**: Flags over-transfers where an owner attempts to convey more share than recorded. Returns *Contradiction Found* if baseline is complete; returns *Review Required* if history is incomplete or dates are missing.
- **R2 — Duplicate Allocation**: Detects double-sale of identical physical portions (`portion_id`) through chain of title. Never triggers on deed numbers alone; respects cancellations and corrections.
- **R3 — Seller's Recorded Interest**: Verifies whether the transferor held recorded interest prior to a transaction. Returns *Contradiction Found* when baseline is complete and records disprove interest.
- **R4 — Subdivision Reconciliation**: Verifies that child parcels reconcile with parent parcel area. Exact match passes; discrepancy within tolerance (`1/2` decimal) returns *Review Required*; discrepancy exceeding tolerance returns *Contradiction Found*.
- **R5 — Survey Continuity**: Verifies link between successive surveys (e.g., CS ➔ SA ➔ RS ➔ BS). Missing link returns *Review Required* (never *Contradiction*).
- **R6 — Deed-Mutation Reconciliation**: Checks that mutation records reconcile with their underlying transfer deeds. Discrepancies return *Review Required*.
- **R7 — Chronological Consistency**: Detects temporal inversions (e.g., mutation registered before deed date). Returns *Contradiction Found* only when both dates and explicit link are present; otherwise returns *Review Required*.

### Evaluation Protocol
Every rule follows strict hierarchical evaluation:
1. Validate required inputs: missing, ambiguous, or undated records immediately yield **Review Required**.
2. Apply rule logic and baseline completeness: author-declared assumptions **never** override missing evidence.

---

## Simulation Invariance & Minimal Evidence

### Purity & Integrity Guarantee
Simulation runs through `simulate(events, proposed_event, history, deeds)`:
- Evaluates the proposed event on a new copy `events + [proposed]`.
- Baseline stored dataset is **never mutated** in memory or on disk.
- Canonical serialization hash before and after simulation must be identical:
  $$\text{hash}_{\text{before}} \equiv \text{hash}_{\text{after}}$$

### Minimal Evidence Sets
When a contradiction occurs, JomiGraph AI isolates the minimal set of records necessary and sufficient to reproduce the finding:
- Iteratively removes candidate records and re-evaluates the rule.
- If removing a record resolves the contradiction, that record is critical.
- Returns all alternative minimal sets (e.g., in multi-deed conflicts).
- Flags `not_minimized = true` if search reaches computation bounds.

---

## Assumptions & Limitations (Honest Disclosure)

1. **Synthetic Data Only**: All parcels, khatians, dags, deeds, and persons are completely invented. Names and identifiers do not correspond to any real individuals or properties.
2. **Decision-Support Prototype**: JomiGraph AI does not replace the sub-registry or AC Land office, does not issue legal rulings, and never certifies legal title.
3. **Exact Fraction Arithmetic**: All areas and shares use Python `fractions.Fraction`. Floating-point arithmetic is strictly forbidden to eliminate rounding errors.
4. **Inheritance Out of Scope**: Complex Muslim or Hindu inheritance partition calculations are out of scope. Undocumented inheritance transitions return *Review Required*.
5. **No External APIs / No ML / No Blockchain**: Operates entirely as a deterministic, explainable, self-contained system without external dependencies or black-box models.

---

## License

MIT License. Designed and built for academic and demonstration purposes.
