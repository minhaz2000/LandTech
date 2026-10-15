"""
JomiGraph AI — API Request & Response Schemas
============================================
Pydantic models for API serialization and strict validation:
  - Rejects float areas with HTTP 422
  - Accepts exact rational fraction strings ("10", "7/2")
"""

from __future__ import annotations

from datetime import date
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator

from jomigraph.models import load_fraction


# ---------------------------------------------------------------------------
# Parcel List Schemas (GET /parcels)
# ---------------------------------------------------------------------------

class ParcelListItem(BaseModel):
    id: str
    label: str
    status_summary: str
    status_summary_code: str = "CONSISTENT"
    status_code: str = "CONSISTENT"
    planted: bool
    category: str


# ---------------------------------------------------------------------------
# Cytoscape Graph Schemas
# ---------------------------------------------------------------------------

class GraphNodeData(BaseModel):
    id: str
    label: str
    type: str
    survey: Optional[str] = None
    record_date: Optional[str] = None
    recorded_area: Optional[str] = None


class GraphNode(BaseModel):
    data: GraphNodeData


class GraphEdgeData(BaseModel):
    id: str
    source: str
    target: str
    label: str
    type: str
    date: Optional[str] = None


class GraphEdge(BaseModel):
    data: GraphEdgeData


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


# ---------------------------------------------------------------------------
# Parcel Detail Schemas (GET /parcel/{id})
# ---------------------------------------------------------------------------

class HolderDetail(BaseModel):
    person_id: str
    person_name: str
    area: str


class SurveyRecordDetail(BaseModel):
    id: str
    parcel_id: str
    survey: str
    khatian_no: str
    record_date: str
    recorded_area: str
    holders: list[HolderDetail]


class EventDetail(BaseModel):
    id: str
    type: str
    seq: int
    event_date: Optional[str]
    parcel_id: str
    from_person: Optional[str]
    from_person_name: Optional[str]
    to_person: Optional[str]
    to_person_name: Optional[str]
    area: Optional[str]
    deed_id: Optional[str]
    portion_id: Optional[str]
    linked_event_id: Optional[str]
    source_record_id: Optional[str]


class CitizenAlertDetail(BaseModel):
    status: str
    status_code: str = "CONSISTENT"
    message: str
    recommended_next_step: str


class ReviewerAlertDetail(BaseModel):
    rule_id: str
    status: str
    status_code: str = "CONSISTENT"
    message: str
    recommended_next_step: str
    evidence_ids: list[str]
    calculation: str
    minimal_evidence_sets: list[list[str]] = Field(default_factory=list)
    not_minimized: bool = False
    impact_event_ids: list[str] = Field(default_factory=list)


# Alias AlertDetail to ReviewerAlertDetail for backwards compatibility
AlertDetail = ReviewerAlertDetail


class CitizenParcelDetailResponse(BaseModel):
    id: str
    dag_no: str
    mouza: str
    parent_id: Optional[str]
    overall_status: str
    overall_status_code: str = "CONSISTENT"
    survey_records: list[SurveyRecordDetail]
    events: list[EventDetail]
    graph: GraphResponse
    alerts: list[CitizenAlertDetail]


class ParcelDetailResponse(BaseModel):
    id: str
    dag_no: str
    mouza: str
    parent_id: Optional[str]
    overall_status: str
    overall_status_code: str = "CONSISTENT"
    survey_records: list[SurveyRecordDetail]
    events: list[EventDetail]
    graph: GraphResponse
    alerts: list[ReviewerAlertDetail]


ReviewerParcelDetailResponse = ParcelDetailResponse


# ---------------------------------------------------------------------------
# Search Schemas (GET /search)
# ---------------------------------------------------------------------------

class SearchResultItem(BaseModel):
    id: str
    parcel_id: str
    dag_no: str
    mouza: str
    label: str
    matched_on: str


# ---------------------------------------------------------------------------
# Report Schemas (GET /report/{parcel_id})
# ---------------------------------------------------------------------------

class ReportParcelItem(BaseModel):
    id: str
    dag_no: str
    mouza: str
    parent_id: Optional[str]
    label: str


class ReportRecordsDetail(BaseModel):
    survey_records: list[SurveyRecordDetail]
    events: list[EventDetail]


class CitizenReportResponse(BaseModel):
    parcel_id: str
    parcel: ReportParcelItem
    role: str
    lang: str
    overall_status: str
    overall_status_code: str = "CONSISTENT"
    records: ReportRecordsDetail
    alerts: list[CitizenAlertDetail]
    recommended_next_steps: list[str]
    disclaimer: str
    dataset_hash: str


class ReviewerReportResponse(BaseModel):
    parcel_id: str
    parcel: ReportParcelItem
    role: str
    lang: str
    overall_status: str
    overall_status_code: str = "CONSISTENT"
    records: ReportRecordsDetail
    alerts: list[ReviewerAlertDetail]
    recommended_next_steps: list[str]
    disclaimer: str
    dataset_hash: str


ReportResponse = ReviewerReportResponse


# ---------------------------------------------------------------------------
# Simulation Schemas (POST /simulate)
# ---------------------------------------------------------------------------

class SimulateRequest(BaseModel):
    parcel_id: str
    from_person: str
    to_person: Optional[str] = "P_BUYER_SIM"
    area: str
    portion_id: Optional[str] = None
    deed_id: Optional[str] = None
    date: Optional[str] = None
    lang: str = "bn"

    @field_validator("area", mode="before")
    @classmethod
    def validate_area(cls, v: Any) -> str:
        """
        Strictly reject float areas with HTTP 422.
        Must be a string representing an integer or rational fraction ('10', '7/2').
        """
        if isinstance(v, float):
            raise ValueError(
                "Float areas are strictly forbidden in JomiGraph; "
                "provide an exact integer or fraction string (e.g. '5' or '7/2')."
            )
        if not isinstance(v, (str, int)):
            raise ValueError(f"Area must be a string or integer, got {type(v).__name__}.")

        s = str(v).strip()
        if "." in s:
            raise ValueError(
                f"Float decimal area '{s}' is strictly forbidden; "
                "use exact rational fraction strings e.g. '7/2'."
            )
        try:
            load_fraction(s)
        except Exception as exc:
            raise ValueError(f"Invalid area '{s}': {exc}")
        return s

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError("Date must be an ISO format string YYYY-MM-DD.")
        try:
            date.fromisoformat(v)
        except Exception as exc:
            raise ValueError(f"Invalid ISO date '{v}': {exc}")
        return v

    @field_validator("lang")
    @classmethod
    def validate_lang(cls, v: str) -> str:
        if v not in ("bn", "en"):
            raise ValueError("Language parameter must be either 'bn' or 'en'.")
        return v


class ProposedEventDetail(BaseModel):
    id: str
    type: str
    seq: int
    event_date: Optional[str]
    parcel_id: str
    from_person: Optional[str]
    to_person: Optional[str]
    area: str
    deed_id: Optional[str] = None
    portion_id: Optional[str] = None


class SimulateResponse(BaseModel):
    proposed_event: ProposedEventDetail
    available_before: str
    available_after: str
    r1_calculation: Optional[str] = None
    alerts: list[AlertDetail]
    status_code: Optional[str] = "CONSISTENT"
    overall_status_code: Optional[str] = "CONSISTENT"


# ---------------------------------------------------------------------------
# Benchmark Schemas (GET /benchmark)
# ---------------------------------------------------------------------------

class CoverageRowItem(BaseModel):
    rule_id: str
    has_planted_case: bool
    detected: bool
    status_detected: Optional[str]
    status_code: Optional[str] = None


class SimulationIntegrityResult(BaseModel):
    dataset_hash_before: str
    dataset_hash_after: str
    unchanged: bool


class BenchmarkResponse(BaseModel):
    clean_false_alarm_count: int
    coverage_table: list[CoverageRowItem]
    simulation_integrity: SimulationIntegrityResult
    total_parcels: Optional[int] = None
    planted_parcel_count: Optional[int] = None
    planted_detected_count: Optional[int] = None
