from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.core.enums import IncidentCategory, ReportStatus, SeverityLevel
from backend.app.core.tenant_context import require_current_tenant_id
from backend.app.models.audit_log import AuditLog
from backend.app.models.cluster import Cluster
from backend.app.models.note import AdminNote
from backend.app.models.report import Report
from backend.app.models.status_history import ReportStatusHistory
from backend.app.models.triage import AITriageResult


class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_report(self, report_id: UUID) -> Report | None:
        tenant_id = require_current_tenant_id()
        stmt = select(Report).where(
            Report.id == report_id,
            Report.tenant_id == tenant_id,
            Report.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

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
    ) -> tuple[list[Report], int]:
        tenant_id = require_current_tenant_id()
        offset = (page - 1) * page_size

        stmt = select(Report).where(
            Report.is_deleted.is_(False),
            Report.tenant_id == tenant_id,
        )

        total_stmt = select(func.count(func.distinct(Report.id))).where(
            Report.is_deleted.is_(False),
            Report.tenant_id == tenant_id,
        )

        if severity is not None or category is not None:
            join_cond = and_(
                AITriageResult.report_id == Report.id,
                AITriageResult.is_current.is_(True),
                AITriageResult.tenant_id == tenant_id,
            )
            stmt = stmt.join(AITriageResult, join_cond)
            total_stmt = total_stmt.join(AITriageResult, join_cond)

            if severity is not None:
                stmt = stmt.where(AITriageResult.severity == severity)
                total_stmt = total_stmt.where(AITriageResult.severity == severity)
            if category is not None:
                stmt = stmt.where(AITriageResult.category == category)
                total_stmt = total_stmt.where(AITriageResult.category == category)

        if status is not None:
            stmt = stmt.where(Report.status == status)
            total_stmt = total_stmt.where(Report.status == status)

        if zone:
            stmt = stmt.where(Report.location_zone.ilike(f"%{zone}%"))
            total_stmt = total_stmt.where(Report.location_zone.ilike(f"%{zone}%"))

        if search:
            like_term = f"%{search}%"
            search_filter = or_(
                Report.location_text.ilike(like_term),
                Report.content_sanitized.ilike(like_term),
                Report.public_reference_code.ilike(like_term),
            )
            stmt = stmt.where(search_filter)
            total_stmt = total_stmt.where(search_filter)

        if date_from is not None:
            stmt = stmt.where(Report.created_at >= date_from)
            total_stmt = total_stmt.where(Report.created_at >= date_from)

        if date_to is not None:
            stmt = stmt.where(Report.created_at < date_to)
            total_stmt = total_stmt.where(Report.created_at < date_to)

        stmt = stmt.order_by(Report.created_at.desc()).limit(page_size).offset(offset)

        reports = self.db.scalars(stmt).all()
        total = self.db.scalar(total_stmt) or 0

        return list(reports), total

    def get_report_detail(self, report_id: UUID) -> Report | None:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(Report)
            .options(
                selectinload(Report.attachments),
                selectinload(Report.notes),
                selectinload(Report.status_history),
            )
            .where(
                Report.id == report_id,
                Report.tenant_id == tenant_id,
                Report.is_deleted.is_(False),
            )
        )
        return self.db.scalar(stmt)

    def get_current_triage(self, report_id: UUID) -> AITriageResult | None:
        tenant_id = require_current_tenant_id()
        stmt = select(AITriageResult).where(
            AITriageResult.report_id == report_id,
            AITriageResult.tenant_id == tenant_id,
            AITriageResult.is_current.is_(True),
        )
        return self.db.scalar(stmt)

    def add_note(self, report_id: UUID, admin_id: UUID, content: str, is_private: bool = True) -> AdminNote:
        tenant_id = require_current_tenant_id()
        note = AdminNote(
            tenant_id=tenant_id,
            report_id=report_id,
            admin_id=admin_id,
            content=content,
            is_private=is_private,
        )
        self.db.add(note)
        self.db.flush()
        return note

    def update_report_status(
        self,
        report_id: UUID,
        new_status: ReportStatus,
        changed_by: UUID,
        reason: str | None = None,
    ) -> ReportStatusHistory:
        tenant_id = require_current_tenant_id()
        report = self.get_report(report_id)
        if report is None:
            raise ValueError("Report not found.")

        previous_status = report.status
        report.status = new_status

        history = ReportStatusHistory(
            tenant_id=tenant_id,
            report_id=report.id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            reason=reason,
        )
        self.db.add(history)
        self.db.flush()
        return history

    def list_status_history(self, report_id: UUID) -> list[ReportStatusHistory]:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(ReportStatusHistory)
            .where(
                ReportStatusHistory.report_id == report_id,
                ReportStatusHistory.tenant_id == tenant_id,
            )
            .order_by(ReportStatusHistory.changed_at.desc())
        )
        return self.db.scalars(stmt).all()

    def create_audit_log(
        self,
        *,
        actor_id: UUID | None,
        action: str,
        target_type: str,
        target_id: UUID | None,
        event_metadata: dict | None = None,
    ) -> AuditLog:
        tenant_id = require_current_tenant_id()
        log = AuditLog(
            tenant_id=tenant_id,
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            meta_data=event_metadata,
        )
        self.db.add(log)
        self.db.flush()
        return log

    def count_reports(self) -> int:
        tenant_id = require_current_tenant_id()
        stmt = select(func.count(Report.id)).where(
            Report.is_deleted.is_(False),
            Report.tenant_id == tenant_id,
        )
        return self.db.scalar(stmt) or 0

    def count_reports_in_review(self) -> int:
        tenant_id = require_current_tenant_id()
        stmt = select(func.count(Report.id)).where(
            Report.is_deleted.is_(False),
            Report.tenant_id == tenant_id,
            Report.status == ReportStatus.IN_REVIEW,
        )
        return self.db.scalar(stmt) or 0

    def count_active_clusters(self) -> int:
        tenant_id = require_current_tenant_id()
        stmt = select(func.count(Cluster.id)).where(
            Cluster.is_active.is_(True),
            Cluster.tenant_id == tenant_id,
        )
        return self.db.scalar(stmt) or 0

    def count_recurrence_reports(self) -> int:
        tenant_id = require_current_tenant_id()
        stmt = select(func.count(Report.id)).where(
            Report.is_deleted.is_(False),
            Report.tenant_id == tenant_id,
            Report.recurrence_flag.is_(True),
        )
        return self.db.scalar(stmt) or 0

    def count_current_triage_by_severity(self, severity: SeverityLevel) -> int:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(func.count(AITriageResult.id))
            .join(Report, Report.id == AITriageResult.report_id)
            .where(
                AITriageResult.is_current.is_(True),
                AITriageResult.tenant_id == tenant_id,
                Report.is_deleted.is_(False),
                Report.tenant_id == tenant_id,
                AITriageResult.severity == severity,
            )
        )
        return self.db.scalar(stmt) or 0

    def most_common_category(self) -> IncidentCategory | None:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(AITriageResult.category, func.count(AITriageResult.id).label("count"))
            .join(Report, Report.id == AITriageResult.report_id)
            .where(
                AITriageResult.is_current.is_(True),
                AITriageResult.tenant_id == tenant_id,
                Report.is_deleted.is_(False),
                Report.tenant_id == tenant_id,
            )
            .group_by(AITriageResult.category)
            .order_by(func.count(AITriageResult.id).desc())
            .limit(1)
        )
        row = self.db.execute(stmt).first()
        return row[0] if row else None

    def most_common_severity(self) -> SeverityLevel | None:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(AITriageResult.severity, func.count(AITriageResult.id).label("count"))
            .join(Report, Report.id == AITriageResult.report_id)
            .where(
                AITriageResult.is_current.is_(True),
                AITriageResult.tenant_id == tenant_id,
                Report.is_deleted.is_(False),
                Report.tenant_id == tenant_id,
            )
            .group_by(AITriageResult.severity)
            .order_by(func.count(AITriageResult.id).desc())
            .limit(1)
        )
        row = self.db.execute(stmt).first()
        return row[0] if row else None