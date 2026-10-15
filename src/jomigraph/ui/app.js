/**
 * JomiGraph AI — Frontend Application
 * ====================================
 * Single-Page Application (SPA) with Hash Routing.
 * All static UI strings are loaded from ui_strings.
 * In-memory role management (no localStorage for roles).
 * No framework, no build step, no npm.
 */

const ui_strings = {
  "bn": {
    "app_title": "জমিগ্রাফ এআই",
    "app_subtitle": "ভূমির রেকর্ড ও মালিকানা ধারাবাহিকতা যাচাই",
    "nav_home": "নীড়পাতা",
    "nav_parcels": "জমির তালিকা",
    "nav_benchmark": "বেঞ্চমার্ক",
    "lang_toggle": "English",
    "disclaimer_banner": "ডেমো, কাল্পনিক তথ্য, আইনি সিদ্ধান্ত নয়",
    "rule_disclaimer": "এটি একটি নিয়মভিত্তিক সতর্কতা, আইনি রায় নয়",
    "card_parcels_title": "জমির রেকর্ড যাচাই করুন",
    "card_parcels_desc": "সকল দাগ ও খতিয়ানের ধারাবাহিকতা এবং অসঙ্গতি পর্যবেক্ষণ করুন।",
    "card_history_title": "জমির ইতিহাস দেখুন",
    "card_history_desc": "চার প্রজন্মের পারিবারিক ধারাবাহিকতা ও হস্তান্তরের কালরেখা দেখুন।",
    "card_lab_title": "প্রস্তাবিত বিক্রি যাচাই করুন",
    "card_lab_desc": "প্রস্তাবিত হস্তান্তরের ফলে অতিরিক্ত বিক্রয় বা অসঙ্গতি হবে কিনা পরীক্ষা করুন।",
    "status_consistent": "সঙ্গতিপূর্ণ",
    "status_review": "পর্যালোচনা প্রয়োজন",
    "status_contradiction": "অসঙ্গতি পাওয়া গেছে",
    "status_unknown": "অজানা",
    "search_placeholder": "দাগ নম্বর বা আইডি দিয়ে খুঁজুন...",
    "filter_all": "সকল দাগ",
    "filter_planted": "পরীক্ষামূলক অসঙ্গতি",
    "filter_clean": "ত্রুটিমুক্ত দাগ",
    "planted_tag": "পরীক্ষামূলক",
    "clean_tag": "ত্রুটিমুক্ত",
    "no_parcels_found": "কোনো দাগ পাওয়া যায়নি।",
    "view_details": "বিস্তারিত তথ্য দেখুন",
    "hide_details": "তথ্য সংক্ষেপ করুন",
    "summary_heading": "ফলাফল সারসংক্ষেপ",
    "summary_consistent_desc": "সরবরাহকৃত সকল খতিয়ান ও দলিলের সাথে এই দাগের রেকর্ড সঙ্গতিপূর্ণ।",
    "summary_review_desc": "কিছু রেকর্ডে তথ্যের ঘাটতি বা পর্যালোচনা প্রয়োজন রয়েছে।",
    "summary_contradiction_desc": "মালিকানা হস্তান্তরে গাণিতিক বা তথ্যগত অসঙ্গতি চিহ্নিত হয়েছে।",
    "alerts_heading": "নিয়মভিত্তিক সতর্কতা",
    "view_evidence": "প্রমাণ দেখুন",
    "hide_evidence": "প্রমাণ লুকান",
    "rule_id_label": "নিয়ম আইডি:",
    "calculation_label": "গণনা বিবরণ:",
    "evidence_ids_label": "যুক্ত প্রমাণ:",
    "next_step_label": "পরামর্শিত পদক্ষেপ:",
    "timeline_heading": "মালিকানা হস্তান্তরের কালরেখা",
    "timeline_empty": "এই দাগের জন্য কোনো হস্তান্তর ইভেন্ট নেই।",
    "col_date": "তারিখ",
    "col_type": "ধরণ",
    "col_from": "হস্তান্তরকারী",
    "col_to": "গ্রহীতা",
    "col_area": "জমির পরিমাণ (শতক)",
    "col_portion": "অংশ/হোল্ডিং",
    "survey_heading": "জরিপ রেকর্ড (খতিয়ান)",
    "khatian_label": "খতিয়ান নং:",
    "record_date_label": "জরিপের তারিখ:",
    "recorded_area_label": "মোট জমি:",
    "holders_label": "রেকর্ডভুক্ত মালিকগণ:",
    "graph_heading": "মালিকানা সংযোগ চিত্র",
    "graph_fallback": "গ্রাফ লোড করা সম্ভব হয়নি। নিচের কালরেখা ও রেকর্ডসমূহ সক্রিয় রয়েছে।",
    "lab_heading": "সিমুলেশন ল্যাব: প্রস্তাবিত হস্তান্তর যাচাই",
    "lab_desc": "বর্তমান রেকর্ড অপরিবর্তিত রেখে কাল্পনিক একটি বিক্রয় প্রস্তাব যাচাই করুন।",
    "lab_from_label": "বিক্রেতা (রেকর্ডভুক্ত অংশীদার নির্বাচন করুন):",
    "lab_to_label": "ক্রেতার নাম/আইডি:",
    "lab_area_label": "বিক্রির পরিমাণ (শতক - পূর্ণসংখ্যা বা ভগ্নাংশ, যেমন ৫ বা ৭/২):",
    "lab_date_label": "প্রস্তাবিত তারিখ (ঐচ্ছিক):",
    "lab_portion_label": "অংশ বা প্লট আইডি (ঐচ্ছিক):",
    "lab_submit_btn": "হস্তান্তর যাচাই করুন",
    "lab_reset_btn": "পুনরায় নির্ধারণ",
    "lab_result_heading": "সিমুলেশন ফলাফল",
    "lab_unchanged_badge": "মূল রেকর্ড অপরিবর্তিত",
    "lab_change_label": "প্রস্তাবিত পরিবর্তন:",
    "lab_before_label": "বিক্রেতার পূর্বে প্রাপ্য অংশ:",
    "lab_after_label": "হস্তান্তরের পর অবশিষ্ট অংশ:",
    "lab_excess_label": "হস্তান্তরের পর ঘাটতি:",
    "lab_excess_prefix": "অতিরিক্ত",
    "lab_remaining_prefix": "অবশিষ্ট",
    "lab_calc_label": "গণনা লাইন:",
    "lab_decimals_unit": "শতক",
    "error_empty_fields": "অনুগ্রহ করে বিক্রেতা, ক্রেতা এবং জমির পরিমাণ সঠিকভাবে পূরণ করুন।",
    "error_float_area": "দশমিক সংখ্যা গ্রহণযোগ্য নয় (যেমন ৫.৫)। পূর্ণসংখ্যা (৫) বা ভগ্নাংশ (১১/২) লিখুন।",
    "error_unknown_person": "বিক্রেতা হিসেবে একজন রেকর্ডভুক্ত ব্যক্তি নির্বাচন করুন।",
    "error_simulate_failed": "সিমুলেশন সম্পন্ন করা সম্ভব হয়নি। অনুগ্রহ করে তথ্য পুনরায় পরীক্ষা করুন।",
    "benchmark_heading": "সিস্টেম বেঞ্চমার্ক ও নির্ভরযোগ্যতা",
    "benchmark_false_alarms": "ত্রুটিমুক্ত দাগে মিথ্যা সতর্কতার সংখ্যা (False Alarms):",
    "benchmark_coverage": "নিয়ম কভারেজ সারণী (R1 - R7)",
    "benchmark_integrity": "সিমুলেশন অখণ্ডতা (ডাটাবেজ হ্যাশ)",
    "hash_before_label": "সিমুলেশনের পূর্বে হ্যাশ:",
    "hash_after_label": "সিমুলেশনের পরে হ্যাশ:",
    "hash_match_label": "হ্যাশ অপরিবর্তিত ও সংরক্ষিত",
    "col_rule": "নিয়ম",
    "col_planted": "পরীক্ষামূলক কেস বিদ্যমান",
    "col_detected": "সফলভাবে চিহ্নিত",
    "col_status": "চিহ্নিত অবস্থা",
    "yes": "হ্যাঁ",
    "no": "না",
    "back_to_parcels": "← দাগের তালিকায় ফিরে যান",
    "back_to_home": "← নীড়পাতায় ফিরে যান",
    "role_select_title": "ব্যবহারকারী ভূমিকা নির্বাচন করুন",
    "role_select_subtitle": "ডেমো ভূমিকা, প্রকৃত প্রমাণীকরণ নয়",
    "role_citizen_title": "নাগরিক / জমি ক্রেতা",
    "role_citizen_desc": "সহজ ভাষায় জমির খতিয়ান ও রেকর্ড যাচাই, কালরেখা পর্যবেক্ষণ এবং প্রস্তাবিত বিক্রয় সিমুলেশন।",
    "role_citizen_cred": "ডেমো ব্যবহারকারী: citizen.demo | অনুমতি: সাধারণ অনুসন্ধান",
    "role_citizen_btn": "নাগরিক হিসেবে প্রবেশ করুন",
    "role_reviewer_title": "ভূমি কর্মকর্তা / পর্যালোচক",
    "role_reviewer_desc": "নিয়মভিত্তিক বিস্তারিত বিশ্লেষণ (R1-R7), প্রমাণ গ্রাফ, বিকল্প প্রমাণ সেট এবং পরবর্তী হস্তান্তর প্রভাব।",
    "role_reviewer_cred": "ডেমো ব্যবহারকারী: ac_land.demo | দপ্তর: সহকারী কমিশনার (ভূমি)",
    "role_reviewer_btn": "পর্যালোচক হিসেবে প্রবেশ করুন",
    "switch_role_btn": "ভূমিকা পরিবর্তন",
    "current_role_label": "ভূমিকা:",
    "role_citizen_badge": "নাগরিক",
    "role_reviewer_badge": "পর্যালোচক",
    "role_demo_notice": "ডেমো ভূমিকা, প্রকৃত প্রমাণীকরণ নয়",
    "search_heading": "জমির রেকর্ড অনুসন্ধান",
    "search_results_title": "অনুসন্ধানের ফলাফল",
    "matched_on_prefix": "মিলেছে:",
    "matched_dag_no": "দাগ নম্বর",
    "matched_khatian_no": "খতিয়ান নম্বর",
    "matched_holder_name": "মালিকের নাম",
    "matched_deed_no": "দলিল নম্বর",
    "matched_parcel_id": "দাগ পরিচিতি",
    "minimal_evidence_heading": "সংক্ষিপ্ত প্রমাণ সেট",
    "alt_set_label": "বিকল্প প্রমাণ সেট",
    "not_minimized_warning": "অতিরিক্ত রেকর্ডের কারণে প্রমাণ সংক্ষেপ করা সম্ভব হয়নি; সকল সম্ভাব্য প্রমাণ প্রদর্শিত হচ্ছে",
    "impact_heading": "পরবর্তী ক্ষতিগ্রস্ত হস্তান্তরসমূহ",
    "impact_empty": "এই অসঙ্গতির কারণে পরবর্তী কোনো হস্তান্তর ক্ষতিগ্রস্ত হয়নি।",
    "impacted_badge": "ক্ষতিগ্রস্ত পরবর্তী হস্তান্তর",
    "benchmark_toggle_title": "বেঞ্চমার্ক ও সিস্টেম অখণ্ডতা রিপোর্ট (পর্যালোচক)",
    "print_report_btn": "প্রতিবেদন প্রিন্ট করুন",
    "print_report_title": "ভূমি রেকর্ড যাচাই প্রতিবেদন",
    "print_generated_at": "তৈরির তারিখ:",
    "print_dataset_hash": "ডাটাবেজ হ্যাশ (SHA-256):",
    "lab_plain_consistent": "বিক্রেতার অংশ পর্যাপ্ত রয়েছে এবং হস্তান্তরের পর কোনো ঘাটতি নেই।",
    "lab_plain_excess_prefix": "বিক্রেতার পূর্বে প্রাপ্য অংশ",
    "lab_plain_excess_mid": ", হস্তান্তরের পর অতিরিক্ত ঘাটতি",
    "event_type_sale": "বিক্রয়",
    "event_type_gift": "দান/হেবা",
    "event_type_mutation": "নামজারি",
    "event_type_subdivide": "উপ-বিভাগ",
    "event_type_cancel": "বাতিল",
    "event_type_correct": "সংশোধন",
    "dag_label": "দাগ",
    "khatian_label_inline": "খতিয়ান",
    "survey_label_inline": "জরিপ",
    "tech_details_summary": "কারিগরি বিবরণ ও সিস্টেম আইডি",
    "tech_system_id": "সিস্টেম আইডি:",
    "tech_parent_id": "প্যারেন্ট দাগ আইডি:",
    "loading_parcels": "লোড হচ্ছে...",
    "loading_parcel_details": "লোড হচ্ছে...",
    "loading_benchmark": "লোড হচ্ছে...",
    "total_parcels_label": "মোট দাগ",
    "planted_detected_label": "চিহ্নিত পরীক্ষামূলক কেস",
    "undated_label": "অনির্ধারিত",
    "survey_unit": "জরিপ",
    "print_parcel_label": "দাগের পরিচিতি:",
    "print_mouza_label": "মৌজা:",
    "print_dag_no_label": "দাগ নং:",
    "print_overall_status_label": "সার্বিক স্থিতি:",
    "print_disclaimer_label": "আইনি সতর্কবার্তা:",
    "proposed_buyer_label": "প্রস্তাবিত ক্রেতা"
  },
  "en": {
    "app_title": "JomiGraph AI",
    "app_subtitle": "Land Record Continuity & Rule-Based Verification",
    "nav_home": "Home",
    "nav_parcels": "Parcels",
    "nav_benchmark": "Benchmark",
    "lang_toggle": "বাংলা",
    "disclaimer_banner": "Demo, fictional data, not a legal ruling",
    "rule_disclaimer": "This is a rule-based warning, not a legal ruling",
    "card_parcels_title": "Check land records",
    "card_parcels_desc": "Inspect record continuity, surveys, and mathematical consistency across parcels.",
    "card_history_title": "View land history",
    "card_history_desc": "Explore four generations of family ownership timeline and recorded transfers.",
    "card_lab_title": "Check a proposed sale",
    "card_lab_desc": "Simulate a proposed sale in the lab to test for over-transfer or duplicate portions.",
    "status_consistent": "Consistent",
    "status_review": "Needs review",
    "status_contradiction": "Contradiction",
    "status_unknown": "Unknown",
    "search_placeholder": "Filter by parcel ID or dag number...",
    "filter_all": "All Parcels",
    "filter_planted": "Planted Tests",
    "filter_clean": "Clean Parcels",
    "planted_tag": "Planted",
    "clean_tag": "Clean",
    "no_parcels_found": "No parcels found matching your filter.",
    "view_details": "View details",
    "hide_details": "Hide details",
    "summary_heading": "Verification Summary",
    "summary_consistent_desc": "All recorded deeds and surveys reconcile consistently for this parcel.",
    "summary_review_desc": "Review required due to missing historical links or survey gaps.",
    "summary_contradiction_desc": "Mathematical or chain-of-title contradiction identified in transfers.",
    "alerts_heading": "Rule-Based Alerts",
    "view_evidence": "View evidence",
    "hide_evidence": "Hide evidence",
    "rule_id_label": "Rule ID:",
    "calculation_label": "Calculation:",
    "evidence_ids_label": "Linked Evidence:",
    "next_step_label": "Recommended Next Step:",
    "timeline_heading": "Events Timeline",
    "timeline_empty": "No recorded transaction events for this parcel.",
    "col_date": "Date",
    "col_type": "Type",
    "col_from": "From",
    "col_to": "To",
    "col_area": "Area (decimals)",
    "col_portion": "Portion/Holding",
    "survey_heading": "Survey Records (Khatian)",
    "khatian_label": "Khatian No:",
    "record_date_label": "Survey Date:",
    "recorded_area_label": "Total Area:",
    "holders_label": "Recorded Holders:",
    "graph_heading": "Chain of Title Graph",
    "graph_fallback": "Graph visualization could not be loaded. Timeline and record details remain active below.",
    "lab_heading": "Simulation Lab: Proposed Transaction",
    "lab_desc": "Test a hypothetical sale counterfactually without modifying or persisting original records.",
    "lab_from_label": "Seller (select recorded holder):",
    "lab_to_label": "Buyer name/ID:",
    "lab_area_label": "Transfer Area (decimals - integer or fraction, e.g. 5 or 7/2):",
    "lab_date_label": "Proposed Date (optional):",
    "lab_portion_label": "Portion ID (optional):",
    "lab_submit_btn": "Simulate Transfer",
    "lab_reset_btn": "Reset Form",
    "lab_result_heading": "Simulation Result",
    "lab_unchanged_badge": "Original records unchanged",
    "lab_change_label": "Proposed Change:",
    "lab_before_label": "Seller's Available Area Before:",
    "lab_after_label": "Seller's Remaining Area After:",
    "lab_excess_label": "Deficit Area After:",
    "lab_excess_prefix": "Excess",
    "lab_remaining_prefix": "Remaining",
    "lab_calc_label": "Calculation Line:",
    "lab_decimals_unit": "decimals",
    "error_empty_fields": "Please fill seller, buyer, and area fields correctly.",
    "error_float_area": "Decimal float values (e.g. 5.5) are rejected. Enter an integer (5) or fraction (11/2).",
    "error_unknown_person": "Please select a recorded holder as the seller.",
    "error_simulate_failed": "Simulation failed. Please verify the input values.",
    "benchmark_heading": "System Benchmark & Integrity",
    "benchmark_false_alarms": "False Alarms on Clean Parcels:",
    "benchmark_coverage": "Rule Coverage Matrix (R1 - R7)",
    "benchmark_integrity": "Simulation Invariance (Dataset Hash)",
    "hash_before_label": "Hash Before Simulation:",
    "hash_after_label": "Hash After Simulation:",
    "hash_match_label": "Hash strictly identical & preserved",
    "col_rule": "Rule",
    "col_planted": "Planted Case Exists",
    "col_detected": "Detected",
    "col_status": "Detected Status",
    "yes": "Yes",
    "no": "No",
    "back_to_parcels": "← Back to Parcels",
    "back_to_home": "← Back to Home",
    "role_select_title": "Select User Role",
    "role_select_subtitle": "Demo roles, not real authentication",
    "role_citizen_title": "Citizen / Buyer",
    "role_citizen_desc": "Plain-language land record verification, ownership timeline, and proposed sale simulation.",
    "role_citizen_cred": "Demo User: citizen.demo | Access: Public Search & Verification",
    "role_citizen_btn": "Continue as Citizen / Buyer",
    "role_reviewer_title": "Land Office Reviewer",
    "role_reviewer_desc": "In-depth rule-based audit (R1-R7), chain-of-title graph, minimal evidence sets, and downstream impact analysis.",
    "role_reviewer_cred": "Demo User: ac_land.demo | Office: Assistant Commissioner (Land)",
    "role_reviewer_btn": "Continue as Reviewer",
    "switch_role_btn": "Switch Role",
    "current_role_label": "Role:",
    "role_citizen_badge": "Citizen",
    "role_reviewer_badge": "Reviewer",
    "role_demo_notice": "Demo roles, not real authentication",
    "search_heading": "Search Land Records",
    "search_results_title": "Search Results",
    "matched_on_prefix": "Matched on:",
    "matched_dag_no": "Dag No",
    "matched_khatian_no": "Khatian No",
    "matched_holder_name": "Holder Name",
    "matched_deed_no": "Deed No",
    "matched_parcel_id": "Parcel ID",
    "minimal_evidence_heading": "Minimal Evidence Sets",
    "alt_set_label": "Alternative Evidence Set",
    "not_minimized_warning": "Too many records to reduce further; showing all candidate evidence",
    "impact_heading": "Downstream Impacted Events",
    "impact_empty": "No downstream events are impacted by this conflict.",
    "impacted_badge": "Downstream Impacted Event",
    "benchmark_toggle_title": "Benchmark & System Integrity Report (Reviewer)",
    "print_report_btn": "Print Report",
    "print_report_title": "Land Record Verification Report",
    "print_generated_at": "Generated on:",
    "print_dataset_hash": "Dataset Hash (SHA-256):",
    "lab_plain_consistent": "Seller has sufficient share and no deficit after transfer.",
    "lab_plain_excess_prefix": "Seller's available share before: ",
    "lab_plain_excess_mid": ", excess deficit after transfer: ",
    "event_type_sale": "Sale",
    "event_type_gift": "Gift",
    "event_type_mutation": "Mutation",
    "event_type_subdivide": "Subdivision",
    "event_type_cancel": "Cancellation",
    "event_type_correct": "Correction",
    "dag_label": "Dag",
    "khatian_label_inline": "Khatian",
    "survey_label_inline": "Survey",
    "tech_details_summary": "Technical Details & System ID",
    "tech_system_id": "System Parcel ID:",
    "tech_parent_id": "Parent Parcel ID:",
    "loading_parcels": "Loading parcels...",
    "loading_parcel_details": "Loading parcel...",
    "loading_benchmark": "Loading benchmark report...",
    "total_parcels_label": "Total Parcels",
    "planted_detected_label": "Planted Cases Detected",
    "undated_label": "Undated",
    "survey_unit": "Survey",
    "print_parcel_label": "Parcel:",
    "print_mouza_label": "Mouza:",
    "print_dag_no_label": "Dag No:",
    "print_overall_status_label": "Overall Status:",
    "print_disclaimer_label": "Disclaimer:",
    "proposed_buyer_label": "Proposed buyer"
  }
};

// ---------------------------------------------------------------------------
// Language & Role State (Role is STRICTLY in-memory)
// ---------------------------------------------------------------------------

let currentRole = null; // 'citizen' | 'reviewer' | null (in-memory only)
let currentLang = "bn";

try {
  const saved = localStorage.getItem("jomigraph_lang");
  if (saved === "en" || saved === "bn") {
    currentLang = saved;
  }
} catch (e) {
  // localStorage safely ignored if disabled
}

function t(key) {
  return ui_strings[currentLang]?.[key] || ui_strings["bn"]?.[key] || key;
}

function setLanguage(newLang) {
  currentLang = newLang;
  try {
    localStorage.setItem("jomigraph_lang", newLang);
  } catch (e) {}
  document.documentElement.lang = currentLang;
  updateGlobalChrome();
  renderCurrentRoute();
}

function setRole(role) {
  currentRole = role;
  updateGlobalChrome();
  const hash = window.location.hash || "#/";
  if (hash === "#/" || hash === "#role-select") {
    window.location.hash = "#/parcels";
  } else {
    renderCurrentRoute();
  }
}

function switchRole() {
  if (!currentRole) {
    currentRole = "citizen";
  } else {
    currentRole = currentRole === "citizen" ? "reviewer" : "citizen";
  }
  updateGlobalChrome();
  renderCurrentRoute();
}

function toBanglaDigits(val) {
  if (val === null || val === undefined) return "";
  const enToBn = {
    "0": "০", "1": "১", "2": "২", "3": "৩", "4": "৪",
    "5": "৫", "6": "৬", "7": "৭", "8": "৮", "9": "৯"
  };
  return String(val).replace(/[0-9]/g, d => enToBn[d] || d);
}

function formatAreaNumber(val) {
  if (val === null || val === undefined) return "—";
  return currentLang === "bn" ? toBanglaDigits(val) : String(val);
}

// ---------------------------------------------------------------------------
// Global Chrome Update (Header, Disclaimer, Nav, Footer, Role Controls)
// ---------------------------------------------------------------------------

function updateGlobalChrome() {
  document.getElementById("brand-title").textContent = t("app_title");
  document.getElementById("brand-subtitle").textContent = t("app_subtitle");
  document.getElementById("disclaimer-banner").textContent = t("disclaimer_banner");

  document.getElementById("nav-home").textContent = t("nav_home");
  document.getElementById("nav-parcels").textContent = t("nav_parcels");

  const benchmarkNav = document.getElementById("nav-benchmark");
  if (benchmarkNav) {
    benchmarkNav.textContent = t("nav_benchmark");
    benchmarkNav.style.display = currentRole === "reviewer" ? "inline-flex" : "none";
  }

  const toggleBtn = document.getElementById("lang-toggle-btn");
  toggleBtn.textContent = t("lang_toggle");
  toggleBtn.setAttribute("aria-label", currentLang === "bn" ? "Switch to English" : "বাংলায় পরিবর্তন করুন");

  // Role Controls in Header
  const roleControls = document.getElementById("role-controls");
  const roleBadge = document.getElementById("header-role-badge");
  const switchBtn = document.getElementById("switch-role-btn");

  if (roleControls && roleBadge && switchBtn) {
    if (currentRole) {
      roleControls.style.display = "inline-flex";
      roleBadge.textContent = currentRole === "citizen" ? t("role_citizen_badge") : t("role_reviewer_badge");
      roleBadge.className = "role-badge " + (currentRole === "citizen" ? "role-badge-citizen" : "role-badge-reviewer");
      switchBtn.textContent = t("switch_role_btn");
      switchBtn.setAttribute("aria-label", t("switch_role_btn"));
    } else {
      roleControls.style.display = "none";
    }
  }

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

// Bind global header buttons
document.getElementById("lang-toggle-btn").addEventListener("click", () => {
  setLanguage(currentLang === "bn" ? "en" : "bn");
});

const switchBtn = document.getElementById("switch-role-btn");
if (switchBtn) {
  switchBtn.addEventListener("click", () => {
    switchRole();
  });
}

// ---------------------------------------------------------------------------
// Badges and Helpers
// ---------------------------------------------------------------------------

function formatStatusBadge(statusCode) {
  const code = (statusCode || "").toUpperCase().trim();
  if (code === "CONTRADICTION") {
    return `<span class="badge badge-contradiction" aria-label="${t('status_contradiction')}"><span aria-hidden="true">✕</span> ${t('status_contradiction')}</span>`;
  } else if (code === "REVIEW") {
    return `<span class="badge badge-review" aria-label="${t('status_review')}"><span aria-hidden="true">⚠</span> ${t('status_review')}</span>`;
  } else if (code === "CONSISTENT") {
    return `<span class="badge badge-consistent" aria-label="${t('status_consistent')}"><span aria-hidden="true">✓</span> ${t('status_consistent')}</span>`;
  } else {
    const unknownLabel = t("status_unknown");
    return `<span class="badge badge-unknown" aria-label="${unknownLabel}"><span aria-hidden="true">?</span> ${unknownLabel}</span>`;
  }
}

// ---------------------------------------------------------------------------
// Router
// ---------------------------------------------------------------------------

function renderCurrentRoute() {
  const hash = window.location.hash || "#/";
  updateGlobalChrome();

  if (!currentRole) {
    renderRoleSelectScreen();
    return;
  }

  if (hash === "#/" || hash === "") {
    renderHomeScreen();
  } else if (hash === "#/parcels") {
    renderParcelsScreen();
  } else if (hash.startsWith("#/parcel/")) {
    const parcelId = hash.replace("#/parcel/", "").split("#")[0].split("?")[0];
    renderParcelDetailScreen(parcelId);
  } else if (hash === "#/benchmark") {
    if (currentRole === "reviewer") {
      renderBenchmarkScreen();
    } else {
      window.location.hash = "#/parcels";
    }
  } else {
    renderHomeScreen();
  }
}

window.addEventListener("hashchange", renderCurrentRoute);

// ---------------------------------------------------------------------------
// Screen: Role Selection Landing Screen (Item 1)
// ---------------------------------------------------------------------------

function renderRoleSelectScreen() {
  const root = document.getElementById("app-root");
  root.innerHTML = `
    <div class="role-landing-container">
      <div class="role-landing-header">
        <h1 class="hero-title">${t("role_select_title")}</h1>
        <div class="demo-notice-pill">
          <span aria-hidden="true">ℹ️</span>
          <span>${t("role_demo_notice")}</span>
        </div>
      </div>

      <div class="role-cards-grid">
        <!-- Card 1: Citizen / Buyer -->
        <div class="role-card role-card-citizen" tabindex="0">
          <div class="role-card-badge">${t("role_citizen_badge")}</div>
          <div class="role-card-icon" aria-hidden="true">👤</div>
          <h2 class="role-card-title">${t("role_citizen_title")}</h2>
          <p class="role-card-desc">${t("role_citizen_desc")}</p>
          <div class="demo-creds-box">
            <strong>${t("role_citizen_cred")}</strong>
          </div>
          <button type="button" class="btn-primary role-select-btn" id="btn-select-citizen">
            ${t("role_citizen_btn")} →
          </button>
        </div>

        <!-- Card 2: Land Office Reviewer -->
        <div class="role-card role-card-reviewer" tabindex="0">
          <div class="role-card-badge">${t("role_reviewer_badge")}</div>
          <div class="role-card-icon" aria-hidden="true">🏛️</div>
          <h2 class="role-card-title">${t("role_reviewer_title")}</h2>
          <p class="role-card-desc">${t("role_reviewer_desc")}</p>
          <div class="demo-creds-box">
            <strong>${t("role_reviewer_cred")}</strong>
          </div>
          <button type="button" class="btn-primary role-select-btn" id="btn-select-reviewer">
            ${t("role_reviewer_btn")} →
          </button>
        </div>
      </div>
    </div>
  `;

  document.getElementById("btn-select-citizen")?.addEventListener("click", () => setRole("citizen"));
  document.getElementById("btn-select-reviewer")?.addEventListener("click", () => setRole("reviewer"));
}

// ---------------------------------------------------------------------------
// Screen A: Home Screen
// ---------------------------------------------------------------------------

function renderHomeScreen() {
  const root = document.getElementById("app-root");
  root.innerHTML = `
    <div class="hero-section">
      <h1 class="hero-title">${t("app_title")}</h1>
      <p class="hero-desc">${t("app_subtitle")}</p>
      <div class="current-role-indicator">
        <span>${t("current_role_label")} <strong>${currentRole === "citizen" ? t("role_citizen_badge") : t("role_reviewer_badge")}</strong></span>
        <button type="button" class="btn-secondary btn-sm" id="home-switch-role-btn">${t("switch_role_btn")}</button>
      </div>
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

  document.getElementById("home-switch-role-btn")?.addEventListener("click", () => switchRole());
}

// ---------------------------------------------------------------------------
// Screen B: Parcel List Screen (Citizen & Reviewer with Search)
// ---------------------------------------------------------------------------

let cachedParcels = [];
let searchDebounceTimer = null;

async function renderParcelsScreen() {
  const root = document.getElementById("app-root");
  root.innerHTML = `
    <div class="parcel-detail-header">
      <h1 class="hero-title" style="text-align: left; margin-bottom: 0.5rem;">${t("nav_parcels")}</h1>
      <p style="color: var(--text-muted); margin: 0 0 1.25rem 0;">${t("card_parcels_desc")}</p>
    </div>

    <!-- Cross-Field Search Box -->
    <div class="search-section">
      <div class="search-input-wrap">
        <span class="search-icon" aria-hidden="true">🔍</span>
        <input type="text" id="parcel-search-input" class="search-input"
          placeholder="${t("search_placeholder")}" aria-label="${t("search_placeholder")}">
      </div>
      <div id="search-results-box" class="search-results-box" style="display: none;"></div>
    </div>

    <!-- Main Parcels List (Never shows planted/category tags) -->
    <div id="parcels-container" class="parcel-list-grid">
      <p style="color: var(--text-muted); padding: 2rem 0;">${t("loading_parcels")}</p>
    </div>
  `;

  const searchInput = document.getElementById("parcel-search-input");
  searchInput?.addEventListener("input", (e) => {
    clearTimeout(searchDebounceTimer);
    const query = e.target.value.trim();
    searchDebounceTimer = setTimeout(() => handleSearch(query), 200);
  });

  try {
    const res = await fetch(`/parcels?lang=${currentLang}`);
    if (!res.ok) throw new Error("Failed to fetch parcels");
    cachedParcels = await res.json();
    displayParcels(cachedParcels);
  } catch (err) {
    document.getElementById("parcels-container").innerHTML = `
      <div class="form-error-msg visible" role="alert">${t("error_simulate_failed")}</div>
    `;
  }
}

async function handleSearch(query) {
  const resultsBox = document.getElementById("search-results-box");
  if (!resultsBox) return;

  if (!query || query.length <= 1) {
    resultsBox.style.display = "none";
    resultsBox.innerHTML = "";
    displayParcels(cachedParcels);
    return;
  }

  try {
    const res = await fetch(`/search?q=${encodeURIComponent(query)}&lang=${currentLang}`);
    if (!res.ok) throw new Error("Search failed");
    const results = await res.json();

    if (results.length === 0) {
      resultsBox.style.display = "block";
      resultsBox.innerHTML = `
        <div class="search-result-empty">${t("no_parcels_found")}</div>
      `;
    } else {
      resultsBox.style.display = "block";
      resultsBox.innerHTML = `
        <div class="search-results-header">${t("search_results_title")} (${results.length})</div>
        <div class="search-results-list">
          ${results.map(r => `
            <a href="#/parcel/${r.id}" class="search-result-item">
              <div class="search-item-info">
                <span class="search-item-title">${r.label}</span>
                ${currentRole === "reviewer" ? `<span class="raw-id-badge">ID: ${r.id}</span>` : ""}
              </div>
              <span class="matched-on-tag">
                ${t("matched_on_prefix")} ${t("matched_" + r.matched_on) || r.matched_on}
              </span>
            </a>
          `).join("")}
        </div>
      `;
    }
  } catch (e) {
    resultsBox.style.display = "none";
  }
}

function displayParcels(parcels) {
  const container = document.getElementById("parcels-container");
  if (!container) return;

  if (parcels.length === 0) {
    container.innerHTML = `<p style="color: var(--text-muted); padding: 1.5rem 0;">${t("no_parcels_found")}</p>`;
    return;
  }

  // Never display planted or category fields (Addition 2)
  container.innerHTML = parcels.map(p => `
    <div class="parcel-item-card">
      <div class="parcel-card-main">
        <h2 class="parcel-info-title">
          <a href="#/parcel/${p.id}">${p.label}</a>
        </h2>
        ${currentRole === "reviewer" ? `<div class="parcel-info-meta"><span>ID: <code>${p.id}</code></span></div>` : ""}
      </div>
      <div class="parcel-actions">
        ${formatStatusBadge(p.status_code || p.status_summary_code)}
        <a href="#/parcel/${p.id}" class="btn-secondary btn-sm">${t("view_details")} →</a>
      </div>
    </div>
  `).join("");
}

// ---------------------------------------------------------------------------
// Screen C: Parcel Detail Screen (Citizen vs. Reviewer Mode)
// ---------------------------------------------------------------------------

let currentCytoscape = null;

async function renderParcelDetailScreen(parcelId) {
  const root = document.getElementById("app-root");
  root.innerHTML = `
    <div class="detail-top-nav">
      <a href="#/parcels" class="back-link">${t("back_to_parcels")}</a>
      <div class="detail-top-actions">
        <button type="button" class="btn-print" id="print-report-btn">
          🖨️ ${t("print_report_btn")}
        </button>
      </div>
    </div>
    <div id="parcel-detail-content">
      <p style="color: var(--text-muted); padding: 2rem 0;">${t("loading_parcel_details")}</p>
    </div>
    <div id="print-modal-container"></div>
  `;

  document.getElementById("print-report-btn")?.addEventListener("click", () => {
    openPrintReport(parcelId);
  });

  try {
    const res = await fetch(`/parcel/${encodeURIComponent(parcelId)}?lang=${currentLang}&role=${currentRole || "citizen"}`);
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

  const isCitizen = currentRole === "citizen";
  const parcelLabel = `${data.mouza} ${currentLang === "bn" ? "দাগ" : "Dag"} ${data.dag_no}`;

  // Summary description based on overall_status_code
  let summaryDesc = t("summary_consistent_desc");
  const osc = (data.overall_status_code || "").toUpperCase();
  if (osc === "CONTRADICTION") {
    summaryDesc = t("summary_contradiction_desc");
  } else if (osc === "REVIEW") {
    summaryDesc = t("summary_review_desc");
  }

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

  // Collect unique holders for the simulation form
  const holdersSet = new Map();
  (data.survey_records || []).forEach(sr => {
    (sr.holders || []).forEach(h => {
      if (!holdersSet.has(h.person_id)) {
        holdersSet.set(h.person_id, h.person_name || h.person_id);
      }
    });
  });
  const holderOptionsHtml = Array.from(holdersSet.entries()).map(([pid, name]) =>
    `<option value="${pid}">${name} ${isCitizen ? "" : `(${pid})`}</option>`
  ).join("");

  // Gather all downstream impacted event IDs across alerts (for Reviewer timeline highlighting)
  const allImpactedEventIds = new Set();
  if (!isCitizen && data.alerts) {
    data.alerts.forEach(a => {
      if (a.impact_event_ids) {
        a.impact_event_ids.forEach(eid => allImpactedEventIds.add(eid));
      }
    });
  }

  container.innerHTML = `
    <!-- Top Result Summary Card -->
    <div class="summary-card">
      <div class="summary-status-row">
        <div>
          <!-- Citizen sees human-readable label ONLY; Reviewer sees ID badge alongside -->
          <h1 class="summary-heading">
            ${parcelLabel}
            ${!isCitizen ? `<span class="raw-id-badge">ID: <code>${data.id}</code></span>` : ""}
          </h1>
          <p class="summary-desc">${summaryDesc}</p>
        </div>
        <div>
          ${formatStatusBadge(data.overall_status_code)}
        </div>
      </div>
      <div class="summary-meta-line">
        <span><strong>${currentLang === "bn" ? "দাগ নং:" : "Dag No:"}</strong> ${data.dag_no}</span> |
        <span><strong>${currentLang === "bn" ? "মৌজা:" : "Mouza:"}</strong> ${data.mouza}</span>
      </div>
    </div>

    <!-- Alert Cards Section -->
    <div class="alerts-section">
      <h2 class="section-title">${t("alerts_heading")}</h2>
      ${data.alerts.length === 0 ? `
        <div class="alert-card status-consistent">
          <div class="alert-header">
            <h3 class="alert-message">${t("summary_consistent_desc")}</h3>
            ${formatStatusBadge("CONSISTENT")}
          </div>
        </div>
      ` : data.alerts.map((alert, idx) => {
        const sc = (alert.status_code || "").toUpperCase();
        const statusClass = sc === "CONTRADICTION" ? "status-contradiction" :
                            sc === "REVIEW" ? "status-review" : "status-consistent";

        if (isCitizen) {
          // CITIZEN ALERT: Only status, message, recommended next step. NO rule_id, calculation, evidence_ids.
          return `
            <div class="alert-card ${statusClass}">
              <div class="alert-header">
                <h3 class="alert-message">${alert.message}</h3>
                ${formatStatusBadge(alert.status_code)}
              </div>
              <div class="alert-next-step">
                <strong>${t("next_step_label")}</strong> ${alert.recommended_next_step}
              </div>
              <div class="alert-rule-disclaimer">ℹ️ ${t("rule_disclaimer")}</div>
            </div>
          `;
        } else {
          // REVIEWER ALERT: Everything plus rule ID, calculation, evidence IDs, minimal evidence sets, impact list.
          const hasImpacts = alert.impact_event_ids && alert.impact_event_ids.length > 0;
          return `
            <div class="alert-card ${statusClass}">
              <div class="alert-header">
                <div>
                  <span class="rule-id-pill"><code>${alert.rule_id}</code></span>
                  <h3 class="alert-message" style="display: inline-block; margin-left: 0.5rem;">${alert.message}</h3>
                </div>
                ${formatStatusBadge(alert.status_code)}
              </div>
              <div class="alert-next-step">
                <strong>${t("next_step_label")}</strong> ${alert.recommended_next_step}
              </div>

              <!-- Technical reviewer audit details -->
              <div class="reviewer-audit-box">
                <div class="audit-row">
                  <strong>${t("calculation_label")}</strong>
                  <code class="audit-calc-text">${alert.calculation || "—"}</code>
                </div>
                <div class="audit-row">
                  <strong>${t("evidence_ids_label")}</strong>
                  <div class="evidence-tags-list">
                    ${(alert.evidence_ids || []).map(eid => `<span class="evidence-tag"><code>${eid}</code></span>`).join("")}
                  </div>
                </div>

                <!-- Minimal Evidence Sets -->
                ${alert.minimal_evidence_sets && alert.minimal_evidence_sets.length > 0 ? `
                  <div class="minimal-evidence-box">
                    <strong>${t("minimal_evidence_heading")}</strong>
                    ${alert.not_minimized ? `
                      <div class="not-minimized-alert">
                        ⚠️ ${t("not_minimized_warning")}
                      </div>
                    ` : ""}
                    <div class="minimal-sets-list">
                      ${alert.minimal_evidence_sets.map((mSet, sIdx) => `
                        <div class="minimal-set-row">
                          <span class="set-label">${alert.minimal_evidence_sets.length > 1 ? `${t("alt_set_label")} ${sIdx + 1}:` : ""}</span>
                          ${mSet.map(sid => `<span class="evidence-tag min-set-tag"><code>${sid}</code></span>`).join("")}
                        </div>
                      `).join("")}
                    </div>
                  </div>
                ` : ""}

                <!-- Downstream Impact List -->
                ${hasImpacts ? `
                  <div class="impact-box">
                    <strong>${t("impact_heading")}:</strong>
                    <div class="impact-items-list">
                      ${alert.impact_event_ids.map(impId => {
                        const ev = (data.events || []).find(e => e.id === impId);
                        if (ev) {
                          return `
                            <div class="impact-item-line">
                              <span class="impact-dot">⚠️</span>
                              <span>
                                📅 <strong>${ev.event_date || "—"}</strong> | <strong>${ev.type}</strong> |
                                ${t("col_from")}: ${ev.from_person_name || ev.from_person} ➔
                                ${t("col_to")}: ${ev.to_person_name || ev.to_person} |
                                ${t("col_area")}: ${formatAreaNumber(ev.area)} ${t("lab_decimals_unit")}
                                ${ev.deed_id ? `(${ev.deed_id})` : ""}
                              </span>
                            </div>
                          `;
                        } else {
                          return `<div class="impact-item-line"><span class="impact-dot">⚠️</span> <code>${impId}</code></div>`;
                        }
                      }).join("")}
                    </div>
                  </div>
                ` : (alert.status_code === "CONTRADICTION" || alert.status_code === "REVIEW" ? `
                  <div class="impact-box" style="color: var(--text-muted); font-size: 0.9rem;">
                    ${t("impact_empty")}
                  </div>
                ` : "")}
              </div>

              <div class="alert-rule-disclaimer">ℹ️ ${t("rule_disclaimer")}</div>
            </div>
          `;
        }
      }).join("")}
    </div>

    <!-- Chain of Title Graph Section (Reviewer only, omitted for Citizen) -->
    ${!isCitizen ? `
      <div class="graph-section">
        <h2 class="section-title">${t("graph_heading")}</h2>
        <div id="cy-container"></div>
      </div>
    ` : ""}

    <!-- Events Timeline Section -->
    <div class="timeline-section">
      <h2 class="section-title">${t("timeline_heading")}</h2>
      ${data.events.length === 0 ? `
        <p style="color: var(--text-muted);">${t("timeline_empty")}</p>
      ` : `
        <div class="stacked-records-list">
          ${data.events.map(ev => {
            const isImpacted = allImpactedEventIds.has(ev.id);
            return `
              <div class="timeline-row-card ${isImpacted ? "impacted-event-row" : ""}" id="timeline-row-${ev.id}">
                <div class="timeline-meta-row">
                  <span>
                    <strong>#${ev.seq} [${ev.type}]</strong>
                    ${!isCitizen ? `ID: <code>${ev.id}</code>` : ""}
                  </span>
                  <span>📅 ${ev.event_date || t("undated_label")}</span>
                </div>
                ${isImpacted ? `
                  <div class="impact-event-badge">
                    ⚠️ ${t("impacted_badge")}
                  </div>
                ` : ""}
                <div class="timeline-data-grid">
                  <div><strong>${t("col_from")}:</strong> ${ev.from_person_name || ev.from_person || "—"}</div>
                  <div><strong>${t("col_to")}:</strong> ${ev.to_person_name || ev.to_person || "—"}</div>
                  <div><strong>${t("col_area")}:</strong> ${formatAreaNumber(ev.area)} ${t("lab_decimals_unit")}</div>
                </div>
                ${ev.portion_id ? `<div style="font-size: 0.85rem; color: var(--text-light); margin-top: 0.25rem;"><strong>${t("col_portion")}:</strong> ${ev.portion_id}</div>` : ""}
              </div>
            `;
          }).join("")}
        </div>
      `}
    </div>

    <!-- Survey Records (Khatian) Section -->
    <div class="survey-section">
      <h2 class="section-title">${t("survey_heading")}</h2>
      <div class="stacked-records-list">
        ${(data.survey_records || []).map(sr => `
          <div class="timeline-row-card" id="survey-row-${sr.id}">
            <div class="timeline-meta-row">
              <span><strong>${sr.survey} ${t("survey_unit")}</strong> ${!isCitizen ? `(<code>${sr.id}</code>)` : ""}</span>
              <span>📅 ${sr.record_date}</span>
            </div>
            <div class="timeline-data-grid">
              <div><strong>${t("khatian_label")}</strong> ${formatAreaNumber(sr.khatian_no)}</div>
              <div><strong>${t("recorded_area_label")}</strong> ${formatAreaNumber(sr.recorded_area)} ${t("lab_decimals_unit")}</div>
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.9rem;">
              <strong>${t("holders_label")}</strong>
              <ul style="margin: 0.25rem 0 0 1.25rem; padding: 0;">
                ${sr.holders.map(h => `<li>${h.person_name} ${!isCitizen ? `(${h.person_id})` : ""} — ${formatAreaNumber(h.area)} ${t("lab_decimals_unit")}</li>`).join("")}
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
            ${holderOptionsHtml.length > 0 ? holderOptionsHtml : `<option value="H">Holder</option>`}
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
      <div id="lab-result-card" class="lab-result-card" role="region" aria-live="polite" style="display: none;">
        <div class="lab-result-header">
          <h3 style="margin: 0; font-size: 1.2rem;">${t("lab_result_heading")}</h3>
          <span class="integrity-badge">
            <span aria-hidden="true">🔒</span>
            ${t("lab_unchanged_badge")}
          </span>
        </div>
        <div id="lab-result-body"></div>
      </div>
    </div>
  `;

  // Attach interactive simulation form handler
  attachLabFormHandler(data.id, isCitizen);

  // Initialize Cytoscape graph for Reviewer only
  if (!isCitizen) {
    initializeCytoscape(data.graph);
  }
}

// ---------------------------------------------------------------------------
// Lab Form Submission & Role-Aware Rendering (Addition 1)
// ---------------------------------------------------------------------------

function attachLabFormHandler(parcelId, isCitizen) {
  const form = document.getElementById("lab-simulation-form");
  const errorBox = document.getElementById("lab-form-error");
  const resultCard = document.getElementById("lab-result-card");
  const resultBody = document.getElementById("lab-result-body");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorBox.textContent = "";
    errorBox.classList.remove("visible");

    const fromPerson = document.getElementById("lab-from-select").value.trim();
    const toPerson = document.getElementById("lab-to-input").value.trim();
    const areaVal = document.getElementById("lab-area-input").value.trim();
    const dateVal = document.getElementById("lab-date-input").value.trim() || null;
    const portionVal = document.getElementById("lab-portion-input").value.trim() || null;

    if (!fromPerson || !toPerson || !areaVal) {
      errorBox.textContent = t("error_empty_fields");
      errorBox.classList.add("visible");
      return;
    }

    // Check float rejection
    if (areaVal.includes(".")) {
      errorBox.textContent = t("error_float_area");
      errorBox.classList.add("visible");
      return;
    }

    const payload = {
      parcel_id: parcelId,
      from_person: fromPerson,
      to_person: toPerson,
      area: areaVal,
      event_date: dateVal,
      portion_id: portionVal,
      lang: currentLang
    };

    try {
      const res = await fetch(`/simulate?lang=${currentLang}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        errorBox.textContent = errJson.detail || t("error_simulate_failed");
        errorBox.classList.add("visible");
        return;
      }

      const simRes = await res.json();
      resultCard.style.display = "block";

      const firstAlert = simRes.alerts && simRes.alerts[0];
      const alertStatusCode = firstAlert ? firstAlert.status_code : (simRes.overall_status_code || "CONSISTENT");
      const nextStep = firstAlert ? firstAlert.recommended_next_step : "";

      if (isCitizen) {
        // CITIZEN LAB: Status, plain-language sentence with numbers in words/numerals, next step, unchanged badge.
        // NO rule ID, NO evidence IDs, NO calculation line. (Addition 1)
        const availBefore = simRes.seller_available_before;
        const excessVal = simRes.excess;
        let plainSentence = "";

        if (excessVal && excessVal !== "0" && !excessVal.startsWith("-")) {
          plainSentence = currentLang === "bn"
            ? `${t("lab_plain_excess_prefix")} ${toBanglaDigits(availBefore)} ${t("lab_decimals_unit")}${t("lab_plain_excess_mid")} ${toBanglaDigits(excessVal)} ${t("lab_decimals_unit")}।`
            : `${t("lab_plain_excess_prefix")}${availBefore} ${t("lab_decimals_unit")}${t("lab_plain_excess_mid")}${excessVal} ${t("lab_decimals_unit")}`;
        } else {
          plainSentence = t("lab_plain_consistent");
        }

        resultBody.innerHTML = `
          <div style="margin: 1rem 0;">
            ${formatStatusBadge(alertStatusCode)}
          </div>
          <div class="citizen-lab-sentence">
            <p style="font-size: 1.1rem; font-weight: 500; margin: 0.5rem 0;">${plainSentence}</p>
          </div>
          ${nextStep ? `
            <div class="alert-next-step" style="margin-top: 0.75rem;">
              <strong>${t("next_step_label")}</strong> ${nextStep}
            </div>
          ` : ""}
        `;
      } else {
        // REVIEWER LAB: Full detail with before/after stats, calculation line, rule ID, and evidence IDs.
        const isExcess = simRes.excess && simRes.excess !== "0" && !simRes.excess.startsWith("-");
        resultBody.innerHTML = `
          <div style="margin: 1rem 0;">
            ${formatStatusBadge(alertStatusCode)}
          </div>
          <div class="lab-result-data">
            <div class="result-stat-box">
              <div class="result-stat-label">${t("lab_before_label")}</div>
              <div class="result-stat-value">${formatAreaNumber(simRes.seller_available_before)} ${t("lab_decimals_unit")}</div>
            </div>
            <div class="result-stat-box">
              <div class="result-stat-label">${t("lab_change_label")}</div>
              <div class="result-stat-value">${formatAreaNumber(simRes.requested_area)} ${t("lab_decimals_unit")}</div>
            </div>
            <div class="result-stat-box">
              <div class="result-stat-label">${isExcess ? t("lab_excess_label") : t("lab_after_label")}</div>
              <div class="result-stat-value" style="color: ${isExcess ? "var(--status-contradiction-text)" : "inherit"}">
                ${isExcess ? `${t("lab_excess_prefix")} ${formatAreaNumber(simRes.excess)}` : `${t("lab_remaining_prefix")} ${formatAreaNumber(simRes.seller_available_after)}`} ${t("lab_decimals_unit")}
              </div>
            </div>
          </div>
          ${firstAlert && firstAlert.calculation ? `
            <div class="r1-calc-line">
              <strong>${t("lab_calc_label")}</strong> <span>${firstAlert.calculation}</span>
            </div>
          ` : ""}
          ${nextStep ? `
            <div class="alert-next-step" style="margin-top: 0.75rem;">
              <strong>${t("next_step_label")}</strong> ${nextStep}
            </div>
          ` : ""}
        `;
      }

      resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } catch (e) {
      errorBox.textContent = t("error_simulate_failed");
      errorBox.classList.add("visible");
    }
  });
}

// ---------------------------------------------------------------------------
// Screen D: Benchmark Screen (Reviewer only, Collapsed by default)
// ---------------------------------------------------------------------------

async function renderBenchmarkScreen() {
  const root = document.getElementById("app-root");
  root.innerHTML = `
    <div class="parcel-detail-header">
      <a href="#/parcels" class="back-link">${t("back_to_parcels")}</a>
      <h1 class="hero-title" style="text-align: left; margin: 0.5rem 0;">${t("benchmark_heading")}</h1>
      <p style="color: var(--text-muted);">${t("role_reviewer_badge")} — ${t("benchmark_integrity")}</p>
    </div>

    <!-- Reviewer-only, Collapsed by default (Addition 2) -->
    <details class="benchmark-details-card" open>
      <summary class="benchmark-summary-header">
        <h2 style="display: inline-block; font-size: 1.15rem; margin: 0;">${t("benchmark_toggle_title")}</h2>
      </summary>

      <div id="benchmark-content-box" style="padding-top: 1rem;">
        <p style="color: var(--text-muted);">${t("loading_benchmark")}</p>
      </div>
    </details>
  `;

  try {
    const res = await fetch("/benchmark");
    if (!res.ok) throw new Error("Failed to fetch benchmark");
    const data = await res.json();

    const box = document.getElementById("benchmark-content-box");
    if (!box) return;

    box.innerHTML = `
      <div class="benchmark-metrics-grid">
        <div class="metric-card">
          <div class="metric-num">${currentLang === "bn" ? toBanglaDigits(data.total_parcels) : data.total_parcels}</div>
          <div class="metric-label">${t("total_parcels_label")}</div>
        </div>
        <div class="metric-card">
          <div class="metric-num">${currentLang === "bn" ? toBanglaDigits(data.clean_false_alarm_count) : data.clean_false_alarm_count}</div>
          <div class="metric-label">${t("benchmark_false_alarms")}</div>
        </div>
        <div class="metric-card">
          <div class="metric-num">${currentLang === "bn" ? toBanglaDigits(data.planted_detected_count) : data.planted_detected_count} / ${currentLang === "bn" ? toBanglaDigits(data.planted_parcel_count) : data.planted_parcel_count}</div>
          <div class="metric-label">${t("planted_detected_label")}</div>
        </div>
      </div>

      <div class="benchmark-table-wrap">
        <h3 class="section-title" style="font-size: 1.1rem;">${t("benchmark_coverage")}</h3>
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
                <td>${row.has_planted_case ? `<span class="badge-tag tag-yes">${t("yes")}</span>` : `<span class="badge-tag tag-no">${t("no")}</span>`}</td>
                <td>${row.detected ? `<span class="badge-tag tag-yes">${t("yes")}</span>` : `<span class="badge-tag tag-no">${t("no")}</span>`}</td>
                <td>${formatStatusBadge(row.status_code)}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  } catch (e) {
    const box = document.getElementById("benchmark-content-box");
    if (box) box.innerHTML = `<div class="form-error-msg visible">${t("error_simulate_failed")}</div>`;
  }
}

// ---------------------------------------------------------------------------
// Print Report Functionality (Item 4 & Addition 3)
// ---------------------------------------------------------------------------

async function openPrintReport(parcelId) {
  try {
    const res = await fetch(`/report/${encodeURIComponent(parcelId)}?lang=${currentLang}&role=${currentRole || "citizen"}`);
    if (!res.ok) throw new Error("Failed to fetch report");
    const report = await res.json();

    const isCitizen = report.role === "citizen";
    const dateStr = new Date().toISOString().split("T")[0];

    const printContainer = document.getElementById("print-modal-container");
    if (!printContainer) return;

    printContainer.innerHTML = `
      <div class="print-document">
        <div class="print-header">
          <h1 class="print-title">${t("print_report_title")}</h1>
          <div class="print-meta-grid">
            <div><strong>${t("print_parcel_label")}</strong> ${report.parcel?.label || report.parcel_id}</div>
            <div><strong>${t("print_mouza_label")}</strong> ${report.parcel?.mouza || "—"}, <strong>${t("print_dag_no_label")}</strong> ${report.parcel?.dag_no || "—"}</div>
            <div><strong>${t("current_role_label")}</strong> ${report.role === "citizen" ? t("role_citizen_badge") : t("role_reviewer_badge")}</div>
            <div><strong>${t("print_generated_at")}</strong> ${dateStr}</div>
          </div>
        </div>

        <div class="print-overall-status">
          <strong>${t("print_overall_status_label")}</strong>
          ${formatStatusBadge(report.overall_status_code)}
        </div>

        <div class="print-section">
          <h2>${t("alerts_heading")}</h2>
          ${report.alerts.length === 0 ? `
            <p>${t("summary_consistent_desc")}</p>
          ` : report.alerts.map(a => `
            <div class="print-alert-item">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>${!isCitizen && a.rule_id ? `<strong>[${a.rule_id}]</strong> ` : ""}${a.message}</span>
                <span>${formatStatusBadge(a.status_code)}</span>
              </div>
              ${!isCitizen && a.calculation ? `<div style="font-size: 0.9rem; margin-top: 0.25rem;"><em>${a.calculation}</em></div>` : ""}
              ${a.recommended_next_step ? `<div style="margin-top: 0.25rem;"><strong>${t("next_step_label")}</strong> ${a.recommended_next_step}</div>` : ""}
            </div>
          `).join("")}
        </div>

        <div class="print-section">
          <h2>${t("timeline_heading")}</h2>
          ${report.records?.events?.length > 0 ? `
            <table class="print-table">
              <thead>
                <tr>
                  <th>${t("col_date")}</th>
                  <th>${t("col_type")}</th>
                  <th>${t("col_from")}</th>
                  <th>${t("col_to")}</th>
                  <th>${t("col_area")}</th>
                </tr>
              </thead>
              <tbody>
                ${report.records.events.map(ev => `
                  <tr>
                    <td>${ev.event_date || "—"}</td>
                    <td>${ev.type}</td>
                    <td>${ev.from_person_name || ev.from_person || "—"}</td>
                    <td>${ev.to_person_name || ev.to_person || "—"}</td>
                    <td>${formatAreaNumber(ev.area)}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          ` : `<p>${t("timeline_empty")}</p>`}
        </div>

        <div class="print-section">
          <h2>${t("survey_heading")}</h2>
          ${report.records?.survey_records?.length > 0 ? `
            <table class="print-table">
              <thead>
                <tr>
                  <th>${t("survey_unit")}</th>
                  <th>${t("khatian_label")}</th>
                  <th>${t("col_date")}</th>
                  <th>${t("recorded_area_label")}</th>
                  <th>${t("holders_label")}</th>
                </tr>
              </thead>
              <tbody>
                ${report.records.survey_records.map(sr => `
                  <tr>
                    <td>${sr.survey}</td>
                    <td>${formatAreaNumber(sr.khatian_no)}</td>
                    <td>${sr.record_date}</td>
                    <td>${formatAreaNumber(sr.recorded_area)}</td>
                    <td>${sr.holders.map(h => `${h.person_name} (${formatAreaNumber(h.area)})`).join(", ")}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          ` : `<p>—</p>`}
        </div>

        <div class="print-footer">
          <div class="print-disclaimer">
            <strong>${t("print_disclaimer_label")}</strong> ${report.disclaimer}
          </div>
          <div class="print-hash">
            <strong>${t("print_dataset_hash")}</strong> <code>${report.dataset_hash}</code>
          </div>
        </div>
      </div>
    `;

    window.print();
  } catch (e) {
    alert(t("error_simulate_failed"));
  }
}

// ---------------------------------------------------------------------------
// Cytoscape.js Initialization (Reviewer Only)
// ---------------------------------------------------------------------------

function initializeCytoscape(graphData) {
  const container = document.getElementById("cy-container");
  if (!container) return;

  if (typeof cytoscape === "undefined") {
    container.innerHTML = `<div class="cy-fallback-msg">${t("graph_fallback")}</div>`;
    return;
  }

  try {
    if (currentCytoscape) {
      currentCytoscape.destroy();
      currentCytoscape = null;
    }

    const elements = [];
    (graphData.nodes || []).forEach(n => {
      elements.push({
        data: {
          id: n.id,
          label: n.label,
          type: n.type,
          color: n.color || "#475569"
        }
      });
    });

    (graphData.edges || []).forEach(e => {
      elements.push({
        data: {
          id: e.id,
          source: e.source,
          target: e.target,
          label: e.label
        }
      });
    });

    currentCytoscape = cytoscape({
      container: container,
      elements: elements,
      style: [
        {
          selector: "node",
          style: {
            "label": "data(label)",
            "background-color": "data(color)",
            "color": "#0f172a",
            "font-size": "12px",
            "font-family": "Noto Sans Bengali, sans-serif",
            "text-valign": "bottom",
            "text-margin-y": 5,
            "width": 34,
            "height": 34
          }
        },
        {
          selector: "edge",
          style: {
            "width": 2,
            "line-color": "#94a3b8",
            "target-arrow-color": "#94a3b8",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "label": "data(label)",
            "font-size": "10px",
            "font-family": "Noto Sans Bengali, sans-serif",
            "color": "#475569"
          }
        }
      ],
      layout: {
        name: "cose",
        animate: false,
        padding: 20
      }
    });
  } catch (err) {
    container.innerHTML = `<div class="cy-fallback-msg">${t("graph_fallback")}</div>`;
  }
}

// Initial load
document.addEventListener("DOMContentLoaded", () => {
  renderCurrentRoute();
});
