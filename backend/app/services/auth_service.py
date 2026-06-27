from __future__ import annotations

import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.enums import UserRole
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.auth import LoginRequest
from backend.app.security.hashing import hash_password, verify_password
from backend.app.security.jwt import create_access_token


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def _ensure_default_tenant(self) -> uuid.UUID:
        tenant_id = self.db.execute(
            text("SELECT id FROM tenants WHERE slug = :slug"),
            {"slug": settings.DEFAULT_TENANT_SLUG},
        ).scalar_one_or_none()

        if tenant_id is not None:
            return tenant_id

        tenant_id = uuid.uuid5(uuid.NAMESPACE_DNS, "safereport-map:default-tenant")
        self.db.execute(
            text(
                """
                INSERT INTO tenants (id, name, slug, status, is_active, settings, created_at, updated_at)
                VALUES (:id, :name, :slug, :status, :is_active, :settings::jsonb, now(), now())
                """
            ),
            {
                "id": str(tenant_id),
                "name": settings.DEFAULT_TENANT_NAME,
                "slug": settings.DEFAULT_TENANT_SLUG,
                "status": "ACTIVE",
                "is_active": True,
                "settings": "{}",
            },
        )
        self.db.commit()
        return tenant_id

    def bootstrap_demo_admin(self) -> User:
        tenant_id = self._ensure_default_tenant()

        existing = self.user_repo.get_by_email(
            settings.DEMO_ADMIN_EMAIL,
            tenant_id=tenant_id,
        )
        if existing is not None:
            return existing

        user = User(
            tenant_id=tenant_id,
            email=settings.DEMO_ADMIN_EMAIL,
            password_hash=hash_password(settings.DEMO_ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
        )
        self.user_repo.create(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self.user_repo.get_by_email(email)
        if user is None:
            raise ValueError("Invalid email or password.")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password.")

        if not user.is_active:
            raise PermissionError("User is inactive.")

        self.user_repo.update_last_login(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, payload: LoginRequest) -> tuple[User, str]:
        user = self.authenticate(payload.email, payload.password)
        token = create_access_token(
            subject=str(user.id),
            email=user.email,
            role=user.role.value,
            tenant_id=str(user.tenant_id),
        )
        return user, token