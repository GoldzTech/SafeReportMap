from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from backend.app.core.enums import IncidentCategory, ReportStatus, SeverityLevel


class ExportFilters(BaseModel):
    format: str = Field(pattern="^(csv|pdf)$")
    date_from: date | None = None
    date_to: date | None = None
    status: ReportStatus | None = None
    severity: SeverityLevel | None = None
    category: IncidentCategory | None = None
    zone: str | None = None
    search: str | None = None


class ExportRow(BaseModel):
    public_reference_code: str
    created_at: str
    incident_date: str | None
    location_zone: str | None
    status: ReportStatus
    category: IncidentCategory | None = None
    severity: SeverityLevel | None = None
    priority_score: float | None = None
    summary: str | None = None
    keywords: str | None = None
    recurrence_flag: bool = False
    cluster_id: str | None = None