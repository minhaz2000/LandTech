"""Generates fictional demo parcels for the seven divisions outside Dhaka.
Writes data/demo_regions.json (same schema as demo_family.json) and
data/demo_places.json (parcel id -> division/district/upazila).
All people, deeds and parcels are invented. Run: python data/regions_generator.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
geo = json.loads((HERE / "bd_geo.json").read_text(encoding="utf-8"))
NAMES = [("Anwar Hossain", "Salma Begum"), ("Kamal Uddin", "Rina Akter"), ("Jahid Mia", "Nasima Khatun"),
         ("Habib Sarker", "Mahmuda Islam"), ("Shafiq Talukder", "Rokeya Sultana"), ("Mizanur Rahman", "Shirin Akhter"),
         ("Delwar Howlader", "Parvin Nahar")]
TAG = {"Barishal": "BAR", "Chattogram": "CTG", "Khulna": "KHL", "Mymensingh": "MYM", "Rajshahi": "RAJ", "Rangpur": "RNG", "Sylhet": "SYL"}
persons, parcels, deeds, histories, places = [], [], [], [], {}

def add(div, district, upazila, n, kind, a, b, dag):
    pid, tag = f"PARCEL_REG_{TAG[div]}_{n:02d}", f"{TAG[div]}{n}"
    pa, pb = f"P_{tag}_A", f"P_{tag}_B"
    persons.extend([{"id": pa, "name": a}, {"id": pb, "name": b}])
    parcels.append({"id": pid, "dag_no": str(dag), "mouza": f"Demo Mouza {tag}", "parent_id": None})
    places[pid] = {"division": div, "district": district, "upazila": upazila}
    sr = f"SR_{tag}"
    area_held, sold, baseline_ok = {"ok": ("20", "20", True), "over": ("10", "15", True), "gap": ("12", "5", False)}[kind]
    deed = f"DEED_{tag}"
    deeds.append({"id": deed, "deed_no": f"D-2010-{dag}", "registration_date": "2010-06-01"})
    seller = pa if kind != "gap" else pb  # gap: seller is not a recorded holder and baseline is incomplete
    histories.append({"parcel_id": pid, "baseline_record_id": sr, "baseline_complete": baseline_ok, "start_record_id": sr, "end_date": "2025-12-31",
        "survey_records": [{"id": sr, "parcel_id": pid, "survey": "BS", "khatian_no": f"{dag}1", "record_date": "2000-01-10",
                            "recorded_area": area_held, "holders": [{"person_id": pa, "area": area_held}]}],
        "events": [{"id": f"E_{tag}_1", "type": "SALE", "seq": 1, "event_date": "2010-06-01", "parcel_id": pid, "from_person": seller,
                    "to_person": pb if seller == pa else pa, "area": sold, "deed_id": deed, "portion_id": None, "linked_event_id": None, "source_record_id": None}]})

i = 0
for dv in geo["divisions"]:
    if dv["en"] == "Dhaka":
        continue
    d0 = dv["districts"][0]
    ups = d0["upazilas"]
    a1, a2 = NAMES[i % 7]; i += 1
    add(dv["en"], d0["en"], ups[0]["en"], 1, "ok", a1, a2, 501 + i * 10)
    add(dv["en"], d0["en"], ups[min(1, len(ups) - 1)]["en"], 2, "gap", a2, a1, 502 + i * 10)
    add(dv["en"], d0["en"], ups[0]["en"], 3, "over", a1, a2, 503 + i * 10)
(HERE / "demo_regions.json").write_text(json.dumps({"persons": persons, "parcels": parcels, "deeds": deeds, "histories": histories}, ensure_ascii=False, indent=1), encoding="utf-8")
(HERE / "demo_places.json").write_text(json.dumps(places, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(parcels), "fictional regional parcels")
