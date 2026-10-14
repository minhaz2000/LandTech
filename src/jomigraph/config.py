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
