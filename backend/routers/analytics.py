"""
SentinelX Analytics Router
Endpoints for threat intelligence analytics and statistics.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import AnalyticsOverview, AnalyticsTrends, CommunityStats
from backend.services import threat_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def get_overview(db: Session = Depends(get_db)):
    """Get aggregate analytics overview: counts by type, severity, source, status."""
    data = threat_service.get_analytics_overview(db)
    return AnalyticsOverview(**data)


@router.get("/trends", response_model=AnalyticsTrends)
def get_trends(
    days: int = Query(30, ge=7, le=90, description="Number of days to look back"),
    db: Session = Depends(get_db),
):
    """Get daily threat volume trends."""
    daily = threat_service.get_daily_trends(db, days)
    return AnalyticsTrends(
        daily_volume=[
            {"date": d["date"], "count": d["count"]}
            for d in daily
        ],
        period_days=days,
    )


@router.get("/community", response_model=CommunityStats)
def get_community_stats(db: Session = Depends(get_db)):
    """Get community contribution statistics."""
    data = threat_service.get_community_stats(db)
    return CommunityStats(**data)
