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
    "lab_area_label": "বিক্রির পরিমাণ (শতক, যেমন ৫, ২.৫ বা ৭/২):",
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
    "lab_area_placeholder": "যেমন ৫, ২.৫ বা ৭/২",
    "error_area_not_positive": "পরিমাণ শূন্যের চেয়ে বেশি হতে হবে।",
    "error_area_format": "পূর্ণসংখ্যা (৫), দশমিক (২.৫) বা ভগ্নাংশ (৫/২) লিখুন।",
    "error_area_too_large": "পরিমাণটি অস্বাভাবিক বেশি। সংখ্যাটি আবার দেখুন।",
    "error_server_unreachable": "সার্ভারের সাথে যোগাযোগ করা যায়নি। সংযোগ দেখে আবার চেষ্টা করুন।",
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
    "proposed_buyer_label": "প্রস্তাবিত ক্রেতা",
    "nav_verify_deed": "দলিল যাচাই",
    "verify_screen_title": "দলিলের অনুলিপি ও ফিঙ্গারপ্রিন্ট যাচাই",
    "verify_screen_desc": "উপস্থাপিত দলিলের তথ্যাদি প্রবেশ করিয়ে রেজিস্ট্রি-সংরক্ষিত ফিঙ্গারপ্রিন্ট ও কিউআর যাচাই করুন।",
    "verify_disclaimer_notice": "এটি একটি গাণিতিক হ্যাশ যাচাইকরণ, কোনো আইনি ডিজিটাল স্বাক্ষর বা সরকারি নিবন্ধন সনদ নয়।",
    "verify_deed_no_label": "দলিল নম্বর:",
    "verify_reg_date_label": "নিবন্ধন তারিখ (YYYY-MM-DD):",
    "verify_parcel_id_label": "দাগ / প্লট আইডি:",
    "verify_seller_label": "বিক্রেতা:",
    "verify_buyer_label": "ক্রেতা:",
    "verify_area_label": "জমির পরিমাণ (শতক):",
    "verify_claimed_hash_label": "দাবি করা হ্যাশ / ফিঙ্গারপ্রিন্ট (ঐচ্ছিক):",
    "verify_btn_submit": "দলিল যাচাই করুন",
    "verify_qr_heading": "দলিল যাচাইকরণ কিউআর কোড",
    "verify_result_heading": "যাচাইকরণের ফলাফল",
    "verify_computed_hash_label": "গণনাকৃত ফিঙ্গারপ্রিন্ট (SHA-256):",
    "verify_recorded_hash_label": "সংরক্ষিত রেজিস্ট্রি ফিঙ্গারপ্রিন্ট:",
    "verify_loading": "দলিল যাচাই করা হচ্ছে...",
    "verify_error": "যাচাইকরণে ত্রুটি দেখা দিয়েছে। তথ্যের সঠিকতা পরীক্ষা করুন।",
    "lab_subdag_label": "উপ-দাগ বা খতিয়ান অংশ (ঐচ্ছিক):",
    "lab_boundary_legend": "চৌহদ্দি বা সীমানা নির্দেশক (ঐচ্ছিক)",
    "lab_boundary_north_label": "উত্তর সীমানা:",
    "lab_boundary_north_placeholder": "উত্তরে রাস্তা/নদী/দাগ...",
    "lab_boundary_south_label": "দক্ষিণ সীমানা:",
    "lab_boundary_south_placeholder": "দক্ষিণে দাগ/সীমানা...",
    "lab_boundary_east_label": "পূর্ব সীমানা:",
    "lab_boundary_east_placeholder": "পূর্বে দাগ/সীমানা...",
    "lab_boundary_west_label": "পশ্চিম সীমানা:",
    "lab_boundary_west_placeholder": "পশ্চিমে দাগ/সীমানা...",
    "coowner_quota_title": "এজমালি দাগের অংশীদারী হিস্যা ও কোটা",
    "traditional_share_disclaimer": "ঐতিহ্যবাহী হিস্যা একক (১৬ আনা = ১ সম্পূর্ণ অংশ)। রূপান্তর সারণি আইন উপদেষ্টার সাথে যাচাই সাপেক্ষ। এটি শুধুমাত্র প্রদর্শনের জন্য; স্বত্ব বা মালিকানার আইনি সনদ নয়।",
    "parcel_locked_badge": "লকড / সরকারি জমি",
    "parcel_lock_warning": "এই দাগে সরকারি বা আদালতের নিষেধাজ্ঞা রয়েছে। নতুন কোনো হস্তান্তর ব্লক করা হয়েছে।",
    "lab_locked_blocked_warning": "সতর্কতা: এই দাগে সরকারি বা আদালতের নিষেধাজ্ঞা রয়েছে। প্রস্তাবিত হস্তান্তর নিবন্ধনের জন্য অনুপযোগী।",
    "filter_khas": "খাস জমি",
    "filter_acquisition": "অধিগ্রহণাধীন",
    "filter_court": "আদালতের মামলা",
    "lab_poa_label": "আমমোক্তারনামা দলিল আইডি (প্রযোজ্য ক্ষেত্রে):",
    "lab_poa_placeholder": "উদা: E_V11_1001",
    "attention_score_label": "মনোযোগ স্কোর:",
    "traffic_light_label": "ঝুঁকির মাত্রা:",
    "score_factors_title": "মনোযোগ স্কোরে প্রভাব বিস্তারকারী বিষয়সমূহ:",
    "score_clean_expl": "০ স্কোর মানে সরবরাহকৃত রেকর্ডে কোনো ফ্ল্যাগ পাওয়া যায়নি; এটি জমি সম্পর্কে কোনো চূড়ান্ত নিশ্চয়তা নয়।",
    "voice_listen_btn": "ফলাফল শুনুন",
    "voice_stop_btn": "শব্দ থামান",
    "voice_fallback_msg": "এই ডিভাইসে বাংলা ভয়েস পাওয়া যায়নি; অনুগ্রহ করে স্ক্রিনের লেখাটি পড়ুন।",
    "voice_playing_msg": "বাংলায় পাঠ করা হচ্ছে...",
    "next_steps_guide_title": "কার্যকরী যাচাই ও পরবর্তী পদক্ষেপ:",
    "law_mentor_review_disclaimer": "যেকোনো আর্থিক বা প্রশাসনিক পদক্ষেপ নেওয়ার আগে একজন উপযুক্ত আইন বিশেষজ্ঞ বা ভূমি কর্মকর্তার পরামর্শ নিন।",
    "nav_ussd": "ফিচার-ফোন (USSD)",
    "ussd_simulator_title": "USSD / ফিচার-ফোন সিমুলেটর (*123*45#)",
    "ussd_simulator_desc": "ইন্টারনেটবিহীন সাধারণ মোবাইলের জন্য প্রদর্শনী সিমুলেটর। এটি কোনো প্রকৃত টেলিকম সেবা নয়।",
    "ussd_phone_frame_title": "মোবাইল স্ক্রিন (সর্বোচ্চ ১৬০ অক্ষর)",
    "ussd_send_btn": "পাঠান",
    "ussd_cancel_btn": "বাতিল",
    "ussd_reset_btn": "পুনরায় শুরু",
    "ussd_dial_placeholder": "পছন্দ বা ইনপুট লিখুন...",
    "nav_certificate": "যাচাইকরণ সনদ",
    "certificate_title": "ভূমির রেকর্ড পরামর্শমূলক যাচাইকরণ প্রত্যয়নপত্র",
    "certificate_subtitle": "সরবরাহকৃত ভূমি রেকর্ডের অনানুষ্ঠানিক পরামর্শমূলক সারসংক্ষেপ",
    "certificate_print_btn": "সনদ প্রিন্ট করুন",
    "certificate_advisory_notice": "এই প্রত্যয়নপত্রটি সরবরাহকৃত রেকর্ডের গাণিতিক ও নিয়মভিত্তিক সারসংক্ষেপ। এটি কোনো চূড়ান্ত মালিকানার নিশ্চয়তা দেয় না এবং সরকারি খতিয়ান বা দলিলের বিকল্প নয়।",
    "certificate_record_hash": "রেকর্ড যাচাইকরণ ফিঙ্গারপ্রিন্ট (SHA-256):",
    "certificate_qr_caption": "দলিল/রেকর্ড সঙ্গতি যাচাই করতে কিউআর কোড স্ক্যান করুন"
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
    "lab_area_label": "Transfer area (decimals, e.g. 5, 2.5 or 7/2):",
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
    "lab_area_placeholder": "e.g. 5, 2.5 or 7/2",
    "error_area_not_positive": "Area must be greater than zero.",
    "error_area_format": "Enter a whole number (5), a decimal (2.5) or a fraction (5/2).",
    "error_area_too_large": "That area is larger than any plausible parcel. Check the number.",
    "error_server_unreachable": "Could not reach the server. Check the connection and try again.",
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
    "proposed_buyer_label": "Proposed buyer",
    "nav_verify_deed": "Verify Deed",
    "verify_screen_title": "Deed Copy & Fingerprint Verification",
    "verify_screen_desc": "Enter presented deed details to verify against registry-recorded cryptographic fingerprint and QR.",
    "verify_disclaimer_notice": "This is a mathematical hash comparison, not a legal digital signature or government title guarantee.",
    "verify_deed_no_label": "Deed Number:",
    "verify_reg_date_label": "Registration Date (YYYY-MM-DD):",
    "verify_parcel_id_label": "Parcel ID:",
    "verify_seller_label": "Seller:",
    "verify_buyer_label": "Buyer:",
    "verify_area_label": "Area (decimals):",
    "verify_claimed_hash_label": "Claimed Hash / Fingerprint (Optional):",
    "verify_btn_submit": "Verify Deed Copy",
    "verify_qr_heading": "Deed Verification QR Code",
    "verify_result_heading": "Verification Result",
    "verify_computed_hash_label": "Computed Fingerprint (SHA-256):",
    "verify_recorded_hash_label": "Recorded Registry Fingerprint:",
    "verify_loading": "Verifying deed copy...",
    "verify_error": "Verification encountered an error. Please inspect supplied fields.",
    "lab_subdag_label": "Sub-dag or Lineage Portion (Optional):",
    "lab_boundary_legend": "Structured Boundary Descriptors (Optional)",
    "lab_boundary_north_label": "North Boundary:",
    "lab_boundary_north_placeholder": "Road / River / Dag to North...",
    "lab_boundary_south_label": "South Boundary:",
    "lab_boundary_south_placeholder": "Dag / Boundary to South...",
    "lab_boundary_east_label": "East Boundary:",
    "lab_boundary_east_placeholder": "Dag / Boundary to East...",
    "lab_boundary_west_label": "West Boundary:",
    "lab_boundary_west_placeholder": "Dag / Boundary to West...",
    "coowner_quota_title": "Ejmali Dag Co-Owner Share Breakdown & Quota",
    "traditional_share_disclaimer": "Traditional share units (16 Ana = 1 whole). Conversion table should be confirmed with the Law mentor. Display only; does not constitute legal proof of title.",
    "parcel_locked_badge": "Locked / Gov Land",
    "parcel_lock_warning": "This parcel is subject to government or court lock. New transactions are blocked.",
    "lab_locked_blocked_warning": "Warning: This parcel has a recorded government or court lock. Proposed transactions are blocked.",
    "filter_khas": "Khas Land",
    "filter_acquisition": "Under Acquisition",
    "filter_court": "Court Case",
    "lab_poa_label": "Power of Attorney ID (if applicable):",
    "lab_poa_placeholder": "e.g. E_V11_1001",
    "attention_score_label": "Attention Score:",
    "traffic_light_label": "Attention Level:",
    "score_factors_title": "Contributing Factors to Attention Score:",
    "score_clean_expl": "A score of 0 means no flags were found in the supplied records; it is not a guarantee about the land.",
    "voice_listen_btn": "Listen to Result",
    "voice_stop_btn": "Stop Audio",
    "voice_fallback_msg": "Bangla voice is not available on this device; please read the on-screen text.",
    "voice_playing_msg": "Playing Bangla speech...",
    "next_steps_guide_title": "Actionable Checks & Verification Steps:",
    "law_mentor_review_disclaimer": "Consult a law specialist or land administration officer before taking financial or administrative action.",
    "nav_ussd": "Feature-Phone (USSD)",
    "ussd_simulator_title": "USSD / Feature-Phone Simulator (*123*45#)",
    "ussd_simulator_desc": "Demonstration simulator for basic mobile devices without internet. Not a real telecom carrier service.",
    "ussd_phone_frame_title": "Mobile Screen (Max 160 Characters)",
    "ussd_send_btn": "Send",
    "ussd_cancel_btn": "Cancel",
    "ussd_reset_btn": "Restart",
    "ussd_dial_placeholder": "Enter choice or input...",
    "nav_certificate": "Vetting Certificate",
    "certificate_title": "Land Record Advisory Vetting Certificate",
    "certificate_subtitle": "Non-judicial advisory summary of supplied land records",
    "certificate_print_btn": "Print Certificate",
    "certificate_advisory_notice": "This document is a mathematical and rule-based summary generated from supplied records. It does not certify ownership or title, nor does it substitute for government deed registration or official record inquiry.",
    "certificate_record_hash": "Record Verification Fingerprint (SHA-256):",
    "certificate_qr_caption": "Scan QR code to verify deed/record consistency"
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

// Exact fraction string ("5/2", "-3/10", "7") -> readable decimal when the
// decimal terminates ("2.5"), otherwise the fraction itself. Integer-only
// arithmetic, so no floating-point rounding is involved.
function fractionToDisplay(val) {
  const m = /^(-?)(\d+)(?:\/(\d+))?$/.exec(String(val).trim());
  if (!m) return String(val);
  const sign = m[1];
  const num = BigInt(m[2]);
  const den = m[3] ? BigInt(m[3]) : 1n;
  if (den === 0n) return String(val);
  if (den === 1n) return sign + num.toString();
  for (let k = 1; k <= 6; k++) {
    const scale = 10n ** BigInt(k);
    if ((num * scale) % den === 0n) {
      const scaled = ((num * scale) / den).toString().padStart(k + 1, "0");
      const cut = scaled.length - k;
      const out = scaled.slice(0, cut) + "." + scaled.slice(cut);
      return sign + out.replace(/0+$/, "").replace(/\.$/, "");
    }
  }
  return sign + num.toString() + "/" + den.toString();
}

function formatAreaNumber(val) {
  if (val === null || val === undefined) return "—";
  const shown = fractionToDisplay(val);
  return currentLang === "bn" ? toBanglaDigits(shown) : shown;
}

// Area text typed by a person -> { ok: true } or { ok: false, key: <string key> }.
// Mirrors the server rules in area_input.py so errors appear instantly.
function checkAreaInput(raw) {
  const bn = "০১২৩৪৫৬৭৮৯";
  const text = String(raw).trim().replace(/[০-৯]/g, d => String(bn.indexOf(d)));
  if (!text) return { ok: false, key: "error_empty_fields" };
  let m;
  let positive;
  if ((m = /^(-?\d+)\s*\/\s*(\d+)$/.exec(text))) {
    if (/^0+$/.test(m[2])) return { ok: false, key: "error_area_format" };
    positive = BigInt(m[1]) > 0n;
  } else if ((m = /^(-?)\d+(\.\d+)?$/.exec(text))) {
    positive = !m[1] && /[1-9]/.test(text);
  } else {
    return { ok: false, key: "error_area_format" };
  }
  if (!positive) return { ok: false, key: "error_area_not_positive" };
  if (text.length > 40) return { ok: false, key: "error_area_too_large" };
  return { ok: true };
}

// FastAPI 422 bodies carry detail as a list. Pull out our AREA_* code and map
// it to a localised string; anything else falls back to the generic message.
function errorKeyFromResponse(errJson) {
  const raw = JSON.stringify(errJson || {});
  const code = /AREA_[A-Z_]+/.exec(raw);
  const map = {
    AREA_EMPTY: "error_empty_fields",
    AREA_FORMAT: "error_area_format",
    AREA_FLOAT_TYPE: "error_area_format",
    AREA_NOT_POSITIVE: "error_area_not_positive",
    AREA_TOO_LARGE: "error_area_too_large"
  };
  return (code && map[code[0]]) || "error_simulate_failed";
}

function formatPortionId(portionId, isCitizen) {
  if (!portionId) return "";
  if (!isCitizen) return `<code>${portionId}</code>`;

  const clean = String(portionId).trim().replace(/^PORTION_/i, "");

  const bnMap = {
    "NORTH": "উত্তর অংশ",
    "SOUTH": "দক্ষিণ অংশ",
    "EAST": "পূর্ব অংশ",
    "WEST": "পশ্চিম অংশ",
    "ALPHA": "ক (আলফা)",
    "BETA": "খ (বিটা)",
    "GAMMA": "গ (গামা)",
    "A": "ক",
    "B": "খ",
    "C": "গ",
    "DAG": "দাগ"
  };

  const enMap = {
    "NORTH": "North portion",
    "SOUTH": "South portion",
    "EAST": "East portion",
    "WEST": "West portion",
    "ALPHA": "Alpha",
    "BETA": "Beta",
    "GAMMA": "Gamma",
    "A": "A",
    "B": "B",
    "C": "C",
    "DAG": "Dag"
  };

  if (currentLang === "bn") {
    const up = clean.toUpperCase();
    if (bnMap[up]) return bnMap[up];
    return clean.split("_").map(w => bnMap[w.toUpperCase()] || toBanglaDigits(w)).join(" ");
  } else {
    const up = clean.toUpperCase();
    if (enMap[up]) return enMap[up];
    return clean.split("_").map(w => enMap[w.toUpperCase()] || (w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())).join(" ");
  }
}

// ---------------------------------------------------------------------------
// Global Chrome Update (Header, Disclaimer, Nav, Footer, Role Controls)
// ---------------------------------------------------------------------------

function updateGlobalChrome() {
  document.getElementById("brand-title").textContent = t("app_title");
  document.getElementById("brand-subtitle").textContent = t("app_subtitle");
  document.getElementById("disclaimer-banner").textContent = t("disclaimer_banner");

  // Navigation Links: Hidden until a role is chosen (Step 2)
  const navContainer = document.querySelector(".nav-links");
  if (navContainer) {
    navContainer.style.display = currentRole ? "flex" : "none";
  }

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
  if (window.extraChrome) window.extraChrome(hash);

  if (!currentRole) {
    renderRoleSelectScreen();
    return;
  }

  if (window.extraRoute && window.extraRoute(hash)) {
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
    const res = await fetch(`/parcels?lang=${currentLang}&role=${currentRole || "citizen"}`);
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
        ${p.is_locked ? `<span class="badge" style="background:#581c87; color:#f3e8ff;" title="${t("parcel_locked_badge")}">🔒 ${t("parcel_locked_badge")}</span>` : ""}
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

function speakResult(textToSpeak) {
  const feedbackEl = document.getElementById("voice-feedback-area");
  if (!('speechSynthesis' in window) || typeof SpeechSynthesisUtterance === 'undefined') {
    if (feedbackEl) {
      feedbackEl.textContent = t("voice_fallback_msg");
      feedbackEl.style.display = "block";
    }
    return;
  }

  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
    const btn = document.getElementById("btn-voice-read");
    if (btn) btn.innerHTML = `🔊 ${t("voice_listen_btn")}`;
    if (feedbackEl) feedbackEl.style.display = "none";
    return;
  }

  const voices = (window.speechSynthesis.getVoices && window.speechSynthesis.getVoices()) || [];
  let selectedVoice = null;
  if (currentLang === "bn") {
    selectedVoice = voices.find(v => v.lang === "bn-BD" || (v.lang && v.lang.toLowerCase() === "bn-bd")) ||
                    voices.find(v => v.lang === "bn-IN" || (v.lang && v.lang.toLowerCase() === "bn-in")) ||
                    voices.find(v => v.lang && v.lang.toLowerCase().startsWith("bn"));
  } else {
    selectedVoice = voices.find(v => v.lang && v.lang.toLowerCase().startsWith("en"));
  }

  if (currentLang === "bn" && !selectedVoice) {
    if (feedbackEl) {
      feedbackEl.textContent = t("voice_fallback_msg");
      feedbackEl.style.display = "block";
    }
    return;
  }

  try {
    const utter = new SpeechSynthesisUtterance(textToSpeak);
    if (selectedVoice) {
      utter.voice = selectedVoice;
      utter.lang = selectedVoice.lang;
    } else {
      utter.lang = currentLang === "bn" ? "bn-BD" : "en-US";
    }

    const btn = document.getElementById("btn-voice-read");
    utter.onstart = () => {
      if (btn) btn.innerHTML = `⏹️ ${t("voice_stop_btn")}`;
      if (feedbackEl) {
        feedbackEl.textContent = t("voice_playing_msg");
        feedbackEl.style.display = "block";
      }
    };
    utter.onend = () => {
      if (btn) btn.innerHTML = `🔊 ${t("voice_listen_btn")}`;
      if (feedbackEl) feedbackEl.style.display = "none";
    };
    utter.onerror = () => {
      if (btn) btn.innerHTML = `🔊 ${t("voice_listen_btn")}`;
      if (feedbackEl) {
        feedbackEl.textContent = t("voice_fallback_msg");
        feedbackEl.style.display = "block";
      }
    };

    window.speechSynthesis.speak(utter);
  } catch (e) {
    if (feedbackEl) {
      feedbackEl.textContent = t("voice_fallback_msg");
      feedbackEl.style.display = "block";
    }
  }
}

async function renderParcelDetailScreen(parcelId) {
  const root = document.getElementById("app-root");
  root.innerHTML = `
    <div class="detail-top-nav">
      <a href="#/parcels" class="back-link">${t("back_to_parcels")}</a>
      <div class="detail-top-actions">
        <button type="button" class="btn-print" id="print-cert-btn" aria-label="${t("certificate_print_btn")}">
          📜 ${t("certificate_print_btn")}
        </button>
        <button type="button" class="btn-print" id="print-report-btn">
          🖨️ ${t("print_report_btn")}
        </button>
      </div>
    </div>
    <div id="parcel-detail-content">
      <p style="color: var(--text-muted); padding: 2rem 0;">${t("loading_parcel_details")}</p>
    </div>
  `;

  document.getElementById("print-report-btn")?.addEventListener("click", () => {
    openPrintReport(parcelId);
  });
  document.getElementById("print-cert-btn")?.addEventListener("click", () => {
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
  const primaryKhatian = (data.survey_records && data.survey_records.length > 0)
    ? (data.survey_records[data.survey_records.length - 1].khatian_no || data.survey_records[0].khatian_no)
    : "";
  const khatianDisplay = primaryKhatian
    ? (currentLang === "bn" ? toBanglaDigits(primaryKhatian) : primaryKhatian)
    : "";
  const dagDisplay = currentLang === "bn" ? toBanglaDigits(data.dag_no) : data.dag_no;

  const reviewerTitle = khatianDisplay
    ? `${data.mouza} ${currentLang === "bn" ? "দাগ" : "Dag"} ${dagDisplay} · ${currentLang === "bn" ? "খতিয়ান" : "Khatian"} ${khatianDisplay}`
    : `${data.mouza} ${currentLang === "bn" ? "দাগ" : "Dag"} ${dagDisplay}`;

  const citizenTitle = `${data.mouza} ${currentLang === "bn" ? "দাগ" : "Dag"} ${dagDisplay}`;
  const pageTitle = isCitizen ? citizenTitle : reviewerTitle;

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
          <!-- Title: Citizen sees Mouza + Dag; Reviewer sees Mouza + Dag + Khatian (no raw ID in title) -->
          <h1 class="summary-heading">
            ${pageTitle}
          </h1>
          <p class="summary-desc">${summaryDesc}</p>
        </div>
        <div>
          ${formatStatusBadge(data.overall_status_code)}
        </div>
      </div>
      <div class="summary-meta-line">
        <span><strong>${currentLang === "bn" ? "দাগ নং:" : "Dag No:"}</strong> ${dagDisplay}</span> |
        <span><strong>${currentLang === "bn" ? "মৌজা:" : "Mouza:"}</strong> ${data.mouza}</span>
        ${khatianDisplay ? ` | <span><strong>${currentLang === "bn" ? "খতিয়ান নং:" : "Khatian No:"}</strong> ${khatianDisplay}</span>` : ""}
      </div>
      ${!isCitizen ? `
        <details class="technical-details-card">
          <summary class="technical-details-summary">🛠️ ${t("tech_details_summary")}</summary>
          <div class="technical-details-content">
            <div><strong>${t("tech_system_id")}</strong> <code>${data.id}</code></div>
            ${data.parent_id ? `<div><strong>${t("tech_parent_id")}</strong> <code>${data.parent_id}</code></div>` : ""}
          </div>
        </details>
      ` : ""}
      ${data.is_locked ? `
        <div class="parcel-lock-banner" role="alert" style="background: rgba(107, 33, 168, 0.12); border-left: 4px solid #6b21a8; padding: 1rem; margin-top: 1rem; border-radius: 4px;">
          <strong style="color: #6b21a8;">🔒 ${t("parcel_locked_badge")}:</strong>
          <span>${t("parcel_lock_warning")}</span>
        </div>
      ` : ""}

      <!-- X2: Offline Voice Control -->
      <div class="summary-voice-row" style="margin-top: 1rem; display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
        <button type="button" class="btn-voice" id="btn-voice-read" aria-label="${t("voice_listen_btn")}">
          🔊 ${t("voice_listen_btn")}
        </button>
        <div id="voice-feedback-area" class="voice-feedback" aria-live="polite" style="display: none;"></div>
      </div>

      <!-- F18: Deterministic Attention Score Card -->
      <div class="attention-score-card">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-weight: 600; font-size: 1rem;">${t("attention_score_label")}</span>
            <span class="score-badge score-${data.traffic_light || 'green'}">
              ${currentLang === "bn" ? toBanglaDigits(data.attention_score ?? 0) : (data.attention_score ?? 0)}/100
            </span>
          </div>
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="font-size: 0.85rem; color: var(--text-muted);">${t("traffic_light_label")}</span>
            <span class="traffic-indicator traffic-${data.traffic_light || 'green'}" title="${data.traffic_light}"></span>
            <strong style="text-transform: capitalize; font-size: 0.9rem; color: ${data.traffic_light === 'red' ? '#dc2626' : data.traffic_light === 'yellow' ? '#ca8a04' : '#16a34a'};">${data.traffic_light || 'green'}</strong>
          </div>
        </div>

        ${isCitizen ? `
          <p class="score-citizen-sentence" style="margin: 0.5rem 0; font-size: 0.95rem; line-height: 1.5;">${esc(data.score_summary || t("score_clean_expl"))}</p>
        ` : `
          <div class="score-reviewer-factors" style="margin: 0.5rem 0;">
            <h4 style="margin: 0 0 0.35rem 0; font-size: 0.95rem; font-weight: 600;">${t("score_factors_title")}</h4>
            ${(data.score_factors && data.score_factors.length > 0) ? `
              <ul style="margin: 0 0 0.5rem 1.25rem; padding: 0; font-size: 0.9rem;">
                ${data.score_factors.map(f => `<li>${esc(f)}</li>`).join("")}
              </ul>
            ` : `<p style="margin: 0; font-size: 0.9rem;">${t("score_clean_expl")}</p>`}
          </div>
        `}
        <p class="score-disclaimer" style="margin: 0.5rem 0 0 0; font-size: 0.8rem; color: var(--text-muted);"><small>ℹ️ ${esc(data.score_disclaimer || t("score_clean_expl"))}</small></p>
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
                            sc === "REVIEW" ? "status-review" :
                            sc === "CONSISTENT" ? "status-consistent" : "status-unknown";

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
              ${alert.actionable_checks && alert.actionable_checks.length > 0 ? `
                <div class="actionable-checks-box">
                  <div class="actionable-checks-title">${t("next_steps_guide_title")}</div>
                  <ul class="actionable-checks-list">
                    ${alert.actionable_checks.map(c => `<li>${esc(c)}</li>`).join("")}
                  </ul>
                  <div class="actionable-disclaimer">ℹ️ ${t("law_mentor_review_disclaimer")}</div>
                </div>
              ` : ""}
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
              ${alert.actionable_checks && alert.actionable_checks.length > 0 ? `
                <div class="actionable-checks-box">
                  <div class="actionable-checks-title">${t("next_steps_guide_title")}</div>
                  <ul class="actionable-checks-list">
                    ${alert.actionable_checks.map(c => `<li>${esc(c)}</li>`).join("")}
                  </ul>
                  <div class="actionable-disclaimer">ℹ️ ${t("law_mentor_review_disclaimer")}</div>
                </div>
              ` : ""}

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
            const eventTypeLabel = t("event_type_" + (ev.type || "").toLowerCase()) || ev.type;
            const seqDisplay = currentLang === "bn" ? toBanglaDigits(ev.seq) : ev.seq;
            return `
              <div class="timeline-row-card ${isImpacted ? "impacted-event-row" : ""}" id="timeline-row-${ev.id}">
                <div class="timeline-meta-row">
                  <span>
                    <strong>#${seqDisplay} [${eventTypeLabel}]</strong>
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
                ${ev.portion_id ? `<div style="font-size: 0.85rem; color: var(--text-light); margin-top: 0.25rem;"><strong>${t("col_portion")}:</strong> ${formatPortionId(ev.portion_id, isCitizen)}</div>` : ""}
                ${ev.deed_id ? `
                  <div style="margin-top: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <a href="#/verify-deed?deed_no=${encodeURIComponent(ev.deed_id)}&parcel_id=${encodeURIComponent(data.id)}&area=${encodeURIComponent(ev.area || '')}&seller=${encodeURIComponent(ev.from_person_name || ev.from_person || '')}&buyer=${encodeURIComponent(ev.to_person_name || ev.to_person || '')}&date=${encodeURIComponent(ev.event_date || '')}" style="font-size: 0.85rem; text-decoration: none; color: #0369a1; font-weight: 500; display: inline-flex; align-items: center; gap: 0.25rem;">
                      📜 ${currentLang === 'bn' ? 'দলিল যাচাই ও কিউআর →' : 'Verify Deed & QR →'}
                    </a>
                  </div>
                ` : ""}
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
                ${sr.holders.map(h => `<li>${h.person_name} ${!isCitizen ? `(${h.person_id})` : ""} — ${formatAreaNumber(h.area)} ${t("lab_decimals_unit")}${h.traditional_share ? ` <span class="share-badge" style="color:var(--text-muted); font-size:0.85em;">[${h.traditional_share}]</span>` : ""}</li>`).join("")}
              </ul>
            </div>
          </div>
        `).join("")}
      </div>
      ${(!isCitizen && data.coowner_quotas && data.coowner_quotas.length > 1) ? `
        <div class="coowner-quota-card" style="margin-top: 1rem; padding: 1rem; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md);">
          <h3 style="margin-top:0; margin-bottom: 0.5rem; font-size: 1rem; color: var(--primary);">${t("coowner_quota_title")}</h3>
          <table class="data-table" style="width: 100%; font-size: 0.85rem; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 1px solid var(--border-color); text-align: left;">
                <th style="padding: 0.4rem;">${t("col_from")}</th>
                <th style="padding: 0.4rem;">${t("col_area")}</th>
                <th style="padding: 0.4rem;">${t("col_portion")}</th>
              </tr>
            </thead>
            <tbody>
              ${data.coowner_quotas.map(cq => `
                <tr style="border-bottom: 1px solid var(--border-color);">
                  <td style="padding: 0.4rem;"><strong>${cq.person_name || cq.person_id}</strong> (<code>${cq.person_id}</code>)</td>
                  <td style="padding: 0.4rem;">${formatAreaNumber(cq.quota_limit)} ${t("lab_decimals_unit")}</td>
                  <td style="padding: 0.4rem;">${cq.traditional_share}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
          ${data.traditional_share_disclaimer ? `<p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.5rem; margin-bottom: 0;">ℹ️ ${data.traditional_share_disclaimer}</p>` : ""}
        </div>
      ` : ""}
    </div>

    <!-- Simulation Lab Section -->
    <div class="lab-section" id="simulation-lab">
      <div class="lab-header">
        <h2 class="section-title" style="margin-bottom: 0.25rem;">${t("lab_heading")}</h2>
        <p style="color: var(--text-muted); margin: 0;">${t("lab_desc")}</p>
      </div>

      <form id="lab-simulation-form" class="lab-form" novalidate>
        ${data.is_locked ? `
          <div class="lab-locked-alert" style="margin-bottom: 1rem; padding: 0.75rem 1rem; background: rgba(107, 33, 168, 0.1); border-left: 4px solid #6b21a8; border-radius: var(--radius-sm); color: #6b21a8;">
            <strong>🔒 ${t("parcel_locked_badge")}:</strong> ${t("lab_locked_blocked_warning")}
          </div>
        ` : ""}

        <div class="form-group">
          <label for="lab-from-select" class="form-label">${t("lab_from_label")}</label>
          <select id="lab-from-select" class="form-select" required>
            ${holderOptionsHtml.length > 0 ? holderOptionsHtml : `<option value="H">Holder</option>`}
          </select>
        </div>

        <div class="form-group">
          <label for="lab-to-input" class="form-label">${t("lab_to_label")}</label>
          <input type="text" id="lab-to-input" class="form-input" value="${t("proposed_buyer_label")}" placeholder="${t("proposed_buyer_label")}" readonly>
        </div>

        <div class="form-group">
          <label for="lab-area-input" class="form-label">${t("lab_area_label")}</label>
          <input type="text" id="lab-area-input" class="form-input" placeholder="${t("lab_area_placeholder")}" inputmode="decimal" autocomplete="off" required>
        </div>

        <div class="form-group">
          <label for="lab-date-input" class="form-label">${t("lab_date_label")}</label>
          <input type="date" id="lab-date-input" class="form-input" value="${defaultSimDate}" required>
        </div>

        <div class="form-group">
          <label for="lab-portion-input" class="form-label">${t("lab_portion_label")}</label>
          <input type="text" id="lab-portion-input" class="form-input" placeholder="PORTION_A">
        </div>

        <div class="form-group">
          <label for="lab-subdag-input" class="form-label">${t("lab_subdag_label")}</label>
          <input type="text" id="lab-subdag-input" class="form-input" placeholder="101/1-ka">
        </div>

        <div class="form-group">
          <label for="lab-poa-input" class="form-label">${t("lab_poa_label")}</label>
          <input type="text" id="lab-poa-input" class="form-input" placeholder="${t("lab_poa_placeholder")}">
        </div>

        <fieldset class="form-fieldset" style="border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 0.75rem; margin-bottom: 1rem;">
          <legend style="font-weight: 600; font-size: 0.85rem; padding: 0 0.25rem; color: var(--text-muted);">${t("lab_boundary_legend")}</legend>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
            <div class="form-group" style="margin-bottom: 0.25rem;">
              <label for="lab-boundary-north" class="form-label" style="font-size: 0.8rem;">${t("lab_boundary_north_label")}</label>
              <input type="text" id="lab-boundary-north" class="form-input" placeholder="${t("lab_boundary_north_placeholder")}">
            </div>
            <div class="form-group" style="margin-bottom: 0.25rem;">
              <label for="lab-boundary-south" class="form-label" style="font-size: 0.8rem;">${t("lab_boundary_south_label")}</label>
              <input type="text" id="lab-boundary-south" class="form-input" placeholder="${t("lab_boundary_south_placeholder")}">
            </div>
            <div class="form-group" style="margin-bottom: 0.25rem;">
              <label for="lab-boundary-east" class="form-label" style="font-size: 0.8rem;">${t("lab_boundary_east_label")}</label>
              <input type="text" id="lab-boundary-east" class="form-input" placeholder="${t("lab_boundary_east_placeholder")}">
            </div>
            <div class="form-group" style="margin-bottom: 0.25rem;">
              <label for="lab-boundary-west" class="form-label" style="font-size: 0.8rem;">${t("lab_boundary_west_label")}</label>
              <input type="text" id="lab-boundary-west" class="form-input" placeholder="${t("lab_boundary_west_placeholder")}">
            </div>
          </div>
        </fieldset>

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

  // Attach voice reader listener
  const voiceBtn = document.getElementById("btn-voice-read");
  if (voiceBtn) {
    const speechText = isCitizen
      ? `${pageTitle}। ${summaryDesc}। ${data.score_summary || ""}`
      : `${pageTitle}। ${summaryDesc}। ${t("attention_score_label")} ${data.attention_score}।`;
    voiceBtn.addEventListener("click", () => {
      speakResult(speechText);
    });
  }

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
  const submitBtn = document.getElementById("lab-submit-btn");
  if (!form) return;

  const showError = (key) => {
    resultCard.style.display = "none";
    resultBody.innerHTML = "";
    errorBox.textContent = t(key);
    errorBox.classList.add("visible");
  };
  const clearError = () => {
    errorBox.textContent = "";
    errorBox.classList.remove("visible");
  };

  form.addEventListener("reset", () => {
    clearError();
    resultCard.style.display = "none";
    resultBody.innerHTML = "";
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError();

    const fromPerson = document.getElementById("lab-from-select").value.trim();
    const areaVal = document.getElementById("lab-area-input").value.trim();
    const dateVal = document.getElementById("lab-date-input").value.trim() || null;
    const portionVal = document.getElementById("lab-portion-input").value.trim() || null;
    const subdagInput = document.getElementById("lab-subdag-input");
    const subdagVal = subdagInput ? subdagInput.value.trim() || null : null;
    const northInput = document.getElementById("lab-boundary-north");
    const northVal = northInput ? northInput.value.trim() || null : null;
    const southInput = document.getElementById("lab-boundary-south");
    const southVal = southInput ? southInput.value.trim() || null : null;
    const eastInput = document.getElementById("lab-boundary-east");
    const eastVal = eastInput ? eastInput.value.trim() || null : null;
    const westInput = document.getElementById("lab-boundary-west");
    const westVal = westInput ? westInput.value.trim() || null : null;
    const poaInput = document.getElementById("lab-poa-input");
    const poaVal = poaInput ? poaInput.value.trim() || null : null;

    if (!fromPerson) {
      showError("error_empty_fields");
      return;
    }
    const check = checkAreaInput(areaVal);
    if (!check.ok) {
      showError(check.key);
      return;
    }

    const payload = {
      parcel_id: parcelId,
      from_person: fromPerson,
      to_person: "P_BUYER_SIM",
      area: areaVal,
      date: dateVal,
      portion_id: portionVal,
      sub_dag: subdagVal,
      boundary_north: northVal,
      boundary_south: southVal,
      boundary_east: eastVal,
      boundary_west: westVal,
      via_poa_id: poaVal,
      lang: currentLang
    };

    if (submitBtn) submitBtn.disabled = true;
    try {
      const role = isCitizen ? "citizen" : "reviewer";
      const res = await fetch(`/simulate?lang=${currentLang}&role=${role}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        showError(errorKeyFromResponse(errJson));
        return;
      }

      const simRes = await res.json();
      resultCard.style.display = "block";

      const alerts = simRes.alerts || [];
      const targetAlert =
        alerts.find(a => a.status_code === "CONTRADICTION") ||
        alerts.find(a => a.status_code === "REVIEW") ||
        alerts[0] || null;
      const alertStatusCode = simRes.overall_status_code || simRes.status_code || (targetAlert ? targetAlert.status_code : "CONSISTENT");
      const nextStep = targetAlert ? targetAlert.recommended_next_step : "";
      const hasExcess = !!simRes.excess && simRes.excess !== "0" && !simRes.excess.startsWith("-");

      if (isCitizen) {
        // CITIZEN LAB: status, one plain sentence, next step. No rule ID,
        // no evidence IDs, no calculation line.
        let plainSentence = "";
        if (hasExcess) {
          const before = formatAreaNumber(simRes.seller_available_before);
          const excess = formatAreaNumber(simRes.excess);
          plainSentence = currentLang === "bn"
            ? `${t("lab_plain_excess_prefix")} ${before} ${t("lab_decimals_unit")}${t("lab_plain_excess_mid")} ${excess} ${t("lab_decimals_unit")}।`
            : `${t("lab_plain_excess_prefix")}${before} ${t("lab_decimals_unit")}${t("lab_plain_excess_mid")}${excess} ${t("lab_decimals_unit")}`;
        } else if (alertStatusCode !== "CONSISTENT" && targetAlert && targetAlert.message) {
          plainSentence = targetAlert.message;
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
          ${simRes.attention_score !== undefined ? `
            <div class="attention-score-card" style="margin-top: 1rem; padding: 0.75rem 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                  <strong>${t("attention_score_label")}</strong>
                  <span class="score-badge score-${simRes.traffic_light || 'green'}">
                    ${currentLang === "bn" ? toBanglaDigits(simRes.attention_score) : simRes.attention_score}/100
                  </span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.4rem;">
                  <span style="font-size: 0.85rem; color: var(--text-muted);">${t("traffic_light_label")}</span>
                  <span class="traffic-indicator traffic-${simRes.traffic_light || 'green'}"></span>
                  <strong style="text-transform: capitalize; color: ${simRes.traffic_light === 'red' ? '#dc2626' : simRes.traffic_light === 'yellow' ? '#ca8a04' : '#16a34a'};">${simRes.traffic_light || 'green'}</strong>
                </div>
              </div>
              <p style="font-size: 0.9rem; margin: 0.4rem 0 0 0;">${esc(simRes.score_summary || t("score_clean_expl"))}</p>
              <p style="font-size: 0.75rem; color: var(--text-muted); margin: 0.4rem 0 0 0;"><small>ℹ️ ${esc(simRes.score_disclaimer || t("score_clean_expl"))}</small></p>
            </div>
          ` : ""}
          ${nextStep ? `
            <div class="alert-next-step" style="margin-top: 0.75rem;">
              <strong>${t("next_step_label")}</strong> ${nextStep}
            </div>
          ` : ""}
        `;
      } else {
        // REVIEWER LAB: before/after numbers, calculation line, next step.
        // Show the transfer arithmetic for consistent and excess cases; for other
        // contradictions (for example R2) show that rule's own calculation.
        const calcText = ((hasExcess || alertStatusCode === "CONSISTENT") && simRes.r1_calculation)
          ? simRes.r1_calculation
          : (targetAlert && targetAlert.calculation) || "";
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
              <div class="result-stat-label">${hasExcess ? t("lab_excess_label") : t("lab_after_label")}</div>
              <div class="result-stat-value" style="color: ${hasExcess ? "var(--status-contradiction-text)" : "inherit"}">
                ${hasExcess ? `${t("lab_excess_prefix")} ${formatAreaNumber(simRes.excess)}` : `${t("lab_remaining_prefix")} ${formatAreaNumber(simRes.seller_available_after)}`} ${t("lab_decimals_unit")}
              </div>
            </div>
          </div>
          ${calcText ? `
            <div class="r1-calc-line">
              <strong>${t("lab_calc_label")}</strong> <span>${calcText}</span>
            </div>
          ` : ""}
          ${simRes.attention_score !== undefined ? `
            <div class="attention-score-card" style="margin-top: 1rem; padding: 0.75rem 1rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                  <strong>${t("attention_score_label")}</strong>
                  <span class="score-badge score-${simRes.traffic_light || 'green'}">
                    ${currentLang === "bn" ? toBanglaDigits(simRes.attention_score) : simRes.attention_score}/100
                  </span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.4rem;">
                  <span style="font-size: 0.85rem; color: var(--text-muted);">${t("traffic_light_label")}</span>
                  <span class="traffic-indicator traffic-${simRes.traffic_light || 'green'}"></span>
                  <strong style="text-transform: capitalize; color: ${simRes.traffic_light === 'red' ? '#dc2626' : simRes.traffic_light === 'yellow' ? '#ca8a04' : '#16a34a'};">${simRes.traffic_light || 'green'}</strong>
                </div>
              </div>
              <div style="font-size: 0.85rem; margin-top: 0.4rem;">
                <strong>${t("score_factors_title")}</strong>
                ${(simRes.score_factors && simRes.score_factors.length > 0) ? `
                  <ul style="margin: 0.2rem 0 0 1.25rem; padding: 0;">
                    ${simRes.score_factors.map(f => `<li>${esc(f)}</li>`).join("")}
                  </ul>
                ` : `<p style="margin: 0;">${t("score_clean_expl")}</p>`}
              </div>
              <p style="font-size: 0.75rem; color: var(--text-muted); margin: 0.4rem 0 0 0;"><small>ℹ️ ${esc(simRes.score_disclaimer || t("score_clean_expl"))}</small></p>
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
    } catch (err) {
      showError("error_server_unreachable");
    } finally {
      if (submitBtn) submitBtn.disabled = false;
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

    <!-- Reviewer-only, Collapsed by default -->
    <details class="benchmark-details-card">
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

    const totalParcels = data.total_parcels !== undefined ? data.total_parcels : (data.coverage_table ? data.coverage_table.length : 0);
    const plantedRows = (data.coverage_table || []).filter(r => r.has_planted_case);
    const plantedTotal = data.planted_parcel_count !== undefined ? data.planted_parcel_count : plantedRows.length;
    const plantedDetected = data.planted_detected_count !== undefined ? data.planted_detected_count : plantedRows.filter(r => r.detected).length;

    box.innerHTML = `
      <div class="benchmark-metrics-grid">
        <div class="metric-card">
          <div class="metric-num">${currentLang === "bn" ? toBanglaDigits(totalParcels) : totalParcels}</div>
          <div class="metric-label">${t("total_parcels_label")}</div>
        </div>
        <div class="metric-card">
          <div class="metric-num">${currentLang === "bn" ? toBanglaDigits(data.clean_false_alarm_count) : data.clean_false_alarm_count}</div>
          <div class="metric-label">${t("benchmark_false_alarms").replace(/:$/, "")}</div>
        </div>
        <div class="metric-card">
          <div class="metric-num">${currentLang === "bn" ? toBanglaDigits(plantedDetected) : plantedDetected} / ${currentLang === "bn" ? toBanglaDigits(plantedTotal) : plantedTotal}</div>
          <div class="metric-label">${t("planted_detected_label")}</div>
        </div>
        <div class="metric-card">
          <div class="metric-num">${data.simulation_integrity && data.simulation_integrity.unchanged ? "✓" : "✗"}</div>
          <div class="metric-label">${t("benchmark_integrity")}</div>
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

      ${data.simulation_integrity ? `
        <div class="integrity-hashes-box" style="margin-top: 1.25rem; font-size: 0.85rem; color: var(--text-muted); background: var(--bg-hover); padding: 0.85rem; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
          <div style="font-weight: 600; margin-bottom: 0.4rem; color: var(--text-main);">${t("benchmark_integrity")}</div>
          <div><strong>${t("hash_before_label")}</strong> <code>${data.simulation_integrity.dataset_hash_before}</code></div>
          <div><strong>${t("hash_after_label")}</strong> <code>${data.simulation_integrity.dataset_hash_after}</code></div>
          <div style="margin-top: 0.35rem; color: var(--success); font-weight: 600;">✓ ${t("hash_match_label")}</div>
        </div>
      ` : ""}
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
  const printContainer = document.getElementById("print-modal-container");
  if (!printContainer) {
    const errorMsg = currentLang === "bn"
      ? "ত্রুটি: প্রিন্ট কন্টেইনার (#print-modal-container) পাওয়া যায়নি।"
      : "Error: Print container (#print-modal-container) is missing from DOM.";
    console.error(errorMsg);
    let errBanner = document.getElementById("print-error-banner");
    if (!errBanner) {
      errBanner = document.createElement("div");
      errBanner.id = "print-error-banner";
      errBanner.className = "form-error-msg visible";
      errBanner.setAttribute("role", "alert");
      const root = document.getElementById("app-root") || document.body;
      root.prepend(errBanner);
    }
    errBanner.textContent = errorMsg;
    return;
  }

  try {
    const res = await fetch(`/report/${encodeURIComponent(parcelId)}?lang=${currentLang}&role=${currentRole || "citizen"}`);
    if (!res.ok) throw new Error("Failed to fetch report");
    const report = await res.json();

    const isCitizen = report.role === "citizen";
    const dateStr = new Date().toISOString().split("T")[0];

    let certQrSvg = "";
    if (typeof qrcode !== "undefined" && report.certificate_qr_payload) {
      try {
        const qr = qrcode(0, "M");
        qr.addData(report.certificate_qr_payload);
        qr.make();
        certQrSvg = qr.createSvgTag(3, 2);
      } catch (e) {
        certQrSvg = "";
      }
    }

    printContainer.innerHTML = `
      <div class="print-document">
        <div class="print-certificate-banner">
          <h1 style="margin: 0 0 0.25rem 0; font-size: 1.5rem; text-transform: uppercase;">${t("certificate_title")}</h1>
          <p style="margin: 0 0 0.5rem 0; font-size: 0.95rem; color: #475569;">${t("certificate_subtitle")}</p>
          <div style="font-size: 0.85rem; border-top: 1px dashed #94a3b8; padding-top: 0.5rem; font-style: italic;">
            ${t("certificate_advisory_notice")}
          </div>
        </div>

        <div class="print-header">
          <div class="print-meta-grid">
            <div><strong>${t("print_parcel_label")}</strong> ${report.parcel?.label || report.parcel_id} ${!isCitizen ? `<code>(${report.parcel_id})</code>` : ""}</div>
            <div><strong>${t("print_mouza_label")}</strong> ${report.parcel?.mouza || "—"}, <strong>${t("print_dag_no_label")}</strong> ${report.parcel?.dag_no || "—"}</div>
            <div><strong>${t("current_role_label")}</strong> ${report.role === "citizen" ? t("role_citizen_badge") : t("role_reviewer_badge")}</div>
            <div><strong>${t("print_generated_at")}</strong> ${dateStr}</div>
          </div>
        </div>

        <div class="print-overall-status" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
          <div>
            <strong>${t("print_overall_status_label")}</strong>
            <span style="margin-left: 0.5rem;">${formatStatusBadge(report.overall_status_code)}</span>
            <span style="margin-left: 0.5rem; font-weight: 600;">${report.overall_status}</span>
          </div>
        </div>

        <!-- Attention Score Section -->
        <div class="print-section" style="border: 1px solid #cbd5e1; padding: 0.75rem; border-radius: 4px; background: #f8fafc;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
            <div>
              <strong>${t("attention_score_label")}</strong>
              <span style="font-size: 1.2rem; font-weight: 700; margin-left: 0.4rem;">
                ${currentLang === "bn" ? toBanglaDigits(report.attention_score ?? 0) : (report.attention_score ?? 0)}/100
              </span>
            </div>
            <div>
              <span>${t("traffic_light_label")}: </span>
              <strong style="text-transform: capitalize;">${report.traffic_light || "green"}</strong>
            </div>
          </div>
          ${isCitizen ? `
            <p style="margin: 0.25rem 0 0 0; font-size: 0.95rem;">${report.score_summary || t("score_clean_expl")}</p>
          ` : `
            <div style="font-size: 0.9rem;">
              <strong>${t("score_factors_title")}</strong>
              ${(report.score_factors && report.score_factors.length > 0) ? `
                <ul style="margin: 0.25rem 0 0 1.25rem; padding: 0;">
                  ${report.score_factors.map(f => `<li>${f}</li>`).join("")}
                </ul>
              ` : `<p style="margin: 0;">${t("score_clean_expl")}</p>`}
            </div>
          `}
          <div style="margin-top: 0.4rem; font-size: 0.8rem; color: #64748b;">
            <small>ℹ️ ${report.score_disclaimer || t("score_clean_expl")}</small>
          </div>
        </div>

        <!-- QR Verification Section -->
        ${certQrSvg ? `
          <div class="certificate-qr-box">
            <div class="certificate-qr-svg">${certQrSvg}</div>
            <div>
              <div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 0.25rem;">${t("certificate_qr_caption")}</div>
              <div style="font-family: monospace; font-size: 0.8rem; color: #334155;">${report.certificate_qr_payload}</div>
              <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.35rem;">
                ${currentLang === "bn" ? "অফলাইন কিউআর কোড স্ক্যান করে উপস্থাপিত দলিলের ডিজিটাল ফিঙ্গারপ্রিন্ট মিলিয়ে দেখুন।" : "Scan offline QR code to verify deed/record cryptographic hash match."}
              </div>
            </div>
          </div>
        ` : ""}

        ${report.recommended_next_steps && report.recommended_next_steps.length > 0 ? `
          <div class="print-section">
            <h2>${t("next_step_label")}</h2>
            <ul class="print-next-steps-list">
              ${report.recommended_next_steps.map(step => `<li>${step}</li>`).join("")}
            </ul>
          </div>
        ` : ""}

        <div class="print-section">
          <h2>${t("alerts_heading")}</h2>
          ${report.alerts.length === 0 ? `
            <p>${t("summary_consistent_desc")}</p>
          ` : report.alerts.map(a => `
            <div class="print-alert-item">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>
                  ${!isCitizen && a.rule_id ? `<strong class="print-rule-id">[${a.rule_id}]</strong> ` : ""}
                  ${a.message}
                </span>
                <span>${formatStatusBadge(a.status_code)}</span>
              </div>

              ${!isCitizen && a.calculation ? `
                <div class="print-alert-calc">
                  <strong>${currentLang === "bn" ? "হিসাব:" : "Calculation:"}</strong> <em>${a.calculation}</em>
                </div>
              ` : ""}

              ${!isCitizen && a.evidence_ids && a.evidence_ids.length > 0 ? `
                <div class="print-alert-evidence">
                  <strong>${currentLang === "bn" ? "প্রাসঙ্গিক প্রমাণাদি:" : "Evidence IDs:"}</strong>
                  ${a.evidence_ids.map(eid => `<code>${eid}</code>`).join(", ")}
                </div>
              ` : ""}

              ${!isCitizen && a.minimal_evidence_sets && a.minimal_evidence_sets.length > 0 ? `
                <div class="print-minimal-evidence">
                  <strong>${t("minimal_evidence_heading")}</strong>
                  ${a.not_minimized ? `
                    <span class="print-warning">⚠️ ${t("not_minimized_warning")}</span>
                  ` : ""}
                  <div style="margin-top: 0.25rem;">
                    ${a.minimal_evidence_sets.map((mSet, sIdx) => `
                      <div>
                        ${a.minimal_evidence_sets.length > 1 ? `<span>${t("alt_set_label")} ${sIdx + 1}:</span> ` : ""}
                        ${mSet.map(sid => `<code>${sid}</code>`).join(", ")}
                      </div>
                    `).join("")}
                  </div>
                </div>
              ` : ""}

              ${!isCitizen && a.impact_event_ids && a.impact_event_ids.length > 0 ? `
                <div class="print-alert-impacts">
                  <strong>${t("impact_heading")}:</strong>
                  <ul class="print-impacts-list" style="margin: 0.25rem 0 0 1.25rem; padding: 0;">
                    ${a.impact_event_ids.map(impId => {
                      const ev = (report.records?.events || []).find(e => e.id === impId);
                      if (ev) {
                        const evType = t("event_type_" + (ev.type || "").toLowerCase()) || ev.type;
                        const fromP = ev.from_person_name || ev.from_person || "—";
                        const toP = ev.to_person_name || ev.to_person || "—";
                        const areaStr = formatAreaNumber(ev.area);
                        return `<li>⚠️ 📅 ${ev.event_date || "—"} | <strong>${evType}</strong> | ${t("col_from")}: ${fromP} ➔ ${t("col_to")}: ${toP} | ${t("col_area")}: ${areaStr} ${t("lab_decimals_unit")} ${ev.deed_id ? `(${ev.deed_id})` : ""}</li>`;
                      } else {
                        return `<li>⚠️ <code>${impId}</code></li>`;
                      }
                    }).join("")}
                  </ul>
                </div>
              ` : ""}

              ${a.recommended_next_step ? `
                <div style="margin-top: 0.35rem;">
                  <strong>${t("next_step_label")}</strong> ${a.recommended_next_step}
                </div>
              ` : ""}
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
                  ${!isCitizen ? `<th>ID</th>` : ""}
                </tr>
              </thead>
              <tbody>
                ${report.records.events.map(ev => `
                  <tr>
                    <td>${ev.event_date || "—"}</td>
                    <td>${t("event_type_" + (ev.type || "").toLowerCase()) || ev.type}</td>
                    <td>${ev.from_person_name || ev.from_person || "—"}</td>
                    <td>${ev.to_person_name || ev.to_person || "—"}</td>
                    <td>${formatAreaNumber(ev.area)} ${t("lab_decimals_unit")}</td>
                    ${!isCitizen ? `<td><code>${ev.id}</code></td>` : ""}
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
                  ${!isCitizen ? `<th>ID</th>` : ""}
                </tr>
              </thead>
              <tbody>
                ${report.records.survey_records.map(sr => `
                  <tr>
                    <td>${sr.survey}</td>
                    <td>${formatAreaNumber(sr.khatian_no)}</td>
                    <td>${sr.record_date}</td>
                    <td>${formatAreaNumber(sr.recorded_area)} ${t("lab_decimals_unit")}</td>
                    <td>${sr.holders.map(h => `${h.person_name}${!isCitizen ? ` (${h.person_id})` : ""} (${formatAreaNumber(h.area)} ${t("lab_decimals_unit")})`).join(", ")}</td>
                    ${!isCitizen ? `<td><code>${sr.id}</code></td>` : ""}
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
    console.error("Failed to generate print report:", e);
    let errBanner = document.getElementById("print-error-banner");
    if (!errBanner) {
      errBanner = document.createElement("div");
      errBanner.id = "print-error-banner";
      errBanner.className = "form-error-msg visible";
      errBanner.setAttribute("role", "alert");
      const root = document.getElementById("app-root") || document.body;
      root.prepend(errBanner);
    }
    errBanner.textContent = t("error_simulate_failed") || "Failed to load report for printing.";
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

    // The API sends Cytoscape-style elements: { data: { id, label, type, ... } }.
    const nodeColors = { parcel: "#1e40af", survey_record: "#047857", person: "#475569" };
    const elements = [];
    (graphData.nodes || []).forEach(n => {
      const d = n.data || n;
      const baseColor = (d.type === "parcel" && d.is_locked) ? "#6b21a8" : (nodeColors[d.type] || "#475569");
      elements.push({
        data: { id: d.id, label: d.label, type: d.type, color: baseColor }
      });
    });

    (graphData.edges || []).forEach(e => {
      const d = e.data || e;
      elements.push({
        data: { id: d.id, source: d.source, target: d.target, label: d.label, type: d.type }
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
            "text-margin-y": 6,
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
            "color": "#475569",
            "text-background-color": "#ffffff",
            "text-background-opacity": 0.85,
            "text-background-padding": "2px"
          }
        },
        { selector: 'edge[type = "SALE"], edge[type = "GIFT"], edge[type = "SUBDIVIDE"]', style: { "line-color": "#b45309", "target-arrow-color": "#b45309", "width": 3 } },
        { selector: 'edge[type = "MORTGAGE"], edge[type = "MORTGAGE_RELEASE"]', style: { "line-color": "#dc2626", "target-arrow-color": "#dc2626", "width": 2 } },
        { selector: 'edge[type = "POA_GRANT"], edge[type = "POA_REVOKE"]', style: { "line-color": "#7c3aed", "target-arrow-color": "#7c3aed", "width": 2 } }
      ],
      layout: {
        name: "breadthfirst",
        directed: true,
        spacingFactor: 1.7,
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
