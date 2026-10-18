"""
JomiGraph AI — Demo Dataset Generator v1.1 (Phase 6 Foundation)
==============================================================
Generates synthetic, deterministic land records for v1.1 new rules (R8–R15):
  - Fixed seed: random.Random(1142)
  - All names and IDs are invented and synthetic
  - Fictional dummy IDs (e.g. DUMMY-ID-0001, DUMMY-ID-0002)
  - Exact rational area strings ("10", "5", "5/2"), NEVER floats
  - Covers planted cases for rules R8 to R15
  - Covers tricky clean cases (mortgage released before sale, POA revoked after sale,
    same deed covering two dags legitimately, same name with different dummy IDs)
  - Does NOT touch or mutate demo_family.json, demo_regions.json, or generator.py
"""

from __future__ import annotations

from datetime import date
from fractions import Fraction
import hashlib
import json
import random
import sys
from pathlib import Path

# Ensure src is on path for direct execution
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from jomigraph.loader import Dataset, parse_dataset_dict, save_dataset

DATA_DIR = Path(__file__).resolve().parent


def compute_canonical_deed_hash(
    deed_no: str,
    registration_date: str,
    parcel_id: str,
    seller: str,
    buyer: str,
    area: str,
) -> str:
    """Compute canonical SHA-256 fingerprint for a deed copy."""
    payload = json.dumps(
        {
            "area": area,
            "buyer": buyer,
            "deed_no": deed_no,
            "parcel_id": parcel_id,
            "registration_date": registration_date,
            "seller": seller,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_v11_dataset_dict(seed: int = 1142) -> dict[str, Any]:
    """Construct the v1.1 demo dataset dictionary with a fixed random seed."""
    rng = random.Random(seed)

    # 1. Persons (Invented names with dummy IDs for disambiguation)
    persons = [
        {"id": "P_V11_ALIM_1", "name": "Abdul Alim", "dummy_id": "DUMMY-ID-0001"},
        {"id": "P_V11_ALIM_2", "name": "Abdul Alim", "dummy_id": "DUMMY-ID-0002"},
        {"id": "P_V11_KARIM", "name": "Karim Baksh", "dummy_id": "DUMMY-ID-0003"},
        {"id": "P_V11_RAHIMA", "name": "Rahima Khatun", "dummy_id": "DUMMY-ID-0004"},
        {"id": "P_V11_SULTAN", "name": "Sultan Ahmed", "dummy_id": "DUMMY-ID-0005"},
        {"id": "P_V11_HASAN", "name": "Hasanuzzaman", "dummy_id": "DUMMY-ID-0006"},
        {"id": "P_V11_HEIR_A", "name": "Jashim Uddin", "dummy_id": "DUMMY-ID-0007"},
        {"id": "P_V11_HEIR_B", "name": "Khadija Begum", "dummy_id": "DUMMY-ID-0008"},
        {"id": "P_V11_POA_AGENT", "name": "Developer Agent Shamim", "dummy_id": "DUMMY-ID-0009"},
        {"id": "P_V11_BANK_REP", "name": "Fictional Bank Officer", "dummy_id": "DUMMY-ID-0010"},
        {"id": "P_V11_BUYER_1", "name": "Monir Hossain", "dummy_id": "DUMMY-ID-0011"},
        {"id": "P_V11_BUYER_2", "name": "Farhana Yasmin", "dummy_id": "DUMMY-ID-0012"},
        {"id": "P_V11_CLEAN_H1", "name": "Zubair Ahmed", "dummy_id": "DUMMY-ID-0013"},
        {"id": "P_V11_CLEAN_H2", "name": "Nusrat Jahan", "dummy_id": "DUMMY-ID-0014"},
        {"id": "P_V11_HASAN_SON", "name": "Hasan Junior", "dummy_id": "DUMMY-ID-0015"},
        {"id": "P_V11_HASAN_DAU", "name": "Rokeya Hasan", "dummy_id": "DUMMY-ID-0016"},
        {"id": "P_V11_JALIL", "name": "Jalil Miah", "dummy_id": "DUMMY-ID-0017"},
        {"id": "P_V11_JALIL_SON", "name": "Rafiq Jalil", "dummy_id": "DUMMY-ID-0018"},
        {"id": "P_V11_JALIL_DAU", "name": "Salma Jalil", "dummy_id": "DUMMY-ID-0019"},
        {"id": "P_V11_AMBIG_1", "name": "Tariqul Islam"},
        {"id": "P_V11_AMBIG_2", "name": "Tariqul Islam"},
    ]

    # Precompute deed hashes
    d12_hash = compute_canonical_deed_hash(
        deed_no="D-V11-1201",
        registration_date="2020-04-10",
        parcel_id="PARCEL_PLANTED_R12",
        seller="P_V11_SULTAN",
        buyer="P_V11_BUYER_1",
        area="5",
    )
    d12_clean_hash = compute_canonical_deed_hash(
        deed_no="D-V11-1202",
        registration_date="2021-06-15",
        parcel_id="PARCEL_CLEAN_R12",
        seller="P_V11_CLEAN_H1",
        buyer="P_V11_CLEAN_H2",
        area="4",
    )

    # 2. Deeds
    deeds = [
        {"id": "DEED_V11_R8_NADABI", "deed_no": "D-V11-0803", "registration_date": "2004-05-10"},
        {"id": "DEED_V11_R9_MORT", "deed_no": "D-V11-0901", "registration_date": "2018-03-01"},
        {"id": "DEED_V11_R9_SALE", "deed_no": "D-V11-0902", "registration_date": "2019-05-15"},
        {"id": "DEED_V11_R9_REL", "deed_no": "D-V11-0903", "registration_date": "2019-01-10"},
        {"id": "DEED_V11_R10_POA", "deed_no": "D-V11-1001", "registration_date": "2017-02-14"},
        {"id": "DEED_V11_R10_SALE", "deed_no": "D-V11-1002", "registration_date": "2019-08-20"},
        {"id": "DEED_V11_R10_REV", "deed_no": "D-V11-1003", "registration_date": "2018-12-01"},
        {"id": "DEED_V11_R11_SALE", "deed_no": "D-V11-1101", "registration_date": "2022-03-10"},
        {"id": "DEED_V11_R12_REC", "deed_no": "D-V11-1201", "registration_date": "2020-04-10", "content_hash": d12_hash},
        {"id": "DEED_V11_R12_CLEAN", "deed_no": "D-V11-1202", "registration_date": "2021-06-15", "content_hash": d12_clean_hash},
        {"id": "DEED_V11_SHARED_13", "deed_no": "D-V11-1301", "registration_date": "2016-07-20"},
        {"id": "DEED_V11_MULTI_13", "deed_no": "D-V11-1302", "registration_date": "2018-03-15"},
        {"id": "DEED_V11_R14_SALE1", "deed_no": "D-V11-1401", "registration_date": "2015-11-10"},
        {"id": "DEED_V11_R14_SALE2", "deed_no": "D-V11-1402", "registration_date": "2016-04-12"},
        {"id": "DEED_V11_R15_SALE1", "deed_no": "D-V11-1501", "registration_date": "2017-09-05"},
        {"id": "DEED_V11_R15_SALE2", "deed_no": "D-V11-1502", "registration_date": "2018-10-15"},
        {"id": "DEED_V11_CLEAN_01", "deed_no": "D-V11-2001", "registration_date": "2014-02-18"},
        {"id": "DEED_V11_CLEAN_02", "deed_no": "D-V11-2002", "registration_date": "2018-09-22"},
        {"id": "DEED_V11_R10_C_POA", "deed_no": "D-V11-1004", "registration_date": "2017-02-14"},
        {"id": "DEED_V11_R10_C_SALE", "deed_no": "D-V11-1005", "registration_date": "2018-05-20"},
        {"id": "DEED_V11_R10_C_REV", "deed_no": "D-V11-1006", "registration_date": "2018-12-01"},
        {"id": "DEED_V11_R11_C_SALE", "deed_no": "D-V11-1102", "registration_date": "2021-06-15"},
    ]
    # Clean deed_no syntax if needed
    for d in deeds:
        if "deed_no=" in d:
            d["deed_no"] = d.pop("deed_no=")

    # 3. Parcels (covering R8–R15 planted + clean)
    parcels = [
        # Planted cases
        {"id": "PARCEL_PLANTED_R8", "dag_no": "801", "mouza": "Savar", "parent_id": None},
        {"id": "PARCEL_PLANTED_R9", "dag_no": "901", "mouza": "Savar", "parent_id": None},
        {"id": "PARCEL_PLANTED_R10", "dag_no": "1001", "mouza": "Uttara", "parent_id": None},
        {
            "id": "PARCEL_PLANTED_R11",
            "dag_no": "1101",
            "mouza": "Tejgaon",
            "parent_id": None,
            "is_khas": True,
            "under_acquisition": True,
            "flag_date": "2020-01-01",
            "court_case_no": "DEMO-CASE-0011",
            "case_status": "pending",
            "injunction": True,
        },
        {"id": "PARCEL_PLANTED_R12", "dag_no": "1201", "mouza": "Mirpur", "parent_id": None},
        {"id": "PARCEL_PLANTED_R13_A", "dag_no": "1301", "mouza": "Dhanmondi", "parent_id": None},
        {"id": "PARCEL_PLANTED_R13_B", "dag_no": "1302", "mouza": "Dhanmondi", "parent_id": None},
        {"id": "PARCEL_PLANTED_R14", "dag_no": "1401", "mouza": "Gulshan", "parent_id": None},
        {"id": "PARCEL_PLANTED_R15", "dag_no": "1501", "mouza": "Badda", "parent_id": None},
        # Clean & tricky clean cases
        {"id": "PARCEL_CLEAN_R8", "dag_no": "802", "mouza": "Savar", "parent_id": None},
        {"id": "PARCEL_CLEAN_R8_TRICKY", "dag_no": "803", "mouza": "Savar", "parent_id": None},
        {"id": "PARCEL_CLEAN_R9_TRICKY", "dag_no": "902", "mouza": "Savar", "parent_id": None},
        {"id": "PARCEL_CLEAN_R10_TRICKY", "dag_no": "1002", "mouza": "Uttara", "parent_id": None},
        {
            "id": "PARCEL_CLEAN_R11",
            "dag_no": "1102",
            "mouza": "Tejgaon",
            "parent_id": None,
            "is_khas": True,
            "under_acquisition": True,
            "flag_date": "2023-01-01",
        },
        {"id": "PARCEL_CLEAN_R12", "dag_no": "1202", "mouza": "Mirpur", "parent_id": None},
        {"id": "PARCEL_CLEAN_R13_MULTI", "dag_no": "1303", "mouza": "Dhanmondi", "parent_id": None},
        {"id": "PARCEL_CLEAN_R14_DISAMBIG", "dag_no": "1402", "mouza": "Gulshan", "parent_id": None},
        {"id": "PARCEL_CLEAN_R15_BOUNDARY", "dag_no": "1502", "mouza": "Badda", "parent_id": None},
    ]

    # 4. Histories
    histories = []

    # Planted R8: Unaccounted heir
    sr_r8 = {
        "id": "SR_V11_R8",
        "parcel_id": "PARCEL_PLANTED_R8",
        "survey": "BS",
        "khatian_no": "8001",
        "record_date": "2000-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_KARIM", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R8",
        "baseline_record_id": "SR_V11_R8",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R8",
        "end_date": "2024-01-01",
        "survey_records": [sr_r8],
        "events": [
            {
                "id": "E_V11_R8_SALE",
                "type": "SALE",
                "seq": 1,
                "event_date": "2015-06-10",
                "parcel_id": "PARCEL_PLANTED_R8",
                "from_person": "P_V11_HEIR_A",
                "to_person": "P_V11_BUYER_1",
                "area": "10",
                "deed_id": "DEED_V11_CLEAN_01",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
            }
        ],
        "heir_declaration": {
            "deceased_id": "P_V11_KARIM",
            "complete": True,
            "declaration_date": "2010-01-01",
            "declared_heirs": [
                {"person_id": "P_V11_HEIR_A", "relation": "son"},
                {"person_id": "P_V11_HEIR_B", "relation": "daughter"},  # Unaccounted in next deed
            ],
            "source_record_id": "SANAD_V11_R8",
        },
    })

    # Clean R8: All declared heirs recorded in subsequent khatian
    sr_r8_c_bs = {
        "id": "SR_V11_R8_C_BS",
        "parcel_id": "PARCEL_CLEAN_R8",
        "survey": "BS",
        "khatian_no": "8003",
        "record_date": "2010-01-01",
        "recorded_area": "10",
        "holders": [
            {"person_id": "P_V11_HASAN_SON", "area": "5"},
            {"person_id": "P_V11_HASAN_DAU", "area": "5"},
        ],
    }
    histories.append({
        "parcel_id": "PARCEL_CLEAN_R8",
        "baseline_record_id": "SR_V11_R8_C_BS",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R8_C_BS",
        "end_date": "2024-01-01",
        "survey_records": [sr_r8_c_bs],
        "events": [],
        "heir_declaration": {
            "deceased_id": "P_V11_HASAN",
            "complete": True,
            "declaration_date": "2005-01-01",
            "declared_heirs": [
                {"person_id": "P_V11_HASAN_SON", "relation": "son"},
                {"person_id": "P_V11_HASAN_DAU", "relation": "daughter"},
            ],
            "source_record_id": "SANAD_V11_R8_C1",
        },
    })

    # Clean R8 Tricky: Omitted heir previously sold/released share by deed
    sr_r8_t_cs = {
        "id": "SR_V11_R8_T_CS",
        "parcel_id": "PARCEL_CLEAN_R8_TRICKY",
        "survey": "CS",
        "khatian_no": "8004",
        "record_date": "1990-01-01",
        "recorded_area": "10",
        "holders": [
            {"person_id": "P_V11_JALIL_SON", "area": "5"},
            {"person_id": "P_V11_JALIL_DAU", "area": "5"},
        ],
    }
    sr_r8_t_bs = {
        "id": "SR_V11_R8_T_BS",
        "parcel_id": "PARCEL_CLEAN_R8_TRICKY",
        "survey": "BS",
        "khatian_no": "8005",
        "record_date": "2008-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_JALIL_SON", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_CLEAN_R8_TRICKY",
        "baseline_record_id": "SR_V11_R8_T_CS",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R8_T_CS",
        "end_date": "2024-01-01",
        "survey_records": [sr_r8_t_cs, sr_r8_t_bs],
        "events": [
            {
                "id": "E_V11_R8_T_REL",
                "type": "SALE",
                "seq": 1,
                "event_date": "2004-05-10",
                "parcel_id": "PARCEL_CLEAN_R8_TRICKY",
                "from_person": "P_V11_JALIL_DAU",
                "to_person": "P_V11_JALIL_SON",
                "area": "5",
                "deed_id": "DEED_V11_R8_NADABI",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
            }
        ],
        "heir_declaration": {
            "deceased_id": "P_V11_JALIL",
            "complete": True,
            "declaration_date": "2000-01-01",
            "declared_heirs": [
                {"person_id": "P_V11_JALIL_SON", "relation": "son"},
                {"person_id": "P_V11_JALIL_DAU", "relation": "daughter"},
            ],
            "source_record_id": "SANAD_V11_R8_TRICKY",
        },
    })

    # Planted R9: Active mortgage at sale
    sr_r9 = {
        "id": "SR_V11_R9",
        "parcel_id": "PARCEL_PLANTED_R9",
        "survey": "BS",
        "khatian_no": "9001",
        "record_date": "2010-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_SULTAN", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R9",
        "baseline_record_id": "SR_V11_R9",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R9",
        "end_date": "2024-01-01",
        "survey_records": [sr_r9],
        "events": [
            {
                "id": "E_V11_R9_MORT",
                "type": "MORTGAGE",
                "seq": 1,
                "event_date": "2018-03-01",
                "parcel_id": "PARCEL_PLANTED_R9",
                "from_person": "P_V11_SULTAN",
                "to_person": "P_V11_BANK_REP",
                "area": "10",
                "deed_id": "DEED_V11_R9_MORT",
                "portion_id": "PORTION_9A",
                "linked_event_id": None,
                "source_record_id": None,
            },
            {
                "id": "E_V11_R9_SALE",
                "type": "SALE",
                "seq": 2,
                "event_date": "2019-05-15",
                "parcel_id": "PARCEL_PLANTED_R9",
                "from_person": "P_V11_SULTAN",
                "to_person": "P_V11_BUYER_1",
                "area": "5",
                "deed_id": "DEED_V11_R9_SALE",
                "portion_id": "PORTION_9A",
                "linked_event_id": None,
                "source_record_id": None,
            },
        ],
    })

    # Clean Tricky R9: Mortgage released before sale
    sr_r9_c = {
        "id": "SR_V11_R9_C",
        "parcel_id": "PARCEL_CLEAN_R9_TRICKY",
        "survey": "BS",
        "khatian_no": "9002",
        "record_date": "2010-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_SULTAN", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_CLEAN_R9_TRICKY",
        "baseline_record_id": "SR_V11_R9_C",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R9_C",
        "end_date": "2024-01-01",
        "survey_records": [sr_r9_c],
        "events": [
            {
                "id": "E_V11_R9_C_MORT",
                "type": "MORTGAGE",
                "seq": 1,
                "event_date": "2018-03-01",
                "parcel_id": "PARCEL_CLEAN_R9_TRICKY",
                "from_person": "P_V11_SULTAN",
                "to_person": "P_V11_BANK_REP",
                "area": "10",
                "deed_id": "DEED_V11_R9_MORT",
                "portion_id": "PORTION_9B",
                "linked_event_id": None,
                "source_record_id": None,
            },
            {
                "id": "E_V11_R9_C_REL",
                "type": "MORTGAGE_RELEASE",
                "seq": 2,
                "event_date": "2019-01-10",
                "parcel_id": "PARCEL_CLEAN_R9_TRICKY",
                "from_person": "P_V11_BANK_REP",
                "to_person": "P_V11_SULTAN",
                "area": "10",
                "deed_id": "DEED_V11_R9_REL",
                "portion_id": "PORTION_9B",
                "linked_event_id": "E_V11_R9_C_MORT",
                "source_record_id": None,
            },
            {
                "id": "E_V11_R9_C_SALE",
                "type": "SALE",
                "seq": 3,
                "event_date": "2019-05-15",
                "parcel_id": "PARCEL_CLEAN_R9_TRICKY",
                "from_person": "P_V11_SULTAN",
                "to_person": "P_V11_BUYER_1",
                "area": "5",
                "deed_id": "DEED_V11_R9_SALE",
                "portion_id": "PORTION_9B",
                "linked_event_id": None,
                "source_record_id": None,
            },
        ],
    })

    # Planted R10: Sale under revoked POA
    sr_r10 = {
        "id": "SR_V11_R10",
        "parcel_id": "PARCEL_PLANTED_R10",
        "survey": "BS",
        "khatian_no": "10001",
        "record_date": "2010-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_RAHIMA", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R10",
        "baseline_record_id": "SR_V11_R10",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R10",
        "end_date": "2024-01-01",
        "survey_records": [sr_r10],
        "events": [
            {
                "id": "E_V11_R10_GRANT",
                "type": "POA_GRANT",
                "seq": 1,
                "event_date": "2017-02-14",
                "parcel_id": "PARCEL_PLANTED_R10",
                "from_person": "P_V11_RAHIMA",
                "to_person": "P_V11_POA_AGENT",
                "area": "10",
                "deed_id": "DEED_V11_R10_POA",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
            },
            {
                "id": "E_V11_R10_REVOKE",
                "type": "POA_REVOKE",
                "seq": 2,
                "event_date": "2018-12-01",
                "parcel_id": "PARCEL_PLANTED_R10",
                "from_person": "P_V11_RAHIMA",
                "to_person": "P_V11_POA_AGENT",
                "area": "10",
                "deed_id": "DEED_V11_R10_REV",
                "portion_id": None,
                "linked_event_id": "E_V11_R10_GRANT",
                "source_record_id": None,
            },
            {
                "id": "E_V11_R10_SALE",
                "type": "SALE",
                "seq": 3,
                "event_date": "2019-08-20",
                "parcel_id": "PARCEL_PLANTED_R10",
                "from_person": "P_V11_RAHIMA",
                "to_person": "P_V11_BUYER_2",
                "area": "5",
                "deed_id": "DEED_V11_R10_SALE",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
                "via_poa_id": "E_V11_R10_GRANT",
            },
        ],
    })

    # Planted R11: Sale after government lock
    sr_r11 = {
        "id": "SR_V11_R11",
        "parcel_id": "PARCEL_PLANTED_R11",
        "survey": "BS",
        "khatian_no": "11001",
        "record_date": "2015-01-01",
        "recorded_area": "8",
        "holders": [{"person_id": "P_V11_HASAN", "area": "8"}],
    }
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R11",
        "baseline_record_id": "SR_V11_R11",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R11",
        "end_date": "2024-01-01",
        "survey_records": [sr_r11],
        "events": [
            {
                "id": "E_V11_R11_SALE",
                "type": "SALE",
                "seq": 1,
                "event_date": "2022-03-10",  # Dated AFTER flag_date 2020-01-01
                "parcel_id": "PARCEL_PLANTED_R11",
                "from_person": "P_V11_HASAN",
                "to_person": "P_V11_BUYER_1",
                "area": "4",
                "deed_id": "DEED_V11_R11_SALE",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
            }
        ],
    })

    # Clean Tricky R10: Sale executed under valid POA, revoked AFTER sale
    sr_r10_c = {
        "id": "SR_V11_R10_C",
        "parcel_id": "PARCEL_CLEAN_R10_TRICKY",
        "survey": "BS",
        "khatian_no": "10002",
        "record_date": "2010-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_RAHIMA", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_CLEAN_R10_TRICKY",
        "baseline_record_id": "SR_V11_R10_C",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R10_C",
        "end_date": "2024-01-01",
        "survey_records": [sr_r10_c],
        "events": [
            {
                "id": "E_V11_R10_C_GRANT",
                "type": "POA_GRANT",
                "seq": 1,
                "event_date": "2017-02-14",
                "parcel_id": "PARCEL_CLEAN_R10_TRICKY",
                "from_person": "P_V11_RAHIMA",
                "to_person": "P_V11_POA_AGENT",
                "area": "10",
                "deed_id": "DEED_V11_R10_C_POA",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
            },
            {
                "id": "E_V11_R10_C_SALE",
                "type": "SALE",
                "seq": 2,
                "event_date": "2018-05-20",  # Dated BEFORE revocation on 2018-12-01
                "parcel_id": "PARCEL_CLEAN_R10_TRICKY",
                "from_person": "P_V11_POA_AGENT",
                "to_person": "P_V11_BUYER_2",
                "area": "5",
                "deed_id": "DEED_V11_R10_C_SALE",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
                "via_poa_id": "E_V11_R10_C_GRANT",
            },
            {
                "id": "E_V11_R10_C_REVOKE",
                "type": "POA_REVOKE",
                "seq": 3,
                "event_date": "2018-12-01",  # Dated AFTER sale
                "parcel_id": "PARCEL_CLEAN_R10_TRICKY",
                "from_person": "P_V11_RAHIMA",
                "to_person": "P_V11_POA_AGENT",
                "area": "10",
                "deed_id": "DEED_V11_R10_C_REV",
                "portion_id": None,
                "linked_event_id": "E_V11_R10_C_GRANT",
                "source_record_id": None,
            },
        ],
    })

    # Clean R11: Sale occurred before government flag date
    sr_r11_c = {
        "id": "SR_V11_R11_C",
        "parcel_id": "PARCEL_CLEAN_R11",
        "survey": "BS",
        "khatian_no": "11002",
        "record_date": "2015-01-01",
        "recorded_area": "8",
        "holders": [{"person_id": "P_V11_HASAN", "area": "8"}],
    }
    histories.append({
        "parcel_id": "PARCEL_CLEAN_R11",
        "baseline_record_id": "SR_V11_R11_C",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R11_C",
        "end_date": "2024-01-01",
        "survey_records": [sr_r11_c],
        "events": [
            {
                "id": "E_V11_R11_C_SALE",
                "type": "SALE",
                "seq": 1,
                "event_date": "2021-06-15",  # Dated BEFORE flag_date 2023-01-01
                "parcel_id": "PARCEL_CLEAN_R11",
                "from_person": "P_V11_HASAN",
                "to_person": "P_V11_BUYER_1",
                "area": "4",
                "deed_id": "DEED_V11_R11_C_SALE",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
            }
        ],
    })

    # Planted R15: Same portion sold twice with matching boundaries
    sr_r15 = {
        "id": "SR_V11_R15",
        "parcel_id": "PARCEL_PLANTED_R15",
        "survey": "BS",
        "khatian_no": "15001",
        "record_date": "2012-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_KARIM", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R15",
        "baseline_record_id": "SR_V11_R15",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R15",
        "end_date": "2024-01-01",
        "survey_records": [sr_r15],
        "events": [
            {
                "id": "E_V11_R15_SALE1",
                "type": "SALE",
                "seq": 1,
                "event_date": "2017-09-05",
                "parcel_id": "PARCEL_PLANTED_R15",
                "from_person": "P_V11_KARIM",
                "to_person": "P_V11_BUYER_1",
                "area": "5",
                "deed_id": "DEED_V11_R15_SALE1",
                "portion_id": "PORTION_NORTH",
                "linked_event_id": None,
                "source_record_id": None,
                "portion": {"portion_id": "PORTION_NORTH", "boundary": "North roadside plot", "portion_area": "5"},
                "boundary": "North roadside plot",
            },
            {
                "id": "E_V11_R15_SALE2",
                "type": "SALE",
                "seq": 2,
                "event_date": "2018-10-15",
                "parcel_id": "PARCEL_PLANTED_R15",
                "from_person": "P_V11_KARIM",
                "to_person": "P_V11_BUYER_2",
                "area": "5",
                "deed_id": "DEED_V11_R15_SALE2",
                "portion_id": "PORTION_SPECIAL_1",  # Different portion_id, same boundary
                "linked_event_id": None,
                "source_record_id": None,
                "portion": {"portion_id": "PORTION_SPECIAL_1", "boundary": "North roadside plot", "portion_area": "5"},
                "boundary": "North roadside plot",
            },
        ],
    })

    # Clean R15: Two distinct boundaries
    sr_r15_c = {
        "id": "SR_V11_R15_C",
        "parcel_id": "PARCEL_CLEAN_R15_BOUNDARY",
        "survey": "BS",
        "khatian_no": "15002",
        "record_date": "2012-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_CLEAN_H1", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_CLEAN_R15_BOUNDARY",
        "baseline_record_id": "SR_V11_R15_C",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R15_C",
        "end_date": "2024-01-01",
        "survey_records": [sr_r15_c],
        "events": [
            {
                "id": "E_V11_R15_C_1",
                "type": "SALE",
                "seq": 1,
                "event_date": "2017-09-05",
                "parcel_id": "PARCEL_CLEAN_R15_BOUNDARY",
                "from_person": "P_V11_CLEAN_H1",
                "to_person": "P_V11_BUYER_1",
                "area": "5",
                "deed_id": "DEED_V11_R15_SALE1",
                "portion_id": "PORTION_NORTH",
                "linked_event_id": None,
                "source_record_id": None,
                "portion": {"portion_id": "PORTION_NORTH", "boundary": "North plot", "portion_area": "5"},
                "boundary": "North plot",
            },
            {
                "id": "E_V11_R15_C_2",
                "type": "SALE",
                "seq": 2,
                "event_date": "2018-10-15",
                "parcel_id": "PARCEL_CLEAN_R15_BOUNDARY",
                "from_person": "P_V11_CLEAN_H1",
                "to_person": "P_V11_BUYER_2",
                "area": "5",
                "deed_id": "DEED_V11_R15_SALE2",
                "portion_id": "PORTION_SOUTH",
                "linked_event_id": None,
                "source_record_id": None,
                "portion": {"portion_id": "PORTION_SOUTH", "boundary": "South plot", "portion_area": "5"},
                "boundary": "South plot",
            },
        ],
    })

    # Planted R12: Tampered deed content
    sr_r12 = {
        "id": "SR_V11_R12",
        "parcel_id": "PARCEL_PLANTED_R12",
        "survey": "BS",
        "khatian_no": "12001",
        "record_date": "2010-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_SULTAN", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R12",
        "baseline_record_id": "SR_V11_R12",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R12",
        "end_date": "2024-01-01",
        "survey_records": [sr_r12],
        "events": [
            {
                "id": "E_V11_R12_SALE",
                "type": "SALE",
                "seq": 1,
                "event_date": "2020-04-10",
                "parcel_id": "PARCEL_PLANTED_R12",
                "from_person": "P_V11_SULTAN",
                "to_person": "P_V11_BUYER_1",
                "area": "7",  # Tampered: recorded content_hash was computed with area="5"
                "deed_id": "DEED_V11_R12_REC",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
            }
        ],
    })

    # Clean R12: Consistent deed content hash
    sr_r12_c = {
        "id": "SR_V11_R12_C",
        "parcel_id": "PARCEL_CLEAN_R12",
        "survey": "BS",
        "khatian_no": "12002",
        "record_date": "2010-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_CLEAN_H1", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_CLEAN_R12",
        "baseline_record_id": "SR_V11_R12_C",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R12_C",
        "end_date": "2024-01-01",
        "survey_records": [sr_r12_c],
        "events": [
            {
                "id": "E_V11_R12_C_SALE",
                "type": "SALE",
                "seq": 1,
                "event_date": "2021-06-15",
                "parcel_id": "PARCEL_CLEAN_R12",
                "from_person": "P_V11_CLEAN_H1",
                "to_person": "P_V11_CLEAN_H2",
                "area": "4",  # Matches recorded content_hash
                "deed_id": "DEED_V11_R12_CLEAN",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
            }
        ],
    })

    # Planted R13: Reused deed number across parcels with differing terms
    sr_r13_a = {
        "id": "SR_V11_R13_A",
        "parcel_id": "PARCEL_PLANTED_R13_A",
        "survey": "BS",
        "khatian_no": "13001",
        "record_date": "2010-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_SULTAN", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R13_A",
        "baseline_record_id": "SR_V11_R13_A",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R13_A",
        "end_date": "2024-01-01",
        "survey_records": [sr_r13_a],
        "events": [
            {
                "id": "E_V11_R13_A",
                "type": "SALE",
                "seq": 1,
                "event_date": "2016-07-20",
                "parcel_id": "PARCEL_PLANTED_R13_A",
                "from_person": "P_V11_SULTAN",
                "to_person": "P_V11_BUYER_1",
                "area": "5",
                "deed_id": "DEED_V11_SHARED_13",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
            }
        ],
    })

    sr_r13_b = {
        "id": "SR_V11_R13_B",
        "parcel_id": "PARCEL_PLANTED_R13_B",
        "survey": "BS",
        "khatian_no": "13002",
        "record_date": "2010-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_KARIM", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R13_B",
        "baseline_record_id": "SR_V11_R13_B",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R13_B",
        "end_date": "2024-01-01",
        "survey_records": [sr_r13_b],
        "events": [
            {
                "id": "E_V11_R13_B",
                "type": "SALE",
                "seq": 1,
                "event_date": "2018-09-01",
                "parcel_id": "PARCEL_PLANTED_R13_B",
                "from_person": "P_V11_KARIM",
                "to_person": "P_V11_BUYER_2",
                "area": "8",
                "deed_id": "DEED_V11_SHARED_13",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
            }
        ],
    })

    # Clean R13: Clean single/multi-dag transaction
    sr_r13_m = {
        "id": "SR_V11_R13_M",
        "parcel_id": "PARCEL_CLEAN_R13_MULTI",
        "survey": "BS",
        "khatian_no": "13003",
        "record_date": "2010-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_CLEAN_H1", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_CLEAN_R13_MULTI",
        "baseline_record_id": "SR_V11_R13_M",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R13_M",
        "end_date": "2024-01-01",
        "survey_records": [sr_r13_m],
        "events": [
            {
                "id": "E_V11_R13_M",
                "type": "SALE",
                "seq": 1,
                "event_date": "2018-03-15",
                "parcel_id": "PARCEL_CLEAN_R13_MULTI",
                "from_person": "P_V11_CLEAN_H1",
                "to_person": "P_V11_CLEAN_H2",
                "area": "5",
                "deed_id": "DEED_V11_MULTI_13",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
            }
        ],
    })

    # Planted R14: Duplicate person name without dummy_id
    sr_r14 = {
        "id": "SR_V11_R14",
        "parcel_id": "PARCEL_PLANTED_R14",
        "survey": "BS",
        "khatian_no": "14001",
        "record_date": "2010-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_AMBIG_1", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R14",
        "baseline_record_id": "SR_V11_R14",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R14",
        "end_date": "2024-01-01",
        "survey_records": [sr_r14],
        "events": [
            {
                "id": "E_V11_R14_SALE",
                "type": "SALE",
                "seq": 1,
                "event_date": "2015-11-10",
                "parcel_id": "PARCEL_PLANTED_R14",
                "from_person": "P_V11_AMBIG_1",
                "to_person": "P_V11_AMBIG_2",
                "area": "5",
                "deed_id": "DEED_V11_R14_SALE1",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
            }
        ],
    })

    # Clean R14: Disambiguated duplicate names with distinct dummy_id
    sr_r14_c = {
        "id": "SR_V11_R14_C",
        "parcel_id": "PARCEL_CLEAN_R14_DISAMBIG",
        "survey": "BS",
        "khatian_no": "14002",
        "record_date": "2010-01-01",
        "recorded_area": "10",
        "holders": [{"person_id": "P_V11_ALIM_1", "area": "10"}],
    }
    histories.append({
        "parcel_id": "PARCEL_CLEAN_R14_DISAMBIG",
        "baseline_record_id": "SR_V11_R14_C",
        "baseline_complete": True,
        "start_record_id": "SR_V11_R14_C",
        "end_date": "2024-01-01",
        "survey_records": [sr_r14_c],
        "events": [
            {
                "id": "E_V11_R14_C_SALE",
                "type": "SALE",
                "seq": 1,
                "event_date": "2016-04-12",
                "parcel_id": "PARCEL_CLEAN_R14_DISAMBIG",
                "from_person": "P_V11_ALIM_1",
                "to_person": "P_V11_ALIM_2",
                "area": "5",
                "deed_id": "DEED_V11_R14_SALE2",
                "portion_id": None,
                "linked_event_id": None,
                "source_record_id": None,
            }
        ],
    })

    return {
        "persons": persons,
        "parcels": parcels,
        "deeds": deeds,
        "histories": histories,
    }


def main() -> None:
    data_dict = build_v11_dataset_dict()
    dataset = parse_dataset_dict(data_dict)
    out_file = DATA_DIR / "demo_v11.json"
    save_dataset(dataset, out_file)
    print(f"Generated v1.1 demo dataset at: {out_file} ({len(dataset.parcels)} parcels)")


if __name__ == "__main__":
    main()
