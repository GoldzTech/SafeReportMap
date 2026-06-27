from __future__ import annotations

from backend.app.core.enums import UserRole


def has_role(user, *roles: UserRole) -> bool:
    return user.role in roles


def is_admin(user) -> bool:
    return user.role == UserRole.ADMIN