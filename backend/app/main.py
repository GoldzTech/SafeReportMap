from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.routes.admin import router as admin_router
from backend.app.api.v1.routes.analytics import router as analytics_router
from backend.app.api.v1.routes.auth import router as auth_router
from backend.app.api.v1.routes.internal import router as internal_router
from backend.app.api.v1.routes.map import router as map_router
from backend.app.api.v1.routes.reports import router as reports_router
from backend.app.core.config import settings
from backend.app.db.init_db import bootstrap_application
from backend.app.middleware.tenant_context import TenantContextMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    version="0.1.0",
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(TenantContextMiddleware)


@app.on_event("startup")
def on_startup() -> None:
    bootstrap_application()


@app.get("/health", tags=["system"])
def health_check():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(map_router, prefix=settings.API_V1_STR)
app.include_router(internal_router, prefix=settings.API_V1_STR)