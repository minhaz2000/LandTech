"""
JomiGraph AI — Cytoscape Graph Builder
======================================
Constructs graph nodes and edges for Cytoscape.js rendering of a parcel's
complete chain-of-title, survey records, and transactions.
"""

from __future__ import annotations

from typing import Any
from jomigraph.loader import Dataset
from jomigraph.models import EventType, ParcelHistory


def build_parcel_graph(history: ParcelHistory, dataset: Dataset, lang: str = "bn") -> dict[str, list[dict[str, Any]]]:
    """
    Build Cytoscape.js compatible graph data:
      {
        "nodes": [{"data": {"id": ..., "label": ..., "type": ...}}, ...],
        "edges": [{"data": {"id": ..., "source": ..., "target": ..., "label": ..., "type": ...}}, ...]
      }
    """
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen_nodes: set[str] = set()

    parcel = dataset.get_parcel(history.parcel_id)
    parcel_node_id = f"parcel_{history.parcel_id}"
    parcel_label = f"{parcel.mouza} Dag {parcel.dag_no}" if parcel else history.parcel_id

    # 1. Parcel node
    nodes.append({
        "data": {
            "id": parcel_node_id,
            "label": parcel_label,
            "type": "parcel",
        }
    })
    seen_nodes.add(parcel_node_id)

    # Helper to add person node if not seen
    def add_person_node(pid: str) -> None:
        if pid not in seen_nodes:
            person = dataset.get_person(pid)
            label = person.name if person else pid
            nodes.append({
                "data": {
                    "id": pid,
                    "label": label,
                    "type": "person",
                }
            })
            seen_nodes.add(pid)

    # 2. Survey records & holders
    for sr in history.survey_records:
        sr_node_id = sr.id
        if sr_node_id not in seen_nodes:
            sr_label = f"{sr.survey} ({sr.record_date.year}) — {str(sr.recorded_area)} dec"
            nodes.append({
                "data": {
                    "id": sr_node_id,
                    "label": sr_label,
                    "type": "survey_record",
                    "survey": sr.survey,
                    "record_date": sr.record_date.isoformat(),
                    "recorded_area": str(sr.recorded_area),
                }
            })
            seen_nodes.add(sr_node_id)

        # Connect survey record to parcel
        edges.append({
            "data": {
                "id": f"edge_survey_parcel_{sr.id}",
                "source": parcel_node_id,
                "target": sr_node_id,
                "label": sr.survey,
                "type": "SURVEY_RECORD",
            }
        })

        # Connect survey record to each holder
        for pid, area in sr.holders:
            add_person_node(pid)
            edges.append({
                "data": {
                    "id": f"edge_holder_{sr.id}_{pid}",
                    "source": sr_node_id,
                    "target": pid,
                    "label": f"{str(area)} dec",
                    "type": "SURVEY_ALLOCATION",
                }
            })

    # 3. Events timeline
    for e in history.events:
        area_str = f"{str(e.area)} dec" if e.area is not None else ""
        date_str = e.event_date.isoformat() if e.event_date else ""

        if e.type in (EventType.SALE, EventType.GIFT):
            if e.from_person and e.to_person:
                add_person_node(e.from_person)
                add_person_node(e.to_person)
                label = f"{e.type.value}: {area_str}" if area_str else e.type.value
                edges.append({
                    "data": {
                        "id": e.id,
                        "source": e.from_person,
                        "target": e.to_person,
                        "label": label,
                        "type": e.type.value,
                        "date": date_str,
                    }
                })

        elif e.type == EventType.SUBDIVIDE:
            if e.from_person:
                add_person_node(e.from_person)
                edges.append({
                    "data": {
                        "id": e.id,
                        "source": e.from_person,
                        "target": parcel_node_id,
                        "label": f"SUBDIVIDE: {area_str}",
                        "type": "SUBDIVIDE",
                        "date": date_str,
                    }
                })

        elif e.type == EventType.MUTATION:
            if e.to_person:
                add_person_node(e.to_person)
                edges.append({
                    "data": {
                        "id": e.id,
                        "source": parcel_node_id,
                        "target": e.to_person,
                        "label": f"MUTATION: {area_str}",
                        "type": "MUTATION",
                        "date": date_str,
                    }
                })

        elif e.type == EventType.CANCEL:
            if e.linked_event_id:
                edges.append({
                    "data": {
                        "id": e.id,
                        "source": parcel_node_id,
                        "target": parcel_node_id,
                        "label": f"CANCEL {e.linked_event_id}",
                        "type": "CANCEL",
                        "date": date_str,
                    }
                })

    return {"nodes": nodes, "edges": edges}
