from __future__ import annotations

from contextvars import ContextVar
from uuid import UUID

_current_tenant_id: ContextVar[UUID | None] = ContextVar("current_tenant_id", default=None)
_current_tenant_slug: ContextVar[str | None] = ContextVar("current_tenant_slug", default=None)


def set_current_tenant(tenant_id: UUID | None, tenant_slug: str | None = None) -> None:
    _current_tenant_id.set(tenant_id)
    _current_tenant_slug.set(tenant_slug)


def clear_current_tenant() -> None:
    _current_tenant_id.set(None)
    _current_tenant_slug.set(None)


def get_current_tenant_id() -> UUID | None:
    return _current_tenant_id.get()


def get_current_tenant_slug() -> str | None:
    return _current_tenant_slug.get()


def require_current_tenant_id() -> UUID:
    tenant_id = get_current_tenant_id()
    if tenant_id is None:
        raise RuntimeError("Tenant context is not set.")
    return tenant_id