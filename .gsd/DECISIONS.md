# DECISIONS.md — Architecture Decision Records

## ADR-001: fractions.Fraction for all arithmetic
**Date**: 2026-10-14
**Status**: Accepted
**Context**: Land area arithmetic must be exact to avoid floating-point drift that could produce false positives or mask contradictions.
**Decision**: Use Python's `fractions.Fraction` for all area and share calculations. No floats anywhere in the rules engine.
**Consequences**: All comparison and arithmetic operations must use Fraction. The tolerance in R4 is also a Fraction.

## ADR-002: Three statuses only
**Date**: 2026-10-14
**Status**: Accepted
**Context**: A richer status vocabulary risks implying legal certainty the system cannot provide.
**Decision**: Exactly three statuses. Never use synonyms "safe", "valid", "legal", "fraud".

## ADR-003: Evaluation order — missing inputs before baseline_complete
**Date**: 2026-10-14
**Status**: Accepted
**Context**: baseline_complete=true must not silently paper over missing evidence.
**Decision**: Always check required inputs first; return Review Required if any is missing. Only then apply baseline_complete and the rule logic.

## ADR-004: Pure evaluate() function
**Date**: 2026-10-14
**Status**: Accepted
**Context**: Simulations must never mutate historical data.
**Decision**: evaluate(events, parcel_history) is a pure function. Simulations pass a new list (events + [proposed]) and verify the baseline hash before and after.
