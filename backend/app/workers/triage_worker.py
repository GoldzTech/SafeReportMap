from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from backend.app.core.tenant_context import clear_current_tenant, set_current_tenant
from backend.app.db.session import SessionLocal
from backend.app.models.report import Report
from backend.app.services.triage_service import TriageService


def process_triage_job(report_id: UUID) -> None:
    db = SessionLocal()
    try:
        tenant_id = db.scalar(select(Report.tenant_id).where(Report.id == report_id))
        if tenant_id is None:
            raise ValueError("Report not found.")

        set_current_tenant(tenant_id)
        service = TriageService(db)
        service.triage_report(report_id)
    finally:
        clear_current_tenant()
        db.close()