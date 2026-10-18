# JomiGraph AI v1.1 — 90-Second Demo Video Script

> **LandTech 2026 Hackathon (Problem P3: Catch Fraud and Double-Selling)**  
> **Duration**: Exactly 90 Seconds  
> **Presenters**: Two Student Presenters (Presenter 1: Tahsin, Presenter 2: Rafiq)  
> **Setup**: Local application running at `http://127.0.0.1:8000` with seeded demonstration dataset.

---

## Timing & Action Overview

| Timestamp | Duration | Scene / Action | Speaker | Key On-Screen Element |
| :--- | :--- | :--- | :--- | :--- |
| **0:00 – 0:15** | 15s | Intro & Problem Context | Presenter 1 | Header, disclaimer banner, role selection |
| **0:15 – 0:30** | 15s | Clean Parcel Demonstration | Presenter 2 | `PARCEL_STORY_01`, Attention score 0, Voice |
| **0:30 – 0:50** | 20s | Planted Contradiction & Evidence | Presenter 1 | `PARCEL_PLANTED_R1`, Reviewer mode, Cytoscape graph |
| **0:50 – 1:10** | 20s | Counterfactual Simulation Lab | Presenter 2 | `PARCEL_LAB_DEMO`, area input, hash immutability |
| **1:10 – 1:25** | 15s | Decision Support & Certificate | Presenter 1 | Digital Vetting Certificate, QR, USSD simulator |
| **1:25 – 1:30** | 5s | Advisory Disclaimer & Wrap-up | Both | Footer advisory disclaimer |

---

## Detailed Script & Cues

### Scene 1: Introduction & Problem Context (0:00 – 0:15)
- **Visual Action**: Camera shows browser on `http://127.0.0.1:8000#/`. Top disclaimer banner is visible: `ডেমো, কাল্পনিক তথ্য, আইনি সিদ্ধান্ত নয়`. Presenter 1 clicks **Citizen (নাগরিক)** role button.
- **Presenter 1 (Tahsin)**:  
  *"Assalamu Alaikum! In Bangladesh, over seventy percent of land disputes originate from fraudulent double-selling and hidden co-owner encumbrances. For LandTech 2026 Problem P3, we built JomiGraph AI—a 100% offline, rule-based decision support engine that mathematically replays record histories to catch documentary contradictions before registration. All demonstration records here are synthetic."*

---

### Scene 2: Clean Parcel & Phase 11 Citizen Experience (0:15 – 0:30)
- **Visual Action**: Presenter 2 clicks `PARCEL_STORY_01` (Dhanmondi, Dag 101). The screen renders the green badge `সরবরাহকৃত রেকর্ডের সাথে সামঞ্জস্যপূর্ণ`, Attention Score `0` with a green traffic light, and the ownership timeline across CS, SA, RS, and BS surveys. Presenter 2 clicks the voice button `🔊 ফলাফল শুনুন`.
- **Presenter 2 (Rafiq)**:  
  *"Here in Citizen view, we open Dag 101. The record history spans four generations—CS, SA, RS, and BS. The engine gives a green status: Consistent with supplied records. Notice our Phase 11 Attention Score: zero points. For rural citizens, clicking 'ফলাফল শুনুন' triggers native offline speech synthesis, reading the status and recommended verification steps aloud."*
- **Audio Output (Browser)**:  
  *(Synthetic Bengali voice)*: *"সরবরাহকৃত রেকর্ডের সাথে সামঞ্জস্যপূর্ণ। মনোযোগ স্কোর শূন্য।"*

---

### Scene 3: Planted Contradiction, Rule Dispatch & Evidence (0:30 – 0:50)
- **Visual Action**: Presenter 1 toggles role switcher to **Reviewer (পর্যালোচক)** and navigates to `PARCEL_PLANTED_R1` (Mirpur, Dag 301). The screen displays high-contrast Red badge `রেকর্ডে অসঙ্গতি পাওয়া গেছে`, Attention Score `85`, Rule `[R1: Excess Transfer]`, the calculation `requested 15, available 10, excess 5`, the minimal evidence set `(E_PLANTED_R1_1, SR_PLANTED_R1_CS)`, and the interactive Cytoscape lineage graph showing affected downstream resale `E_PLANTED_R1_2`.
- **Presenter 1 (Tahsin)**:  
  *"Now we switch to Reviewer view and inspect planted parcel 301. The seller held 10 decimals, but registered a sale for 15 decimals. Rule R1 immediately flags a Contradiction! Unlike a black-box AI, JomiGraph AI isolates the minimal evidence set that proves the conflict, and highlights downstream resales that are mathematically compromised."*

---

### Scene 4: Pure Counterfactual Simulation Lab (0:50 – 1:10)
- **Visual Action**: Presenter 2 navigates to `PARCEL_LAB_DEMO` (Dhanmondi, Dag 401). Scrolls to the **সিমুলেশন ল্যাব (Simulation Lab)**. Enters `3` in the area box and clicks **হস্তান্তর যাচাই করুন (Simulate Transfer)** -> Green Consistent. Then changes area to `5` and clicks again -> Red Contradiction Found (`excess 2`). Points to the invariant dataset hash badge: `b4e585a4...`.
- **Presenter 2 (Rafiq)**:  
  *"Before signing a deed, a buyer can test proposed sales in our Simulation Lab. Tareq Mahmud has 3 decimals remaining. Typing 3 gives a green light. Typing 5 catches an excess transfer of 2 decimals before money changes hands! Crucially, this simulation is pure: the baseline SHA-256 dataset hash before and after simulation remains strictly identical."*

---

### Scene 5: Decision Support, Certificate & USSD Simulator (1:10 – 1:25)
- **Visual Action**: Presenter 1 clicks **ডিজিটাল ভ্যাটিং সার্টিফিকেট (Digital Vetting Certificate)**. A clean printable certificate modal opens with parcel details, attention score, chain summary, evaluation hash, and client-side QR code. Presenter 1 closes modal, clicks the phone frame simulator in the navbar (`*123*45#`), and presses `1` -> `Dhanmondi` -> `101` -> displays 120-character summary screen.
- **Presenter 1 (Tahsin)**:  
  *"For institutional due diligence, one click generates a printable Digital Vetting Certificate with a client-side QR code linking to our local verification endpoint. And for rural citizens with basic 2G feature phones, our USSD simulator dials `*123*45#`, providing step-by-step guidance within strict 160-character screens."*

---

### Scene 6: Concluding Advisory Disclaimer & Sign-off (1:25 – 1:30)
- **Visual Action**: Camera zooms slightly out to show the full responsive application and footer disclaimer. Both presenters on screen.
- **Presenter 2 (Rafiq)**:  
  *"JomiGraph AI does not replace courts or issue legal rulings; it provides transparent, mathematical decision support to stop land conflicts before they start."*
- **Both Presenters**:  
  *"Thank you!"*

---

## Presenter Checklist Before Recording

1. **Local Server**: Running on `http://127.0.0.1:8000` via:
   ```powershell
   python -m uvicorn jomigraph.api.app:create_app --factory --app-dir src --host 127.0.0.1 --port 8000
   ```
2. **Audio Check**: Ensure system volume is enabled so browser speech synthesis can be captured by the recording microphone.
3. **Screen Resolution**: Set display scaling to 100% or 125% at 1080p for crisp text readability.
4. **Browser Zoom**: Set browser zoom to 100% and test both desktop and mobile viewports.
5. **Fixture Verification**: Verify that `PARCEL_STORY_01`, `PARCEL_PLANTED_R1`, and `PARCEL_LAB_DEMO` appear in the parcel listing.
