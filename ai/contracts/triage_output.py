from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.core.enums import IncidentCategory, SeverityLevel


class TriageOutput(BaseModel):
    report_id: UUID
    category: IncidentCategory
    severity: SeverityLevel
    priority_score: float = Field(ge=0.0, le=1.0)
    summary: str
    keywords: list[str]
    recurrence_flag: bool
    recurrence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    justification: str
    model_version: str
    pipeline_version: str
    processed_at: datetime