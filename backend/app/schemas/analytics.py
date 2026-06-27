from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.core.enums import IncidentCategory, SeverityLevel


class TimelinePoint(BaseModel):
    day: date
    count: int


class CategoryStat(BaseModel):
    category: IncidentCategory
    count: int


class SeverityStat(BaseModel):
    severity: SeverityLevel
    count: int


class LocationStat(BaseModel):
    location_zone: str | None
    count: int


class HeatmapPoint(BaseModel):
    latitude: float
    longitude: float
    intensity: float = Field(ge=0.0)


class ClusterStat(BaseModel):
    cluster_id: UUID
    label: str
    cluster_type: str
    recurrence_count: int
    severity_level: SeverityLevel | None = None


class AnalyticsOverview(BaseModel):
    total_reports: int
    reports_in_review: int
    critical_reports: int
    high_reports: int
    active_clusters: int
    recurrence_rate: float = Field(ge=0.0, le=1.0)
    most_common_category: IncidentCategory | None = None
    most_common_severity: SeverityLevel | None = None


class AnalyticsResponse(BaseModel):
    overview: AnalyticsOverview
    timeline: list[TimelinePoint]
    categories: list[CategoryStat]
    severities: list[SeverityStat]
    top_locations: list[LocationStat]
    clusters: list[ClusterStat]