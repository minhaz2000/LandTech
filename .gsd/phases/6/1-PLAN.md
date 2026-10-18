# Phase 6 Plan: v1.1 Core Foundation

> **Phase**: 6
> **Objective**: Shared rule dispatcher, extended data models & loader, config weights, v1.1 demo dataset foundation.
> **Status**: In Progress

## Tasks

1. **Shared Rule Dispatcher Refactor (`src/jomigraph/engine/rules.py`, `src/jomigraph/engine/simulate.py`, `src/jomigraph/engine/benchmark.py`)**:
   - Extract `dispatch_event_rules` and `dispatch_history_rules` into `rules.py`.
   - Wire `evaluate()` in `simulate.py` and `evaluate_history()` in `benchmark.py` to use the shared dispatcher.
   - Verify deterministic rule ordering (R3 -> R1 -> R2 for SALE/GIFT, R4 for SUBDIVIDE, R6 -> R7 for MUTATION, R5 for successive survey records).
   - Ensure simulation pure-function contract and dataset hash are preserved.

2. **Data Model Extensions (`src/jomigraph/models.py`)**:
   - `Deed.content_hash: Optional[str] = None`
   - `Person.dummy_id: Optional[str] = None`
   - `Event.portion: Optional[dict[str, Any]] = None`
   - `Event.boundary: Optional[str | dict[str, Any]] = None`
   - `Event.via_poa_id: Optional[str] = None`
   - `Parcel.is_khas: bool = False`
   - `Parcel.under_acquisition: bool = False`
   - `Parcel.flag_date: Optional[date] = None`
   - `Parcel.court_case_no: Optional[str] = None`
   - `Parcel.case_status: Optional[str] = None`
   - `Parcel.injunction: bool = False`
   - `EventType`: `MORTGAGE = "MORTGAGE"`, `MORTGAGE_RELEASE = "MORTGAGE_RELEASE"`, `POA_GRANT = "POA_GRANT"`, `POA_REVOKE = "POA_REVOKE"`
   - `ParcelHistory.heir_declaration: Optional[dict[str, Any] | list[Any]] = None`

3. **Data Loader & Replay Updates (`src/jomigraph/loader.py`, `src/jomigraph/engine/replay.py`, `src/jomigraph/engine/simulate.py`)**:
   - Update `parse_dataset_dict` and `dataset_to_dict` to handle new fields transparently with defaults.
   - Update `compute_state` in `replay.py` to recognize `MORTGAGE`, `MORTGAGE_RELEASE`, `POA_GRANT`, `POA_REVOKE` as valid non-transferring event types.
   - Update `hash_dataset` in `simulate.py` to include new event fields only when present, preserving the existing baseline dataset hash.

4. **Configuration Constants (`src/jomigraph/config.py`)**:
   - Add attention weights tables (`ATTENTION_STATUS_WEIGHTS` and `ATTENTION_RULE_WEIGHTS`) for deterministic 0–100 attention scoring.

5. **Demo v1.1 Dataset Generator & Skeleton (`data/generator_v11.py`, `data/demo_v11.json`)**:
   - Create deterministic fixed-seed generator for v1.1 synthetic data.
   - Create valid `data/demo_v11.json` skeleton covering the new models and event types.

6. **Regression & Foundation Tests (`tests/test_phase6_foundation.py`)**:
   - Test shared dispatcher consistency.
   - Test model backward compatibility and serialization.
   - Test non-transferring replay of mortgage and POA events.
   - Test dataset hash immutability.
   - Test `demo_v11.json` loading and schema validity.
