from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.tenant_context import require_current_tenant_id
from backend.app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        tenant_id = require_current_tenant_id()
        stmt = select(User).where(
            User.id == user_id,
            User.tenant_id == tenant_id,
        )
        return self.db.scalar(stmt)

    def get_by_email(self, email: str, tenant_id: UUID | None = None) -> User | None:
        effective_tenant_id = tenant_id or require_current_tenant_id()
        stmt = select(User).where(
            User.email == email,
            User.tenant_id == effective_tenant_id,
        )
        return self.db.scalar(stmt)

    def list_active(self) -> Sequence[User]:
        tenant_id = require_current_tenant_id()
        stmt = select(User).where(
            User.tenant_id == tenant_id,
            User.is_active.is_(True),
        )
        return self.db.scalars(stmt).all()

    def update_last_login(self, user: User) -> User:
        user.last_login = datetime.now(timezone.utc)
        self.db.flush()
        return user