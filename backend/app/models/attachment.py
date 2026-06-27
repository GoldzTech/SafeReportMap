import uuid

from sqlalchemy import Boolean, BigInteger, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.base import TenantMixin, TimestampMixin, UUIDMixin


class ReportAttachment(TimestampMixin, UUIDMixin, TenantMixin, Base):
    __tablename__ = "report_attachments"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    tenant = relationship("Tenant", back_populates="attachments")
    report = relationship("Report", back_populates="attachments")