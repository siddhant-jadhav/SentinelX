"""
SentinelX Threat Service
Business logic for threat management operations.
"""
import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, case, desc
from sqlalchemy.orm import Session

from backend.models import Threat, User


def get_threats(
    db: Session,
    source: Optional[str] = None,
    severity: Optional[str] = None,
    indicator_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> tuple[list[Threat], int]:
    """
    Get a filtered, paginated list of threats.

    Returns:
        Tuple of (threats list, total count).
    """
    query = db.query(Threat)

    # Apply filters
    if source:
        query = query.filter(Threat.source == source)
    if severity:
        query = query.filter(Threat.severity == severity)
    if indicator_type:
        query = query.filter(Threat.indicator_type == indicator_type)
    if status:
        query = query.filter(Threat.status == status)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Threat.title.ilike(search_term)) |
            (Threat.indicator.ilike(search_term)) |
            (Threat.description.ilike(search_term))
        )

    # Get total count
    total = query.count()

    # Apply sorting
    sort_column = getattr(Threat, sort_by, Threat.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)

    # Apply pagination
    offset = (page - 1) * limit
    threats = query.offset(offset).limit(limit).all()

    return threats, total


def get_threat_by_id(db: Session, threat_id: int) -> Optional[Threat]:
    """Get a single threat by its ID."""
    return db.query(Threat).filter(Threat.id == threat_id).first()


def create_threat(
    db: Session,
    title: str,
    indicator: str,
    indicator_type: str,
    severity: str = "Medium",
    description: str = "",
    source: str = "Community",
    status: str = "Pending",
    reference_url: str = "",
    risk_score: Optional[float] = None,
    tags: Optional[list[str]] = None,
    submitted_by: Optional[int] = None,
) -> Threat:
    """Create a new threat entry."""
    if risk_score is None:
        risk_score = _severity_to_score(severity)

    threat = Threat(
        title=title,
        indicator=indicator,
        indicator_type=indicator_type,
        severity=severity,
        description=description,
        source=source,
        status=status,
        reference_url=reference_url,
        risk_score=risk_score,
        tags=json.dumps(tags or []),
        submitted_by=submitted_by,
    )
    db.add(threat)
    db.commit()
    db.refresh(threat)
    return threat


def update_threat(
    db: Session,
    threat_id: int,
    **kwargs,
) -> Optional[Threat]:
    """Update a threat's fields."""
    threat = db.query(Threat).filter(Threat.id == threat_id).first()
    if not threat:
        return None

    for key, value in kwargs.items():
        if value is not None and hasattr(threat, key):
            if key == "tags" and isinstance(value, list):
                threat.tags = json.dumps(value)
            else:
                setattr(threat, key, value)

    threat.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(threat)
    return threat


def delete_threat(db: Session, threat_id: int) -> bool:
    """Delete a threat by ID. Returns True if deleted."""
    threat = db.query(Threat).filter(Threat.id == threat_id).first()
    if not threat:
        return False
    db.delete(threat)
    db.commit()
    return True


def search_threats(
    db: Session,
    query: str,
    indicator_type: Optional[str] = None,
) -> list[Threat]:
    """Search threats by indicator value in local database."""
    search_term = f"%{query}%"
    db_query = db.query(Threat).filter(
        (Threat.indicator.ilike(search_term)) |
        (Threat.title.ilike(search_term))
    )

    if indicator_type:
        db_query = db_query.filter(Threat.indicator_type == indicator_type)

    # Only return approved or OTX threats
    db_query = db_query.filter(
        (Threat.status == "Approved") | (Threat.source == "OTX")
    )

    return db_query.order_by(desc(Threat.created_at)).limit(50).all()


def get_analytics_overview(db: Session) -> dict:
    """Get aggregate analytics data."""
    total = db.query(Threat).count()
    otx_count = db.query(Threat).filter(Threat.source == "OTX").count()
    community_count = db.query(Threat).filter(Threat.source == "Community").count()

    # Severity counts
    severity_counts = {}
    for sev in ["Critical", "High", "Medium", "Low", "Info"]:
        severity_counts[sev] = db.query(Threat).filter(Threat.severity == sev).count()

    # Status counts
    pending = db.query(Threat).filter(Threat.status == "Pending").count()
    approved = db.query(Threat).filter(Threat.status == "Approved").count()
    rejected = db.query(Threat).filter(Threat.status == "Rejected").count()

    # Threats by indicator type
    type_counts = dict(
        db.query(Threat.indicator_type, func.count(Threat.id))
        .group_by(Threat.indicator_type)
        .all()
    )

    return {
        "total_threats": total,
        "otx_count": otx_count,
        "community_count": community_count,
        "critical_count": severity_counts.get("Critical", 0),
        "high_count": severity_counts.get("High", 0),
        "medium_count": severity_counts.get("Medium", 0),
        "low_count": severity_counts.get("Low", 0),
        "info_count": severity_counts.get("Info", 0),
        "pending_count": pending,
        "approved_count": approved,
        "rejected_count": rejected,
        "threats_by_type": type_counts,
        "threats_by_severity": severity_counts,
    }


def get_daily_trends(db: Session, days: int = 30) -> list[dict]:
    """Get daily threat volume for the last N days."""
    from datetime import timedelta

    trends = []
    today = datetime.now(timezone.utc).date()

    for i in range(days, -1, -1):
        date = today - timedelta(days=i)
        start = datetime(date.year, date.month, date.day, tzinfo=timezone.utc)
        end = start + timedelta(days=1)

        count = db.query(Threat).filter(
            Threat.created_at >= start,
            Threat.created_at < end,
        ).count()

        trends.append({
            "date": date.isoformat(),
            "count": count,
        })

    return trends


def get_community_stats(db: Session) -> dict:
    """Get community contribution statistics."""
    community_threats = db.query(Threat).filter(Threat.source == "Community")
    total = community_threats.count()
    approved = community_threats.filter(Threat.status == "Approved").count()
    rejected = community_threats.filter(Threat.status == "Rejected").count()
    pending = community_threats.filter(Threat.status == "Pending").count()

    approval_rate = (approved / total * 100) if total > 0 else 0

    # Top contributors
    top_contributors = (
        db.query(
            User.username,
            func.count(Threat.id).label("count"),
        )
        .join(Threat, Threat.submitted_by == User.id)
        .filter(Threat.source == "Community")
        .group_by(User.username)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )

    return {
        "total_submissions": total,
        "approved_count": approved,
        "rejected_count": rejected,
        "pending_count": pending,
        "approval_rate": round(approval_rate, 1),
        "top_contributors": [
            {"username": c.username, "count": c.count}
            for c in top_contributors
        ],
    }


def _severity_to_score(severity: str) -> float:
    """Convert severity label to risk score."""
    return {
        "Critical": 9.5,
        "High": 7.5,
        "Medium": 5.0,
        "Low": 3.0,
        "Info": 1.0,
    }.get(severity, 5.0)
