from __future__ import annotations

import csv
from io import BytesIO, StringIO
from datetime import date
from typing import Iterable

from sqlalchemy.orm import Session

from backend.app.core.enums import IncidentCategory, ReportStatus, SeverityLevel
from backend.app.repositories.export_repository import ExportRepository

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
except Exception:  # pragma: no cover
    SimpleDocTemplate = None


class ExportService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ExportRepository(db)

    def fetch_rows(
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
        return self.repo.get_export_rows(
            date_from=date_from,
            date_to=date_to,
            status=status,
            severity=severity,
            category=category,
            zone=zone,
            search=search,
        )

    def build_csv(self, rows: list[dict]) -> bytes:
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "public_reference_code",
                "created_at",
                "incident_date",
                "location_zone",
                "status",
                "category",
                "severity",
                "priority_score",
                "summary",
                "keywords",
                "recurrence_flag",
                "cluster_id",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        return output.getvalue().encode("utf-8")

    def build_pdf(self, rows: list[dict]) -> bytes:
        if SimpleDocTemplate is None:
            raise RuntimeError("reportlab is not installed. Install it with: pip install reportlab")

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        story = []
        story.append(Paragraph("SafeReport Map - Anonymous Export", styles["Title"]))
        story.append(Spacer(1, 12))

        table_data = [[
            "Ref",
            "Created",
            "Zone",
            "Status",
            "Category",
            "Severity",
            "Priority",
            "Summary",
        ]]

        for row in rows:
            table_data.append([
                row["public_reference_code"] or "",
                row["created_at"] or "",
                row["location_zone"] or "",
                row["status"] or "",
                row["category"] or "",
                row["severity"] or "",
                str(row["priority_score"]) if row["priority_score"] is not None else "",
                (row["summary"] or "")[:80],
            ])

        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ])
        )

        story.append(table)
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes