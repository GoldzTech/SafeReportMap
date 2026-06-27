from __future__ import annotations

from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.app.core.enums import IncidentCategory, ReportStatus, SeverityLevel
from backend.app.core.tenant_context import require_current_tenant_id
from backend.app.models.report import Report
from backend.app.models.triage import AITriageResult


class ExportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_export_rows(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        status: ReportStatus | None = None,
        severity: SeverityLevel | None = None,
        category: IncidentCategory | None = None,
        zone: str | None = None,
        search: str | None = None,
    ) -> list[dict]:
        tenant_id = require_current_tenant_id()

        triage_subquery = (
            select(
                AITriageResult.report_id.label("report_id"),
                AITriageResult.category.label("category"),
                AITriageResult.severity.label("severity"),
                AITriageResult.priority_score.label("priority_score"),
                AITriageResult.summary.label("summary"),
                AITriageResult.keywords.label("keywords"),
            )
            .where(
                AITriageResult.tenant_id == tenant_id,
                AITriageResult.is_current.is_(True),
            )
            .subquery()
        )

        stmt = (
            select(
                Report.public_reference_code.label("public_reference_code"),
                Report.created_at.label("created_at"),
                Report.incident_date.label("incident_date"),
                Report.location_zone.label("location_zone"),
                Report.status.label("status"),
                triage_subquery.c.category.label("category"),
                triage_subquery.c.severity.label("severity"),
                triage_subquery.c.priority_score.label("priority_score"),
                triage_subquery.c.summary.label("summary"),
                triage_subquery.c.keywords.label("keywords"),
                Report.recurrence_flag.label("recurrence_flag"),
                Report.cluster_id.label("cluster_id"),
            )
            .select_from(Report)
            .join(triage_subquery, triage_subquery.c.report_id == Report.id, isouter=True)
            .where(
                Report.is_deleted.is_(False),
                Report.tenant_id == tenant_id,
            )
            .order_by(Report.created_at.desc())
        )

        if status is not None:
            stmt = stmt.where(Report.status == status)

        if severity is not None:
            stmt = stmt.where(triage_subquery.c.severity == severity)

        if category is not None:
            stmt = stmt.where(triage_subquery.c.category == category)

        if zone:
            stmt = stmt.where(Report.location_zone.ilike(f"%{zone}%"))

        if search:
            like_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Report.location_text.ilike(like_term),
                    Report.public_reference_code.ilike(like_term),
                )
            )

        if date_from is not None:
            stmt = stmt.where(Report.created_at >= date_from)

        if date_to is not None:
            stmt = stmt.where(Report.created_at < date_to)

        rows = self.db.execute(stmt).all()

        result: list[dict] = []
        for row in rows:
            keywords_value = row.keywords
            if isinstance(keywords_value, dict):
                keywords_value = keywords_value.get("keywords", [])
            if isinstance(keywords_value, list):
                keywords_text = ", ".join(str(k) for k in keywords_value)
            else:
                keywords_text = None

            result.append(
                {
                    "public_reference_code": row.public_reference_code,
                    "created_at": row.created_at.isoformat() if row.created_at else "",
                    "incident_date": row.incident_date.isoformat() if row.incident_date else None,
                    "location_zone": row.location_zone,
                    "status": row.status.value if hasattr(row.status, "value") else str(row.status),
                    "category": row.category.value if row.category else None,
                    "severity": row.severity.value if row.severity else None,
                    "priority_score": float(row.priority_score) if row.priority_score is not None else None,
                    "summary": row.summary,
                    "keywords": keywords_text,
                    "recurrence_flag": bool(row.recurrence_flag),
                    "cluster_id": str(row.cluster_id) if row.cluster_id else None,
                }
            )

        return result