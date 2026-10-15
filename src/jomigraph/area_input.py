"""
JomiGraph AI - Area input parsing
=================================
Turns text typed by a person into an exact, positive ``Fraction``.

Accepted forms (ASCII or Bangla digits, optional spaces around the slash):
    "5", "2.5", "0.75", "5/2", "১০", "২.৫"

Decimal strings are read as exact rationals ("2.5" becomes 5/2), so no
floating-point number is ever created. Real float values are still refused.

Failures raise AreaInputError with a stable ``code`` that the UI maps to a
localised message.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any

# Largest accepted area in decimals (shatak). Far above any real parcel,
# small enough to stop absurd input from producing huge numbers.
MAX_AREA = Fraction(10_000_000)

MESSAGES = {
    "AREA_EMPTY": "Enter an area.",
    "AREA_FORMAT": "Enter a whole number, a decimal such as 2.5, or a fraction such as 5/2.",
    "AREA_FLOAT_TYPE": "Send the area as text (for example \"2.5\"), not as a JSON number.",
    "AREA_NOT_POSITIVE": "Area must be greater than zero.",
    "AREA_TOO_LARGE": "Area is larger than any plausible parcel. Check the number.",
}

_BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
_DECIMAL_RE = re.compile(r"^-?[0-9]+(\.[0-9]+)?$")
_FRACTION_RE = re.compile(r"^(-?[0-9]+)\s*/\s*([0-9]+)$")


class AreaInputError(ValueError):
    """Raised for unusable area input. ``code`` is one of MESSAGES."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(f"{code}|{MESSAGES[code]}")


def parse_area(value: Any) -> Fraction:
    """Return a strictly positive exact Fraction, or raise AreaInputError."""
    if isinstance(value, bool) or isinstance(value, float):
        raise AreaInputError("AREA_FLOAT_TYPE")
    if isinstance(value, Fraction):
        result = value
    else:
        if isinstance(value, int):
            value = str(value)
        if not isinstance(value, str):
            raise AreaInputError("AREA_FORMAT")
        text = value.strip().translate(_BN_DIGITS)
        if not text:
            raise AreaInputError("AREA_EMPTY")
        if len(text) > 40:
            raise AreaInputError("AREA_TOO_LARGE")
        frac_match = _FRACTION_RE.match(text)
        if frac_match:
            num, den = int(frac_match.group(1)), int(frac_match.group(2))
            if den == 0:
                raise AreaInputError("AREA_FORMAT")
            result = Fraction(num, den)
        elif _DECIMAL_RE.match(text):
            result = Fraction(text)
        else:
            raise AreaInputError("AREA_FORMAT")
    if result <= 0:
        raise AreaInputError("AREA_NOT_POSITIVE")
    if result > MAX_AREA:
        raise AreaInputError("AREA_TOO_LARGE")
    return result
