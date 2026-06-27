from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.core.enums import SeverityLevel


class MapPoint(BaseModel):
    report_id: UUID
    location_zone: str | None
    cluster_id: UUID | None
    severity: SeverityLevel | None
    intensity: float = Field(ge=0.0)


class HeatmapResponse(BaseModel):
    points: list[MapPoint]


class ClusterMapItem(BaseModel):
    cluster_id: UUID
    label: str
    cluster_type: str
    recurrence_count: int
    severity_level: SeverityLevel | None = None