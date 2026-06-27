from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.core.enums import SeverityLevel
from backend.app.repositories.analytics_repository import AnalyticsRepository
from backend.app.schemas.analytics import (
    AnalyticsOverview,
    AnalyticsResponse,
    CategoryStat,
    ClusterStat,
    HeatmapPoint,
    LocationStat,
    SeverityStat,
    TimelinePoint,
)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AnalyticsRepository(db)

    def overview(self) -> AnalyticsOverview:
        total_reports = self.repo.count_total_reports()
        recurrence_count = self.repo.count_recurrence_reports()
        recurrence_rate = round((recurrence_count / total_reports), 4) if total_reports else 0.0

        return AnalyticsOverview(
            total_reports=total_reports,
            reports_in_review=self.repo.count_reports_in_review(),
            critical_reports=self.repo.count_by_severity(SeverityLevel.CRITICAL),
            high_reports=self.repo.count_by_severity(SeverityLevel.HIGH),
            active_clusters=self.repo.count_active_clusters(),
            recurrence_rate=recurrence_rate,
            most_common_category=self.repo.most_common_category(),
            most_common_severity=self.repo.most_common_severity(),
        )

    def dashboard(self) -> AnalyticsResponse:
        timeline = [
            TimelinePoint(day=day, count=count)
            for day, count in self.repo.timeline_by_day()
        ]

        categories = [
            CategoryStat(category=category, count=count)
            for category, count in self.repo.category_distribution()
        ]

        severities = [
            SeverityStat(severity=severity, count=count)
            for severity, count in self.repo.severity_distribution()
        ]

        top_locations = [
            LocationStat(location_zone=location_zone, count=count)
            for location_zone, count in self.repo.top_locations()
        ]

        clusters = [
            ClusterStat(
                cluster_id=cluster.id,
                label=cluster.label,
                cluster_type=cluster.cluster_type,
                recurrence_count=cluster.recurrence_count,
                severity_level=cluster.severity_level,
            )
            for cluster in self.repo.clusters()
        ]

        return AnalyticsResponse(
            overview=self.overview(),
            timeline=timeline,
            categories=categories,
            severities=severities,
            top_locations=top_locations,
            clusters=clusters,
        )