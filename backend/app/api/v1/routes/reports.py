from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.report import ReportCreate, ReportPublicConfirmation
from backend.app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportPublicConfirmation, status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportCreate, db: Session = Depends(get_db)):
    service = ReportService(db)
    report = service.create_report(payload)

    return ReportPublicConfirmation(
        public_reference_code=report.public_reference_code,
        status=report.status,
        created_at=report.created_at,
    )


@router.get("/{public_reference_code}/confirmation", response_model=ReportPublicConfirmation)
def get_report_confirmation(public_reference_code: str, db: Session = Depends(get_db)):
    service = ReportService(db)
    report = service.get_report_by_public_reference_code(public_reference_code)

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    return ReportPublicConfirmation(
        public_reference_code=report.public_reference_code,
        status=report.status,
        created_at=report.created_at,
    )