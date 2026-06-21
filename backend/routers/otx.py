"""
SentinelX OTX Router
Proxy endpoints for AlienVault OTX API data.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.auth import require_admin
from backend.services import otx_service
from backend.services import threat_service

router = APIRouter(prefix="/otx", tags=["OTX Integration"])


@router.get("/latest")
def get_latest_otx_pulses(
    limit: int = Query(20, ge=1, le=50, description="Number of pulses to fetch"),
):
    """Fetch the latest threat pulses from AlienVault OTX."""
    pulses = otx_service.get_latest_pulses(limit=limit)
    return {
        "pulses": pulses,
        "total": len(pulses),
        "source": "live" if otx_service.is_otx_available() else "demo",
    }


@router.post("/sync")
def sync_otx_pulses(
    limit: int = Query(20, ge=1, le=50, description="Number of pulses to sync"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    Sync OTX pulses into the local database. Admin only.
    Creates new threat entries for each OTX pulse.
    """
    pulses = otx_service.get_latest_pulses(limit=limit)
    synced = 0
    skipped = 0

    for pulse in pulses:
        # Check if indicator already exists
        from backend.models import Threat
        existing = db.query(Threat).filter(
            Threat.indicator == pulse["indicator"],
            Threat.source == "OTX",
        ).first()

        if existing:
            skipped += 1
            continue

        threat_service.create_threat(
            db=db,
            title=pulse["title"],
            indicator=pulse["indicator"],
            indicator_type=pulse["indicator_type"],
            severity=pulse["severity"],
            description=pulse.get("description", ""),
            source="OTX",
            status="Approved",
            reference_url=pulse.get("reference_url", ""),
            risk_score=pulse.get("risk_score", 5.0),
            tags=pulse.get("tags", []),
        )
        synced += 1

    return {
        "synced": synced,
        "skipped": skipped,
        "total_processed": len(pulses),
        "message": f"Successfully synced {synced} new threats from OTX",
    }


@router.get("/status")
def otx_status():
    """Check OTX API connection status."""
    return {
        "configured": otx_service.is_otx_available(),
        "mode": "live" if otx_service.is_otx_available() else "demo",
        "message": (
            "Connected to AlienVault OTX API"
            if otx_service.is_otx_available()
            else "Running in demo mode. Set OTX_API_KEY in .env for live data."
        ),
    }
