from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.core.enums import JobStatus, ReportStatus
from backend.app.core.tenant_context import require_current_tenant_id
from backend.app.models.job import ProcessingJob
from backend.app.models.report import Report
from backend.app.repositories.report_repository import ReportRepository
from backend.app.schemas.report import ReportCreate
from backend.app.utils.ids import generate_public_reference_code
from backend.app.utils.sanitization import sanitize_text


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReportRepository(db)

    def create_report(self, payload: ReportCreate) -> Report:
        tenant_id = require_current_tenant_id()
        sanitized = sanitize_text(payload.content_raw)
        public_code = self._generate_unique_public_code()

        report = Report(
            tenant_id=tenant_id,
            incident_date=payload.incident_date,
            location_text=payload.location_text.strip(),
            location_zone=payload.location_zone.strip() if payload.location_zone else None,
            institution_area_id=payload.institution_area_id,
            content_raw=payload.content_raw.strip(),
            content_sanitized=sanitized,
            urgency_self_reported=payload.urgency_self_reported,
            status=ReportStatus.RECEIVED,
            recurrence_flag=False,
            cluster_id=None,
            submitted_from_demo=False,
            is_deleted=False,
            public_reference_code=public_code,
        )

        self.repo.create(report)

        job = ProcessingJob(
            tenant_id=tenant_id,
            report_id=report.id,
            job_type="TRIAGE",
            status=JobStatus.PENDING,
            attempt_count=0,
            scheduled_at=datetime.now(timezone.utc),
            started_at=None,
            finished_at=None,
            error_message=None,
            payload={"report_id": str(report.id), "tenant_id": str(tenant_id)},
        )
        self.repo.create_processing_job(job)

        self.db.commit()
        self.db.refresh(report)
        return report

    def get_report_by_public_reference_code(self, code: str) -> Report | None:
        return self.repo.get_by_public_reference_code(code)

    def _generate_unique_public_code(self) -> str:
        for _ in range(10):
            candidate = generate_public_reference_code()
            existing = self.repo.get_by_public_reference_code(candidate)
            if existing is None:
                return candidate
        raise RuntimeError("Could not generate a unique public reference code.")