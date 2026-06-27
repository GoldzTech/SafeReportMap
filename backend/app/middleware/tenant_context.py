from __future__ import annotations

from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.config import settings
from backend.app.core.tenant_context import clear_current_tenant, set_current_tenant
from backend.app.db.session import SessionLocal
from backend.app.services.tenant_service import TenantService


class TenantContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        tenant_slug = request.headers.get(settings.TENANT_HEADER_NAME, settings.DEFAULT_TENANT_SLUG)

        db: Session = SessionLocal()
        try:
            service = TenantService(db)
            try:
                tenant = service.resolve_tenant(tenant_slug)
            except LookupError as exc:
                return JSONResponse(status_code=404, content={"detail": str(exc)})

            set_current_tenant(tenant.id, tenant.slug)
            request.state.tenant_id = tenant.id
            request.state.tenant_slug = tenant.slug

            response = await call_next(request)
            return response
        finally:
            clear_current_tenant()
            db.close()