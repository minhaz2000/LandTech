"""
JomiGraph AI — Traditional Bangladeshi Land Share Representation (Ana-Ganda-Kora-Kranti-Til)
=============================================================================================
SPEC § X1 Share Display:
  "Helper converting a Fraction share into traditional units for display only:
     16 ana = 1 whole (১ সম্পূর্ণ অংশ)
     1 ana = 20 ganda (২০ গণ্ডা)
     1 ganda = 4 kora (৪ কড়া)
     1 kora = 3 kranti (৩ ক্রান্তি)
     1 kranti = 20 til (২০ তিল)
   Total units per whole = 76,800 Til.
   e.g. 1/4 = 4 ana; 1/5 = 3 ana 4 ganda.
   Show the exact Fraction as well. Add a note that the conversion table should be
   confirmed with the Law mentor. Show each co-owner's share and limit in the Reviewer
   view, with tests for R1 on a 5-co-owner (Ejmali) dag."

Invariants:
  - Exact rational arithmetic only (Fraction); no binary float rounding.
  - Display only; clearly distinguished from physical land area and legal ownership certification.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Sequence, Union


# Conversion factors
ANA_PER_WHOLE = 16
GANDA_PER_ANA = 20
KORA_PER_GANDA = 4
KRANTI_PER_KORA = 3
TIL_PER_KRANTI = 20

# 16 * 20 * 4 * 3 * 20 = 76,800
TIL_PER_WHOLE = ANA_PER_WHOLE * GANDA_PER_ANA * KORA_PER_GANDA * KRANTI_PER_KORA * TIL_PER_KRANTI

EN_TO_BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

TRADITIONAL_SHARE_DISCLAIMER_EN = (
    "Traditional share units (16 Ana = 1 whole). Conversion table should be confirmed with the Law mentor. "
    "Display only; does not constitute legal proof of title."
)
TRADITIONAL_SHARE_DISCLAIMER_BN = (
    "ঐতিহ্যবাহী হিস্যা একক (১৬ আনা = ১ সম্পূর্ণ অংশ)। রূপান্তর সারণি আইন উপদেষ্টার সাথে যাচাই সাপেক্ষ। "
    "এটি শুধুমাত্র প্রদর্শনের জন্য; স্বত্ব বা মালিকানার আইনি সনদ নয়।"
)


def to_bangla_digits(val: Any) -> str:
    return str(val).translate(EN_TO_BN_DIGITS)


def fraction_to_traditional_share(share: Union[Fraction, int, str]) -> dict[str, Any]:
    """
    Decompose an exact rational share into traditional integer units and remainder:
      ana: int (0 to 16)
      ganda: int (0 to 19)
      kora: int (0 to 3)
      kranti: int (0 to 2)
      til: int (0 to 19)
      remainder_til: Fraction (exact remainder fraction of a til, if any)
    """
    fr = share if isinstance(share, Fraction) else Fraction(str(share))
    if fr < 0:
        raise ValueError(f"Share cannot be negative: {fr}")

    total_til_fraction = fr * TIL_PER_WHOLE
    int_til_total = int(total_til_fraction.numerator // total_til_fraction.denominator)
    remainder_til = total_til_fraction - int_til_total

    til = int_til_total % TIL_PER_KRANTI
    kranti_total = int_til_total // TIL_PER_KRANTI

    kranti = kranti_total % KRANTI_PER_KORA
    kora_total = kranti_total // KRANTI_PER_KORA

    kora = kora_total % KORA_PER_GANDA
    ganda_total = kora_total // KORA_PER_GANDA

    ganda = ganda_total % GANDA_PER_ANA
    ana = ganda_total // GANDA_PER_ANA

    return {
        "ana": ana,
        "ganda": ganda,
        "kora": kora,
        "kranti": kranti,
        "til": til,
        "remainder_til": remainder_til,
        "fraction": fr,
    }


def format_traditional_share(
    share: Union[Fraction, int, str],
    lang: str = "bn",
    include_fraction: bool = True,
) -> str:
    """
    Format a rational share into traditional textual representation:
      BN: '৪ আনা (১/৪)' or '৩ আনা ৪ গণ্ডা (১/৫)'
      EN: '4 ana (1/4)' or '3 ana 4 ganda (1/5)'
    """
    data = fraction_to_traditional_share(share)
    ana = data["ana"]
    ganda = data["ganda"]
    kora = data["kora"]
    kranti = data["kranti"]
    til = data["til"]
    rem = data["remainder_til"]
    fr = data["fraction"]

    units_bn = []
    units_en = []

    if ana > 0:
        units_bn.append(f"{to_bangla_digits(ana)} আনা")
        units_en.append(f"{ana} ana")
    if ganda > 0:
        units_bn.append(f"{to_bangla_digits(ganda)} গণ্ডা")
        units_en.append(f"{ganda} ganda")
    if kora > 0:
        units_bn.append(f"{to_bangla_digits(kora)} কড়া")
        units_en.append(f"{kora} kora")
    if kranti > 0:
        units_bn.append(f"{to_bangla_digits(kranti)} ক্রান্তি")
        units_en.append(f"{kranti} kranti")
    if til > 0:
        units_bn.append(f"{to_bangla_digits(til)} তিল")
        units_en.append(f"{til} til")
    if rem > 0:
        rem_str = f"{rem.numerator}/{rem.denominator}"
        units_bn.append(f"{to_bangla_digits(rem_str)} তিল (অবশিষ্ট)")
        units_en.append(f"{rem_str} til (rem)")

    if not units_bn:
        text_bn = "০ আনা"
        text_en = "0 ana"
    else:
        text_bn = " ".join(units_bn)
        text_en = " ".join(units_en)

    if include_fraction:
        fr_str = f"{fr.numerator}/{fr.denominator}" if fr.denominator != 1 else str(fr.numerator)
        text_bn = f"{text_bn} ({to_bangla_digits(fr_str)})"
        text_en = f"{text_en} ({fr_str})"

    return text_bn if lang == "bn" else text_en


def calculate_coowner_quotas(
    holders: Sequence[tuple[str, Fraction]],
    total_area: Fraction,
    lang: str = "bn",
) -> list[dict[str, Any]]:
    """
    Compute co-owner ownership share breakdown on an Ejmali dag:
      - individual area limit (quota)
      - share as fraction of total_area
      - traditional units display
    """
    results = []
    for person_id, area in holders:
        share_fraction = area / total_area if total_area > 0 else Fraction(0)
        trad_display = format_traditional_share(share_fraction, lang=lang, include_fraction=True)
        results.append({
            "person_id": person_id,
            "recorded_area": area,
            "quota_limit": area,
            "share_fraction": share_fraction,
            "traditional_share": trad_display,
        })
    return results
