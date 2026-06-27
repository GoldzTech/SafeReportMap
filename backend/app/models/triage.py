import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.enums import IncidentCategory, SeverityLevel
from backend.app.db.base import Base
from backend.app.db.types import INCIDENT_CATEGORY_ENUM, SEVERITY_LEVEL_ENUM
from backend.app.models.base import TenantMixin, TimestampMixin, UUIDMixin


class AITriageResult(TimestampMixin, UUIDMixin, TenantMixin, Base):
    __tablename__ = "ai_triage_results"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category: Mapped[IncidentCategory] = mapped_column(INCIDENT_CATEGORY_ENUM, nullable=False, index=True)
    severity: Mapped[SeverityLevel] = mapped_column(SEVERITY_LEVEL_ENUM, nullable=False, index=True)

    priority_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    keywords: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    justification: Mapped[str] = mapped_column(Text, nullable=False)

    recurrence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    pipeline_version: Mapped[str] = mapped_column(String(80), nullable=False)

    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    tenant = relationship("Tenant", back_populates="triage_results")
    report = relationship("Report", back_populates="triage_results")