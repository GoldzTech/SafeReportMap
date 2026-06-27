from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.tenant_context import require_current_tenant_id
from backend.app.models.report import Report
from backend.app.models.triage import AITriageResult


class TriageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_report_by_id(self, report_id: UUID) -> Report | None:
        tenant_id = require_current_tenant_id()
        stmt = select(Report).where(
            Report.id == report_id,
            Report.tenant_id == tenant_id,
            Report.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def set_all_triages_not_current(self, report_id: UUID) -> None:
        tenant_id = require_current_tenant_id()
        stmt = select(AITriageResult).where(
            AITriageResult.report_id == report_id,
            AITriageResult.tenant_id == tenant_id,
            AITriageResult.is_current.is_(True),
        )
        current_triages = self.db.scalars(stmt).all()
        for triage in current_triages:
            triage.is_current = False

    def create_triage_result(self, triage: AITriageResult) -> AITriageResult:
        self.db.add(triage)
        self.db.flush()
        return triage

    def get_current_triage(self, report_id: UUID) -> AITriageResult | None:
        tenant_id = require_current_tenant_id()
        stmt = select(AITriageResult).where(
            AITriageResult.report_id == report_id,
            AITriageResult.tenant_id == tenant_id,
            AITriageResult.is_current.is_(True),
        )
        return self.db.scalar(stmt)