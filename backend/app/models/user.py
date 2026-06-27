from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.enums import UserRole
from backend.app.db.base import Base
from backend.app.db.types import USER_ROLE_ENUM
from backend.app.models.base import TenantMixin, TimestampMixin, UUIDMixin


class User(TimestampMixin, UUIDMixin, TenantMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_id_email"),
    )

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(USER_ROLE_ENUM, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant = relationship("Tenant", back_populates="users")
    notes = relationship("AdminNote", back_populates="admin")
    status_changes = relationship("ReportStatusHistory", back_populates="changed_by_user")
    audit_logs = relationship("AuditLog", back_populates="actor")