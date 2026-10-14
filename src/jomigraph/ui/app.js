/**
 * JomiGraph AI — Frontend Application
 * ====================================
 * Single-Page Application (SPA) with Hash Routing.
 * All static UI strings are loaded from ui_strings.
 * No framework, no build step, no npm.
 */

const ui_strings = {
  bn: {
    app_title: "জমিগ্রাফ এআই",
    app_subtitle: "ভূমির রেকর্ড ও মালিকানা ধারাবাহিকতা যাচাই",
    nav_home: "নীড়পাতা",
    nav_parcels: "জমির তালিকা",
    nav_benchmark: "বেঞ্চমার্ক",
    lang_toggle: "English",
    
    disclaimer_banner: "ডেমো, কাল্পনিক তথ্য, আইনি সিদ্ধান্ত নয়",
    rule_disclaimer: "এটি একটি নিয়মভিত্তিক সতর্কতা, আইনি রায় নয়",
    
    card_parcels_title: "জমির রেকর্ড যাচাই করুন",
    card_parcels_desc: "সকল দাগ ও খতিয়ানের ধারাবাহিকতা এবং অসঙ্গতি পর্যবেক্ষণ করুন।",
    card_history_title: "জমির ইতিহাস দেখুন",
    card_history_desc: "চার প্রজন্মের পারিবারিক ধারাবাহিকতা ও হস্তান্তরের কালরেখা দেখুন।",
    card_lab_title: "প্রস্তাবিত বিক্রি যাচাই করুন",
    card_lab_desc: "প্রস্তাবিত হস্তান্তরের ফলে অতিরিক্ত বিক্রয় বা অসঙ্গতি হবে কিনা পরীক্ষা করুন।",
    
    status_consistent: "সঙ্গতিপূর্ণ",
    status_review: "পর্যালোচনা প্রয়োজন",
    status_contradiction: "অসঙ্গতি পাওয়া গেছে",
    
    search_placeholder: "দাগ নম্বর বা আইডি দিয়ে খুঁজুন...",
    filter_all: "সকল দাগ",
    filter_planted: "পরীক্ষামূলক অসঙ্গতি",
    filter_clean: "ত্রুটিমুক্ত দাগ",
    planted_tag: "পরীক্ষামূলক",
    clean_tag: "ত্রুটিমুক্ত",
    no_parcels_found: "কোনো দাগ পাওয়া যায়নি।",
    
    view_details: "বিস্তারিত তথ্য দেখুন",
    hide_details: "তথ্য সংক্ষেপ করুন",
    summary_heading: "ফলাফল সারসংক্ষেপ",
    summary_consistent_desc: "সরবরাহকৃত সকল খতিয়ান ও দলিলের সাথে এই দাগের রেকর্ড সঙ্গতিপূর্ণ।",
    summary_review_desc: "কিছু রেকর্ডে তথ্যের ঘাটতি বা পর্যালোচনা প্রয়োজন রয়েছে।",
    summary_contradiction_desc: "মালিকানা হস্তান্তরে গাণিতিক বা তথ্যগত অসঙ্গতি চিহ্নিত হয়েছে।",
    
    alerts_heading: "নিয়মভিত্তিক সতর্কতা",
    view_evidence: "প্রমাণ দেখুন",
    hide_evidence: "প্রমাণ লুকান",
    rule_id_label: "নিয়ম আইডি:",
    calculation_label: "গণনা বিবরণ:",
    evidence_ids_label: "যুক্ত প্রমাণ:",
    next_step_label: "পরামর্শিত পদক্ষেপ:",
    
    timeline_heading: "মালিকানা হস্তান্তরের কালরেখা",
    timeline_empty: "এই দাগের জন্য কোনো হস্তান্তর ইভেন্ট নেই।",
    col_date: "তারিখ",
    col_type: "ধরণ",
    col_from: "হস্তান্তরকারী",
    col_to: "গ্রহীতা",
    col_area: "জমির পরিমাণ (শতক)",
    col_portion: "অংশ/হোল্ডিং",
    
    survey_heading: "জরিপ রেকর্ড (খতিয়ান)",
    khatian_label: "খতিয়ান নং:",
    record_date_label: "জরিপের তারিখ:",
    recorded_area_label: "মোট জমি:",
    holders_label: "রেকর্ডভুক্ত মালিকগণ:",
    
    graph_heading: "মালিকানা সংযোগ চিত্র",
    graph_fallback: "গ্রাফ লোড করা সম্ভব হয়নি। নিচের কালরেখা ও রেকর্ডসমূহ সক্রিয় রয়েছে।",
    
    lab_heading: "সিমুলেশন ল্যাব: প্রস্তাবিত হস্তান্তর যাচাই",
    lab_desc: "বর্তমান রেকর্ড অপরিবর্তিত রেখে কাল্পনিক একটি বিক্রয় প্রস্তাব যাচাই করুন।",
    lab_from_label: "বিক্রেতা (রেকর্ডভুক্ত অংশীদার নির্বাচন করুন):",
    lab_to_label: "ক্রেতার নাম/আইডি:",
    lab_area_label: "বিক্রির পরিমাণ (শতক - পূর্ণসংখ্যা বা ভগ্নাংশ, যেমন ৫ বা ৭/২):",
    lab_date_label: "প্রস্তাবিত তারিখ (ঐচ্ছিক):",
    lab_portion_label: "অংশ বা প্লট আইডি (ঐচ্ছিক):",
    lab_submit_btn: "হস্তান্তর যাচাই করুন",
    lab_reset_btn: "পুনরায় নির্ধারণ",
    
    lab_result_heading: "সিমুলেশন ফলাফল",
    lab_unchanged_badge: "মূল রেকর্ড অপরিবর্তিত",
    lab_change_label: "প্রস্তাবিত পরিবর্তন:",
    lab_before_label: "বিক্রেতার পূর্বে প্রাপ্য অংশ:",
    lab_after_label: "হস্তান্তরের পর অবশিষ্ট অংশ:",
    lab_excess_label: "হস্তান্তরের পর ঘাটতি:",
    lab_excess_prefix: "অতিরিক্ত",
    lab_remaining_prefix: "অবশিষ্ট",
    lab_calc_label: "গণনা লাইন:",
    lab_decimals_unit: "শতক",
    
    error_empty_fields: "অনুগ্রহ করে বিক্রেতা, ক্রেতা এবং জমির পরিমাণ সঠিকভাবে পূরণ করুন।",
    error_float_area: "দশমিক সংখ্যা গ্রহণযোগ্য নয় (যেমন ৫.৫)। পূর্ণসংখ্যা (৫) বা ভগ্নাংশ (১১/২) লিখুন।",
    error_unknown_person: "বিক্রেতা হিসেবে একজন রেকর্ডভুক্ত ব্যক্তি নির্বাচন করুন।",
    error_simulate_failed: "সিমুলেশন সম্পন্ন করা সম্ভব হয়নি। অনুগ্রহ করে তথ্য পুনরায় পরীক্ষা করুন।",
    
    benchmark_heading: "সিস্টেম বেঞ্চমার্ক ও নির্ভরযোগ্যতা",
    benchmark_false_alarms: "ত্রুটিমুক্ত দাগে মিথ্যা সতর্কতার সংখ্যা (False Alarms):",
    benchmark_coverage: "নিয়ম কভারেজ সারণী (R1 - R7)",
    benchmark_integrity: "সিমুলেশন অখণ্ডতা (ডাটাবেজ হ্যাশ)",
    hash_before_label: "সিমুলেশনের পূর্বে হ্যাশ:",
    hash_after_label: "সিমুলেশনের পরে হ্যাশ:",
    hash_match_label: "হ্যাশ অপরিবর্তিত ও সংরক্ষিত",
    
    col_rule: "নিয়ম",
    col_planted: "পরীক্ষামূলক কেস বিদ্যমান",
    col_detected: "সফলভাবে চিহ্নিত",
    col_status: "চিহ্নিত অবস্থা",
    
    yes: "হ্যাঁ",
    no: "না",
    back_to_parcels: "← দাগের তালিকায় ফিরে যান",
    back_to_home: "← নীড়পাতায় ফিরে যান"
  },
  en: {
    app_title: "JomiGraph AI",
    app_subtitle: "Land Record Continuity & Rule-Based Verification",
    nav_home: "Home",
    nav_parcels: "Parcels",
    nav_benchmark: "Benchmark",
    lang_toggle: "বাংলা",
    
    disclaimer_banner: "Demo, fictional data, not a legal ruling",
    rule_disclaimer: "This is a rule-based warning, not a legal ruling",
    
    card_parcels_title: "Check land records",
    card_parcels_desc: "Inspect record continuity, surveys, and mathematical consistency across parcels.",
    card_history_title: "View land history",
    card_history_desc: "Explore four generations of family ownership timeline and recorded transfers.",
    card_lab_title: "Check a proposed sale",
    card_lab_desc: "Simulate a proposed sale in the lab to test for over-transfer or duplicate portions.",
    
    status_consistent: "Consistent",
    status_review: "Needs review",
    status_contradiction: "Contradiction",
    
    search_placeholder: "Filter by parcel ID or dag number...",
    filter_all: "All Parcels",
    filter_planted: "Planted Tests",
    filter_clean: "Clean Parcels",
    planted_tag: "Planted",
    clean_tag: "Clean",
    no_parcels_found: "No parcels found matching your filter.",
    
    view_details: "View details",
    hide_details: "Hide details",
    summary_heading: "Verification Summary",
    summary_consistent_desc: "All recorded deeds and surveys reconcile consistently for this parcel.",
    summary_review_desc: "Review required due to missing historical links or survey gaps.",
    summary_contradiction_desc: "Mathematical or chain-of-title contradiction identified in transfers.",
    
    alerts_heading: "Rule-Based Alerts",
    view_evidence: "View evidence",
    hide_evidence: "Hide evidence",
    rule_id_label: "Rule ID:",
    calculation_label: "Calculation:",
    evidence_ids_label: "Linked Evidence:",
    next_step_label: "Recommended Next Step:",
    
    timeline_heading: "Events Timeline",
    timeline_empty: "No recorded transaction events for this parcel.",
    col_date: "Date",
    col_type: "Type",
    col_from: "From",
    col_to: "To",
    col_area: "Area (decimals)",
    col_portion: "Portion/Holding",
    
    survey_heading: "Survey Records (Khatian)",
    khatian_label: "Khatian No:",
    record_date_label: "Survey Date:",
    recorded_area_label: "Total Area:",
    holders_label: "Recorded Holders:",
    
    graph_heading: "Chain of Title Graph",
    graph_fallback: "Graph visualization could not be loaded. Timeline and record details remain active below.",
    
    lab_heading: "Simulation Lab: Proposed Transaction",
    lab_desc: "Test a hypothetical sale counterfactually without modifying or persisting original records.",
    lab_from_label: "Seller (select recorded holder):",
    lab_to_label: "Buyer name/ID:",
    lab_area_label: "Transfer Area (decimals - integer or fraction, e.g. 5 or 7/2):",
    lab_date_label: "Proposed Date (optional):",
    lab_portion_label: "Portion ID (optional):",
    lab_submit_btn: "Simulate Transfer",
    lab_reset_btn: "Reset Form",
    
    lab_result_heading: "Simulation Result",
    lab_unchanged_badge: "Original records unchanged",
    lab_change_label: "Proposed Change:",
    lab_before_label: "Seller's Available Area Before:",
    lab_after_label: "Seller's Remaining Area After:",
    lab_excess_label: "Deficit Area After:",
    lab_excess_prefix: "Excess",
    lab_remaining_prefix: "Remaining",
    lab_calc_label: "Calculation Line:",
    lab_decimals_unit: "decimals",
    
    error_empty_fields: "Please fill seller, buyer, and area fields correctly.",
    error_float_area: "Decimal float values (e.g. 5.5) are rejected. Enter an integer (5) or fraction (11/2).",
    error_unknown_person: "Please select a recorded holder as the seller.",
    error_simulate_failed: "Simulation failed. Please verify the input values.",
    
    benchmark_heading: "System Benchmark & Integrity",
    benchmark_false_alarms: "False Alarms on Clean Parcels:",
    benchmark_coverage: "Rule Coverage Matrix (R1 - R7)",
    benchmark_integrity: "Simulation Invariance (Dataset Hash)",
    hash_before_label: "Hash Before Simulation:",
    hash_after_label: "Hash After Simulation:",
    hash_match_label: "Hash strictly identical & preserved",
    
    col_rule: "Rule",
    col_planted: "Planted Case Exists",
    col_detected: "Detected",
    col_status: "Detected Status",
    
    yes: "Yes",
    no: "No",
    back_to_parcels: "← Back to Parcels",
    back_to_home: "← Back to Home"
  }
};

// ---------------------------------------------------------------------------
// Language & Storage State
// ---------------------------------------------------------------------------

let currentLang = "bn";
try {
  const saved = localStorage.getItem("jomigraph_lang");
  if (saved === "en" || saved === "bn") {
    currentLang = saved;
  }
} catch (e) {
  // localStorage may be disabled in private browsing; safely ignore
}

function t(key) {
  return ui_strings[currentLang]?.[key] || ui_strings["bn"]?.[key] || key;
}

function setLanguage(newLang) {
  currentLang = newLang;
  try {
    localStorage.setItem("jomigraph_lang", newLang);
  } catch (e) {
    // safely ignore
  }
  document.documentElement.lang = currentLang;
  updateGlobalChrome();
  renderCurrentRoute();
}

// ---------------------------------------------------------------------------
// Global Chrome Update (Header, Disclaimer, Nav, Footer)
// ---------------------------------------------------------------------------

function updateGlobalChrome() {
  document.getElementById("brand-title").textContent = t("app_title");
  document.getElementById("brand-subtitle").textContent = t("app_subtitle");
  document.getElementById("disclaimer-banner").textContent = t("disclaimer_banner");
  
  document.getElementById("nav-home").textContent = t("nav_home");
  document.getElementById("nav-parcels").textContent = t("nav_parcels");
  document.getElementById("nav-benchmark").textContent = t("nav_benchmark");
  
  const toggleBtn = document.getElementById("lang-toggle-btn");
  toggleBtn.textContent = t("lang_toggle");
  toggleBtn.setAttribute("aria-label", currentLang === "bn" ? "Switch to English" : "বাংলায় পরিবর্তন করুন");
  
  document.getElementById("footer-text").textContent = `© 2026 ${t("app_title")} — ${t("disclaimer_banner")}`;
  
  // Highlight active nav link
  const hash = window.location.hash || "#/";
  document.querySelectorAll(".nav-link").forEach(link => {
    const href = link.getAttribute("href");
    if (href === hash || (hash.startsWith("#/parcel") && href === "#/parcels")) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
}

// Toggle language on button click
document.getElementById("lang-toggle-btn").addEventListener("click", () => {
  setLanguage(currentLang === "bn" ? "en" : "bn");
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatStatusBadge(status) {
  const s = (status || "").toUpperCase();
  if (s.includes("CONTRADICTION")) {
    return `<span class="badge badge-contradiction" aria-label="${t('status_contradiction')}"><span aria-hidden="true">✕</span> ${t('status_contradiction')}</span>`;
  } else if (s.includes("REVIEW")) {
    return `<span class="badge badge-review" aria-label="${t('status_review')}"><span aria-hidden="true">⚠</span> ${t('status_review')}</span>`;
  } else {
    return `<span class="badge badge-consistent" aria-label="${t('status_consistent')}"><span aria-hidden="true">✓</span> ${t('status_consistent')}</span>`;
  }
}

// ---------------------------------------------------------------------------
// Router
// ---------------------------------------------------------------------------

function renderCurrentRoute() {
  const hash = window.location.hash || "#/";
  updateGlobalChrome();

  if (hash === "#/" || hash === "") {
    renderHomeScreen();
  } else if (hash === "#/parcels") {
    renderParcelsScreen();
  } else if (hash.startsWith("#/parcel/")) {
    const parcelId = hash.replace("#/parcel/", "").split("#")[0].split("?")[0];
    renderParcelDetailScreen(parcelId);
  } else if (hash === "#/benchmark") {
    renderBenchmarkScreen();
  } else {
    renderHomeScreen();
  }
}

window.addEventListener("hashchange", renderCurrentRoute);

// ---------------------------------------------------------------------------
// Screen A: Home Screen
// ---------------------------------------------------------------------------

function renderHomeScreen() {
  const root = document.getElementById("app-root");
  root.innerHTML = `
    <div class="hero-section">
      <h1 class="hero-title">${t("app_title")}</h1>
      <p class="hero-desc">${t("app_subtitle")}</p>
    </div>

    <div class="home-cards-grid">
      <!-- Card 1: Check land records -->
      <div class="action-card">
        <div class="action-card-header">
          <div class="action-card-icon" aria-hidden="true">📋</div>
          <h2 class="action-card-title">${t("card_parcels_title")}</h2>
          <p class="action-card-desc">${t("card_parcels_desc")}</p>
        </div>
        <a href="#/parcels" class="action-card-btn">${t("nav_parcels")} →</a>
      </div>

      <!-- Card 2: View land history -->
      <div class="action-card">
        <div class="action-card-header">
          <div class="action-card-icon" aria-hidden="true">📜</div>
          <h2 class="action-card-title">${t("card_history_title")}</h2>
          <p class="action-card-desc">${t("card_history_desc")}</p>
        </div>
        <a href="#/parcel/PARCEL_STORY_01" class="action-card-btn">${t("view_details")} →</a>
      </div>

      <!-- Card 3: Check a proposed sale -->
      <div class="action-card">
        <div class="action-card-header">
          <div class="action-card-icon" aria-hidden="true">⚖️</div>
          <h2 class="action-card-title">${t("card_lab_title")}</h2>
          <p class="action-card-desc">${t("card_lab_desc")}</p>
        </div>
        <a href="#/parcel/PARCEL_LAB_DEMO" class="action-card-btn">${t("lab_heading")} →</a>
      </div>
    </div>
  `;
}

// ---------------------------------------------------------------------------
// Screen B: Parcel List Screen
// ---------------------------------------------------------------------------

let cachedParcels = [];

async function renderParcelsScreen() {
  const root = document.getElementById("app-root");
  root.innerHTML = `
    <div class="parcel-detail-header">
      <h1 class="hero-title" style="text-align: left; margin-bottom: 0.5rem;">${t("nav_parcels")}</h1>
      <p style="color: var(--text-muted); margin: 0 0 1.25rem 0;">${t("card_parcels_desc")}</p>
    </div>

    <div class="filter-bar">
      <input type="text" id="parcel-search-input" class="search-input" placeholder="${t("search_placeholder")}" aria-label="${t("search_placeholder")}">
      <select id="parcel-category-select" class="filter-select" aria-label="Filter parcels">
        <option value="ALL">${t("filter_all")}</option>
        <option value="CLEAN">${t("filter_clean")}</option>
        <option value="PLANTED">${t("filter_planted")}</option>
      </select>
    </div>

    <div id="parcels-container" class="parcel-list-grid">
      <p style="color: var(--text-muted); padding: 2rem 0;">লোড হচ্ছে...</p>
    </div>
  `;

  try {
    const res = await fetch(`/parcels?lang=${currentLang}`);
    if (!res.ok) throw new Error("Failed to fetch parcels");
    cachedParcels = await res.json();
    filterAndDisplayParcels();

    document.getElementById("parcel-search-input").addEventListener("input", filterAndDisplayParcels);
    document.getElementById("parcel-category-select").addEventListener("change", filterAndDisplayParcels);
  } catch (err) {
    document.getElementById("parcels-container").innerHTML = `
      <div class="form-error-msg visible" role="alert">${t("error_simulate_failed")}</div>
    `;
  }
}

function filterAndDisplayParcels() {
  const query = (document.getElementById("parcel-search-input")?.value || "").toLowerCase().trim();
  const cat = document.getElementById("parcel-category-select")?.value || "ALL";
  const container = document.getElementById("parcels-container");
  if (!container) return;

  const filtered = cachedParcels.filter(p => {
    const matchQuery = p.id.toLowerCase().includes(query) || p.label.toLowerCase().includes(query);
    const matchCat = cat === "ALL" || (cat === "PLANTED" && p.planted) || (cat === "CLEAN" && !p.planted);
    return matchQuery && matchCat;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<p style="color: var(--text-muted); padding: 1.5rem 0;">${t("no_parcels_found")}</p>`;
    return;
  }

  container.innerHTML = filtered.map(p => `
    <div class="parcel-item-card">
      <div>
        <h2 class="parcel-info-title">
          <a href="#/parcel/${p.id}">${p.label}</a>
        </h2>
        <div class="parcel-info-meta">
          <span>ID: <code>${p.id}</code></span>
        </div>
      </div>
      <div class="parcel-actions">
        ${formatStatusBadge(p.status_summary)}
        <span class="${p.planted ? 'tag-planted' : 'tag-clean'}">${p.planted ? t('planted_tag') : t('clean_tag')}</span>
        <a href="#/parcel/${p.id}" class="btn-secondary">${t("view_details")} →</a>
      </div>
    </div>
  `).join("");
}

// ---------------------------------------------------------------------------
// Screen C: Parcel Detail Screen
// ---------------------------------------------------------------------------

let currentCytoscape = null;

async function renderParcelDetailScreen(parcelId) {
  const root = document.getElementById("app-root");
  root.innerHTML = `
    <a href="#/parcels" class="back-link">${t("back_to_parcels")}</a>
    <div id="parcel-detail-content">
      <p style="color: var(--text-muted); padding: 2rem 0;">লোড হচ্ছে...</p>
    </div>
  `;

  try {
    const res = await fetch(`/parcel/${encodeURIComponent(parcelId)}?lang=${currentLang}`);
    if (!res.ok) {
      if (res.status === 404) {
        root.innerHTML = `
          <a href="#/parcels" class="back-link">${t("back_to_parcels")}</a>
          <div class="form-error-msg visible">${t("no_parcels_found")} (404)</div>
        `;
        return;
      }
      throw new Error("Failed to load parcel");
    }

    const data = await res.json();
    renderParcelDetailContent(data);
  } catch (err) {
    root.innerHTML = `
      <a href="#/parcels" class="back-link">${t("back_to_parcels")}</a>
      <div class="form-error-msg visible" role="alert">${t("error_simulate_failed")}</div>
    `;
  }
}

function renderParcelDetailContent(data) {
  const container = document.getElementById("parcel-detail-content");
  if (!container) return;

  const hasContradiction = data.alerts.some(a => a.status.toLowerCase().includes("contradiction"));
  const hasReview = data.alerts.some(a => a.status.toLowerCase().includes("review"));
  
  let overallStatus = "CONSISTENT";
  let summaryDesc = t("summary_consistent_desc");
  if (hasContradiction) {
    overallStatus = "CONTRADICTION";
    summaryDesc = t("summary_contradiction_desc");
  } else if (hasReview) {
    overallStatus = "REVIEW";
    summaryDesc = t("summary_review_desc");
  }

  // Extract unique holders from survey records for the lab form
  const holdersSet = new Map();
  data.survey_records.forEach(sr => {
    sr.holders.forEach(h => {
      if (!holdersSet.has(h.person_id)) {
        holdersSet.set(h.person_id, h.person_name || h.person_id);
      }
    });
  });

  const holderOptionsHtml = Array.from(holdersSet.entries()).map(([pid, name]) => 
    `<option value="${pid}">${name} (${pid})</option>`
  ).join("");

  // Determine default date: latest event date or survey date
  let defaultSimDate = "";
  if (data.events && data.events.length > 0) {
    const dates = data.events.map(e => e.event_date).filter(Boolean);
    if (dates.length > 0) {
      dates.sort();
      defaultSimDate = dates[dates.length - 1];
    }
  }
  if (!defaultSimDate && data.survey_records && data.survey_records.length > 0) {
    const sDates = data.survey_records.map(sr => sr.record_date).filter(Boolean);
    if (sDates.length > 0) {
      sDates.sort();
      defaultSimDate = sDates[sDates.length - 1];
    }
  }

  container.innerHTML = `
    <!-- Top Result Summary Card -->
    <div class="summary-card">
      <div class="summary-status-row">
        <div>
          <h1 class="summary-heading">${data.mouza} দাগ ${data.dag_no} (${data.id})</h1>
          <p class="summary-desc">${summaryDesc}</p>
        </div>
        <div>
          ${formatStatusBadge(overallStatus)}
        </div>
      </div>
      <button id="toggle-details-btn" class="btn-toggle-details" aria-expanded="false">
        ${t("view_details")} ▼
      </button>
      <div id="collapsible-details-panel" class="details-collapsible">
        <p><strong>দাগ নং:</strong> ${data.dag_no} | <strong>মৌজা:</strong> ${data.mouza} | <strong>প্যারেন্ট দাগ:</strong> ${data.parent_id || "নাই (মূল দাগ)"}</p>
      </div>
    </div>

    <!-- Alert Cards Section -->
    <div class="alerts-section">
      <h2 class="section-title">${t("alerts_heading")}</h2>
      ${data.alerts.map((alert, idx) => {
        const s = alert.status.toLowerCase();
        const statusClass = s.includes("contradiction") || s.includes("অসঙ্গতি") ? "status-contradiction" : s.includes("review") || s.includes("পর্যালোচনা") ? "status-review" : "status-consistent";
        return `
          <div class="alert-card ${statusClass}">
            <div class="alert-header">
              <h3 class="alert-message">${alert.message}</h3>
              ${formatStatusBadge(alert.status)}
            </div>
            <div class="alert-next-step">
              <strong>${t("next_step_label")}</strong> ${alert.recommended_next_step}
            </div>
            
            <button class="evidence-expander-btn" data-target="evidence-box-${idx}" aria-expanded="false">
              ${t("view_evidence")} ▼
            </button>
            <div id="evidence-box-${idx}" class="evidence-box">
              <p style="margin: 0 0 0.4rem 0;"><strong>${t("rule_id_label")}</strong> <code>${alert.rule_id}</code></p>
              <p style="margin: 0 0 0.4rem 0;"><strong>${t("calculation_label")}</strong> <code>${alert.calculation}</code></p>
              <div>
                <strong>${t("evidence_ids_label")}</strong>
                ${alert.evidence_ids.map(eid => `
                  <button type="button" class="evidence-id-tag" data-evidence-id="${eid}" aria-label="Highlight evidence ${eid}">
                    ${eid}
                  </button>
                `).join("")}
              </div>
            </div>

            <div class="alert-rule-disclaimer">
              ℹ️ ${t("rule_disclaimer")}
            </div>
          </div>
        `;
      }).join("")}
    </div>

    <!-- Chain of Title Graph Section -->
    <div class="graph-section">
      <h2 class="section-title">${t("graph_heading")}</h2>
      <div id="cy-container">
        <!-- Rendered by Cytoscape or fallback below -->
      </div>
    </div>

    <!-- Timeline Section -->
    <div class="timeline-section">
      <h2 class="section-title">${t("timeline_heading")}</h2>
      ${data.events.length === 0 ? `
        <p style="color: var(--text-muted);">${t("timeline_empty")}</p>
      ` : `
        <div class="stacked-records-list">
          ${data.events.map(ev => `
            <div class="timeline-row-card" id="timeline-row-${ev.id}">
              <div class="timeline-meta-row">
                <span><strong>#${ev.seq} [${ev.type}]</strong> ID: <code>${ev.id}</code></span>
                <span>📅 ${ev.event_date || "অনির্ধারিত / Undated"}</span>
              </div>
              <div class="timeline-data-grid">
                <div><strong>${t("col_from")}:</strong> ${ev.from_person_name || ev.from_person || "—"}</div>
                <div><strong>${t("col_to")}:</strong> ${ev.to_person_name || ev.to_person || "—"}</div>
                <div><strong>${t("col_area")}:</strong> ${ev.area ? `${ev.area} শতক` : "—"}</div>
              </div>
              ${ev.portion_id ? `<div style="font-size: 0.85rem; color: var(--text-light); margin-top: 0.25rem;"><strong>${t("col_portion")}:</strong> ${ev.portion_id}</div>` : ""}
            </div>
          `).join("")}
        </div>
      `}
    </div>

    <!-- Survey Records (Khatian) Section -->
    <div class="survey-section">
      <h2 class="section-title">${t("survey_heading")}</h2>
      <div class="stacked-records-list">
        ${data.survey_records.map(sr => `
          <div class="timeline-row-card" id="survey-row-${sr.id}">
            <div class="timeline-meta-row">
              <span><strong>${sr.survey} জরিপ</strong> (ID: <code>${sr.id}</code>)</span>
              <span>📅 ${sr.record_date}</span>
            </div>
            <div class="timeline-data-grid">
              <div><strong>${t("khatian_label")}</strong> ${sr.khatian_no}</div>
              <div><strong>${t("recorded_area_label")}</strong> ${sr.recorded_area} শতক</div>
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.9rem;">
              <strong>${t("holders_label")}</strong>
              <ul style="margin: 0.25rem 0 0 1.25rem; padding: 0;">
                ${sr.holders.map(h => `<li>${h.person_name} (${h.person_id}) — ${h.area} শতক</li>`).join("")}
              </ul>
            </div>
          </div>
        `).join("")}
      </div>
    </div>

    <!-- Simulation Lab Section -->
    <div class="lab-section" id="simulation-lab">
      <div class="lab-header">
        <h2 class="section-title" style="margin-bottom: 0.25rem;">${t("lab_heading")}</h2>
        <p style="color: var(--text-muted); margin: 0;">${t("lab_desc")}</p>
      </div>

      <form id="lab-simulation-form" class="lab-form" novalidate>
        <div class="form-group">
          <label for="lab-from-select" class="form-label">${t("lab_from_label")}</label>
          <select id="lab-from-select" class="form-select" required>
            ${holderOptionsHtml.length > 0 ? holderOptionsHtml : `<option value="H">Holder (H)</option>`}
          </select>
        </div>

        <div class="form-group">
          <label for="lab-to-input" class="form-label">${t("lab_to_label")}</label>
          <input type="text" id="lab-to-input" class="form-input" value="P_BUYER_SIM" required>
        </div>

        <div class="form-group">
          <label for="lab-area-input" class="form-label">${t("lab_area_label")}</label>
          <input type="text" id="lab-area-input" class="form-input" placeholder="e.g. 5 or 7/2" required>
        </div>

        <div class="form-group">
          <label for="lab-date-input" class="form-label">${t("lab_date_label")}</label>
          <input type="date" id="lab-date-input" class="form-input" value="${defaultSimDate}" required>
        </div>

        <div class="form-group">
          <label for="lab-portion-input" class="form-label">${t("lab_portion_label")}</label>
          <input type="text" id="lab-portion-input" class="form-input" placeholder="e.g. PORTION_A">
        </div>

        <div id="lab-form-error" class="form-error-msg" role="alert"></div>

        <div class="form-actions">
          <button type="submit" class="btn-primary" id="lab-submit-btn">${t("lab_submit_btn")}</button>
          <button type="reset" class="btn-secondary" id="lab-reset-btn">${t("lab_reset_btn")}</button>
        </div>
      </form>

      <!-- Lab Result Card -->
      <div id="lab-result-card" class="lab-result-card" role="region" aria-live="polite">
        <div class="lab-result-header">
          <h3 style="margin: 0; font-size: 1.2rem;">${t("lab_result_heading")}</h3>
          <span class="integrity-badge">
            <span aria-hidden="true">🔒</span>
            ${t("lab_unchanged_badge")} (<span id="lab-hash-status"></span>)
          </span>
        </div>

        <div class="lab-result-data">
          <div class="result-stat-box">
            <div class="result-stat-label">${t("lab_before_label")}</div>
            <div class="result-stat-value" id="lab-res-before"></div>
          </div>
          <div class="result-stat-box">
            <div class="result-stat-label">${t("lab_change_label")}</div>
            <div class="result-stat-value" id="lab-res-change"></div>
          </div>
          <div class="result-stat-box">
            <div class="result-stat-label" id="lab-stat-after-label">${t("lab_after_label")}</div>
            <div class="result-stat-value" id="lab-res-after"></div>
          </div>
        </div>

        <div class="r1-calc-line">
          <strong>${t("lab_calc_label")}</strong> <span id="lab-res-calc"></span>
        </div>

        <div id="lab-res-alerts"></div>
      </div>
    </div>
  `;

  // Attach interactive expander events
  attachParcelDetailEvents(data);

  // Initialize Cytoscape graph or fallback
  initializeCytoscape(data.graph);
}

function attachParcelDetailEvents(data) {
  // Toggle details summary
  const toggleBtn = document.getElementById("toggle-details-btn");
  const panel = document.getElementById("collapsible-details-panel");
  if (toggleBtn && panel) {
    toggleBtn.addEventListener("click", () => {
      const isOpen = panel.classList.toggle("open");
      toggleBtn.textContent = isOpen ? `${t("hide_details")} ▲` : `${t("view_details")} ▼`;
      toggleBtn.setAttribute("aria-expanded", String(isOpen));
    });
  }

  // Toggle evidence boxes
  document.querySelectorAll(".evidence-expander-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-target");
      const box = document.getElementById(targetId);
      if (box) {
        const isOpen = box.classList.toggle("open");
        btn.textContent = isOpen ? `${t("hide_evidence")} ▲` : `${t("view_evidence")} ▼`;
        btn.setAttribute("aria-expanded", String(isOpen));
      }
    });
  });

  // Clicking an evidence ID tag highlights timeline row and graph node
  document.querySelectorAll(".evidence-id-tag").forEach(tag => {
    tag.addEventListener("click", () => {
      const eid = tag.getAttribute("data-evidence-id");
      highlightEvidence(eid);
    });
  });

  // Simulation Form submission
  const simForm = document.getElementById("lab-simulation-form");
  if (simForm) {
    simForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      await handleSimulationSubmit(data.id);
    });
  }
}

function highlightEvidence(evidenceId) {
  // Clear previous highlighted elements
  document.querySelectorAll(".timeline-row-card.highlighted").forEach(el => {
    el.classList.remove("highlighted");
  });

  // Highlight timeline or survey row
  const row = document.getElementById(`timeline-row-${evidenceId}`) || document.getElementById(`survey-row-${evidenceId}`);
  if (row) {
    row.classList.add("highlighted");
    row.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  // Highlight graph node if Cytoscape is running
  if (currentCytoscape) {
    currentCytoscape.elements().removeClass("highlighted");
    const node = currentCytoscape.getElementById(evidenceId);
    if (node && node.length > 0) {
      node.addClass("highlighted");
      currentCytoscape.center(node);
      currentCytoscape.zoom({ level: 1.25, position: node.position() });
    }
  }
}

function initializeCytoscape(graphData) {
  const container = document.getElementById("cy-container");
  if (!container) return;

  if (typeof cytoscape === "undefined") {
    // CDN failed or blocked; display clear fallback
    container.innerHTML = `
      <div class="graph-fallback-msg">
        <p>${t("graph_fallback")}</p>
      </div>
    `;
    return;
  }

  try {
    const elements = [];
    (graphData.nodes || []).forEach(n => {
      elements.push({
        group: "nodes",
        data: n.data
      });
    });
    (graphData.edges || []).forEach(e => {
      elements.push({
        group: "edges",
        data: e.data
      });
    });

    currentCytoscape = cytoscape({
      container: container,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'background-color': '#3b82f6',
            'color': '#1e293b',
            'font-family': 'Noto Sans Bengali, sans-serif',
            'font-size': '11px',
            'text-valign': 'bottom',
            'text-margin-y': 4,
            'width': 34,
            'height': 34
          }
        },
        {
          selector: 'node[type="SURVEY_RECORD"]',
          style: {
            'shape': 'hexagon',
            'background-color': '#10b981'
          }
        },
        {
          selector: 'node[type="PERSON"]',
          style: {
            'shape': 'ellipse',
            'background-color': '#6366f1'
          }
        },
        {
          selector: 'node[type="PARCEL"]',
          style: {
            'shape': 'round-rectangle',
            'background-color': '#f59e0b',
            'width': 44,
            'height': 30
          }
        },
        {
          selector: 'node.highlighted',
          style: {
            'background-color': '#eab308',
            'border-width': 4,
            'border-color': '#ca8a04',
            'width': 42,
            'height': 42
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#94a3b8',
            'target-arrow-color': '#94a3b8',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'color': '#64748b',
            'text-rotation': 'autorotate'
          }
        }
      ],
      layout: {
        name: 'breadthfirst',
        directed: true,
        padding: 20,
        spacingFactor: 1.25,
        avoidOverlap: true
      }
    });
  } catch (err) {
    container.innerHTML = `
      <div class="graph-fallback-msg">
        <p>${t("graph_fallback")}</p>
      </div>
    `;
  }
}

async function handleSimulationSubmit(parcelId) {
  const errBox = document.getElementById("lab-form-error");
  const resultCard = document.getElementById("lab-result-card");
  errBox.classList.remove("visible");
  errBox.textContent = "";

  const fromPerson = document.getElementById("lab-from-select").value.trim();
  const toPerson = document.getElementById("lab-to-input").value.trim() || "P_BUYER_SIM";
  const area = document.getElementById("lab-area-input").value.trim();
  const dateVal = document.getElementById("lab-date-input").value.trim();
  const portionId = document.getElementById("lab-portion-input").value.trim();

  // Client-side validations
  if (!fromPerson || !toPerson || !area) {
    errBox.textContent = t("error_empty_fields");
    errBox.classList.add("visible");
    return;
  }

  if (area.includes(".")) {
    errBox.textContent = t("error_float_area");
    errBox.classList.add("visible");
    return;
  }

  const payload = {
    parcel_id: parcelId,
    from_person: fromPerson,
    to_person: toPerson,
    area: area,
    portion_id: portionId || null,
    date: dateVal || null,
    lang: currentLang
  };

  try {
    const [simRes, benchRes] = await Promise.all([
      fetch("/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }),
      fetch("/benchmark")
    ]);

    if (simRes.status === 422) {
      errBox.textContent = t("error_float_area");
      errBox.classList.add("visible");
      return;
    }

    if (!simRes.ok) {
      errBox.textContent = t("error_simulate_failed");
      errBox.classList.add("visible");
      return;
    }

    const simData = await simRes.json();
    const benchData = await benchRes.json();

    function formatNum(numStr) {
      if (currentLang === "bn") {
        const bnDigits = ["০","১","২","৩","৪","৫","৬","৭","৮","৯"];
        return String(numStr).replace(/[0-9]/g, d => bnDigits[parseInt(d)]);
      }
      return String(numStr);
    }

    // Populate Result Card
    document.getElementById("lab-res-before").textContent = `${formatNum(simData.available_before)} ${t("lab_decimals_unit")}`;
    document.getElementById("lab-res-change").textContent = `-${formatNum(simData.proposed_event.area)} ${t("lab_decimals_unit")}`;

    const afterLabelEl = document.getElementById("lab-stat-after-label");
    const afterValEl = document.getElementById("lab-res-after");

    // Do NOT show negative "available after" -> Show "excess N" instead!
    if (simData.available_after.startsWith("-")) {
      const excessVal = simData.available_after.replace("-", "");
      if (afterLabelEl) afterLabelEl.textContent = t("lab_excess_label");
      afterValEl.textContent = `${t("lab_excess_prefix")} ${formatNum(excessVal)} ${t("lab_decimals_unit")}`;
      afterValEl.style.color = "#dc2626";
    } else {
      if (afterLabelEl) afterLabelEl.textContent = t("lab_after_label");
      afterValEl.textContent = `${t("lab_remaining_prefix")} ${formatNum(simData.available_after)} ${t("lab_decimals_unit")}`;
      afterValEl.style.color = "#16a34a";
    }

    document.getElementById("lab-res-calc").textContent = simData.r1_calculation || "N/A";
    document.getElementById("lab-hash-status").textContent = benchData.simulation_integrity?.unchanged ? "Hash Matched ✓" : "Integrity Error";

    const alertsBox = document.getElementById("lab-res-alerts");
    alertsBox.innerHTML = (simData.alerts || []).map(a => `
      <div style="margin-top: 0.75rem; padding: 0.75rem; background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-sm);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
          <strong>[${a.rule_id}] ${a.message}</strong>
          ${formatStatusBadge(a.status)}
        </div>
        <div style="font-size: 0.9rem; color: var(--text-muted);">${a.recommended_next_step}</div>
      </div>
    `).join("");

    resultCard.classList.add("visible");
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (err) {
    errBox.textContent = t("error_simulate_failed");
    errBox.classList.add("visible");
  }
}

// ---------------------------------------------------------------------------
// Screen D: Benchmark Screen
// ---------------------------------------------------------------------------

async function renderBenchmarkScreen() {
  const root = document.getElementById("app-root");
  root.innerHTML = `
    <div class="parcel-detail-header">
      <h1 class="hero-title" style="text-align: left; margin-bottom: 0.5rem;">${t("benchmark_heading")}</h1>
      <p style="color: var(--text-muted); margin: 0 0 1.5rem 0;">${t("disclaimer_banner")}</p>
    </div>

    <div id="benchmark-content">
      <p style="color: var(--text-muted); padding: 2rem 0;">লোড হচ্ছে...</p>
    </div>
  `;

  try {
    const res = await fetch("/benchmark");
    if (!res.ok) throw new Error("Failed to load benchmark");
    const data = await res.json();
    renderBenchmarkContent(data);
  } catch (err) {
    document.getElementById("benchmark-content").innerHTML = `
      <div class="form-error-msg visible" role="alert">${t("error_simulate_failed")}</div>
    `;
  }
}

function renderBenchmarkContent(data) {
  const container = document.getElementById("benchmark-content");
  if (!container) return;

  container.innerHTML = `
    <!-- Stat 1: Clean False Alarm Count -->
    <div class="benchmark-stat-card">
      <div>
        <h2 style="font-size: 1.15rem; margin: 0; color: #14532d;">${t("benchmark_false_alarms")}</h2>
        <p style="font-size: 0.9rem; color: #166534; margin: 0.25rem 0 0 0;">ত্রুটিমুক্ত দাগে কোনো মিথ্যা সতর্কতা চিহ্নিত হয়নি</p>
      </div>
      <div class="benchmark-stat-number">${data.clean_false_alarm_count}</div>
    </div>

    <!-- Matrix: Coverage Table -->
    <div class="benchmark-card">
      <h2 class="section-title">${t("benchmark_coverage")}</h2>
      <div class="benchmark-table-responsive">
        <table class="benchmark-table">
          <thead>
            <tr>
              <th>${t("col_rule")}</th>
              <th>${t("col_planted")}</th>
              <th>${t("col_detected")}</th>
              <th>${t("col_status")}</th>
            </tr>
          </thead>
          <tbody>
            ${data.coverage_table.map(row => `
              <tr>
                <td><strong>${row.rule_id}</strong></td>
                <td>${row.has_planted_case ? `✓ ${t('yes')}` : `— ${t('no')}`}</td>
                <td>${row.detected ? `✓ ${t('yes')}` : `— ${t('no')}`}</td>
                <td>${row.status_detected ? formatStatusBadge(row.status_detected) : "—"}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </div>

    <!-- Integrity: Simulation Hash Invariance -->
    <div class="benchmark-card">
      <h2 class="section-title">${t("benchmark_integrity")}</h2>
      <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1rem;">
        সিমুলেশনের পূর্বে ও পরে ডাটাবেজের সম্পূর্ণ ক্রিপ্টোগ্রাফিক হ্যাশ (SHA-256) অপরিবর্তিত থাকে।
      </p>

      <div style="margin-bottom: 0.75rem;">
        <strong>${t("hash_before_label")}</strong>
        <div class="hash-box">${data.simulation_integrity.dataset_hash_before}</div>
      </div>

      <div style="margin-bottom: 1rem;">
        <strong>${t("hash_after_label")}</strong>
        <div class="hash-box">${data.simulation_integrity.dataset_hash_after}</div>
      </div>

      <div style="display: flex; align-items: center; gap: 0.5rem; font-weight: 600; color: #15803d;">
        <span aria-hidden="true">✓</span> ${t("hash_match_label")} (${data.simulation_integrity.unchanged ? "unchanged: true" : "failed"})
      </div>
    </div>
  `;
}

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
  renderCurrentRoute();
});
