import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.enums import ReportStatus
from backend.app.db.base import Base
from backend.app.db.types import REPORT_STATUS_ENUM
from backend.app.models.base import TenantMixin, TimestampMixin, UUIDMixin


class Report(TimestampMixin, UUIDMixin, TenantMixin, Base):
    __tablename__ = "reports"

    incident_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    location_text: Mapped[str] = mapped_column(String(255), nullable=False)
    location_zone: Mapped[str | None] = mapped_column(String(120), nullable=True)

    institution_area_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institution_areas.id", ondelete="SET NULL"),
        nullable=True,
    )

    content_raw: Mapped[str] = mapped_column(Text, nullable=False)
    content_sanitized: Mapped[str] = mapped_column(Text, nullable=False)

    urgency_self_reported: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status: Mapped[ReportStatus] = mapped_column(
        REPORT_STATUS_ENUM,
        nullable=False,
        default=ReportStatus.RECEIVED,
        index=True,
    )

    recurrence_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    cluster_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clusters.id", ondelete="SET NULL"),
        nullable=True,
    )

    submitted_from_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    public_reference_code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)

    tenant = relationship("Tenant", back_populates="reports")
    institution_area = relationship("InstitutionArea", back_populates="reports")
    cluster = relationship("Cluster", back_populates="reports")
    attachments = relationship("ReportAttachment", back_populates="report", cascade="all, delete-orphan")
    triage_results = relationship("AITriageResult", back_populates="report", cascade="all, delete-orphan")
    notes = relationship("AdminNote", back_populates="report", cascade="all, delete-orphan")
    status_history = relationship("ReportStatusHistory", back_populates="report", cascade="all, delete-orphan")
    jobs = relationship("ProcessingJob", back_populates="report", cascade="all, delete-orphan")