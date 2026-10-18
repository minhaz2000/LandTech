"""
JomiGraph AI — Configuration
============================
Named constants and parameters for rule evaluations.
All arithmetic values use fractions.Fraction — no floats.
"""

from fractions import Fraction

# R4 Subdivision reconciliation tolerance:
# Area difference > 0 and <= R4_TOLERANCE returns Review Required.
# Area difference > R4_TOLERANCE returns Contradiction Found.
R4_TOLERANCE = Fraction(1, 10)  # 0.1 decimal (exact rational)

# ---------------------------------------------------------------------------
# Attention Score (F18) Configuration Weights
# ---------------------------------------------------------------------------
# Deterministic integer score 0–100 per parcel / simulation.
# Derived from fired alerts. Contradiction weight > Review weight.
# Consistent alerts always contribute 0 points.
ATTENTION_STATUS_BASE_WEIGHTS: dict[str, int] = {
    "CONTRADICTION": 40,
    "REVIEW": 15,
    "CONSISTENT": 0,
}

# Per-rule specific weights (points assigned when a rule fires with non-consistent status)
ATTENTION_RULE_WEIGHTS: dict[str, int] = {
    "R1": 45,   # Excess transfer (critical contradiction)
    "R2": 45,   # Duplicate portion allocation
    "R3": 40,   # Seller without interest
    "R4": 35,   # Subdivision area discrepancy
    "R5": 15,   # Survey continuity gap (Review only)
    "R6": 15,   # Deed-mutation mismatch (Review only)
    "R7": 40,   # Mutation precedes deed
    "R8": 25,   # Unaccounted heir declaration
    "R9": 45,   # Active mortgage at sale
    "R10": 40,  # Power of attorney discrepancy
    "R11": 50,  # Government / court lock
    "R12": 45,  # Deed hash mismatch
    "R13": 20,  # Reused deed number (Review only)
    "R14": 25,  # Identity ambiguity
    "R15": 45,  # Same portion sold twice (boundary match)
    "HYGIENE": 30,  # Undated or malformed history
}

TRAFFIC_LIGHT_RED = "red"
TRAFFIC_LIGHT_YELLOW = "yellow"
TRAFFIC_LIGHT_GREEN = "green"

LABEL_ATTENTION_SCORE_BN = "মনোযোগ স্কোর"
LABEL_ATTENTION_SCORE_EN = "Attention score"
DISCLAIMER_ATTENTION_SCORE_BN = "০ স্কোর মানে সরবরাহকৃত রেকর্ডে কোনো ফ্ল্যাগ পাওয়া যায়নি; এটি জমি সম্পর্কে কোনো চূড়ান্ত নিশ্চয়তা নয়।"
DISCLAIMER_ATTENTION_SCORE_EN = "A score of 0 means no flags were found in the supplied records; it is not a guarantee about the land."

