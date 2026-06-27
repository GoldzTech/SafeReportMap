from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.triage import TriageResultRead, TriageStatusResponse
from backend.app.services.triage_service import TriageService
from backend.app.workers.triage_worker import process_triage_job
from backend.app.security.dependencies import get_current_active_admin_user

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/triage/{report_id}", response_model=TriageStatusResponse)
def triage_report(
    report_id: UUID,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_admin_user),
    db: Session = Depends(get_db),
):
    service = TriageService(db)
    report = service.repo.get_report_by_id(report_id)

    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

    background_tasks.add_task(process_triage_job, report_id)

    return TriageStatusResponse(
        report_id=report_id,
        triaged=False,
        message="Triagem enfileirada com sucesso.",
    )


@router.get("/triage/{report_id}", response_model=TriageResultRead)
def get_current_triage(report_id: UUID, current_user=Depends(get_current_active_admin_user), db: Session = Depends(get_db)):
    service = TriageService(db)
    triage = service.get_current_triage(report_id)

    if triage is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Triage not found.")

    return triage