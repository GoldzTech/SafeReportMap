from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.app.core.enums import IncidentCategory, SeverityLevel


class TriageKeywords(BaseModel):
    keywords: list[str] = Field(default_factory=list)


class TriageRunRequest(BaseModel):
    report_id: UUID


class TriageOutput(BaseModel):
    report_id: UUID
    category: IncidentCategory
    severity: SeverityLevel
    priority_score: float = Field(ge=0.0, le=1.0)
    summary: str = Field(min_length=1)
    keywords: list[str] = Field(default_factory=list)
    recurrence_flag: bool = False
    recurrence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    justification: str = Field(min_length=1)
    model_version: str
    pipeline_version: str


class TriageResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    category: IncidentCategory
    severity: SeverityLevel
    priority_score: float
    summary: str
    keywords: dict | list[str]
    confidence: float
    justification: str
    recurrence_score: float | None
    processed_at: datetime
    model_version: str
    pipeline_version: str
    is_current: bool


class TriageStatusResponse(BaseModel):
    report_id: UUID
    triaged: bool
    message: str