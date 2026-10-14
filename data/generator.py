"""
JomiGraph AI — Demo Dataset Generator
====================================
Generates synthetic, deterministic land records for the demo dataset:
  - Fixed seed: random.Random(42)
  - All names are invented and synthetic
  - All areas are represented as exact rational strings ("10", "7/2"), NEVER floats
  - Main story: One family across four generations (CS, SA, RS, BS)
    with 8 to 10 parcels, including 1 valid subdivision (diff = 0)
    and baseline_complete=True for story parcels.
  - Seven planted problem parcels:
    (a) PARCEL_PLANTED_R1: over-transfer (10 sold 7, later sold 5 -> R1 Contradiction excess 2)
    (b) PARCEL_PLANTED_R2: duplicate portion sale without cancellation (R2 Contradiction)
    (c) PARCEL_PLANTED_R3: stranger sells, not a recorded holder (R3 Contradiction)
    (d) PARCEL_PLANTED_R4: children sum != parent area (R4 Contradiction)
    (e) PARCEL_PLANTED_R5: survey gap with unlinked successive records (R5 Review)
    (f) PARCEL_PLANTED_R6: mutation area does not match linked sale area (R6 Review)
    (g) PARCEL_PLANTED_R7: mutation date precedes deed registration date (R7 Contradiction)
  - 20 clean parcels/cases with valid transfers returning zero Contradictions and zero Reviews.
  - No unsupported CANCEL/CORRECT events and no undated events anywhere.
"""

from __future__ import annotations

from datetime import date
from fractions import Fraction
from pathlib import Path
import random
from typing import Any

from jomigraph.loader import Dataset, parse_dataset_dict, save_dataset


def build_raw_dataset_dict(seed: int = 42) -> dict[str, Any]:
    """
    Construct the demo dataset dictionary with a fixed random seed.
    All areas are strings, all names invented.
    """
    rng = random.Random(seed)

    # 1. Persons (Family across 4 generations + External buyers/sellers)
    persons = [
        # Generation 1 (Great Grandfather)
        {"id": "P_G1_RAHIM", "name": "Abdur Rahim Chowdhury"},
        # Generation 2 (Grandfather & Aunt)
        {"id": "P_G2_KHORSHED", "name": "Khorshed Alam Chowdhury"},
        {"id": "P_G2_ROKEYA", "name": "Rokeya Begum"},
        # Generation 3 (Father & Uncle)
        {"id": "P_G3_TAREQ", "name": "Tareq Mahmud Chowdhury"},
        {"id": "P_G3_ENAMUL", "name": "Enamul Haque Chowdhury"},
        # Generation 4 (Son & Daughter)
        {"id": "P_G4_FARHAN", "name": "Farhan Mahmud Chowdhury"},
        {"id": "P_G4_SADIA", "name": "Sadia Mahmud Chowdhury"},
        # External parties (all invented names)
        {"id": "P_EXT_LATIF", "name": "Abdul Latif Mia"},
        {"id": "P_EXT_RAFIQ", "name": "Rafiqul Islam"},
        {"id": "P_EXT_KABIR", "name": "Kabir Hossain"},
        {"id": "P_EXT_MONIR", "name": "Monirul Haque"},
        {"id": "P_EXT_SHAHID", "name": "Shahidul Alam"},
        {"id": "P_EXT_BASHAR", "name": "Abul Bashar"},
        {"id": "P_EXT_JAHANGIR", "name": "Jahangir Sikder"},
        {"id": "P_EXT_ALI", "name": "Mohammad Ali"},
        {"id": "P_EXT_NASREEN", "name": "Nasreen Akhtar"},
        {"id": "P_EXT_DELWAR", "name": "Delwar Hossain"},
        {"id": "P_EXT_FARIDA", "name": "Farida Yasmin"},
        {"id": "P_EXT_KAMAL", "name": "Kamal Uddin"},
        {"id": "P_EXT_SELIM", "name": "Selim Reza"},
        {"id": "P_EXT_MAMTAZ", "name": "Mamtaz Begum"},
        {"id": "P_EXT_ANIS", "name": "Anisur Rahman"},
        {"id": "P_EXT_BILKIS", "name": "Bilkis Banu"},
        {"id": "P_EXT_SHAFIQ", "name": "Shafiqul Huq"},
        {"id": "P_EXT_TARIQ", "name": "Tariqul Islam"},
        {"id": "P_EXT_MOSTAFA", "name": "Mostafa Kamal"},
        {"id": "P_EXT_ZILLUR", "name": "Zillur Rahman"},
        {"id": "P_EXT_HASINA", "name": "Hasina Khatun"},
        {"id": "P_EXT_NURUL", "name": "Nurul Huda"},
    ]

    # 2. Deeds
    deeds = [
        # Story deeds
        {"id": "DEED_STORY_01_GIFT1", "deed_no": "D-1948-001", "registration_date": "1948-02-10"},
        {"id": "DEED_STORY_01_GIFT2", "deed_no": "D-1975-002", "registration_date": "1975-06-15"},
        {"id": "DEED_STORY_01_GIFT3", "deed_no": "D-2005-003", "registration_date": "2005-09-20"},
        {"id": "DEED_STORY_02_1", "deed_no": "D-1942-011", "registration_date": "1942-01-15"},
        {"id": "DEED_STORY_02_2", "deed_no": "D-1978-012", "registration_date": "1978-08-10"},
        {"id": "DEED_STORY_03_1", "deed_no": "D-1968-021", "registration_date": "1968-04-12"},
        {"id": "DEED_STORY_03_2", "deed_no": "D-1999-022", "registration_date": "1999-11-05"},
        {"id": "DEED_STORY_04_1", "deed_no": "D-1952-031", "registration_date": "1952-10-14"},
        {"id": "DEED_STORY_05_1", "deed_no": "D-2001-041", "registration_date": "2001-03-25"},
        {"id": "DEED_STORY_06_1", "deed_no": "D-1935-051", "registration_date": "1935-07-20"},
        {"id": "DEED_STORY_06_2", "deed_no": "D-1938-052", "registration_date": "1938-11-12"},
        {"id": "DEED_STORY_07_1", "deed_no": "D-1990-061", "registration_date": "1990-05-18"},
        {"id": "DEED_STORY_09_1", "deed_no": "D-2016-071", "registration_date": "2016-01-10"},
        {"id": "DEED_STORY_10_1", "deed_no": "D-2016-072", "registration_date": "2016-03-20"},
        # Additional clean deeds
        {"id": "DEED_CLEAN_01_1", "deed_no": "D-1992-101", "registration_date": "1992-06-15"},
        {"id": "DEED_CLEAN_02_1", "deed_no": "D-1965-102", "registration_date": "1965-09-10"},
        {"id": "DEED_CLEAN_03_1", "deed_no": "D-1930-103", "registration_date": "1930-03-12"},
        {"id": "DEED_CLEAN_03_2", "deed_no": "D-1934-104", "registration_date": "1934-08-22"},
        {"id": "DEED_CLEAN_04_1", "deed_no": "D-1968-105", "registration_date": "1968-02-14"},
        {"id": "DEED_CLEAN_04_2", "deed_no": "D-1975-106", "registration_date": "1975-10-30"},
        {"id": "DEED_CLEAN_05_1", "deed_no": "D-1988-107", "registration_date": "1988-04-10"},
        {"id": "DEED_CLEAN_06_1", "deed_no": "D-2018-108", "registration_date": "2018-01-20"},
        {"id": "DEED_CLEAN_07_1", "deed_no": "D-1971-109", "registration_date": "1971-11-08"},
        {"id": "DEED_CLEAN_08_1", "deed_no": "D-1960-110", "registration_date": "1960-03-15"},
        {"id": "DEED_CLEAN_08_2", "deed_no": "D-2000-111", "registration_date": "2000-08-20"},
        {"id": "DEED_CLEAN_09_1", "deed_no": "D-1995-112", "registration_date": "1995-05-10"},
        {"id": "DEED_CLEAN_10_1", "deed_no": "D-1990-113", "registration_date": "1990-01-15"},
        {"id": "DEED_CLEAN_10_2", "deed_no": "D-1992-114", "registration_date": "1992-08-10"},
        # Lab demo deed
        {"id": "DEED_LAB_DEMO_1", "deed_no": "D-1995-301", "registration_date": "1995-04-10"},
        # Planted deeds
        {"id": "DEED_PLANTED_R1_1", "deed_no": "D-1930-201", "registration_date": "1930-05-10"},
        {"id": "DEED_PLANTED_R1_2", "deed_no": "D-1935-202", "registration_date": "1935-08-20"},
        {"id": "DEED_PLANTED_R2_1", "deed_no": "D-1930-203", "registration_date": "1930-04-10"},
        {"id": "DEED_PLANTED_R2_2", "deed_no": "D-1932-204", "registration_date": "1932-09-15"},
        {"id": "DEED_PLANTED_R3_1", "deed_no": "D-1930-205", "registration_date": "1930-05-10"},
        # Planted R6: mutation area mismatch with sale
        {"id": "DEED_PLANTED_R6_1", "deed_no": "D-1985-206", "registration_date": "1985-09-10"},
        # Planted R7: deed registered after mutation date
        {"id": "DEED_PLANTED_R7_1", "deed_no": "D-1995-207", "registration_date": "1995-06-20"},
    ]

    # 3. Parcels (10 story + 10 clean + 1 lab demo + 9 planted = 30 total)
    parcels = [
        # Story parcels
        {"id": "PARCEL_STORY_01", "dag_no": "101", "mouza": "Dhanmondi", "parent_id": None},
        {"id": "PARCEL_STORY_02", "dag_no": "102", "mouza": "Dhanmondi", "parent_id": None},
        {"id": "PARCEL_STORY_03", "dag_no": "103", "mouza": "Dhanmondi", "parent_id": None},
        {"id": "PARCEL_STORY_04", "dag_no": "104", "mouza": "Dhanmondi", "parent_id": None},
        {"id": "PARCEL_STORY_05", "dag_no": "105", "mouza": "Dhanmondi", "parent_id": None},
        {"id": "PARCEL_STORY_06", "dag_no": "106", "mouza": "Dhanmondi", "parent_id": None},
        {"id": "PARCEL_STORY_07", "dag_no": "107", "mouza": "Dhanmondi", "parent_id": None},
        {"id": "PARCEL_STORY_08", "dag_no": "108", "mouza": "Dhanmondi", "parent_id": None},  # Subdivision Parent
        {"id": "PARCEL_STORY_09", "dag_no": "108/A", "mouza": "Dhanmondi", "parent_id": "PARCEL_STORY_08"},  # Child 1
        {"id": "PARCEL_STORY_10", "dag_no": "108/B", "mouza": "Dhanmondi", "parent_id": "PARCEL_STORY_08"},  # Child 2
        # Clean parcels
        {"id": "PARCEL_CLEAN_01", "dag_no": "201", "mouza": "Tejgaon", "parent_id": None},
        {"id": "PARCEL_CLEAN_02", "dag_no": "202", "mouza": "Tejgaon", "parent_id": None},
        {"id": "PARCEL_CLEAN_03", "dag_no": "203", "mouza": "Tejgaon", "parent_id": None},
        {"id": "PARCEL_CLEAN_04", "dag_no": "204", "mouza": "Tejgaon", "parent_id": None},
        {"id": "PARCEL_CLEAN_05", "dag_no": "205", "mouza": "Tejgaon", "parent_id": None},
        {"id": "PARCEL_CLEAN_06", "dag_no": "206", "mouza": "Tejgaon", "parent_id": None},
        {"id": "PARCEL_CLEAN_07", "dag_no": "207", "mouza": "Tejgaon", "parent_id": None},
        {"id": "PARCEL_CLEAN_08", "dag_no": "208", "mouza": "Tejgaon", "parent_id": None},
        {"id": "PARCEL_CLEAN_09", "dag_no": "209", "mouza": "Tejgaon", "parent_id": None},
        {"id": "PARCEL_CLEAN_10", "dag_no": "210", "mouza": "Tejgaon", "parent_id": None},
        # Lab demo parcel
        {"id": "PARCEL_LAB_DEMO", "dag_no": "401", "mouza": "Dhanmondi", "parent_id": None},
        # Planted problem parcels
        {"id": "PARCEL_PLANTED_R1", "dag_no": "301", "mouza": "Mirpur", "parent_id": None},
        {"id": "PARCEL_PLANTED_R2", "dag_no": "302", "mouza": "Mirpur", "parent_id": None},
        {"id": "PARCEL_PLANTED_R3", "dag_no": "303", "mouza": "Mirpur", "parent_id": None},
        {"id": "PARCEL_PLANTED_R4", "dag_no": "304", "mouza": "Mirpur", "parent_id": None},
        {"id": "PARCEL_PLANTED_R4_A", "dag_no": "304/A", "mouza": "Mirpur", "parent_id": "PARCEL_PLANTED_R4"},
        {"id": "PARCEL_PLANTED_R4_B", "dag_no": "304/B", "mouza": "Mirpur", "parent_id": "PARCEL_PLANTED_R4"},
        {"id": "PARCEL_PLANTED_R5", "dag_no": "305", "mouza": "Mirpur", "parent_id": None},
        {"id": "PARCEL_PLANTED_R6", "dag_no": "306", "mouza": "Mirpur", "parent_id": None},
        {"id": "PARCEL_PLANTED_R7", "dag_no": "307", "mouza": "Mirpur", "parent_id": None},
    ]

    # 4. Histories
    histories: list[dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # Story Parcel 01: All 4 survey records (CS, SA, RS, BS) with linking gifts
    # -------------------------------------------------------------------------
    histories.append({
        "parcel_id": "PARCEL_STORY_01",
        "baseline_record_id": "SR_S01_CS",
        "baseline_complete": True,
        "start_record_id": "SR_S01_CS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_S01_CS", "parcel_id": "PARCEL_STORY_01", "survey": "CS",
                "khatian_no": "1001", "record_date": "1920-03-15", "recorded_area": "40",
                "holders": [{"person_id": "P_G1_RAHIM", "area": "40"}],
            },
            {
                "id": "SR_S01_SA", "parcel_id": "PARCEL_STORY_01", "survey": "SA",
                "khatian_no": "2001", "record_date": "1958-05-20", "recorded_area": "40",
                "holders": [{"person_id": "P_G2_KHORSHED", "area": "40"}],
            },
            {
                "id": "SR_S01_RS", "parcel_id": "PARCEL_STORY_01", "survey": "RS",
                "khatian_no": "3001", "record_date": "1982-11-10", "recorded_area": "40",
                "holders": [{"person_id": "P_G3_TAREQ", "area": "40"}],
            },
            {
                "id": "SR_S01_BS", "parcel_id": "PARCEL_STORY_01", "survey": "BS",
                "khatian_no": "4001", "record_date": "2015-02-18", "recorded_area": "40",
                "holders": [{"person_id": "P_G4_FARHAN", "area": "40"}],
            },
        ],
        "events": [
            {
                "id": "E_S01_1", "type": "GIFT", "seq": 1, "event_date": "1948-02-10",
                "parcel_id": "PARCEL_STORY_01", "from_person": "P_G1_RAHIM", "to_person": "P_G2_KHORSHED",
                "area": "40", "deed_id": "DEED_STORY_01_GIFT1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                "id": "E_S01_2", "type": "GIFT", "seq": 2, "event_date": "1975-06-15",
                "parcel_id": "PARCEL_STORY_01", "from_person": "P_G2_KHORSHED", "to_person": "P_G3_TAREQ",
                "area": "40", "deed_id": "DEED_STORY_01_GIFT2", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                "id": "E_S01_3", "type": "GIFT", "seq": 3, "event_date": "2005-09-20",
                "parcel_id": "PARCEL_STORY_01", "from_person": "P_G3_TAREQ", "to_person": "P_G4_FARHAN",
                "area": "40", "deed_id": "DEED_STORY_01_GIFT3", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # -------------------------------------------------------------------------
    # Story Parcel 02: CS, SA, RS surveys linked by valid sales
    # -------------------------------------------------------------------------
    histories.append({
        "parcel_id": "PARCEL_STORY_02",
        "baseline_record_id": "SR_S02_CS",
        "baseline_complete": True,
        "start_record_id": "SR_S02_CS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_S02_CS", "parcel_id": "PARCEL_STORY_02", "survey": "CS",
                "khatian_no": "1002", "record_date": "1920-03-15", "recorded_area": "25",
                "holders": [{"person_id": "P_G1_RAHIM", "area": "25"}],
            },
            {
                "id": "SR_S02_SA", "parcel_id": "PARCEL_STORY_02", "survey": "SA",
                "khatian_no": "2002", "record_date": "1958-05-20", "recorded_area": "25",
                "holders": [{"person_id": "P_G2_KHORSHED", "area": "25"}],
            },
            {
                "id": "SR_S02_RS", "parcel_id": "PARCEL_STORY_02", "survey": "RS",
                "khatian_no": "3002", "record_date": "1982-11-10", "recorded_area": "25",
                "holders": [{"person_id": "P_G3_TAREQ", "area": "25"}],
            },
        ],
        "events": [
            {
                "id": "E_S02_1", "type": "SALE", "seq": 1, "event_date": "1942-01-15",
                "parcel_id": "PARCEL_STORY_02", "from_person": "P_G1_RAHIM", "to_person": "P_G2_KHORSHED",
                "area": "25", "deed_id": "DEED_STORY_02_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                "id": "E_S02_2", "type": "SALE", "seq": 2, "event_date": "1978-08-10",
                "parcel_id": "PARCEL_STORY_02", "from_person": "P_G2_KHORSHED", "to_person": "P_G3_TAREQ",
                "area": "25", "deed_id": "DEED_STORY_02_2", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # -------------------------------------------------------------------------
    # Story Parcel 03: SA, RS, BS surveys linked by gift and sale
    # -------------------------------------------------------------------------
    histories.append({
        "parcel_id": "PARCEL_STORY_03",
        "baseline_record_id": "SR_S03_SA",
        "baseline_complete": True,
        "start_record_id": "SR_S03_SA",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_S03_SA", "parcel_id": "PARCEL_STORY_03", "survey": "SA",
                "khatian_no": "2003", "record_date": "1958-05-20", "recorded_area": "15",
                "holders": [{"person_id": "P_G2_KHORSHED", "area": "15"}],
            },
            {
                "id": "SR_S03_RS", "parcel_id": "PARCEL_STORY_03", "survey": "RS",
                "khatian_no": "3003", "record_date": "1982-11-10", "recorded_area": "15",
                "holders": [{"person_id": "P_G3_TAREQ", "area": "15"}],
            },
            {
                "id": "SR_S03_BS", "parcel_id": "PARCEL_STORY_03", "survey": "BS",
                "khatian_no": "4003", "record_date": "2015-02-18", "recorded_area": "15",
                "holders": [{"person_id": "P_G4_FARHAN", "area": "15"}],
            },
        ],
        "events": [
            {
                "id": "E_S03_1", "type": "GIFT", "seq": 1, "event_date": "1968-04-12",
                "parcel_id": "PARCEL_STORY_03", "from_person": "P_G2_KHORSHED", "to_person": "P_G3_TAREQ",
                "area": "15", "deed_id": "DEED_STORY_03_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                "id": "E_S03_2", "type": "SALE", "seq": 2, "event_date": "1999-11-05",
                "parcel_id": "PARCEL_STORY_03", "from_person": "P_G3_TAREQ", "to_person": "P_G4_FARHAN",
                "area": "15", "deed_id": "DEED_STORY_03_2", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # -------------------------------------------------------------------------
    # Story Parcel 04: CS to SA gift
    # -------------------------------------------------------------------------
    histories.append({
        "parcel_id": "PARCEL_STORY_04",
        "baseline_record_id": "SR_S04_CS",
        "baseline_complete": True,
        "start_record_id": "SR_S04_CS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_S04_CS", "parcel_id": "PARCEL_STORY_04", "survey": "CS",
                "khatian_no": "1004", "record_date": "1920-03-15", "recorded_area": "18",
                "holders": [{"person_id": "P_G1_RAHIM", "area": "18"}],
            },
            {
                "id": "SR_S04_SA", "parcel_id": "PARCEL_STORY_04", "survey": "SA",
                "khatian_no": "2004", "record_date": "1958-05-20", "recorded_area": "18",
                "holders": [{"person_id": "P_G2_ROKEYA", "area": "18"}],
            },
        ],
        "events": [
            {
                "id": "E_S04_1", "type": "GIFT", "seq": 1, "event_date": "1952-10-14",
                "parcel_id": "PARCEL_STORY_04", "from_person": "P_G1_RAHIM", "to_person": "P_G2_ROKEYA",
                "area": "18", "deed_id": "DEED_STORY_04_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # -------------------------------------------------------------------------
    # Story Parcel 05: RS to BS gift
    # -------------------------------------------------------------------------
    histories.append({
        "parcel_id": "PARCEL_STORY_05",
        "baseline_record_id": "SR_S05_RS",
        "baseline_complete": True,
        "start_record_id": "SR_S05_RS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_S05_RS", "parcel_id": "PARCEL_STORY_05", "survey": "RS",
                "khatian_no": "3005", "record_date": "1982-11-10", "recorded_area": "12",
                "holders": [{"person_id": "P_G3_ENAMUL", "area": "12"}],
            },
            {
                "id": "SR_S05_BS", "parcel_id": "PARCEL_STORY_05", "survey": "BS",
                "khatian_no": "4005", "record_date": "2015-02-18", "recorded_area": "12",
                "holders": [{"person_id": "P_G4_SADIA", "area": "12"}],
            },
        ],
        "events": [
            {
                "id": "E_S05_1", "type": "GIFT", "seq": 1, "event_date": "2001-03-25",
                "parcel_id": "PARCEL_STORY_05", "from_person": "P_G3_ENAMUL", "to_person": "P_G4_SADIA",
                "area": "12", "deed_id": "DEED_STORY_05_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # -------------------------------------------------------------------------
    # Story Parcel 06: CS baseline with two partial sales to external parties
    # -------------------------------------------------------------------------
    histories.append({
        "parcel_id": "PARCEL_STORY_06",
        "baseline_record_id": "SR_S06_CS",
        "baseline_complete": True,
        "start_record_id": "SR_S06_CS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_S06_CS", "parcel_id": "PARCEL_STORY_06", "survey": "CS",
                "khatian_no": "1006", "record_date": "1920-03-15", "recorded_area": "30",
                "holders": [{"person_id": "P_G1_RAHIM", "area": "30"}],
            },
        ],
        "events": [
            {
                "id": "E_S06_1", "type": "SALE", "seq": 1, "event_date": "1935-07-20",
                "parcel_id": "PARCEL_STORY_06", "from_person": "P_G1_RAHIM", "to_person": "P_EXT_LATIF",
                "area": "10", "deed_id": "DEED_STORY_06_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                "id": "E_S06_2", "type": "SALE", "seq": 2, "event_date": "1938-11-12",
                "parcel_id": "PARCEL_STORY_06", "from_person": "P_G1_RAHIM", "to_person": "P_EXT_RAFIQ",
                "area": "10", "deed_id": "DEED_STORY_06_2", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # -------------------------------------------------------------------------
    # Story Parcel 07: RS baseline with sale and registered mutation
    # -------------------------------------------------------------------------
    histories.append({
        "parcel_id": "PARCEL_STORY_07",
        "baseline_record_id": "SR_S07_RS",
        "baseline_complete": True,
        "start_record_id": "SR_S07_RS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_S07_RS", "parcel_id": "PARCEL_STORY_07", "survey": "RS",
                "khatian_no": "3007", "record_date": "1982-11-10", "recorded_area": "14",
                "holders": [{"person_id": "P_G3_TAREQ", "area": "14"}],
            },
        ],
        "events": [
            {
                "id": "E_S07_1", "type": "SALE", "seq": 1, "event_date": "1990-05-18",
                "parcel_id": "PARCEL_STORY_07", "from_person": "P_G3_TAREQ", "to_person": "P_EXT_KABIR",
                "area": "6", "deed_id": "DEED_STORY_07_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                "id": "E_S07_2", "type": "MUTATION", "seq": 2, "event_date": "1990-07-22",
                "parcel_id": "PARCEL_STORY_07", "from_person": None, "to_person": "P_EXT_KABIR",
                "area": "6", "deed_id": "DEED_STORY_07_1", "portion_id": None,
                "linked_event_id": "E_S07_1", "source_record_id": None,
            },
        ],
    })

    # -------------------------------------------------------------------------
    # Story Parcels 08, 09, 10: Valid Subdivision (20 = 12 + 8)
    # -------------------------------------------------------------------------
    # Parent Parcel 08
    histories.append({
        "parcel_id": "PARCEL_STORY_08",
        "baseline_record_id": "SR_S08_RS",
        "baseline_complete": True,
        "start_record_id": "SR_S08_RS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_S08_RS", "parcel_id": "PARCEL_STORY_08", "survey": "RS",
                "khatian_no": "3008", "record_date": "1982-11-10", "recorded_area": "20",
                "holders": [{"person_id": "P_G3_TAREQ", "area": "20"}],
            },
        ],
        "events": [
            {
                "id": "E_S08_SUBDIV", "type": "SUBDIVIDE", "seq": 1, "event_date": "2008-04-15",
                "parcel_id": "PARCEL_STORY_08", "from_person": "P_G3_TAREQ", "to_person": None,
                "area": "20", "deed_id": None, "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # Child Parcel 09 (Child 1 of Parcel 08: 12 decimals)
    histories.append({
        "parcel_id": "PARCEL_STORY_09",
        "baseline_record_id": "SR_S09_BS",
        "baseline_complete": True,
        "start_record_id": "SR_S09_BS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_S09_BS", "parcel_id": "PARCEL_STORY_09", "survey": "BS",
                "khatian_no": "4009", "record_date": "2015-02-18", "recorded_area": "12",
                "holders": [{"person_id": "P_G4_FARHAN", "area": "12"}],
            },
        ],
        "events": [
            {
                "id": "E_S09_1", "type": "SALE", "seq": 1, "event_date": "2016-01-10",
                "parcel_id": "PARCEL_STORY_09", "from_person": "P_G4_FARHAN", "to_person": "P_EXT_MONIR",
                "area": "4", "deed_id": "DEED_STORY_09_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # Child Parcel 10 (Child 2 of Parcel 08: 8 decimals)
    histories.append({
        "parcel_id": "PARCEL_STORY_10",
        "baseline_record_id": "SR_S10_BS",
        "baseline_complete": True,
        "start_record_id": "SR_S10_BS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_S10_BS", "parcel_id": "PARCEL_STORY_10", "survey": "BS",
                "khatian_no": "4010", "record_date": "2015-02-18", "recorded_area": "8",
                "holders": [{"person_id": "P_G4_SADIA", "area": "8"}],
            },
        ],
        "events": [
            {
                "id": "E_S10_1", "type": "GIFT", "seq": 1, "event_date": "2016-03-20",
                "parcel_id": "PARCEL_STORY_10", "from_person": "P_G4_SADIA", "to_person": "P_EXT_SHAHID",
                "area": "3", "deed_id": "DEED_STORY_10_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # -------------------------------------------------------------------------
    # 10 Additional Clean Parcels (Clean Parcels 01 to 10)
    # -------------------------------------------------------------------------
    # Clean 01: Simple sale
    histories.append({
        "parcel_id": "PARCEL_CLEAN_01",
        "baseline_record_id": "SR_C01_RS",
        "baseline_complete": True,
        "start_record_id": "SR_C01_RS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_C01_RS", "parcel_id": "PARCEL_CLEAN_01", "survey": "RS",
                "khatian_no": "5001", "record_date": "1982-11-10", "recorded_area": "20",
                "holders": [{"person_id": "P_EXT_LATIF", "area": "20"}],
            },
        ],
        "events": [
            {
                "id": "E_C01_1", "type": "SALE", "seq": 1, "event_date": "1992-06-15",
                "parcel_id": "PARCEL_CLEAN_01", "from_person": "P_EXT_LATIF", "to_person": "P_EXT_MONIR",
                "area": "8", "deed_id": "DEED_CLEAN_01_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # Clean 02: Simple gift
    histories.append({
        "parcel_id": "PARCEL_CLEAN_02",
        "baseline_record_id": "SR_C02_SA",
        "baseline_complete": True,
        "start_record_id": "SR_C02_SA",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_C02_SA", "parcel_id": "PARCEL_CLEAN_02", "survey": "SA",
                "khatian_no": "5002", "record_date": "1958-05-20", "recorded_area": "15",
                "holders": [{"person_id": "P_EXT_RAFIQ", "area": "15"}],
            },
        ],
        "events": [
            {
                "id": "E_C02_1", "type": "GIFT", "seq": 1, "event_date": "1965-09-10",
                "parcel_id": "PARCEL_CLEAN_02", "from_person": "P_EXT_RAFIQ", "to_person": "P_EXT_KABIR",
                "area": "5", "deed_id": "DEED_CLEAN_02_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # Clean 03: Sequential sales from holder
    histories.append({
        "parcel_id": "PARCEL_CLEAN_03",
        "baseline_record_id": "SR_C03_CS",
        "baseline_complete": True,
        "start_record_id": "SR_C03_CS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_C03_CS", "parcel_id": "PARCEL_CLEAN_03", "survey": "CS",
                "khatian_no": "5003", "record_date": "1920-03-15", "recorded_area": "30",
                "holders": [{"person_id": "P_EXT_SHAHID", "area": "30"}],
            },
        ],
        "events": [
            {
                "id": "E_C03_1", "type": "SALE", "seq": 1, "event_date": "1930-03-12",
                "parcel_id": "PARCEL_CLEAN_03", "from_person": "P_EXT_SHAHID", "to_person": "P_EXT_BASHAR",
                "area": "10", "deed_id": "DEED_CLEAN_03_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                "id": "E_C03_2", "type": "SALE", "seq": 2, "event_date": "1934-08-22",
                "parcel_id": "PARCEL_CLEAN_03", "from_person": "P_EXT_SHAHID", "to_person": "P_EXT_JAHANGIR",
                "area": "12", "deed_id": "DEED_CLEAN_03_2", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # Clean 04: Chain of title (buyer becomes subsequent seller)
    histories.append({
        "parcel_id": "PARCEL_CLEAN_04",
        "baseline_record_id": "SR_C04_SA",
        "baseline_complete": True,
        "start_record_id": "SR_C04_SA",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_C04_SA", "parcel_id": "PARCEL_CLEAN_04", "survey": "SA",
                "khatian_no": "5004", "record_date": "1958-05-20", "recorded_area": "20",
                "holders": [{"person_id": "P_EXT_ALI", "area": "20"}],
            },
        ],
        "events": [
            {
                "id": "E_C04_1", "type": "SALE", "seq": 1, "event_date": "1968-02-14",
                "parcel_id": "PARCEL_CLEAN_04", "from_person": "P_EXT_ALI", "to_person": "P_EXT_NASREEN",
                "area": "10", "deed_id": "DEED_CLEAN_04_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                "id": "E_C04_2", "type": "SALE", "seq": 2, "event_date": "1975-10-30",
                "parcel_id": "PARCEL_CLEAN_04", "from_person": "P_EXT_NASREEN", "to_person": "P_EXT_DELWAR",
                "area": "6", "deed_id": "DEED_CLEAN_04_2", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # Clean 05: Sale + Mutation (R6 & R7 clean)
    histories.append({
        "parcel_id": "PARCEL_CLEAN_05",
        "baseline_record_id": "SR_C05_RS",
        "baseline_complete": True,
        "start_record_id": "SR_C05_RS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_C05_RS", "parcel_id": "PARCEL_CLEAN_05", "survey": "RS",
                "khatian_no": "5005", "record_date": "1982-11-10", "recorded_area": "18",
                "holders": [{"person_id": "P_EXT_FARIDA", "area": "18"}],
            },
        ],
        "events": [
            {
                "id": "E_C05_1", "type": "SALE", "seq": 1, "event_date": "1988-04-10",
                "parcel_id": "PARCEL_CLEAN_05", "from_person": "P_EXT_FARIDA", "to_person": "P_EXT_KAMAL",
                "area": "7", "deed_id": "DEED_CLEAN_05_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                "id": "E_C05_2", "type": "MUTATION", "seq": 2, "event_date": "1988-06-15",
                "parcel_id": "PARCEL_CLEAN_05", "from_person": None, "to_person": "P_EXT_KAMAL",
                "area": "7", "deed_id": "DEED_CLEAN_05_1", "portion_id": None,
                "linked_event_id": "E_C05_1", "source_record_id": None,
            },
        ],
    })

    # Clean 06: Sale + Mutation in modern period
    histories.append({
        "parcel_id": "PARCEL_CLEAN_06",
        "baseline_record_id": "SR_C06_BS",
        "baseline_complete": True,
        "start_record_id": "SR_C06_BS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_C06_BS", "parcel_id": "PARCEL_CLEAN_06", "survey": "BS",
                "khatian_no": "5006", "record_date": "2015-02-18", "recorded_area": "25",
                "holders": [{"person_id": "P_EXT_SELIM", "area": "25"}],
            },
        ],
        "events": [
            {
                "id": "E_C06_1", "type": "SALE", "seq": 1, "event_date": "2018-01-20",
                "parcel_id": "PARCEL_CLEAN_06", "from_person": "P_EXT_SELIM", "to_person": "P_EXT_MAMTAZ",
                "area": "15", "deed_id": "DEED_CLEAN_06_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                "id": "E_C06_2", "type": "MUTATION", "seq": 2, "event_date": "2018-04-12",
                "parcel_id": "PARCEL_CLEAN_06", "from_person": None, "to_person": "P_EXT_MAMTAZ",
                "area": "15", "deed_id": "DEED_CLEAN_06_1", "portion_id": None,
                "linked_event_id": "E_C06_1", "source_record_id": None,
            },
        ],
    })

    # Clean 07: SA and RS survey continuity (R5 clean)
    histories.append({
        "parcel_id": "PARCEL_CLEAN_07",
        "baseline_record_id": "SR_C07_SA",
        "baseline_complete": True,
        "start_record_id": "SR_C07_SA",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_C07_SA", "parcel_id": "PARCEL_CLEAN_07", "survey": "SA",
                "khatian_no": "5007", "record_date": "1958-05-20", "recorded_area": "22",
                "holders": [{"person_id": "P_EXT_ANIS", "area": "22"}],
            },
            {
                "id": "SR_C07_RS", "parcel_id": "PARCEL_CLEAN_07", "survey": "RS",
                "khatian_no": "6007", "record_date": "1982-11-10", "recorded_area": "22",
                "holders": [{"person_id": "P_EXT_BILKIS", "area": "22"}],
            },
        ],
        "events": [
            {
                "id": "E_C07_1", "type": "SALE", "seq": 1, "event_date": "1971-11-08",
                "parcel_id": "PARCEL_CLEAN_07", "from_person": "P_EXT_ANIS", "to_person": "P_EXT_BILKIS",
                "area": "22", "deed_id": "DEED_CLEAN_07_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # Clean 08: Three-survey continuity CS -> RS -> BS (R5 clean)
    histories.append({
        "parcel_id": "PARCEL_CLEAN_08",
        "baseline_record_id": "SR_C08_CS",
        "baseline_complete": True,
        "start_record_id": "SR_C08_CS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_C08_CS", "parcel_id": "PARCEL_CLEAN_08", "survey": "CS",
                "khatian_no": "5008", "record_date": "1920-03-15", "recorded_area": "16",
                "holders": [{"person_id": "P_EXT_SHAFIQ", "area": "16"}],
            },
            {
                "id": "SR_C08_RS", "parcel_id": "PARCEL_CLEAN_08", "survey": "RS",
                "khatian_no": "6008", "record_date": "1982-11-10", "recorded_area": "16",
                "holders": [{"person_id": "P_EXT_TARIQ", "area": "16"}],
            },
            {
                "id": "SR_C08_BS", "parcel_id": "PARCEL_CLEAN_08", "survey": "BS",
                "khatian_no": "7008", "record_date": "2015-02-18", "recorded_area": "16",
                "holders": [{"person_id": "P_EXT_MOSTAFA", "area": "16"}],
            },
        ],
        "events": [
            {
                "id": "E_C08_1", "type": "SALE", "seq": 1, "event_date": "1960-03-15",
                "parcel_id": "PARCEL_CLEAN_08", "from_person": "P_EXT_SHAFIQ", "to_person": "P_EXT_TARIQ",
                "area": "16", "deed_id": "DEED_CLEAN_08_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                "id": "E_C08_2", "type": "SALE", "seq": 2, "event_date": "2000-08-20",
                "parcel_id": "PARCEL_CLEAN_08", "from_person": "P_EXT_TARIQ", "to_person": "P_EXT_MOSTAFA",
                "area": "16", "deed_id": "DEED_CLEAN_08_2", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # Clean 09: Single portion sale with lineage (R2 clean)
    histories.append({
        "parcel_id": "PARCEL_CLEAN_09",
        "baseline_record_id": "SR_C09_RS",
        "baseline_complete": True,
        "start_record_id": "SR_C09_RS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_C09_RS", "parcel_id": "PARCEL_CLEAN_09", "survey": "RS",
                "khatian_no": "5009", "record_date": "1982-11-10", "recorded_area": "18",
                "holders": [{"person_id": "P_EXT_ZILLUR", "area": "18"}],
            },
        ],
        "events": [
            {
                "id": "E_C09_1", "type": "SALE", "seq": 1, "event_date": "1995-05-10",
                "parcel_id": "PARCEL_CLEAN_09", "from_person": "P_EXT_ZILLUR", "to_person": "P_EXT_HASINA",
                "area": "5", "deed_id": "DEED_CLEAN_09_1", "portion_id": "PORTION_DAG_209_SOUTH",
                "linked_event_id": "ROOT_DEED_CLEAN_09", "source_record_id": None,
            },
        ],
    })

    # Clean 10: Two sequential partial sales from holder
    histories.append({
        "parcel_id": "PARCEL_CLEAN_10",
        "baseline_record_id": "SR_C10_RS",
        "baseline_complete": True,
        "start_record_id": "SR_C10_RS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_C10_RS", "parcel_id": "PARCEL_CLEAN_10", "survey": "RS",
                "khatian_no": "5010", "record_date": "1982-11-10", "recorded_area": "25",
                "holders": [{"person_id": "P_EXT_LATIF", "area": "25"}],
            },
        ],
        "events": [
            {
                "id": "E_C10_1", "type": "SALE", "seq": 1, "event_date": "1990-01-15",
                "parcel_id": "PARCEL_CLEAN_10", "from_person": "P_EXT_LATIF", "to_person": "P_EXT_RAFIQ",
                "area": "10", "deed_id": "DEED_CLEAN_10_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                "id": "E_C10_2", "type": "SALE", "seq": 2, "event_date": "1993-04-20",
                "parcel_id": "PARCEL_CLEAN_10", "from_person": "P_EXT_LATIF", "to_person": "P_EXT_KABIR",
                "area": "8", "deed_id": "DEED_CLEAN_10_2", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # -------------------------------------------------------------------------
    # 3 Planted Problem Parcels (R1, R2, R5)
    # -------------------------------------------------------------------------
    # Planted 1: R1 Over-transfer (Holder has 10, sells 7, later sells 5 -> R1 Contradiction excess 2)
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R1",
        "baseline_record_id": "SR_PLANTED_R1_CS",
        "baseline_complete": True,
        "start_record_id": "SR_PLANTED_R1_CS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_PLANTED_R1_CS", "parcel_id": "PARCEL_PLANTED_R1", "survey": "CS",
                "khatian_no": "9001", "record_date": "1920-03-15", "recorded_area": "10",
                "holders": [{"person_id": "P_G1_RAHIM", "area": "10"}],
            },
        ],
        "events": [
            {
                "id": "E_PLANTED_R1_1", "type": "SALE", "seq": 1, "event_date": "1930-05-10",
                "parcel_id": "PARCEL_PLANTED_R1", "from_person": "P_G1_RAHIM", "to_person": "P_EXT_LATIF",
                "area": "7", "deed_id": "DEED_PLANTED_R1_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                "id": "E_PLANTED_R1_2", "type": "SALE", "seq": 2, "event_date": "1935-08-20",
                "parcel_id": "PARCEL_PLANTED_R1", "from_person": "P_G1_RAHIM", "to_person": "P_EXT_RAFIQ",
                "area": "5", "deed_id": "DEED_PLANTED_R1_2", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # Planted 2: R2 Duplicate portion sale to two buyers without cancellation
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R2",
        "baseline_record_id": "SR_PLANTED_R2_CS",
        "baseline_complete": True,
        "start_record_id": "SR_PLANTED_R2_CS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_PLANTED_R2_CS", "parcel_id": "PARCEL_PLANTED_R2", "survey": "CS",
                "khatian_no": "9002", "record_date": "1920-03-15", "recorded_area": "20",
                "holders": [{"person_id": "P_G1_RAHIM", "area": "20"}],
            },
        ],
        "events": [
            {
                "id": "E_PLANTED_R2_1", "type": "SALE", "seq": 1, "event_date": "1930-04-10",
                "parcel_id": "PARCEL_PLANTED_R2", "from_person": "P_G1_RAHIM", "to_person": "P_EXT_BASHAR",
                "area": "5", "deed_id": "DEED_PLANTED_R2_1", "portion_id": "PORTION_DAG_101_NORTH",
                "linked_event_id": "PARENT_DEED_1920", "source_record_id": None,
            },
            {
                "id": "E_PLANTED_R2_2", "type": "SALE", "seq": 2, "event_date": "1932-09-15",
                "parcel_id": "PARCEL_PLANTED_R2", "from_person": "P_G1_RAHIM", "to_person": "P_EXT_JAHANGIR",
                "area": "5", "deed_id": "DEED_PLANTED_R2_2", "portion_id": "PORTION_DAG_101_NORTH",
                "linked_event_id": "PARENT_DEED_1920", "source_record_id": None,
            },
        ],
    })

    # Planted 3: R5 Survey gap where later survey holder has no linking transaction
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R5",
        "baseline_record_id": "SR_PLANTED_R5_CS",
        "baseline_complete": True,
        "start_record_id": "SR_PLANTED_R5_CS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_PLANTED_R5_CS", "parcel_id": "PARCEL_PLANTED_R5", "survey": "CS",
                "khatian_no": "9005", "record_date": "1920-03-15", "recorded_area": "15",
                "holders": [{"person_id": "P_G1_RAHIM", "area": "15"}],
            },
            {
                "id": "SR_PLANTED_R5_RS", "parcel_id": "PARCEL_PLANTED_R5", "survey": "RS",
                "khatian_no": "9006", "record_date": "1982-11-10", "recorded_area": "15",
                "holders": [{"person_id": "P_EXT_NURUL", "area": "15"}],
            },
        ],
        "events": [],
    })

    # Planted 4: R3 Stranger sells, not a recorded holder
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R3",
        "baseline_record_id": "SR_PLANTED_R3_CS",
        "baseline_complete": True,
        "start_record_id": "SR_PLANTED_R3_CS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_PLANTED_R3_CS", "parcel_id": "PARCEL_PLANTED_R3", "survey": "CS",
                "khatian_no": "9003", "record_date": "1920-03-15", "recorded_area": "15",
                "holders": [{"person_id": "P_G1_RAHIM", "area": "15"}],
            },
        ],
        "events": [
            {
                "id": "E_PLANTED_R3_1", "type": "SALE", "seq": 1, "event_date": "1930-05-10",
                "parcel_id": "PARCEL_PLANTED_R3", "from_person": "P_EXT_BASHAR", "to_person": "P_EXT_JAHANGIR",
                "area": "5", "deed_id": "DEED_PLANTED_R3_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # Planted 5: R4 Children sum to parent minus more than R4_TOLERANCE (parent 20, children 10 + 8 = 18, diff 2 > 0.01)
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R4",
        "baseline_record_id": "SR_PLANTED_R4_RS",
        "baseline_complete": True,
        "start_record_id": "SR_PLANTED_R4_RS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_PLANTED_R4_RS", "parcel_id": "PARCEL_PLANTED_R4", "survey": "RS",
                "khatian_no": "9004", "record_date": "1982-11-10", "recorded_area": "20",
                "holders": [{"person_id": "P_G3_TAREQ", "area": "20"}],
            },
        ],
        "events": [
            {
                "id": "E_PLANTED_R4_SUBDIV", "type": "SUBDIVIDE", "seq": 1, "event_date": "2008-04-15",
                "parcel_id": "PARCEL_PLANTED_R4", "from_person": "P_G3_TAREQ", "to_person": None,
                "area": "20", "deed_id": None, "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # Child 1 of Planted R4 parent (area 10)
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R4_A",
        "baseline_record_id": "SR_PLANTED_R4_A_BS",
        "baseline_complete": True,
        "start_record_id": "SR_PLANTED_R4_A_BS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_PLANTED_R4_A_BS", "parcel_id": "PARCEL_PLANTED_R4_A", "survey": "BS",
                "khatian_no": "9014", "record_date": "2015-02-18", "recorded_area": "10",
                "holders": [{"person_id": "P_G4_FARHAN", "area": "10"}],
            },
        ],
        "events": [],
    })

    # Child 2 of Planted R4 parent (area 8)
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R4_B",
        "baseline_record_id": "SR_PLANTED_R4_B_BS",
        "baseline_complete": True,
        "start_record_id": "SR_PLANTED_R4_B_BS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_PLANTED_R4_B_BS", "parcel_id": "PARCEL_PLANTED_R4_B", "survey": "BS",
                "khatian_no": "9024", "record_date": "2015-02-18", "recorded_area": "8",
                "holders": [{"person_id": "P_G4_SADIA", "area": "8"}],
            },
        ],
        "events": [],
    })

    # Lab demo parcel: H=10, sells 7 to B, baseline_complete=True, no pending second sale
    histories.append({
        "parcel_id": "PARCEL_LAB_DEMO",
        "baseline_record_id": "SR_LAB_DEMO_RS",
        "baseline_complete": True,
        "start_record_id": "SR_LAB_DEMO_RS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_LAB_DEMO_RS", "parcel_id": "PARCEL_LAB_DEMO", "survey": "RS",
                "khatian_no": "8001", "record_date": "1982-11-10", "recorded_area": "10",
                "holders": [{"person_id": "P_G3_TAREQ", "area": "10"}],
            },
        ],
        "events": [
            {
                "id": "E_LAB_DEMO_1", "type": "SALE", "seq": 1, "event_date": "1995-04-10",
                "parcel_id": "PARCEL_LAB_DEMO", "from_person": "P_G3_TAREQ", "to_person": "P_EXT_KABIR",
                "area": "7", "deed_id": "DEED_LAB_DEMO_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
        ],
    })

    # -------------------------------------------------------------------------
    # Planted 6: R6 Deed-mutation reconciliation mismatch
    # Sale area = 9, mutation area = 7 (on the same deed) -> R6 Review Required
    # -------------------------------------------------------------------------
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R6",
        "baseline_record_id": "SR_PLANTED_R6_RS",
        "baseline_complete": True,
        "start_record_id": "SR_PLANTED_R6_RS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_PLANTED_R6_RS", "parcel_id": "PARCEL_PLANTED_R6", "survey": "RS",
                "khatian_no": "9006", "record_date": "1982-11-10", "recorded_area": "20",
                "holders": [{"person_id": "P_EXT_SELIM", "area": "20"}],
            },
        ],
        "events": [
            {
                "id": "E_PLANTED_R6_1", "type": "SALE", "seq": 1, "event_date": "1985-07-15",
                "parcel_id": "PARCEL_PLANTED_R6", "from_person": "P_EXT_SELIM",
                "to_person": "P_EXT_MAMTAZ",
                "area": "9", "deed_id": "DEED_PLANTED_R6_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                # Area mismatch: mutation says 7 but the sale is for 9 -> R6 REVIEW REQUIRED
                "id": "E_PLANTED_R6_2", "type": "MUTATION", "seq": 2,
                "event_date": "1985-09-20",
                "parcel_id": "PARCEL_PLANTED_R6", "from_person": None,
                "to_person": "P_EXT_MAMTAZ",
                "area": "7", "deed_id": "DEED_PLANTED_R6_1", "portion_id": None,
                "linked_event_id": "E_PLANTED_R6_1", "source_record_id": None,
            },
        ],
    })

    # -------------------------------------------------------------------------
    # Planted 7: R7 Mutation date precedes deed registration date
    # Mutation date 1994-12-01 < deed registration 1995-06-20 -> R7 Contradiction
    # -------------------------------------------------------------------------
    histories.append({
        "parcel_id": "PARCEL_PLANTED_R7",
        "baseline_record_id": "SR_PLANTED_R7_RS",
        "baseline_complete": True,
        "start_record_id": "SR_PLANTED_R7_RS",
        "end_date": "2025-12-31",
        "survey_records": [
            {
                "id": "SR_PLANTED_R7_RS", "parcel_id": "PARCEL_PLANTED_R7", "survey": "RS",
                "khatian_no": "9007", "record_date": "1982-11-10", "recorded_area": "12",
                "holders": [{"person_id": "P_EXT_ANIS", "area": "12"}],
            },
        ],
        "events": [
            {
                "id": "E_PLANTED_R7_1", "type": "SALE", "seq": 1, "event_date": "1995-06-20",
                "parcel_id": "PARCEL_PLANTED_R7", "from_person": "P_EXT_ANIS",
                "to_person": "P_EXT_BILKIS",
                "area": "8", "deed_id": "DEED_PLANTED_R7_1", "portion_id": None,
                "linked_event_id": None, "source_record_id": None,
            },
            {
                # Mutation date (1994-12-01) precedes deed registration (1995-06-20) -> R7 CONTRADICTION
                "id": "E_PLANTED_R7_2", "type": "MUTATION", "seq": 2,
                "event_date": "1994-12-01",
                "parcel_id": "PARCEL_PLANTED_R7", "from_person": None,
                "to_person": "P_EXT_BILKIS",
                "area": "8", "deed_id": "DEED_PLANTED_R7_1", "portion_id": None,
                "linked_event_id": "E_PLANTED_R7_1", "source_record_id": None,
            },
        ],
    })

    return {
        "persons": persons,
        "deeds": deeds,
        "parcels": parcels,
        "histories": histories,
    }


def build_demo_dataset(seed: int = 42) -> Dataset:
    """Build and parse the complete demo dataset into validated typed models."""
    raw = build_raw_dataset_dict(seed=seed)
    return parse_dataset_dict(raw)


def generate_and_save(output_path: str | Path = "data/demo_family.json", seed: int = 42) -> None:
    """Generate the demo dataset and save to JSON file."""
    dataset = build_demo_dataset(seed=seed)
    save_dataset(dataset, output_path)


if __name__ == "__main__":
    generate_and_save("data/demo_family.json", seed=42)
    print("Successfully generated data/demo_family.json with seed=42.")
