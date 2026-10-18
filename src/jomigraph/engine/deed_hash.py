"""
JomiGraph AI — Canonical Deed Serialization and Content Hashing
===============================================================
Implements deterministic, canonical deed serialization and SHA-256 hashing (F13 / R12).

Hashing Invariants:
1. Canonicalization is deterministic: keys are sorted, separators are (",", ":").
2. The same logical deed produces the identical hash regardless of whitespace or input formatting.
3. Fields participating in hash: deed_no, registration_date, parcel_id, seller, buyer, area.
4. The stored content_hash field is never hashed into itself.
5. All area representations normalize to canonical exact rational form via Fraction.
6. Zero external network requests; pure cryptographic SHA-256.
"""

from __future__ import annotations

from datetime import date
from fractions import Fraction
import hashlib
import json
import re
from typing import Any, Union

from jomigraph.area_input import parse_area


def canonical_area_repr(area: Union[str, int, float, Fraction]) -> str:
    """
    Normalize any area input to a canonical exact rational string representation.
    Integers/whole numbers become "10", fractions become "5/2".
    Floats are rejected or parsed via parse_area.
    """
    if isinstance(area, Fraction):
        fr = area
    else:
        fr = parse_area(str(area))

    if fr.denominator == 1:
        return str(fr.numerator)
    return f"{fr.numerator}/{fr.denominator}"


def canonical_deed_payload(
    deed_no: str,
    registration_date: Union[str, date],
    parcel_id: str,
    seller: str,
    buyer: str,
    area: Union[str, int, float, Fraction],
) -> dict[str, str]:
    """
    Construct canonical dictionary of participating deed fields.
    Does NOT include content_hash or internal database identifiers.
    """
    reg_date_str = (
        registration_date.isoformat()
        if isinstance(registration_date, date)
        else str(registration_date).strip()
    )

    return {
        "area": canonical_area_repr(area),
        "buyer": re.sub(r"\s+", " ", str(buyer).strip()),
        "deed_no": re.sub(r"\s+", " ", str(deed_no).strip()),
        "parcel_id": re.sub(r"\s+", " ", str(parcel_id).strip()),
        "registration_date": reg_date_str,
        "seller": re.sub(r"\s+", " ", str(seller).strip()),
    }


def hash_deed_content(
    deed_no: str,
    registration_date: Union[str, date],
    parcel_id: str,
    seller: str,
    buyer: str,
    area: Union[str, int, float, Fraction],
) -> str:
    """
    Compute 64-character lowercase hexadecimal SHA-256 fingerprint over canonical deed fields.
    """
    payload = canonical_deed_payload(
        deed_no=deed_no,
        registration_date=registration_date,
        parcel_id=parcel_id,
        seller=seller,
        buyer=buyer,
        area=area,
    )
    canonical_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest().lower()


def build_deed_qr_payload(deed_no: str, content_hash: str) -> str:
    """
    Construct relative QR verification link containing deed_no and first 16 hex chars of hash.
    Format: #/verify-deed?deed_no=<deed_no>&hash=<hash_16>
    """
    hash_prefix = str(content_hash).strip().lower()[:16]
    clean_deed = str(deed_no).strip()
    return f"#/verify-deed?deed_no={clean_deed}&hash={hash_prefix}"
