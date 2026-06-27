from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.tenant import Tenant


class TenantRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, tenant: Tenant) -> Tenant:
        self.db.add(tenant)
        self.db.flush()
        return tenant

    def get_by_id(self, tenant_id: UUID) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        return self.db.scalar(stmt)

    def get_by_slug(self, slug: str) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.slug == slug)
        return self.db.scalar(stmt)

    def list_active(self) -> list[Tenant]:
        stmt = select(Tenant).where(Tenant.is_active.is_(True)).order_by(Tenant.name.asc())
        return self.db.scalars(stmt).all()