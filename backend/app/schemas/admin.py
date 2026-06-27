from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.app.core.enums import IncidentCategory, ReportStatus, SeverityLevel
from backend.app.schemas.common import PageMeta


class ReportAttachmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    file_name: str
    file_path: str
    mime_type: str
    file_size_bytes: int
    created_at: datetime
    reason: str | None
    changed_at: datetime

    created_at: datetime
    ai_justification: str | None = None
    model_version: str | None = None
    processed_at: datetime | None = None
    recurrence_score: float | None = None
    keywords: list[str] = Field(default_factory=list)

    attachments: list[ReportAttachmentRead] = Field(default_factory=list)
    notes: list[AdminNoteRead] = Field(default_factory=list)
    status_history: list[ReportStatusHistoryRead] = Field(default_factory=list)


class AdminActionResponse(BaseModel):
    report_id: UUID
    message: str


class AdminNoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    admin_id: UUID
    content: str
    is_private: bool
    created_at: datetime
    updated_at: datetime


class ReportStatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    previous_status: ReportStatus | None
    new_status: ReportStatus
    changed_by: UUID | None
    reason: str | None
    changed_at: datetime


class ReportAttachmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    file_name: str
    file_path: str
    mime_type: str
    file_size_bytes: int
    created_at: datetime
    is_deleted: bool
  

class AdminReportListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    public_reference_code: str
    incident_date: date | None
    location_text: str
    location_zone: str | None
    status: ReportStatus
    created_at: datetime

    ai_category: IncidentCategory | None = None
    ai_severity: SeverityLevel | None = None
    ai_priority_score: float | None = None
    ai_summary: str | None = None
    ai_confidence: float | None = None

    recurrence_flag: bool = False
    cluster_id: UUID | None = None


class AdminReportDetail(AdminReportListItem):
    content_sanitized: str
    content_raw: str
    urgency_self_reported: int | None
    submitted_from_demo: bool
    is_deleted: bool
    updated_at: datetime

    ai_justification: str | None = None
    model_version: str | None = None
    processed_at: datetime | None = None
    recurrence_score: float | None = None
    keywords: list[str] = Field(default_factory=list)

    attachments: list[ReportAttachmentRead] = Field(default_factory=list)
    notes: list[AdminNoteRead] = Field(default_factory=list)
    status_history: list[ReportStatusHistoryRead] = Field(default_factory=list)


class DashboardMetrics(BaseModel):
    total_reports: int
    reports_in_review: int
    critical_reports: int
    high_reports: int
    active_clusters: int
    recurrence_rate: float
    most_common_category: IncidentCategory | None = None
    most_common_severity: SeverityLevel | None = None


class AdminReportPage(BaseModel):
    items: list[AdminReportListItem]
    meta: PageMeta


class AdminCaseNoteCreate(BaseModel):
    admin_id: UUID
    content: str = Field(min_length=1, max_length=10000)
    is_private: bool = True


class AdminCaseStatusUpdate(BaseModel):
    changed_by: UUID
    new_status: ReportStatus
    reason: str | None = Field(default=None, max_length=2000)