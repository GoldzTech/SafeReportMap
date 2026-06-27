from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class TriageInput(BaseModel):
    report_id: UUID
    content_raw: str = Field(min_length=1)
    content_sanitized: str = Field(min_length=1)
    incident_date: date | None = None
    location_text: str = Field(min_length=1)
    location_zone: str | None = None
    urgency_self_reported: int | None = Field(default=None, ge=1, le=5)
    cluster_id: UUID | None = None
    submitted_from_demo: bool = False