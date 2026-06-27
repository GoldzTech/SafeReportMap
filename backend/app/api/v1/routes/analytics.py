from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.analytics import AnalyticsOverview, AnalyticsResponse
from backend.app.services.analytics_service import AnalyticsService
from backend.app.security.dependencies import get_current_active_admin_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def get_overview(current_user=Depends(get_current_active_admin_user), db: Session = Depends(get_db)):
    service = AnalyticsService(db)
    return service.overview()


@router.get("/dashboard", response_model=AnalyticsResponse)
def get_dashboard(current_user=Depends(get_current_active_admin_user), db: Session = Depends(get_db)):
    service = AnalyticsService(db)
    return service.dashboard()