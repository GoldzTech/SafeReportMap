from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.tenant import Tenant
from backend.app.repositories.tenant_repository import TenantRepository


class TenantService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TenantRepository(db)

    def bootstrap_default_tenant(self) -> Tenant:
        existing = self.repo.get_by_slug(settings.DEFAULT_TENANT_SLUG)
        if existing is not None:
            return existing

        tenant = Tenant(
            name=settings.DEFAULT_TENANT_NAME,
            slug=settings.DEFAULT_TENANT_SLUG,
            status="ACTIVE",
            is_active=True,
            settings={},
        )

        self.repo.create(tenant)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            tenant = self.repo.get_by_slug(settings.DEFAULT_TENANT_SLUG)
            if tenant is not None:
                return tenant
            raise

        self.db.refresh(tenant)
        return tenant

    def resolve_tenant(self, slug: str | None) -> Tenant:
        normalized_slug = (slug or settings.DEFAULT_TENANT_SLUG).strip().lower()

        tenant = self.repo.get_by_slug(normalized_slug)
        if tenant is not None:
            return tenant

        if normalized_slug == settings.DEFAULT_TENANT_SLUG:
            return self.bootstrap_default_tenant()

        raise LookupError(f"Tenant '{normalized_slug}' not found.")