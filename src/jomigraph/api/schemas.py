"""
JomiGraph AI — API Request & Response Schemas
============================================
Pydantic models for API serialization and strict validation:
  - Rejects float-typed areas, zero and negative areas with HTTP 422
  - Accepts exact integer, decimal and fraction strings ("10", "2.5", "7/2")
"""

from __future__ import annotations

from datetime import date
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator

from jomigraph.area_input import parse_area


# ---------------------------------------------------------------------------
# Parcel List Schemas (GET /parcels)
# ---------------------------------------------------------------------------

class ParcelListItem(BaseModel):
    id: str
    label: str
    status_summary: str
    status_summary_code: str = "CONSISTENT"
    status_code: str = "CONSISTENT"
    # Staging fields: present for the reviewer role only (see GET /parcels).
    planted: Optional[bool] = None
    category: Optional[str] = None
    is_khas: Optional[bool] = None
    under_acquisition: Optional[bool] = None
    court_case_no: Optional[str] = None
    injunction: Optional[bool] = None
    is_locked: Optional[bool] = None


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
    dummy_id: Optional[str] = None
    is_locked: Optional[bool] = None


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
    share_fraction: Optional[str] = None
    traditional_share: Optional[str] = None


class CoownerQuotaDetail(BaseModel):
    person_id: str
    person_name: str
    recorded_area: str
    quota_limit: str
    share_fraction: str
    traditional_share: str


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
    via_poa_id: Optional[str] = None


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
    coowner_quotas: Optional[list[CoownerQuotaDetail]] = None
    traditional_share_disclaimer: Optional[str] = None
    is_khas: Optional[bool] = None
    under_acquisition: Optional[bool] = None
    flag_date: Optional[str] = None
    court_case_no: Optional[str] = None
    case_status: Optional[str] = None
    injunction: Optional[bool] = None
    is_locked: Optional[bool] = None
    attention_score: Optional[int] = 0
    traffic_light: Optional[str] = "green"
    score_summary: Optional[str] = None
    score_disclaimer: Optional[str] = None


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
    coowner_quotas: Optional[list[CoownerQuotaDetail]] = None
    traditional_share_disclaimer: Optional[str] = None
    is_khas: Optional[bool] = None
    under_acquisition: Optional[bool] = None
    flag_date: Optional[str] = None
    court_case_no: Optional[str] = None
    case_status: Optional[str] = None
    injunction: Optional[bool] = None
    is_locked: Optional[bool] = None
    attention_score: Optional[int] = 0
    traffic_light: Optional[str] = "green"
    score_factors: Optional[list[dict[str, Any]]] = None
    score_disclaimer: Optional[str] = None


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
    holder_name: Optional[str] = None
    dummy_id: Optional[str] = None
    person_id: Optional[str] = None


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
    attention_score: Optional[int] = 0
    traffic_light: Optional[str] = "green"
    score_summary: Optional[str] = None
    score_disclaimer: Optional[str] = None
    certificate_qr_payload: Optional[str] = None


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
    attention_score: Optional[int] = 0
    traffic_light: Optional[str] = "green"
    score_factors: Optional[list[dict[str, Any]]] = None
    score_disclaimer: Optional[str] = None
    certificate_qr_payload: Optional[str] = None


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
    sub_dag: Optional[str] = None
    boundary_north: Optional[str] = None
    boundary_south: Optional[str] = None
    boundary_east: Optional[str] = None
    boundary_west: Optional[str] = None
    boundary: Optional[Any] = None
    portion: Optional[dict[str, Any]] = None
    portion_area: Optional[str] = None
    via_poa_id: Optional[str] = None
    lang: str = "bn"

    @field_validator("area", mode="before")
    @classmethod
    def validate_area(cls, v: Any) -> str:
        """
        Accept an exact positive area as text: "5", "2.5" or "5/2".
        Decimal strings are parsed straight into a Fraction, so no float is
        ever created. JSON numbers with a fractional part, zero, negative
        values and malformed text are rejected with HTTP 422 and a code
        (AREA_*) that the UI turns into a localised message.
        """
        return str(parse_area(v))

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, v: Any) -> Optional[str]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        if not isinstance(v, str):
            raise ValueError("Date must be an ISO format string YYYY-MM-DD.")
        try:
            date.fromisoformat(v)
        except Exception as exc:
            raise ValueError(f"Invalid ISO date '{v}': {exc}")
        return v.strip()

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
    boundary: Optional[Any] = None
    portion: Optional[Any] = None
    via_poa_id: Optional[str] = None


class SimulateResponse(BaseModel):
    """Reviewer view of a simulated transfer (full detail)."""
    proposed_event: ProposedEventDetail
    available_before: str
    available_after: str
    # Plain numbers the UI shows directly. All are exact fraction strings.
    requested_area: str
    seller_available_before: str
    seller_available_after: str
    excess: str = "0"
    r1_calculation: Optional[str] = None
    alerts: list[AlertDetail]
    status_code: Optional[str] = "CONSISTENT"
    overall_status_code: Optional[str] = "CONSISTENT"
    attention_score: Optional[int] = 0
    traffic_light: Optional[str] = "green"
    score_factors: Optional[list[dict[str, Any]]] = None
    score_disclaimer: Optional[str] = None


class CitizenSimulateResponse(BaseModel):
    """
    Citizen view of a simulated transfer. Carries no rule IDs, calculations,
    evidence IDs or internal record IDs. This is a demo role, not access control.
    """
    requested_area: str
    seller_available_before: str
    seller_available_after: str
    excess: str = "0"
    alerts: list[CitizenAlertDetail]
    status_code: Optional[str] = "CONSISTENT"
    overall_status_code: Optional[str] = "CONSISTENT"
    attention_score: Optional[int] = 0
    traffic_light: Optional[str] = "green"
    score_summary: Optional[str] = None
    score_disclaimer: Optional[str] = None


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


class Phase10BenchmarkDetail(BaseModel):
    rule_id: str = "R8"
    planted_detected: bool
    clean_passed: bool
    tricky_clean_passed: bool


class Phase11FeaturesBenchmarkDetail(BaseModel):
    attention_scoring_verified: bool = True
    bangla_voice_verified: bool = True
    next_step_guide_verified: bool = True
    ussd_simulator_verified: bool = True
    vetting_certificate_verified: bool = True


class ExtendedBenchmarkResponse(BaseModel):
    dataset_name: str
    total_parcels: int
    clean_parcel_count: int
    clean_false_alarm_count: int
    planted_parcel_count: int
    planted_case_count: int
    planted_detected_count: int
    coverage_table: list[CoverageRowItem]
    phase10_heir_declaration: Optional[Phase10BenchmarkDetail] = None
    phase11_features: Optional[Phase11FeaturesBenchmarkDetail] = None
    simulation_integrity: Optional[SimulationIntegrityResult] = None
    disclaimer: str


class BenchmarkResponse(BaseModel):
    clean_false_alarm_count: int
    coverage_table: list[CoverageRowItem]
    simulation_integrity: SimulationIntegrityResult
    total_parcels: Optional[int] = None
    planted_case_count: Optional[int] = None
    planted_detected_count: Optional[int] = None
    extended: Optional[ExtendedBenchmarkResponse] = None



# ---------------------------------------------------------------------------
# Deed Verification Schemas (POST /verify-deed)
# ---------------------------------------------------------------------------

class VerifyDeedRequest(BaseModel):
    deed_no: str = Field(min_length=1, max_length=50)
    registration_date: str = Field(min_length=1, max_length=20)
    parcel_id: str = Field(min_length=1, max_length=60)
    seller: str = Field(min_length=1, max_length=100)
    buyer: str = Field(min_length=1, max_length=100)
    area: str = Field(min_length=1, max_length=40)
    claimed_hash: Optional[str] = Field(default=None, max_length=128)
    lang: str = Field(default="bn", pattern="^(bn|en)$")
    role: str = Field(default="reviewer", pattern="^(citizen|reviewer)$")

    @field_validator("registration_date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            date.fromisoformat(v.strip())
        except Exception as exc:
            raise ValueError(f"Invalid ISO date '{v}': {exc}")
        return v.strip()

    @field_validator("area")
    @classmethod
    def validate_area_field(cls, v: str) -> str:
        try:
            fr = parse_area(v)
            if fr <= 0:
                raise ValueError("Area must be strictly greater than zero.")
        except Exception as exc:
            raise ValueError(f"Invalid area '{v}': {exc}")
        return v.strip()


class VerifyDeedResponse(BaseModel):
    status: str
    status_code: str
    rule_id: Optional[str] = None
    computed_hash: str
    recorded_hash: Optional[str] = None
    claimed_hash: Optional[str] = None
    matches_registry: bool
    message: str
    recommended_next_step: str
    qr_payload: str
    disclaimer: str


# ---------------------------------------------------------------------------
# USSD Feature-Phone Simulator Schemas (POST /ussd)
# ---------------------------------------------------------------------------

class USSDRequest(BaseModel):
    text: str = ""
    phone_number: Optional[str] = "01700000000"
    session_id: Optional[str] = "USSD_SESSION_01"


class USSDResponse(BaseModel):
    message: str
    action: str
    character_count: int
    screen: str
    lang: str

