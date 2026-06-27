from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.app.core.enums import ReportStatus, SeverityLevel, IncidentCategory


class ReportAttachmentInput(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=1, max_length=100)
    file_size_bytes: int = Field(ge=1)


class ReportAttachmentRead(ReportAttachmentInput):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    file_path: str
    created_at: datetime
    is_deleted: bool


class ReportCreate(BaseModel):
    incident_date: date | None = None
    location_text: str = Field(min_length=1, max_length=255)
    location_zone: str | None = Field(default=None, max_length=120)
    institution_area_id: UUID | None = None
    content_raw: str = Field(min_length=1, max_length=10000)
    urgency_self_reported: int | None = Field(default=None, ge=1, le=5)
    attachments: list[ReportAttachmentInput] = Field(default_factory=list)


class ReportPublicConfirmation(BaseModel):
    public_reference_code: str
    status: ReportStatus
    created_at: datetime
    message: str = "Relato recebido com sucesso."


class ReportStatusUpdate(BaseModel):
    new_status: ReportStatus
    reason: str | None = Field(default=None, max_length=2000)


class ReportBaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    public_reference_code: str
    incident_date: date | None
    location_text: str
    location_zone: str | None
    institution_area_id: UUID | None
    content_sanitized: str
    urgency_self_reported: int | None
    status: ReportStatus
    recurrence_flag: bool
    cluster_id: UUID | None
    submitted_from_demo: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class ReportDetailRead(ReportBaseRead):
    content_raw: str
    attachments: list[ReportAttachmentRead] = Field(default_factory=list)

    ai_category: IncidentCategory | None = None
    ai_severity: SeverityLevel | None = None
    ai_summary: str | None = None
    ai_priority_score: float | None = None
    ai_keywords: dict | list[str] | None = None
    ai_confidence: float | None = None
    ai_justification: str | None = None
    model_version: str | None = None
    processed_at: datetime | None = None
    recurrence_score: float | None = None


class ReportListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    public_reference_code: str
    location_text: str
    location_zone: str | None
    status: ReportStatus
    created_at: datetime

    ai_category: IncidentCategory | None = None
    ai_severity: SeverityLevel | None = None
    ai_priority_score: float | None = None
    ai_summary: str | None = None
    recurrence_flag: bool = False
    cluster_id: UUID | None = None


class ReportFilters(BaseModel):
    status: ReportStatus | None = None
    severity: SeverityLevel | None = None
    category: IncidentCategory | None = None
    date_from: date | None = None
    date_to: date | None = None
    zone: str | None = None
    search: str | None = None
    priority_min: float | None = Field(default=None, ge=0.0, le=1.0)
    priority_max: float | None = Field(default=None, ge=0.0, le=1.0)