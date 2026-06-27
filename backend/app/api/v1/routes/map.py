from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.map import ClusterMapItem, HeatmapResponse, MapPoint
from backend.app.services.analytics_service import AnalyticsService
from backend.app.repositories.analytics_repository import AnalyticsRepository
from backend.app.security.dependencies import get_current_active_admin_user

router = APIRouter(prefix="/map", tags=["map"])


@router.get("/heatmap", response_model=HeatmapResponse)
def get_heatmap(current_user=Depends(get_current_active_admin_user), db: Session = Depends(get_db)):
    repo = AnalyticsRepository(db)
    points = [
        MapPoint(
            report_id=report_id,
            location_zone=location_zone,
            cluster_id=cluster_id,
            severity=severity,
            intensity=float(intensity or 0.0),
        )
        for report_id, location_zone, cluster_id, severity, intensity in repo.heatmap_points()
    ]
    return HeatmapResponse(points=points)


@router.get("/clusters", response_model=list[ClusterMapItem])
def get_clusters(current_user=Depends(get_current_active_admin_user), db: Session = Depends(get_db)):
    repo = AnalyticsRepository(db)
    clusters = repo.clusters()
    return [
        ClusterMapItem(
            cluster_id=cluster.id,
            label=cluster.label,
            cluster_type=cluster.cluster_type,
            recurrence_count=cluster.recurrence_count,
            severity_level=cluster.severity_level,
        )
        for cluster in clusters
    ]