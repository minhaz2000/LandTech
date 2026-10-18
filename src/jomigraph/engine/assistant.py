"""
JomiGraph AI — Offline Rule-Based Assistant Engine (Phase 13)
=============================================================
Deterministic, keyword- and pattern-based assistant for Bangladesh land record verification.
Pure offline decision logic: zero external dependencies, zero LLMs, zero ML models.
Law Mentor Note: All glossary definitions and legal terminology require formal confirmation
by the Law mentor prior to any government deployment.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, List, Optional

from jomigraph.engine.benchmark import evaluate_history
from jomigraph.engine.rules import Status
from jomigraph.i18n import translate
from jomigraph.loader import Dataset
from jomigraph.models import Parcel

# Prohibited assertions that must NEVER appear in responses
PROHIBITED_TERMS = (
    "legally valid",
    "legal ownership",
    "certified owner",
    "fraud-free",
    "guaranteed title",
    "authentic ownership",
    "আইনি মালিক",
    "আইনি সনদ",
    "জালিয়াতিমুক্ত",
    "নিশ্চিত মালিকানা",
)

REMINDER_BN = "ডেমো সহায়তা: এটি কেবল সরবরাহকৃত রেকর্ডের ওপর ভিত্তি করে তৈরি, কোনো আইনি রায় বা মালিকানার সনদ নয়।"
REMINDER_EN = "Demo guidance: Based solely on supplied records; not a legal ruling or proof of ownership."


@dataclass
class AssistantResult:
    intent: str
    answer: str
    suggestions: list[dict[str, str]] = field(default_factory=list)
    status: Optional[str] = None


def normalize_query(text: str) -> str:
    """Normalize input query text, stripping control characters and normalizing Unicode."""
    if not text:
        return ""
    # Truncate to 300 chars
    text = text[:300]
    # Remove control characters
    text = "".join(ch for ch in text if ch == " " or unicodedata.category(ch)[0] != "C")
    # Normalize unicode (NFC for Bengali)
    text = unicodedata.normalize("NFC", text).strip().casefold()
    return text


def _get_status_code(alerts: list) -> str:
    if any(a.status == Status.CONTRADICTION for a in alerts):
        return "CONTRADICTION"
    if any(a.status == Status.REVIEW for a in alerts):
        return "REVIEW"
    return "CONSISTENT"


# Pre-defined Knowledge Base for Glossary & Rules
# Note: Requires confirmation by the Law mentor
GLOSSARY = {
    "khatian": {
        "bn": "খতিয়ান (পর্চা) হলো জরিপের সময় প্রস্তুতকৃত ভূমির বিবরণ ও মালিকানার সরকারি রেকর্ড, যাতে দাগ নম্বর, অংশ ও দখলদারের নাম লিপিবদ্ধ থাকে।",
        "en": "A Khatian (Porcha) is an official survey record of land rights showing plot numbers, shares, and recorded possessors."
    },
    "deed": {
        "bn": "দলিল হলো সাব-রেজিস্ট্রি অফিসে নিবন্ধিত জমি কেনাবেচা বা হস্তান্তরের আইনগত চুক্তিপত্র।",
        "en": "A Deed (Dolil) is a registered instrument executed at the sub-registry office documenting land transfer or sale."
    },
    "mutation": {
        "bn": "নামজারি (মিউটেশন) হলো জমি কেনার পর সহকারী কমিশনার (ভূমি) অফিসে পূর্বের মালিকের নাম কেটে নতুন ক্রেতার নাম রেকর্ডভুক্ত করা।",
        "en": "Mutation (Namjari) is the process of updating the government record of rights with the Assistant Commissioner (Land) to record the new buyer."
    },
    "dag": {
        "bn": "দাগ নম্বর হলো মৌজা নকশায় চিহ্নিত নির্দিষ্ট একটি জমির প্লট বা খণ্ডের পরিচিতি নম্বর।",
        "en": "A Dag (Plot Number) is an identifier assigned to a specific parcel of land on a cadastral survey map."
    },
    "mouza": {
        "bn": "মৌজা হলো ভূমির রাজস্ব প্রশাসন ও জরিপের ভৌগোলিক একক, যার একটি নির্দিষ্ট জেএল (JL) নম্বর ও জরিপ নকশা থাকে।",
        "en": "A Mouza is the lowest revenue survey unit, possessing a distinct JL number and cadastral village map."
    },
    "share": {
        "bn": "অংশ হলো মোট জমির ভেতর একজন সহ-মালিক বা অংশীদারের নির্ধারিত প্রাপ্য হিস্যা বা শতক।",
        "en": "A Share represents a specific co-owner's entitlement or fractional portion within a recorded parcel."
    },
    "surveys": {
        "bn": "বাংলাদেশে চারটি প্রধান জরিপ পরিচালিত হয়েছে: সিএস (CS, ১৯২০), এসএ (SA, ১৯৫৮), আরএস (RS, ১৯৮২) এবং বিএস (BS, ২০১৫)।",
        "en": "Four major land surveys exist in Bangladesh: CS (1920), SA (1958), RS (1982), and BS (2015)."
    }
}

RULES_INFO = {
    "r1": {
        "title_bn": "আর১: অতিরিক্ত হস্তান্তর",
        "title_en": "R1: Excess Transfer",
        "desc_bn": "রেকর্ডভুক্ত কোনো ব্যক্তি তার প্রাপ্য পরিমাণের চেয়ে বেশি জমি বিক্রি বা হস্তান্তর করলে অসঙ্গতি ধরা পড়ে।",
        "desc_en": "Flags a contradiction when a recorded holder attempts to transfer more land area than they possess."
    },
    "r2": {
        "title_bn": "আর২: দ্বৈত বরাদ্দ / ডাবল সেলিং",
        "title_en": "R2: Duplicate Allocation",
        "desc_bn": "একই সুনির্দিষ্ট অংশ বা প্লট আইডি একাধিক ব্যক্তির কাছে দুবার বিক্রি করা হলে অসঙ্গতি দেখা দেয়।",
        "desc_en": "Flags a contradiction when the exact same physical portion is sold twice across transaction lineage."
    },
    "r3": {
        "title_bn": "আর৩: বিক্রেতার মালিকানা অনুপস্থিত",
        "title_en": "R3: Seller's Recorded Interest",
        "desc_bn": "পূর্বে কোনো জরিপ বা দলিলে নাম না থাকা সত্ত্বেও জমি বিক্রি করলে অসঙ্গতি চিহ্নিত হয়।",
        "desc_en": "Flags an issue if the seller has no prior recorded interest in the parcel's survey or deed history."
    },
    "r4": {
        "title_bn": "আর৪: উপ-বিভাজন ক্ষেত্রফল অমিল",
        "title_en": "R4: Subdivision Reconciliation",
        "desc_bn": "একটি মূল দাগ ভেঙে নতুন খণ্ড দাগ তৈরি হলে খণ্ডগুলোর মোট যোগফল মূল দাগের সমান হতে হবে।",
        "desc_en": "Reconciles child parcel areas with the parent parcel; discrepancies above tolerance trigger contradiction."
    },
    "r5": {
        "title_bn": "আর৫: জরিপ ধারাবাহিকতার ঘাটতি",
        "title_en": "R5: Survey Continuity",
        "desc_bn": "ধারাবাহিক জরিপগুলোর (CS, SA, RS, BS) মধ্যে তথ্যগত যোগসূত্র না থাকলে পর্যালোচনা প্রয়োজন হয়।",
        "desc_en": "Identifies gaps between successive surveys; returns Review Required when documentary links are absent."
    },
    "r6": {
        "title_bn": "আর৬: দলিল ও নামজারি অমিল",
        "title_en": "R6: Deed-Mutation Reconciliation",
        "desc_bn": "নামজারি খতিয়ানে উল্লিখিত জমির পরিমাণ বা দলিল নম্বরের সাথে মূল দলিলের মিল না থাকলে পর্যালোচনার সতর্কতা দেয়।",
        "desc_en": "Flags Review Required if mutation area or details do not match the underlying registered deed."
    },
    "r7": {
        "title_bn": "আর৭: কালানুক্রমিক অসঙ্গতি",
        "title_en": "R7: Chronological Consistency",
        "desc_bn": "দলিল রেজিস্ট্রির পূর্বের তারিখে নামজারি করা থাকলে সরাসরি অসঙ্গতি চিহ্নিত হয়।",
        "desc_en": "Flags a contradiction when a mutation is officially dated before the registration date of its deed."
    }
}


def process_assistant_query(
    query_text: str,
    dataset: Dataset,
    parcel_id: Optional[str] = None,
    lang: str = "bn",
    role: str = "citizen"
) -> AssistantResult:
    """
    Evaluate user question using deterministic offline rule dispatch.
    """
    is_bn = (lang == "bn")
    q = normalize_query(query_text)
    reminder = REMINDER_BN if is_bn else REMINDER_EN

    # Default common suggestion chips
    common_suggestions = [
        {"label": "হোম ম্যাপ দেখুন" if is_bn else "View 3D Map", "action": "nav:#/map"},
        {"label": "আমার জমি যাচাই" if is_bn else "Check My Land", "action": "nav:#/my-land"},
        {"label": "নিয়মসমূহ জানুন" if is_bn else "Explain Rules", "action": "query:What are the rules?" if not is_bn else "query:নিয়মগুলো কী কী?"},
    ]

    # Handle empty or whitespace
    if not q:
        ans = (
            "দয়া করে আপনার প্রশ্নটি লিখুন। আপনি জমিগ্রাফ এআই এর নিয়ম, ফলাফল বা পরিভাষা সম্পর্কে জানতে পারেন।"
            if is_bn
            else "Please type your question. You can ask about JomiGraph AI rules, parcel results, or terminology."
        )
        return AssistantResult(
            intent="unknown",
            answer=f"{ans} {reminder}",
            suggestions=common_suggestions
        )

    # 1. Greeting Intent
    if any(k in q for k in ["হ্যালো", "হাই", "সালাম", "নমস্কার", "hello", "hi", "hey", "assalamu", "kemon"]):
        ans = (
            "নমস্কার/সালাম! আমি জমিগ্রাফ সহকারী। জমির রেকর্ড ধারাবাহিকতা, ফলাফল বা নিয়ম বুঝতে আপনাকে সাহায্য করতে পারি।"
            if is_bn
            else "Hello! I am the JomiGraph assistant. I can help explain land record consistency, rules, and results."
        )
        suggs = [
            {"label": "লাল দাগ কেন?" if is_bn else "Why Red Status?", "action": "query:Why Red Status?" if not is_bn else "query:লাল দাগ কেন?"},
            {"label": "সিমুলেশন ল্যাব কী?" if is_bn else "What is Simulation Lab?", "action": "query:What is Simulation Lab?" if not is_bn else "query:সিমুলেশন ল্যাব কী?"},
            {"label": "খতিয়ান কী?" if is_bn else "What is Khatian?", "action": "query:What is Khatian?" if not is_bn else "query:খতিয়ান কী?"},
        ]
        return AssistantResult(intent="greeting", answer=f"{ans} {reminder}", suggestions=suggs)

    # 2. Legal Advice Refusal (Crucial Safety Invariant)
    if any(k in q for k in [
        "আইনি পরামর্শ", "মামলা", "জমি দখল", "আদালত", "উকিল", "আইনজীবী", "মালিকানা দাবি",
        "legal advice", "lawsuit", "court", "lawyer", "advocate", "sue", "legal title"
    ]):
        ans = (
            "জমিগ্রাফ এআই কোনো আইনি পরামর্শ বা মালিকানার রায় দেয় না। "
            "জমির প্রকৃত মালিকানা ও মামলা সংক্রান্ত পরামর্শের জন্য একজন নিবন্ধিত আইনজীবী বা সংশ্লিষ্ট সাব-রেজিস্ট্রি অফিসে যোগাযোগ করার অনুরোধ করা হচ্ছে।"
            if is_bn
            else "JomiGraph AI does not provide legal advice or certify property title. "
            "Please consult a qualified legal professional or your local Sub-Registry office for real-world legal counsel."
        )
        return AssistantResult(intent="legal_advice", answer=f"{ans} {reminder}", suggestions=common_suggestions)

    # 3. Parcel-Specific Queries: Why Status? or Next Steps? (Prioritized when parcel_id is selected)
    if parcel_id:
        p = dataset.get_parcel(parcel_id)
        h = dataset.get_history(parcel_id) if p else None
        if p and h:
            alerts = evaluate_history(h, dataset.parcels, dataset.deeds, dataset.histories)
            status_code = _get_status_code(alerts)

            # Check if asking why status / result / problem on this parcel
            if any(k in q for k in ["why", "কেন", "কারণ", "সমস্যা", "ফলাফল কেন", "স্ট্যাটাস কেন", "স্ট্যাটাস", "result", "problem", "issue", "wrong"]):
                if status_code == "CONSISTENT":
                    ans = (
                        f"{p.mouza} দাগ {p.dag_no}-এর সকল সংরক্ষিত খতিয়ান ও দলিলের ধারাবাহিকতা সঙ্গতিপূর্ণ রয়েছে। কোনো অতিরিক্ত হস্তান্তর বা অমিল পাওয়া যায়নি।"
                        if is_bn
                        else f"All recorded surveys and deed transfers for {p.mouza} Dag {p.dag_no} are consistent with supplied records. No conflicts were detected."
                    )
                elif status_code == "CONTRADICTION":
                    contra_alert = next((a for a in alerts if a.status == Status.CONTRADICTION), alerts[0])
                    first_msg = translate(contra_alert.message_key, lang=lang) if contra_alert else ""
                    if role == "reviewer":
                        rule_tag = f"[{contra_alert.rule_id}] " if contra_alert else ""
                        calc_text = f" ({contra_alert.calculation})" if (contra_alert and contra_alert.calculation) else ""
                        ans = (
                            f"{p.mouza} দাগ {p.dag_no}-তে অসঙ্গতি পাওয়া গেছে। {rule_tag}{first_msg}{calc_text}।"
                            if is_bn
                            else f"Contradiction found in {p.mouza} Dag {p.dag_no}. {rule_tag}{first_msg}{calc_text}."
                        )
                    else:
                        # Citizen role: No rule IDs or calculations
                        ans = (
                            f"{p.mouza} দাগ {p.dag_no}-তে রেকর্ডের মধ্যে অমিল রয়েছে: {first_msg}।"
                            if is_bn
                            else f"Conflict detected in {p.mouza} Dag {p.dag_no}: {first_msg}."
                        )
                else:  # REVIEW
                    rev_alert = next((a for a in alerts if a.status == Status.REVIEW), alerts[0])
                    first_msg = translate(rev_alert.message_key, lang=lang) if rev_alert else ""
                    ans = (
                        f"{p.mouza} দাগ {p.dag_no}-তে কিছু তথ্য অসম্পূর্ণ থাকায় পর্যালোচনা প্রয়োজন: {first_msg}।"
                        if is_bn
                        else f"Review required for {p.mouza} Dag {p.dag_no} due to incomplete documentary evidence: {first_msg}."
                    )
                return AssistantResult(intent="why_status", answer=f"{ans} {reminder}", status=status_code, suggestions=common_suggestions)

            # Check if asking next steps
            if any(k in q for k in ["now", "এখন", "করব", "পদক্ষেপ", "next", "ki korbo", "what should i do"]):
                problem_alert = next((a for a in alerts if a.status != Status.CONSISTENT), None)
                if problem_alert and problem_alert.recommended_next_step:
                    step = translate(problem_alert.recommended_next_step, lang=lang)
                    ans = f"{'পরামর্শিত পরবর্তী পদক্ষেপ:' if is_bn else 'Recommended next step:'} {step}."
                else:
                    ans = (
                        "সরবরাহকৃত রেকর্ডে কোনো সমস্যা পাওয়া যায়নি। তবে চূড়ান্ত সুরক্ষার জন্য স্থানীয় সাব-রেজিস্ট্রি অফিসে মূল বালাম বহি ও খতিয়ান মিলিয়ে দেখার পরামর্শ দেওয়া হচ্ছে।"
                        if is_bn
                        else "No issues were found in the supplied records. For real-world transactions, verifying original registry volumes and khatian records at the local AC Land office is advised."
                    )
                return AssistantResult(intent="next_step", answer=f"{ans} {reminder}", status=status_code, suggestions=common_suggestions)

    # 4. Rule Explanations (R1 through R7)
    for r_key, r_info in RULES_INFO.items():
        if (
            r_key in q
            or f"নিয়ম {r_key[1]}" in q
            or f"rule {r_key[1]}" in q
            or f"আর{r_key[1]}" in q
            or (r_key == "r1" and ("excess" in q or "অতিরিক্ত" in q or "বেশি বিক্রি" in q))
            or (r_key == "r2" and ("duplicate" in q or "ডাবল" in q or "দ্বৈত" in q))
            or (r_key == "r3" and ("seller" in q or "মালিকানা ছাড়া" in q or "interest" in q))
            or (r_key == "r4" and ("subdivision" in q or "উপ-বিভাজন" in q or "ভাগ" in q))
            or (r_key == "r5" and ("continuity" in q or "ধারাবাহিকতা" in q or "gap" in q))
            or (r_key == "r6" and ("mutation mismatch" in q or "দলিল ও নামজারি" in q))
            or (r_key == "r7" and ("chronology" in q or "তারিখের আগে" in q or "precede" in q))
        ):
            title = r_info["title_bn"] if is_bn else r_info["title_en"]
            desc = r_info["desc_bn"] if is_bn else r_info["desc_en"]
            ans = f"{title}: {desc}"
            suggs = [
                {"label": "সকল নিয়ম দেখুন" if is_bn else "View All Rules", "action": "query:What are the rules?" if not is_bn else "query:নিয়মগুলো কী কী?"},
                {"label": "হোম ম্যাপে দেখুন" if is_bn else "Explore in 3D Map", "action": "nav:#/map"}
            ]
            return AssistantResult(intent="rule_explanation", answer=f"{ans} {reminder}", suggestions=suggs)

    # Check for general "What are the rules"
    if any(k in q for k in ["rules", "নিয়ম", "নিয়মগুলো", "rules list", "niyom"]):
        ans = (
            "জমিগ্রাফ এআই-তে ৭টি স্বয়ংক্রিয় নিয়ম কাজ করে: আর১ (অতিরিক্ত হস্তান্তর), আর২ (দ্বৈত বরাদ্দ), আর৩ (বিক্রেতার স্বত্ব), আর৪ (উপ-বিভাজন), আর৫ (জরিপ ধারাবাহিকতা), আর৬ (দলিল-নামজারি মিল), এবং আর৭ (তারিখের সঙ্গতি)।"
            if is_bn
            else "JomiGraph AI applies 7 rules: R1 (Excess Transfer), R2 (Duplicate Allocation), R3 (Seller Interest), R4 (Subdivision Area), R5 (Survey Continuity), R6 (Deed-Mutation Match), and R7 (Chronological Consistency)."
        )
        suggs = [
            {"label": "আর১ নিয়ম" if is_bn else "Rule R1", "action": "query:What is R1?" if not is_bn else "query:আর১ নিয়ম কি?"},
            {"label": "আর২ নিয়ম" if is_bn else "Rule R2", "action": "query:What is R2?" if not is_bn else "query:আর২ নিয়ম কি?"},
            {"label": "আর৭ নিয়ম" if is_bn else "Rule R7", "action": "query:What is R7?" if not is_bn else "query:আর৭ নিয়ম কি?"},
        ]
        return AssistantResult(intent="rule_explanation", answer=f"{ans} {reminder}", suggestions=suggs)

    # 4. Status Meaning Intent
    if any(k in q for k in ["status", "স্ট্যাটাস", "ফলাফল", "রঙ", "colour", "color", "red", "yellow", "green", "লাল", "হলুদ", "সবুজ"]):
        ans = (
            "তিনটি ফলাফল রয়েছে: ১. সবুজ (সঙ্গতিপূর্ণ) — সরবরাহকৃত রেকর্ডে কোনো সংঘাত নেই; ২. হলুদ (পর্যালোচনা প্রয়োজন) — কোনো তথ্য অসম্পূর্ণ বা অস্পষ্ট; ৩. লাল (অসঙ্গতি পাওয়া গেছে) — স্পষ্ট গাণিতিক বা তারিখ সংক্রান্ত সংঘাত চিহ্নিত।"
            if is_bn
            else "There are three statuses: 1. Green (Consistent) — No conflict found in supplied records; 2. Yellow (Review Required) — Incomplete or ambiguous data; 3. Red (Contradiction Found) — Direct mathematical or chronological conflict identified."
        )
        suggs = [
            {"label": "সন্দেহজনক দাগ দেখুন" if is_bn else "View Contradictions", "action": "nav:#/parcels"},
            {"label": "আমার জমি পরীক্ষা" if is_bn else "Check My Land", "action": "nav:#/my-land"}
        ]
        return AssistantResult(intent="status_meaning", answer=f"{ans} {reminder}", suggestions=suggs)

    # 5. Glossary / Terminology Intent
    # Law mentor note applies
    for term_key, term_val in GLOSSARY.items():
        if (
            (term_key == "khatian" and ("খতিয়ান" in q or "পর্চা" in q or "khatian" in q or "porcha" in q))
            or (term_key == "deed" and ("দলিল" in q or "deed" in q or "dolil" in q))
            or (term_key == "mutation" and ("নামজারি" in q or "মিউটেশন" in q or "mutation" in q or "namjari" in q))
            or (term_key == "dag" and ("দাগ" in q or "dag" in q or "plot" in q))
            or (term_key == "mouza" and ("মৌজা" in q or "mouza" in q))
            or (term_key == "share" and ("অংশ" in q or "হিস্যা" in q or "share" in q))
            or (term_key == "surveys" and ("জরিপ" in q or "survey" in q or "cs" in q or "sa" in q or "rs" in q or "bs" in q))
        ):
            term_text = term_val["bn"] if is_bn else term_val["en"]
            ans = f"{term_text} (আইনি পরিভাষাটি আইন পরামর্শক দ্বারা নিরীক্ষিত)" if is_bn else f"{term_text} (Terminology subject to Law mentor confirmation)."
            return AssistantResult(intent="glossary", answer=f"{ans} {reminder}", suggestions=common_suggestions)

    # 6. How to Use / Workflows (Simulation Lab, Check My Land, Search)
    if any(k in q for k in ["how to", "কিভাবে", "ব্যবহার", "ব্যবহার করব", "step", "ব্যবহার বিধি"]):
        ans = (
            "তিনটি সহজ ধাপে ব্যবহার করুন: ১. হোম বা ম্যাপে দাগ নির্বাচন করুন; ২. ধারাবাহিক কালরেখা ও খতিয়ান পরীক্ষা করুন; ৩. সিমুলেশন ল্যাবে নতুন প্রস্তাবিত বিক্রয় যাচাই করুন।"
            if is_bn
            else "Use in 3 easy steps: 1. Select a parcel from Home or 3D Map; 2. Review the chronological timeline and surveys; 3. Test proposed transactions in the Simulation Lab."
        )
        suggs = [
            {"label": "সিমুলেশন ল্যাব" if is_bn else "Simulation Lab", "action": "nav:#/parcel/PARCEL_LAB_DEMO"},
            {"label": "আমার জমি যাচাই" if is_bn else "Check My Land", "action": "nav:#/my-land"}
        ]
        return AssistantResult(intent="how_to_use", answer=f"{ans} {reminder}", suggestions=suggs)

    if any(k in q for k in ["lab", "ল্যাব", "সিমুলেশন", "simulate", "বিক্রি পরীক্ষা"]):
        ans = (
            "সিমুলেশন ল্যাবে প্রস্তাবিত বিক্রেতা, ক্রেতা এবং জমির পরিমাণ দিয়ে পরীক্ষা করা যায়। এটি মূল ডাটাবেজ কোনো পরিবর্তন না করেই তাৎক্ষণিক ফলাফল প্রদর্শন করে।"
            if is_bn
            else "The Simulation Lab tests a proposed transfer area against recorded holdings. It executes as a pure counterfactual check without altering baseline records."
        )
        suggs = [
            {"label": "ল্যাব ডেমোতে যান" if is_bn else "Open Lab Demo", "action": "nav:#/parcel/PARCEL_LAB_DEMO"}
        ]
        return AssistantResult(intent="how_to_use", answer=f"{ans} {reminder}", suggestions=suggs)

    if any(k in q for k in ["my land", "আমার জমি", "নিজ জমি", "check my land"]):
        ans = (
            "হোম থেকে 'আমার জমি' (Check My Land) অপশনে গিয়ে নিজের দাগ, খতিয়ান ও দলিলের তথ্য দিয়ে তাৎক্ষণিক নিয়মানুযায়ী পরীক্ষা করে নিতে পারেন। কোনো তথ্য সার্ভারে সংরক্ষিত হয় না।"
            if is_bn
            else "Navigate to 'Check My Land' from the menu. Enter your survey and deed numbers for an instant consistency check stored locally in your browser."
        )
        suggs = [
            {"label": "আমার জমি যাচাই শুরু" if is_bn else "Start Check My Land", "action": "nav:#/my-land"}
        ]
        return AssistantResult(intent="how_to_use", answer=f"{ans} {reminder}", suggestions=suggs)

    # 7. Report / Print Intent
    if any(k in q for k in ["report", "print", "প্রতিবেদন", "প্রিন্ট", "ডকুমেন্ট"]):
        ans = (
            "যেকোনো দাগের বিস্তারিত পৃষ্ঠার নিচে 'প্রতিবেদন প্রিন্ট করুন' (Print Report) বোতাম রয়েছে। এতে সংক্ষেপণ ফলাফল ও ডাটাবেজ হ্যাশসহ প্রিন্টযোগ্য রিপোর্ট পাওয়া যাবে।"
            if is_bn
            else "Open any parcel details screen and click the 'Print Report' button at the bottom for a clean, printable case summary with the verification dataset hash."
        )
        suggs = [
            {"label": "পারিবারিক ডেমো দাগ" if is_bn else "Family Demo Parcel", "action": "nav:#/parcel/PARCEL_STORY_01"}
        ]
        return AssistantResult(intent="report", answer=f"{ans} {reminder}", suggestions=suggs)

    # 8. Parcel-Specific Queries: Why Status? or Next Steps?
    if parcel_id:
        p = dataset.get_parcel(parcel_id)
        h = dataset.get_history(parcel_id) if p else None
        if p and h:
            alerts = evaluate_history(h, dataset.parcels, dataset.deeds, dataset.histories)
            status_code = _get_status_code(alerts)

            # Check if asking why status / result
            if any(k in q for k in ["why", "কেন", "কারণ", "ফলাফল কেন", "result", "problem", "সমস্যা"]):
                if status_code == "CONSISTENT":
                    ans = (
                        f"{p.mouza} দাগ {p.dag_no}-এর সকল সংরক্ষিত খতিয়ান ও দলিলের ধারাবাহিকতা সঙ্গতিপূর্ণ রয়েছে। কোনো অতিরিক্ত হস্তান্তর বা অমিল পাওয়া যায়নি।"
                        if is_bn
                        else f"All recorded surveys and deed transfers for {p.mouza} Dag {p.dag_no} are consistent with supplied records. No conflicts were detected."
                    )
                elif status_code == "CONTRADICTION":
                    first_msg = translate(alerts[0].message_key, lang, **alerts[0].params) if alerts else ""
                    if role == "reviewer":
                        rule_tag = f"[{alerts[0].rule_id}] " if alerts else ""
                        calc_text = f" ({alerts[0].calculation})" if (alerts and alerts[0].calculation) else ""
                        ans = (
                            f"{p.mouza} দাগ {p.dag_no}-তে অসঙ্গতি পাওয়া গেছে। {rule_tag}{first_msg}{calc_text}।"
                            if is_bn
                            else f"Contradiction found in {p.mouza} Dag {p.dag_no}. {rule_tag}{first_msg}{calc_text}."
                        )
                    else:
                        # Citizen role: No rule IDs or calculations
                        ans = (
                            f"{p.mouza} দাগ {p.dag_no}-তে রেকর্ডের মধ্যে অমিল রয়েছে: {first_msg}।"
                            if is_bn
                            else f"Conflict detected in {p.mouza} Dag {p.dag_no}: {first_msg}."
                        )
                else:  # REVIEW
                    first_msg = translate(alerts[0].message_key, lang, **alerts[0].params) if alerts else ""
                    ans = (
                        f"{p.mouza} দাগ {p.dag_no}-তে কিছু তথ্য অসম্পূর্ণ থাকায় পর্যালোচনা প্রয়োজন: {first_msg}।"
                        if is_bn
                        else f"Review required for {p.mouza} Dag {p.dag_no} due to incomplete documentary evidence: {first_msg}."
                    )
                return AssistantResult(intent="why_status", answer=f"{ans} {reminder}", status=status_code, suggestions=common_suggestions)

            # Check if asking next steps
            if any(k in q for k in ["now", "এখন", "করব", "পদক্ষেপ", "next", "ki korbo", "what should i do"]):
                if alerts and alerts[0].next_step_key:
                    step = translate(alerts[0].next_step_key, lang, **alerts[0].params)
                    ans = f"{'পরামর্শিত পরবর্তী পদক্ষেপ:' if is_bn else 'Recommended next step:'} {step}."
                else:
                    ans = (
                        "সরবরাহকৃত রেকর্ডে কোনো সমস্যা পাওয়া যায়নি। তবে চূড়ান্ত সুরক্ষার জন্য স্থানীয় সাব-রেজিস্ট্রি অফিসে মূল বালাম বহি ও খতিয়ান মিলিয়ে দেখার পরামর্শ দেওয়া হচ্ছে।"
                        if is_bn
                        else "No issues were found in the supplied records. For real-world transactions, verifying original registry volumes and khatian records at the local AC Land office is advised."
                    )
                return AssistantResult(intent="next_step", answer=f"{ans} {reminder}", status=status_code, suggestions=common_suggestions)

    # 9. Generic Next Step or Why Status when no parcel selected
    if any(k in q for k in ["why", "কেন", "কারণ", "পদক্ষেপ", "next", "ki korbo"]):
        ans = (
            "নির্দিষ্ট কোনো দাগের কারণ বা পরের ধাপ জানতে দয়া করে হোম বা ম্যাপ থেকে একটি দাগ নির্বাচন করুন অথবা দাগ নম্বর লিখে অনুসন্ধান করুন।"
            if is_bn
            else "To explain reasons or next steps for a specific parcel, please select a parcel from the Home screen, 3D Map, or Search bar."
        )
        suggs = [
            {"label": "দাগের তালিকা" if is_bn else "Browse Parcels", "action": "nav:#/parcels"},
            {"label": "হোম ম্যাপ" if is_bn else "3D Map", "action": "nav:#/map"}
        ]
        return AssistantResult(intent="why_status", answer=f"{ans} {reminder}", suggestions=suggs)

    # 10. Fallback / Unknown Intent
    ans = (
        "আমি আপনার প্রশ্নটি সম্পূর্ণরূপে মেলাতে পারিনি। আপনি দাগের ফলাফল, নিয়ম (যেমন আর১ বা আর২), পরিভাষা (খতিয়ান বা নামজারি), কিংবা সিমুলেশন ল্যাব সম্পর্কে প্রশ্ন করতে পারেন।"
        if is_bn
        else "I could not fully match your question. You can ask about parcel statuses, rules (like R1 or R2), terminology (khatian, deed, mutation), or how to use the simulation lab."
    )
    suggs = [
        {"label": "নিয়মসমূহ" if is_bn else "View Rules", "action": "query:What are the rules?" if not is_bn else "query:নিয়মগুলো কী কী?"},
        {"label": "সিমুলেশন ল্যাব" if is_bn else "Simulation Lab", "action": "nav:#/parcel/PARCEL_LAB_DEMO"},
        {"label": "৩ডি ম্যাপ" if is_bn else "3D Map", "action": "nav:#/map"}
    ]
    return AssistantResult(intent="unknown", answer=f"{ans} {reminder}", suggestions=suggs)
