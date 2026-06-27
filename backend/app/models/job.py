import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.enums import JobStatus
from backend.app.db.base import Base
from backend.app.db.types import JOB_STATUS_ENUM
from backend.app.models.base import TenantMixin, TimestampMixin, UUIDMixin


class ProcessingJob(TimestampMixin, UUIDMixin, TenantMixin, Base):
    __tablename__ = "processing_jobs"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[JobStatus] = mapped_column(JOB_STATUS_ENUM, nullable=False, index=True)

    attempt_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)

    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    tenant = relationship("Tenant", back_populates="jobs")
    report = relationship("Report", back_populates="jobs")