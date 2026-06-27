from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.core.enums import IncidentCategory, ReportStatus, SeverityLevel
from backend.app.repositories.admin_repository import AdminRepository
from backend.app.schemas.admin import (
    AdminCaseNoteCreate,
    AdminCaseStatusUpdate,
    AdminNoteRead,
    AdminReportDetail,
    AdminReportListItem,
    AdminReportPage,
    DashboardMetrics,
    ReportAttachmentRead,
    ReportStatusHistoryRead,
)
from backend.app.schemas.common import PageMeta


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AdminRepository(db)

    def list_reports(
        self,
        *,
        page: int,
        page_size: int,
        status: ReportStatus | None = None,
        severity: SeverityLevel | None = None,
        category: IncidentCategory | None = None,
        zone: str | None = None,
        search: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> AdminReportPage:
        reports, total = self.repo.list_reports(
            page=page,
            page_size=page_size,
            status=status,
            severity=severity,
            category=category,
            zone=zone,
            search=search,
            date_from=date_from,
            date_to=date_to,
        )

        items: list[AdminReportListItem] = []

        for report in reports:
            triage = self.repo.get_current_triage(report.id)
            items.append(
                AdminReportListItem(
                    id=report.id,
                    public_reference_code=report.public_reference_code,
                    incident_date=report.incident_date,
                    location_text=report.location_text,
                    location_zone=report.location_zone,
                    status=report.status,
                    created_at=report.created_at,
                    ai_category=triage.category if triage else None,
                    ai_severity=triage.severity if triage else None,
                    ai_priority_score=triage.priority_score if triage else None,
                    ai_summary=triage.summary if triage else None,
                    ai_confidence=triage.confidence if triage else None,
                    recurrence_flag=report.recurrence_flag,
                    cluster_id=report.cluster_id,
                )
            )

        return AdminReportPage(
            items=items,
            meta=PageMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=max((total + page_size - 1) // page_size, 1) if total else 0,
            ),
        )

    def get_report_detail(self, report_id: UUID) -> AdminReportDetail | None:
        report = self.repo.get_report_detail(report_id)
        if report is None:
            return None

        triage = self.repo.get_current_triage(report_id)

        return AdminReportDetail(
            id=report.id,
            public_reference_code=report.public_reference_code,
            incident_date=report.incident_date,
            location_text=report.location_text,
            location_zone=report.location_zone,
            status=report.status,
            created_at=report.created_at,
            ai_category=triage.category if triage else None,
            ai_severity=triage.severity if triage else None,
            ai_priority_score=triage.priority_score if triage else None,
            ai_summary=triage.summary if triage else None,
            ai_confidence=triage.confidence if triage else None,
            recurrence_flag=report.recurrence_flag,
            cluster_id=report.cluster_id,
            content_sanitized=report.content_sanitized,
            content_raw=report.content_raw,
            urgency_self_reported=report.urgency_self_reported,
            submitted_from_demo=report.submitted_from_demo,
            is_deleted=report.is_deleted,
            updated_at=report.updated_at,
            ai_justification=triage.justification if triage else None,
            model_version=triage.model_version if triage else None,
            processed_at=triage.processed_at if triage else None,
            recurrence_score=triage.recurrence_score if triage else None,
            keywords=(triage.keywords.get("keywords", []) if triage and isinstance(triage.keywords, dict) else []),
            attachments=[
                ReportAttachmentRead.model_validate(attachment)
                for attachment in report.attachments
            ],
            notes=[
                AdminNoteRead.model_validate(note)
                for note in report.notes
            ],
            status_history=[
                ReportStatusHistoryRead.model_validate(history)
                for history in report.status_history
            ],
        )

    def dashboard_metrics(self) -> DashboardMetrics:
        total_reports = self.repo.count_reports()
        reports_in_review = self.repo.count_reports_in_review()
        critical_reports = self.repo.count_current_triage_by_severity(SeverityLevel.CRITICAL)
        high_reports = self.repo.count_current_triage_by_severity(SeverityLevel.HIGH)
        active_clusters = self.repo.count_active_clusters()

        recurrence_count = self.repo.count_recurrence_reports()
        recurrence_rate = round((recurrence_count / total_reports), 4) if total_reports else 0.0

        return DashboardMetrics(
            total_reports=total_reports,
            reports_in_review=reports_in_review,
            critical_reports=critical_reports,
            high_reports=high_reports,
            active_clusters=active_clusters,
            recurrence_rate=recurrence_rate,
            most_common_category=self.repo.most_common_category(),
            most_common_severity=self.repo.most_common_severity(),
        )

    def add_note(self, report_id: UUID, payload: AdminCaseNoteCreate, current_user_id: UUID) -> AdminNoteRead:
        report = self.repo.get_report(report_id)
        if report is None:
            raise ValueError("Report not found.")

        note = self.repo.add_note(
            report_id=report_id,
            admin_id=current_user_id,
            content=payload.content,
            is_private=payload.is_private,
        )

        self.repo.create_audit_log(
            actor_id=current_user_id,
            action="REPORT_NOTE_CREATED",
            target_type="REPORT",
            target_id=report_id,
            event_metadata={"is_private": payload.is_private},
        )

        self.db.commit()
        self.db.refresh(note)
        return AdminNoteRead.model_validate(note)

    def update_status(self, report_id: UUID, payload: AdminCaseStatusUpdate, current_user_id: UUID) -> ReportStatusHistoryRead:
        report = self.repo.get_report(report_id)
        if report is None:
            raise ValueError("Report not found.")

        if report.status == payload.new_status:
            raise ValueError("Report already has this status.")

        history = self.repo.update_report_status(
            report_id=report_id,
            new_status=payload.new_status,
            changed_by=current_user_id,
            reason=payload.reason,
        )

        self.repo.create_audit_log(
            actor_id=current_user_id,
            action="REPORT_STATUS_UPDATED",
            target_type="REPORT",
            target_id=report_id,
            event_metadata={
                "previous_status": history.previous_status.value if history.previous_status else None,
                "new_status": history.new_status.value,
                "reason": payload.reason,
            },
        )

        self.db.commit()
        self.db.refresh(history)
        return ReportStatusHistoryRead.model_validate(history)

    def get_status_history(self, report_id: UUID) -> list[ReportStatusHistoryRead]:
        history = self.repo.list_status_history(report_id)
        return [ReportStatusHistoryRead.model_validate(item) for item in history]