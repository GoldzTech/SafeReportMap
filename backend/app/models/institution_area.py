from sqlalchemy import Boolean, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.base import TenantMixin, TimestampMixin, UUIDMixin


class InstitutionArea(TimestampMixin, UUIDMixin, TenantMixin, Base):
    __tablename__ = "institution_areas"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_institution_areas_tenant_id_code"),
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    area_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    tenant = relationship("Tenant", back_populates="institution_areas")
    reports = relationship("Report", back_populates="institution_area")