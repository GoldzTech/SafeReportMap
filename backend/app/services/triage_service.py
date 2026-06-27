from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from ai.contracts.triage_input import TriageInput
from ai.orchestrator.triage_orchestrator import TriageOrchestrator
from backend.app.core.enums import IncidentCategory, ReportStatus, SeverityLevel
from backend.app.models.triage import AITriageResult
from backend.app.repositories.triage_repository import TriageRepository


class TriageService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TriageRepository(db)
        self.orchestrator = TriageOrchestrator()

    def triage_report(self, report_id: UUID) -> AITriageResult:
        report = self.repo.get_report_by_id(report_id)
        if report is None:
            raise ValueError("Report not found.")

        triage_input = TriageInput(
            report_id=report.id,
            content_raw=report.content_raw,
            content_sanitized=report.content_sanitized,
            incident_date=report.incident_date,
            location_text=report.location_text,
            location_zone=report.location_zone,
            urgency_self_reported=report.urgency_self_reported,
            cluster_id=report.cluster_id,
            submitted_from_demo=report.submitted_from_demo,
        )

        triage_output = self.orchestrator.triage(triage_input)

        self.repo.set_all_triages_not_current(report_id)

        triage = AITriageResult(
            tenant_id=report.tenant_id,
            report_id=report.id,
            category=triage_output.category,
            severity=triage_output.severity,
            priority_score=triage_output.priority_score,
            summary=triage_output.summary,
            keywords={"keywords": triage_output.keywords},
            confidence=triage_output.confidence,
            justification=triage_output.justification,
            recurrence_score=triage_output.recurrence_score,
            processed_at=triage_output.processed_at or datetime.now(timezone.utc),
            model_version=triage_output.model_version,
            pipeline_version=triage_output.pipeline_version,
            is_current=True,
        )

        self.repo.create_triage_result(triage)

        report.recurrence_flag = triage_output.recurrence_flag

        if triage_output.severity in {SeverityLevel.HIGH, SeverityLevel.CRITICAL}:
            report.status = ReportStatus.IN_REVIEW
        elif report.status == ReportStatus.RECEIVED:
            report.status = ReportStatus.IN_REVIEW

        self.db.commit()
        self.db.refresh(triage)
        return triage

    def get_current_triage(self, report_id: UUID) -> AITriageResult | None:
        return self.repo.get_current_triage(report_id)