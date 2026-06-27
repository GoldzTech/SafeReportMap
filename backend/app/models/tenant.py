from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.base import TimestampMixin, UUIDMixin


class Tenant(TimestampMixin, UUIDMixin, Base):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(160), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="tenant", cascade="all, delete-orphan")
    clusters = relationship("Cluster", back_populates="tenant", cascade="all, delete-orphan")
    institution_areas = relationship("InstitutionArea", back_populates="tenant", cascade="all, delete-orphan")
    triage_results = relationship("AITriageResult", back_populates="tenant", cascade="all, delete-orphan")
    admin_notes = relationship("AdminNote", back_populates="tenant", cascade="all, delete-orphan")
    status_history = relationship("ReportStatusHistory", back_populates="tenant", cascade="all, delete-orphan")
    attachments = relationship("ReportAttachment", back_populates="tenant", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="tenant", cascade="all, delete-orphan")
    jobs = relationship("ProcessingJob", back_populates="tenant", cascade="all, delete-orphan")