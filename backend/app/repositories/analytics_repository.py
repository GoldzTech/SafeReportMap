from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.enums import IncidentCategory, ReportStatus, SeverityLevel
from backend.app.core.tenant_context import require_current_tenant_id
from backend.app.models.cluster import Cluster
from backend.app.models.report import Report
from backend.app.models.triage import AITriageResult


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def count_total_reports(self) -> int:
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

    def count_by_severity(self, severity: SeverityLevel) -> int:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(func.count(AITriageResult.id))
            .join(Report, Report.id == AITriageResult.report_id)
            .where(
                Report.is_deleted.is_(False),
                Report.tenant_id == tenant_id,
                AITriageResult.is_current.is_(True),
                AITriageResult.tenant_id == tenant_id,
                AITriageResult.severity == severity,
            )
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

    def most_common_category(self) -> IncidentCategory | None:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(AITriageResult.category, func.count(AITriageResult.id).label("count"))
            .join(Report, Report.id == AITriageResult.report_id)
            .where(
                Report.is_deleted.is_(False),
                Report.tenant_id == tenant_id,
                AITriageResult.is_current.is_(True),
                AITriageResult.tenant_id == tenant_id,
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
                Report.is_deleted.is_(False),
                Report.tenant_id == tenant_id,
                AITriageResult.is_current.is_(True),
                AITriageResult.tenant_id == tenant_id,
            )
            .group_by(AITriageResult.severity)
            .order_by(func.count(AITriageResult.id).desc())
            .limit(1)
        )
        row = self.db.execute(stmt).first()
        return row[0] if row else None

    def timeline_by_day(self) -> list[tuple[date, int]]:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(func.date(Report.created_at).label("day"), func.count(Report.id))
            .where(
                Report.is_deleted.is_(False),
                Report.tenant_id == tenant_id,
            )
            .group_by(func.date(Report.created_at))
            .order_by(func.date(Report.created_at))
        )
        return [(row[0], row[1]) for row in self.db.execute(stmt).all()]

    def category_distribution(self) -> list[tuple[IncidentCategory, int]]:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(AITriageResult.category, func.count(AITriageResult.id))
            .join(Report, Report.id == AITriageResult.report_id)
            .where(
                Report.is_deleted.is_(False),
                Report.tenant_id == tenant_id,
                AITriageResult.is_current.is_(True),
                AITriageResult.tenant_id == tenant_id,
            )
            .group_by(AITriageResult.category)
            .order_by(func.count(AITriageResult.id).desc())
        )
        return [(row[0], row[1]) for row in self.db.execute(stmt).all()]

    def severity_distribution(self) -> list[tuple[SeverityLevel, int]]:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(AITriageResult.severity, func.count(AITriageResult.id))
            .join(Report, Report.id == AITriageResult.report_id)
            .where(
                Report.is_deleted.is_(False),
                Report.tenant_id == tenant_id,
                AITriageResult.is_current.is_(True),
                AITriageResult.tenant_id == tenant_id,
            )
            .group_by(AITriageResult.severity)
            .order_by(func.count(AITriageResult.id).desc())
        )
        return [(row[0], row[1]) for row in self.db.execute(stmt).all()]

    def top_locations(self) -> list[tuple[str | None, int]]:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(Report.location_zone, func.count(Report.id))
            .where(
                Report.is_deleted.is_(False),
                Report.tenant_id == tenant_id,
            )
            .group_by(Report.location_zone)
            .order_by(func.count(Report.id).desc())
            .limit(10)
        )
        return [(row[0], row[1]) for row in self.db.execute(stmt).all()]

    def clusters(self) -> list[Cluster]:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(Cluster)
            .where(
                Cluster.is_active.is_(True),
                Cluster.tenant_id == tenant_id,
            )
            .order_by(Cluster.recurrence_count.desc())
        )
        return self.db.scalars(stmt).all()

    def heatmap_points(self) -> list[tuple[UUID, str | None, UUID | None, SeverityLevel | None, float]]:
        tenant_id = require_current_tenant_id()
        stmt = (
            select(
                Report.id,
                Report.location_zone,
                Report.cluster_id,
                AITriageResult.severity,
                AITriageResult.priority_score,
            )
            .join(AITriageResult, AITriageResult.report_id == Report.id)
            .where(
                Report.is_deleted.is_(False),
                Report.tenant_id == tenant_id,
                AITriageResult.is_current.is_(True),
                AITriageResult.tenant_id == tenant_id,
            )
            .order_by(Report.created_at.desc())
        )
        return self.db.execute(stmt).all()