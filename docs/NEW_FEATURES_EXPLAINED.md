# JomiGraph AI v1.1 — New Features & Technical Walkthrough

> **LandTech 2026 Hackathon**  
> **Problem P3: Catch Fraud and Double-Selling**  
> **Target Audience**: Hackathon Judges, Land Administration Mentors, and Student Presenters

---

## 1. Overview of v1.1 Features

JomiGraph AI v1.1 extends the foundational consistency engine with practical, user-centric tools designed for real stakeholders in Bangladesh: rural citizens, urban flat buyers, commercial banks, Sub-Registry offices, AC Land offices, and land courts.

### 1.1 Extended Rule Set (R8–R15)

1. **R8: Unaccounted Heir Declaration Consistency (Phase 10)**
   - *Problem*: In rural inheritance transfers, female heirs or minor children are frequently omitted from subsequent khatians or partitioned deeds without their knowledge or consent.
   - *How it works*: Inspects recorded heir declarations (`heir_declaration` on a parcel history). When a subsequent khatian or sale deed omits a declared heir without a registered deed of release (না-দাবি দলিল), gift (হেবা), or sale executed by that heir, the system alerts the reviewer.
   - *Status*: Returns `Contradiction Found` if the declaration is marked complete and subsequent records omit the heir; returns `Review Required` if dates or documentary chains are incomplete.

2. **R9: Active Mortgage Encumbrance at Sale**
   - *Problem*: Mortgaged land is sold to unsuspecting buyers, or the same plot is pledged to a second bank before releasing the first lien.
   - *How it works*: Tracks `MORTGAGE` and `MORTGAGE_RELEASE` event sequences per identified holding or portion. A sale executed while a mortgage remains unreleased triggers an immediate alert. Replay models mortgages as non-transferring encumbrances (they do not alter ownership area).
   - *Status*: Returns `Contradiction Found` for active mortgages or duplicate unreleased pledges; `Review Required` if release dates are missing.

3. **R10: Power of Attorney (POA) Authority & Revocation**
   - *Problem*: In urban developments, apartments or plots are sold by developer agents using expired, revoked, or non-existent Power of Attorney deeds.
   - *How it works*: Event types `POA_GRANT` and `POA_REVOKE` track agent authority. Any sale executed via an agent (`via_poa_id`) must have a corresponding grant from the recorded owner covering that parcel, with no revocation dated prior to the sale.
   - *Status*: Returns `Contradiction Found` if the grant is missing or was revoked before the sale date; `Review Required` if scope or dates are ambiguous.

4. **R11: Government & Court Locks**
   - *Problem*: Transactions are executed on government khas land, property slated for public acquisition, or land under active court injunctions.
   - *How it works*: Parcels carry metadata flags (`is_khas`, `under_acquisition`, `flag_date`, `court_case_no`, `injunction`). Transfers dated after a khas or acquisition flag trigger a contradiction. Pending cases or injunctions flag the transaction for administrative review.
   - *UI Representation*: Locked parcels receive high-contrast visual indicators in the 3D map and Cytoscape lineage graph, and transaction inputs are blocked.

5. **R12: Canonical Deed Fingerprint & Client-Side QR Verification**
   - *Problem*: Altered, counterfeit, or forged paper copies of deeds are presented to buyers with manipulated acreage or fictitious party names.
   - *How it works*: Pre-computes a canonical SHA-256 fingerprint over registered deed fields (`deed_no`, `registration_date`, `parcel_id`, `seller`, `buyer`, `area`) using deterministic key sorting. The endpoint `POST /verify-deed` recomputes the fingerprint from presented fields and compares it against registry records.
   - *Client-Side QR*: Generates an offline QR code containing a relative link (`#/verify-deed?deed_no=...&hash=...`) using locally vendored `qrcode.js`.

6. **R13: Reused Deed Volume Numbers**
   - *Problem*: Fictitious deed numbers copied from unrelated registry volumes are recycled onto bogus plots.
   - *How it works*: Scans across all parcels in the repository. If the same `deed_no` appears with differing registration dates, parties, or areas, the system flags it.
   - *Status*: Returns `Review Required` only—never `Contradiction Found`, because in legitimate Bangladesh registry practice, a single deed may legitimately encompass multiple distinct dags.

7. **R14: Dummy Identity Disambiguation**
   - *Problem*: Individuals sharing common names (e.g., "Abdul Alim" or "Mohammad Ali") are accidentally or deceptively fused in ownership registries.
   - *How it works*: Associates an explicit synthetic identifier (`DUMMY-ID-0001`) with each person. Identical names with differing dummy IDs are treated as strictly distinct individuals across search, graph, and lineage. Duplicate occurrences of a name lacking disambiguating identifiers trigger `Review Required`.

8. **R15: Physical Boundary Duplicate Sale (Sub-Dag / Cadastral Descriptors)**
   - *Problem*: Sellers circumvent sub-plot label checks by selling the identical physical land under newly invented sub-plot numbers or vague descriptions.
   - *How it works*: Inspects structured boundary descriptors (North, South, East, West boundaries and sub-dag identifiers like `101/1-ka`). If two uncancelled transfers allocate the identical physical boundary descriptors or one spatial boundary encloses another, the engine triggers an alert.

---

### 1.2 Decision Support & User Experience Enhancements (Phase 11)

1. **Deterministic Attention Score (0–100) & High-Contrast Traffic Light (F18)**
   - Computes an integer score from active alerts using calibrated weights in `config.py` (Contradictions carry higher weight than Reviews; Clean parcels strictly score 0).
   - High-contrast visual cues: Green (`Consistent`), Yellow (`Review Required`), Red (`Contradiction Found`).
   - Accompanied by mandatory disclaimer: *"A score of 0 means no flags were found in the supplied records; it is not a guarantee about the land."*

2. **Traditional Bengali Land Share Display (X1)**
   - Translates exact fractional shares into traditional Bengali cadastral units (16 Ana = 1 Whole; 1 Ana = 20 Ganda; 1 Ganda = 4 Kora; 1 Kora = 3 Kranti; 1 Kranti = 20 Til).
   - Displays traditional units alongside exact mathematical fractions (`fractions.Fraction`) to facilitate communication between village elders, revenue officers, and young buyers.

3. **Offline Native Bangla Speech Synthesis (X2)**
   - Enables audio playback ("ফলাফল শুনুন") of evaluation outcomes using browser-native `window.speechSynthesis`.
   - Feature-detects Bengali voice models (`bn-BD` / `bn-IN`) with graceful offline fallback banners if device voice packages are missing. Uses plain, citizen-safe translated phrasing.

4. **Concrete Actionable Next Steps (X3)**
   - Provides 2–4 concrete documentary checks for every rule in English and Bengali (e.g., requesting original registry volume inspections, verifying mutation porcha receipts, consulting revenue officers).
   - Explicitly framed as preliminary documentary verification checks, not formal legal advice.

5. **USSD / Feature-Phone Simulator (X4)**
   - Dialing invented code `*123*45#` launches a text-only phone simulator in the browser.
   - Emulates feature-phone access for rural citizens without smartphones, strictly enforcing the 160-character GSM limit across all navigation menus (Language -> Mouza -> Dag -> Result).

6. **Digital Vetting Certificate (X5)**
   - One-page printable summary featuring parcel metadata, three-status result, attention score, transaction timeline, SHA-256 evaluation fingerprint, verification QR code, and standard advisory disclaimer.

---

## 2. Fifteen Likely Judge Questions & Technically Accurate Answers

Suitable for the two student presenters:

### Q1: How does your rule dispatch architecture work?
> **Answer**: We extracted a single, unified dispatcher in `src/jomigraph/engine/rules.py` (`dispatch_history_rules` and `dispatch_event_rules`). Both baseline evaluation (`evaluate_history()`) and the counterfactual simulation lab (`simulate()`) use this exact same dispatch pipeline. This guarantees zero discrepancy between historical audits and simulated transactions.

### Q2: How does the simulation lab test a proposed sale without altering real data?
> **Answer**: `simulate()` is a pure, side-effect-free function. It receives the historical event list, appends the proposed transfer, and replays state in memory without mutating stored records. We mathematically prove immutability by computing a canonical SHA-256 hash of all dataset events and survey records before and after simulation; the hash remains strictly identical.

### Q3: What do your three statuses mean, and why don't you use words like "fraud" or "legal"?
> **Answer**: We output strictly three statuses: `Consistent with supplied records`, `Contradiction Found`, and `Review Required`. We never output words like "fraud", "forged", or "legally valid" because our software is a technical decision-support tool, not a judicial court. A mathematical conflict demonstrates inconsistent documentation, not criminal intent.

### Q4: How do you verify dataset integrity and baseline immutability?
> **Answer**: We use deterministic JSON canonicalization (sorted keys, compact separators) and SHA-256 cryptographic hashing in `src/jomigraph/engine/simulate.py`. Our baseline dataset (`data/demo_family.json`) has a fixed hash (`b4e585a484a4394e81cf32c5687836807f8ad2ea9dfc0c4d39c845dcfd632b01`) that is verified on every test execution.

### Q5: How do you prevent internal rule IDs and raw evidence from leaking to citizens?
> **Answer**: We maintain strict role separation in our API schemas (`CitizenParcelDetailResponse`, `CitizenSimulateResponse`, `CitizenReportResponse`). The citizen response model completely excludes fields like `rule_id`, `calculation`, `evidence_ids`, and `minimal_evidence_sets`. Automated tests in `test_phase11_decision_and_ux.py` assert that none of these keys appear in citizen payloads.

### Q6: Where did this data come from, and does it represent real people or land?
> **Answer**: 100% of our data is synthetic. It is generated deterministically using fixed random seeds in `data/generator.py` and `data/generator_v11.py`. All names, parcel IDs, and case numbers (`DEMO-CASE-0011`, `DUMMY-ID-0001`) are entirely fictional. We do not scrape, store, or process any real Bangladesh citizen NIDs or confidential registry data.

### Q7: Is your Attention Score a machine learning prediction or probability of fraud?
> **Answer**: No. It is an explainable, deterministic integer score (0–100) calculated from active rule alerts using transparent weights in `config.py`. It is not a probability and uses no black-box machine learning. A score of 0 simply means no flags were found in the supplied records.

### Q8: Does Rule R8 calculate Islamic Farayez or statutory inheritance shares?
> **Answer**: No. Religious and statutory inheritance share calculation is an explicit non-goal. Succession shares under Islamic Farayez or the Hindu Succession Act depend on intricate family trees and legal interpretation. R8 only checks consistency: if a deceased owner has a recorded heir declaration, it verifies that every declared heir is accounted for in subsequent khatians or deeds.

### Q9: Does the deed QR code connect to a government database or blockchain?
> **Answer**: No. The QR code contains an offline relative link containing the deed number and the first 16 hexadecimal characters of its canonical SHA-256 fingerprint. It is generated entirely client-side using locally vendored `qrcode.js`. Clicking or scanning it opens the local `/verify-deed` interface.

### Q10: Does the USSD simulator connect to a live telecom operator?
> **Answer**: No. It is a browser-based state machine simulation (`src/jomigraph/engine/ussd.py`) demonstrating how feature-phone users can navigate records using text-only inputs (`*123*45#`). It strictly enforces the 160-character GSM limit on every screen to prove feasibility on 2G mobile networks.

### Q11: Can JomiGraph AI run in an offline, air-gapped Upazila land office?
> **Answer**: Yes. JomiGraph AI has zero external network calls at runtime. All stylesheets, fonts (Noto Sans Bengali), and JavaScript libraries (Three.js, Cytoscape.js, qrcode.js) are vendored locally. The entire application runs self-contained inside a standard Docker container.

### Q12: How does minimal evidence set generation work?
> **Answer**: When a contradiction is found, `src/jomigraph/engine/evidence.py` computes the smallest subset of records necessary to reproduce the alert. It explores candidate combinations up to a bounded limit of 12 records; if the history exceeds that limit, it flags the result as `not_minimized` to ensure predictable runtime.

### Q13: Why do you strictly enforce `fractions.Fraction` instead of standard floating-point numbers?
> **Answer**: In Bangladesh land records, shares are registered as fractional parts (e.g., 1/3, 5/16). Standard IEEE floating-point arithmetic produces precision errors (such as `0.3333333333333333`), which cause false-alarm alerts on legitimate land partitions. Exact rational fractions eliminate rounding errors entirely.

### Q14: What can JomiGraph AI NOT prove or detect?
> **Answer**: JomiGraph AI evaluates structured record consistency. It cannot detect a physical forged signature on paper, cannot verify wet-ink stamps, and cannot verify whether an unrecorded verbal partition took place. It is a decision-support filter that flags documentary conflicts for human investigation.

### Q15: How does this help real citizens and land officials in LandTech 2026?
> **Answer**: In Bangladesh, over 70% of civil litigation stems from land disputes, primarily double-selling and unrecorded co-owner claims. By providing instant, bilingual preliminary consistency checks before registration, JomiGraph AI empowers buyers and registry officials to catch documentary conflicts early.
