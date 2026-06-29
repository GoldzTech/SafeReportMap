from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from backend.app.security.dependencies import get_current_active_admin_user
from backend.app.schemas.export import ExportFilters
from backend.app.services.export_service import ExportService
from backend.app.core.enums import IncidentCategory, ReportStatus, SeverityLevel
from backend.app.db.session import get_db
from backend.app.schemas.admin import (
    AdminCaseNoteCreate,
    AdminCaseStatusUpdate,
    AdminNoteRead,
    AdminReportDetail,
    AdminReportPage,
    DashboardMetrics,
    ReportStatusHistoryRead,
)
from backend.app.services.admin_service import AdminService
from backend.app.repositories.export_repository import ExportRepository

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.get("/dashboard/metrics", response_model=DashboardMetrics)
def dashboard_metrics(current_user=Depends(get_current_active_admin_user), db: Session = Depends(get_db)):
    service = AdminService(db)
    return service.dashboard_metrics()


@router.get("/reports", response_model=AdminReportPage)
def list_reports(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: ReportStatus | None = Query(default=None, alias="status"),
    severity: SeverityLevel | None = None,
    category: IncidentCategory | None = None,
    zone: str | None = None,
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    current_user=Depends(get_current_active_admin_user),
    db: Session = Depends(get_db),
):
    service = AdminService(db)
    return service.list_reports(
        page=page,
        page_size=page_size,
        status=status_filter,
        severity=severity,
        category=category,
        zone=zone,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/reports/{report_id}", response_model=AdminReportDetail)
def get_report_detail(report_id: UUID, current_user=Depends(get_current_active_admin_user), db: Session = Depends(get_db)):
    service = AdminService(db)
    report = service.get_report_detail(report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    return report


@router.get("/reports/{report_id}/history", response_model=list[ReportStatusHistoryRead])
def get_status_history(report_id: UUID, current_user=Depends(get_current_active_admin_user), db: Session = Depends(get_db)):
    service = AdminService(db)
    return service.get_status_history(report_id)


@router.post("/reports/{report_id}/notes", response_model=AdminNoteRead, status_code=status.HTTP_201_CREATED)
def add_note(
    report_id: UUID,
    payload: AdminCaseNoteCreate,
    current_user=Depends(get_current_active_admin_user),
    db: Session = Depends(get_db),
):
    service = AdminService(db)
    try:
        return service.add_note(report_id, payload, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/reports/{report_id}/status", response_model=ReportStatusHistoryRead)
def update_status(
    report_id: UUID,
    payload: AdminCaseStatusUpdate,
    current_user=Depends(get_current_active_admin_user),
    db: Session = Depends(get_db),
):
    service = AdminService(db)
    try:
        return service.update_status(report_id, payload, current_user.id)
    except ValueError as exc:
        detail = str(exc)
        if detail == "Report not found.":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
    
    
@router.get("/export")
def export_reports(
    format: str = Query(default="csv", pattern="^(csv|pdf)$"),
    date_from: date | None = None,
    date_to: date | None = None,
    status: ReportStatus | None = Query(default=None, alias="status"),
    severity: SeverityLevel | None = None,
    category: IncidentCategory | None = None,
    zone: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_active_admin_user),
    db: Session = Depends(get_db),
):
    service = ExportService(db)
    rows = service.fetch_rows(
        date_from=date_from,
        date_to=date_to,
        status=status,
        severity=severity,
        category=category,
        zone=zone,
        search=search,
    )

    if format == "csv":
        content = service.build_csv(rows)
        filename = "safereport_map_export.csv"
        media_type = "text/csv; charset=utf-8"
    else:
        content = service.build_pdf(rows)
        filename = "safereport_map_export.pdf"
        media_type = "application/pdf"

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )