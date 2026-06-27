from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.enums import ReportStatus
from backend.app.core.tenant_context import require_current_tenant_id
from backend.app.models.job import ProcessingJob
from backend.app.models.report import Report


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, report: Report) -> Report:
        self.db.add(report)
        self.db.flush()
        return report

    def get_by_id(self, report_id: UUID) -> Report | None:
        tenant_id = require_current_tenant_id()
        stmt = select(Report).where(
            Report.id == report_id,
            Report.tenant_id == tenant_id,
            Report.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def get_by_public_reference_code(self, code: str) -> Report | None:
        tenant_id = require_current_tenant_id()
        stmt = select(Report).where(
            Report.public_reference_code == code,
            Report.tenant_id == tenant_id,
            Report.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def list_public(self, limit: int = 20, offset: int = 0) -> Sequence[Report]:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(Report)
            .where(
                Report.tenant_id == tenant_id,
                Report.is_deleted.is_(False),
            )
            .order_by(Report.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.db.scalars(stmt).all()

    def update_status(self, report: Report, new_status: ReportStatus) -> Report:
        report.status = new_status
        self.db.flush()
        return report

    def create_processing_job(self, job: ProcessingJob) -> ProcessingJob:
        self.db.add(job)
        self.db.flush()
        return job