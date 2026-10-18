"""
JomiGraph AI — Rule-Specific Next-Step Guides (X3)
=================================================
Provides 2–4 concrete, actionable documentary checks for every rule (R1–R15),
plus general parcel history hygiene.

Invariants:
  - Never fabricate government fees, deadlines, or official procedures.
  - Frame items as documentary checks, not legal advice.
  - Include the standard legal mentor review disclaimer.
  - Strict fallback for unknown rule IDs (never return undefined keys).
  - 100% parity across English and Bengali.
  - Zero forbidden words (safe, valid, legal, verified owner, fraud, forged, scam, you will be cheated, জালিয়াতি, আইনগত, বৈধ).
"""

from __future__ import annotations

from typing import Any

DISCLAIMER_LAW_MENTOR_EN = (
    "Notice: These steps are documentary verification checks for preliminary review; "
    "to be confirmed by the Law mentor and property counsel."
)
DISCLAIMER_LAW_MENTOR_BN = (
    "সতর্কবার্তা: এই পদক্ষেপসমূহ প্রাথমিক পর্যালোচনার জন্য তথ্যভিত্তিক নির্দেশিকা; "
    "আইন বিশেষজ্ঞ ও পরামর্শকের মাধ্যমে নিশ্চিত করা প্রয়োজন।"
)

# Rule-specific concrete steps in English
RULE_NEXT_STEPS_EN: dict[str, list[str]] = {
    "R1": [
        "Request certified copies of prior sale deeds and khatian distributions from the Sub-Registry office.",
        "Verify the seller's cumulative previous transfers to confirm remaining acreage.",
        "Consult the local land revenue office (AC Land) to verify current mutation records.",
    ],
    "R2": [
        "Inspect registered deed schedules to verify portion/plot numbering and lineage links.",
        "Request field verification with a local survey Amin to identify physical boundaries.",
        "Examine earlier transfer deeds for conflicting claims over the same holding.",
    ],
    "R3": [
        "Ask the seller to produce their recorded title deeds, inheritance sanad, or registered khatian.",
        "Verify whether the seller's name was omitted due to pending mutation or unrecorded succession.",
        "Consult an authorized property advisor or land reviewer before proceeding.",
    ],
    "R4": [
        "Check subdivision (খারিজ) khatians against the original parent parcel area.",
        "Request a certified demarcation sketch or trace map from the land survey office.",
        "Reconcile area discrepancies with co-sharers or the revenue office.",
    ],
    "R5": [
        "Search for the linking registered deeds connecting CS, SA, RS, and BS survey records.",
        "Inspect mutation (নামজারি) porcha and DCR receipts establishing chain of possession.",
        "Verify if intermediate transfers were executed through family partition or gift.",
    ],
    "R6": [
        "Compare the transferred area stated on the deed with the recorded mutation khatian area.",
        "Verify mutation case records at the Upazila Land Office.",
        "Request explanation from the seller regarding any unmutated portion.",
    ],
    "R7": [
        "Check the exact registration date of the deed against the mutation order sheet date.",
        "Verify if mutation was opened under an earlier registered agreement or deed.",
        "Review the original land office order sheet to clarify timeline discrepancies.",
    ],
    "R8": [
        "Verify the registered succession certificate (warish sanad) at the issuing local council.",
        "Check sub-registry records for any registered release deed (না-দাবি), gift, or sale by the co-heir.",
        "Inspect subsequent survey khatians (RS/BS/namjari) to confirm whether all declared heirs were recorded.",
    ],
    "R9": [
        "Ask the seller to provide a formal bank non-encumbrance / lien clearance certificate (না-দাবি সনদ).",
        "Search deed registers and mortgage volumes at the Sub-Registry office for active hypothecation.",
        "Confirm full debt satisfaction and redemption registration before entering into a transfer.",
    ],
    "R10": [
        "Inspect the Power of Attorney revocation register at the concerned Sub-Registry office.",
        "Confirm the principal (original owner) is alive and verify their direct written consent.",
        "Verify that the specific parcel and transfer authorization are explicitly covered in the power of attorney.",
    ],
    "R11": [
        "Inspect AC Land office records and local land revenue register to verify khas status or acquisition notices.",
        "Check District Collectorate acquisition gazettes if acquisition proceedings are indicated.",
        "Inquire at the relevant civil court regarding the status of any pending suit or injunction order.",
    ],
    "R12": [
        "Verify the presented physical deed copy directly against the original registry volume.",
        "Check the official Sub-Registrar seal, volume number, page number, and registration serial.",
        "Consult the Sub-Registry office to obtain an official certified true copy (সহি-মহুরি নকল).",
    ],
    "R13": [
        "Inspect Sub-Registry registers to verify whether the deed legitimately covers multiple parcels.",
        "Verify that registration date, parties, and consideration are identical across all scheduled dags.",
        "If terms differ, seek clarification from the Sub-Registry office regarding volume cross-referencing.",
    ],
    "R14": [
        "Verify National Identity cards (NID) and parents' names for parties sharing identical names.",
        "Inspect citizenship/warish certificates issued by the local Union Parishad or Ward Councilor.",
        "Cross-reference voter lists and holding tax receipts to confirm the exact person identity.",
    ],
    "R15": [
        "Inspect the official mouza map and compare boundary descriptors (north, south, east, west).",
        "Conduct an on-site survey with an experienced licensed Amin to measure physical plot borders.",
        "Review adjacent plot deeds to ensure the seller has not previously alienated the same physical piece.",
    ],
    "HYGIENE": [
        "Inspect undated events or ungrounded cancellations in parcel history.",
        "Obtain dated registration slips for all transactions lacking explicit dates.",
        "Reconcile historical records with the revenue circle inspector.",
    ],
}

# Rule-specific concrete steps in Bengali
RULE_NEXT_STEPS_BN: dict[str, list[str]] = {
    "R1": [
        "সাব-রেজিস্ট্রি অফিস থেকে বিক্রেতার পূর্ববর্তী বায়া দলিল ও খতিয়ান বণ্টনের সহি-মহুরি নকল সংগ্রহ করুন।",
        "বিক্রেতার ইতিপূর্বে হস্তান্তরিত মোট জমির পরিমাণ হিসাব করে অবশিষ্ট অংশ যাচাই করুন।",
        "সহকারী কমিশনার (ভূমি) বা ইউনিয়ন ভূমি অফিসে গিয়ে নামজারি ও জমাভাগ রেকর্ড মিলিয়ে নিন।",
    ],
    "R2": [
        "রেজিস্ট্রিকৃত দলিলের তফসিল পরীক্ষা করে প্লট/হোল্ডিং নম্বর ও হস্তান্তরের ধারাবাহিকতা যাচাই করুন।",
        "স্থানীয় সার্ভেয়ার (আমিন) দ্বারা সরেজমিনে দাগের সীমানা ও অংশ চিহ্নিত করুন।",
        "একই অংশের উপর পূর্ববর্তী কোনো রেজিস্ট্রিকৃত হস্তান্তর দলিল রয়েছে কিনা তা তল্লাশি দিন।",
    ],
    "R3": [
        "বিক্রেতার রেকর্ডভুক্ত মালিকানার দলিল, ওয়ারিশ সনদ বা নামজারি খতিয়ান প্রদর্শন করতে বলুন।",
        "নামজারি অসমাপ্ত থাকার কারণে বা অরেকর্ডকৃত ওয়ারিশের কারণে নাম বাদ পড়েছে কিনা তা যাচাই করুন।",
        "পরবর্তী পদক্ষেপের পূর্বে সংশ্লিষ্ট ভূমি কর্মকর্তা বা পরামর্শকের সাথে পর্যালোচনা করুন।",
    ],
    "R4": [
        "মূল দাগের মোট পরিমাণের সাথে খারিজকৃত খতিয়ানসমূহের মোট পরিমাণ মিলিয়ে নিন।",
        "ভূমি জরিপ অফিস থেকে ডিমারকেশন স্কেচ বা মৌজা নকশার ট্রেস সংগ্রহ করুন।",
        "অংশীদারদের সাথে বা সহকারী কমিশনার (ভূমি) অফিসে পরিমাপের ফারাক নিরসন করুন।",
    ],
    "R5": [
        "সিএস, এসএ, আরএস ও বিএস খতিয়ানের মধ্যবর্তী যোগসূত্র স্থাপনকারী রেজিস্ট্রিকৃত দলিলসমূহ অনুসন্ধান করুন।",
        "দখল ও ধারাবাহিকতা প্রমাণের জন্য নামজারি পর্চা ও ডিসিআর দাখিলা যাচাই করুন।",
        "মধ্যবর্তী হস্তান্তরগুলো পারিবারিক হেবা বা আপস-বণ্টন দলিলের মাধ্যমে হয়েছিল কিনা তা পরীক্ষা করুন।",
    ],
    "R6": [
        "মূল রেজিস্ট্রেশন দলিলে উল্লিখিত জমির পরিমাণের সাথে নামজারি খতিয়ানের পরিমাণ মিলিয়ে দেখুন।",
        "উপজেলা ভূমি অফিসে নামজারি মিস কেসের নথি ও আদেশ পরীক্ষা করুন।",
        "নামজারি ছাড়া অবশিষ্ট অংশের বিষয়ে বিক্রেতার নিকট সুস্পষ্ট ব্যাখ্যা চান।",
    ],
    "R7": [
        "মূল দলিলের রেজিস্ট্রেশন তারিখের সাথে নামজারি আদেশের তারিখের ক্রম যাচাই করুন।",
        "নামজারিটি পূর্ববর্তী কোনো বায়নানামা বা অন্য দলিলের ভিত্তিতে হয়েছিল কিনা পরীক্ষা করুন।",
        "ভূমি অফিসের মূল আদেশের নথি দেখে তারিখের অসঙ্গতি পর্যালোচনা করুন।",
    ],
    "R8": [
        "ইউনিয়ন পরিষদ বা পৌরসভা থেকে ওয়ারিশ সনদ ও উত্তরাধিকারীদের তালিকা যাচাই করুন।",
        "বাদ পড়া ওয়ারিশের কোনো রেজিস্ট্রিকৃত না-দাবি পত্র, হেবা বা বিক্রয় দলিল রয়েছে কি না সাব-রেজিস্ট্রি অফিসে তল্লাশি দিন।",
        "পরবর্তী জরিপ খতিয়ানসমূহে (আরএস/বিএস/নামজারি) সকল ওয়ারিশের অংশ অন্তর্ভুক্ত ছিল কিনা পরীক্ষা করুন।",
    ],
    "R9": [
        "সংশ্লিষ্ট ব্যাংক বা আর্থিক প্রতিষ্ঠান থেকে হালনাগাদ দায়মুক্তি সনদ বা অনাপত্তিপত্র সংগ্রহ করতে বলুন।",
        "সাব-রেজিস্ট্রি অফিসের বন্ধকি বালাম ও রেজিস্টারে কোনো সক্রিয় দায় রয়েছে কিনা তল্লাশি দিন।",
        "ঋণ সম্পূর্ণ পরিশোধ এবং বন্ধক অবমুক্তি দলিল রেজিস্ট্রি সম্পন্ন হওয়া নিশ্চিত করুন।",
    ],
    "R10": [
        "সংশ্লিষ্ট সাব-রেজিস্ট্রি অফিসে আমমোক্তারনামা বাতিলের রেজিস্টার তল্লাশি দিন।",
        "মূল মালিক জীবিত আছেন কিনা নিশ্চিত হন এবং তার সাথে সরাসরি যোগাযোগ করে সম্মতি জানুন।",
        "আমমোক্তারনামা দলিলে এই নির্দিষ্ট জমি বিক্রির সুস্পষ্ট ক্ষমতা প্রদান করা হয়েছে কিনা তা পরীক্ষা করুন।",
    ],
    "R11": [
        "সহকারী কমিশনার (ভূমি) অফিসের রেজিস্টার থেকে খাস খতিয়ান বা সরকারি অধিগ্রহণের বিজ্ঞপ্তি যাচাই করুন।",
        "অধিগ্রহণ প্রক্রিয়া চলমান থাকলে জেলা প্রশাসকের কার্যালয়ের ভূমি অধিগ্রহণ গেজেট পরীক্ষা করুন।",
        "আদালতের কোনো মামলা বা নিষেধাজ্ঞা থাকলে সংশ্লিষ্ট দেওয়ানি আদালতে মামলার বর্তমান অবস্থা খোঁজ নিন।",
    ],
    "R12": [
        "উপস্থাপিত শারীরিক দলিলের অনুলিপি সাব-রেজিস্ট্রি অফিসের মূল বালাম বইয়ের সাথে সরাসরি মিলিয়ে দেখুন।",
        "দলিলের সিলমোহর, বালাম নম্বর, পৃষ্ঠা নম্বর ও রেজিস্ট্রি ক্রমিক সঠিক রয়েছে কিনা পরীক্ষা করুন।",
        "সাব-রেজিস্ট্রি অফিস থেকে সরকারি ফি দিয়ে সহি-মহুরি নকল তুলে যাচাই করুন।",
    ],
    "R13": [
        "সাব-রেজিস্ট্রি রেজিস্টার দেখে নিশ্চিত হন দলিলটি একাধিক দাগ বা প্লটের যৌথ দলিল কিনা।",
        "সকল দাগের ক্ষেত্রে দলিলের তারিখ, পক্ষ ও শর্তাবলি হুবহু এক রয়েছে কিনা মিলিয়ে নিন।",
        "তথ্যের অমিল থাকলে সাব-রেজিস্ট্রি অফিসের মহাফেজখানায় মূল বালাম দেখে স্পষ্টীকরণ নিন।",
    ],
    "R14": [
        "একই নামধারী ব্যক্তিদের পৃথকভাবে শনাক্ত করতে জাতীয় পরিচয়পত্র (এনআইডি) ও পিতা/মাতার নাম মিলিয়ে নিন।",
        "ইউনিয়ন পরিষদ বা ওয়ার্ড কাউন্সিলর অফিস থেকে নাগরিকত্ব বা উত্তরাধিকার সনদ যাচাই করুন।",
        "ভোটার তালিকা ও হোল্ডিং ট্যাক্স দাখিলা দেখে সঠিক ব্যক্তি নিশ্চিত করুন।",
    ],
    "R15": [
        "মৌজা নকশা সংগ্রহ করুন এবং দলিলের চারদিকের চৌহদ্দি (উত্তর, দক্ষিণ, পূর্ব, পশ্চিম) মিলিয়ে দেখুন।",
        "অভিজ্ঞ আমিন দ্বারা সরেজমিনে জমি পরিমাপ করে নির্দিষ্ট অংশের অবস্থান চিহ্নিত করুন।",
        "পার্শ্ববর্তী অংশের দলিলসমূহ পরীক্ষা করে নিশ্চিত হন যে একই জমি ইতিপূর্বে অন্য কারো কাছে বিক্রি হয়নি।",
    ],
    "HYGIENE": [
        "জমির রেকর্ডে তারিখবিহীন ঘটনা বা ভিত্তিহীন আদেশ পর্যালোচনা করুন।",
        "তারিখের ঘাটতি পূরণে রেজিস্ট্রিকৃত দলিলের মূল রশিদ বা দাখিলা সংগ্রহ করুন।",
        "রাজস্ব সার্কেল পরিদর্শকের সাথে ঐতিহাসিক তথ্যাবলি সমন্বয় করুন।",
    ],
}

FALLBACK_STEPS_EN = [
    "Inspect the certified chain of deeds at the Sub-Registry office.",
    "Verify current mutation and tax receipts at the local land revenue office.",
    "Consult an authorized property expert or land reviewer.",
]

FALLBACK_STEPS_BN = [
    "সাব-রেজিস্ট্রি অফিস থেকে দলিলের সহি-মহুরি নকল যাচাই করুন।",
    "স্থানীয় ভূমি অফিসে নামজারি ও খাজনা দাখিলা পরীক্ষা করুন।",
    "প্রয়োজনে একজন অভিজ্ঞ ভূমি পরামর্শকের সাথে পর্যালোচনা করুন।",
]


def get_rule_next_steps(rule_id: str, lang: str = "bn") -> dict[str, Any]:
    """
    Get 2-4 concrete, actionable checks for a specific rule ID.
    Returns:
      {
        "rule_id": str,
        "steps": list[str],
        "disclaimer": str,
      }
    """
    clean_id = (rule_id or "").strip().upper()
    steps_map = RULE_NEXT_STEPS_BN if lang == "bn" else RULE_NEXT_STEPS_EN
    fallback = FALLBACK_STEPS_BN if lang == "bn" else FALLBACK_STEPS_EN
    disclaimer = DISCLAIMER_LAW_MENTOR_BN if lang == "bn" else DISCLAIMER_LAW_MENTOR_EN

    steps = steps_map.get(clean_id, fallback)

    return {
        "rule_id": clean_id,
        "steps": list(steps),
        "disclaimer": disclaimer,
    }
