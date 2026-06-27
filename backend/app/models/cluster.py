from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.enums import ClusterType, SeverityLevel
from backend.app.db.base import Base
from backend.app.db.types import CLUSTER_TYPE_ENUM, SEVERITY_LEVEL_ENUM
from backend.app.models.base import TenantMixin, TimestampMixin, UUIDMixin


class Cluster(TimestampMixin, UUIDMixin, TenantMixin, Base):
    __tablename__ = "clusters"

    cluster_type: Mapped[ClusterType] = mapped_column(CLUSTER_TYPE_ENUM, nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    severity_level: Mapped[SeverityLevel | None] = mapped_column(SEVERITY_LEVEL_ENUM, nullable=True, index=True)

    recurrence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    zone_reference: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    tenant = relationship("Tenant", back_populates="clusters")
    reports = relationship("Report", back_populates="cluster")