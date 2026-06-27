import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.enums import ReportStatus
from backend.app.db.base import Base
from backend.app.db.types import REPORT_STATUS_ENUM
from backend.app.models.base import TenantMixin, TimestampMixin, UUIDMixin


class ReportStatusHistory(TimestampMixin, UUIDMixin, TenantMixin, Base):
    __tablename__ = "report_status_history"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    previous_status: Mapped[ReportStatus | None] = mapped_column(REPORT_STATUS_ENUM, nullable=True)
    new_status: Mapped[ReportStatus] = mapped_column(REPORT_STATUS_ENUM, nullable=False, index=True)

    changed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    tenant = relationship("Tenant", back_populates="status_history")
    report = relationship("Report", back_populates="status_history")
    changed_by_user = relationship("User", back_populates="status_changes")