"""
SentinelX Threats Router
CRUD endpoints for threat intelligence management.
"""
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.schemas import (
    ThreatCreate, ThreatUpdate, ThreatResponse, ThreatListResponse
)
from backend.auth import get_current_user, require_auth, require_admin
from backend.services import threat_service

router = APIRouter(prefix="/threats", tags=["Threats"])


@router.get("", response_model=ThreatListResponse)
def list_threats(
    source: Optional[str] = Query(None, description="Filter by source: OTX or Community"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    indicator_type: Optional[str] = Query(None, description="Filter by indicator type"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in title, indicator, description"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    List all threats with optional filters and pagination.
    Public endpoint — returns only Approved/OTX threats unless user is admin.
    """
    # Non-admin users only see approved threats and OTX threats
    effective_status = status_filter
    if not current_user or current_user.role != "admin":
        if not effective_status:
            effective_status = "Approved"

    threats, total = threat_service.get_threats(
        db=db,
        source=source,
        severity=severity,
        indicator_type=indicator_type,
        status=effective_status,
        search=search,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    # Convert to response models
    threat_responses = []
    for t in threats:
        tr = ThreatResponse(
            id=t.id,
            title=t.title,
            indicator=t.indicator,
            indicator_type=t.indicator_type,
            severity=t.severity,
            description=t.description or "",
            source=t.source,
            status=t.status,
            reference_url=t.reference_url or "",
            risk_score=t.risk_score,
            tags=t.tags_list,
            submitted_by=t.submitted_by,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )
        threat_responses.append(tr)

    pages = max(1, (total + limit - 1) // limit)

    return ThreatListResponse(
        threats=threat_responses,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/{threat_id}", response_model=ThreatResponse)
def get_threat(
    threat_id: int,
    db: Session = Depends(get_db),
):
    """Get a single threat by ID."""
    threat = threat_service.get_threat_by_id(db, threat_id)
    if not threat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Threat not found",
        )

    return ThreatResponse(
        id=threat.id,
        title=threat.title,
        indicator=threat.indicator,
        indicator_type=threat.indicator_type,
        severity=threat.severity,
        description=threat.description or "",
        source=threat.source,
        status=threat.status,
        reference_url=threat.reference_url or "",
        risk_score=threat.risk_score,
        tags=threat.tags_list,
        submitted_by=threat.submitted_by,
        created_at=threat.created_at,
        updated_at=threat.updated_at,
    )


@router.post("", response_model=ThreatResponse, status_code=status.HTTP_201_CREATED)
def create_threat(
    payload: ThreatCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Submit a new threat. Requires authentication. Status starts as Pending."""
    threat = threat_service.create_threat(
        db=db,
        title=payload.title,
        indicator=payload.indicator,
        indicator_type=payload.indicator_type,
        severity=payload.severity,
        description=payload.description or "",
        source="Community",
        status="Pending",
        reference_url=payload.reference_url or "",
        tags=payload.tags,
        submitted_by=user.id,
    )

    return ThreatResponse(
        id=threat.id,
        title=threat.title,
        indicator=threat.indicator,
        indicator_type=threat.indicator_type,
        severity=threat.severity,
        description=threat.description or "",
        source=threat.source,
        status=threat.status,
        reference_url=threat.reference_url or "",
        risk_score=threat.risk_score,
        tags=threat.tags_list,
        submitted_by=threat.submitted_by,
        created_at=threat.created_at,
        updated_at=threat.updated_at,
    )


@router.put("/{threat_id}", response_model=ThreatResponse)
def update_threat(
    threat_id: int,
    payload: ThreatUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Update a threat. Admin only."""
    update_data = payload.model_dump(exclude_unset=True)
    threat = threat_service.update_threat(db, threat_id, **update_data)

    if not threat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Threat not found",
        )

    return ThreatResponse(
        id=threat.id,
        title=threat.title,
        indicator=threat.indicator,
        indicator_type=threat.indicator_type,
        severity=threat.severity,
        description=threat.description or "",
        source=threat.source,
        status=threat.status,
        reference_url=threat.reference_url or "",
        risk_score=threat.risk_score,
        tags=threat.tags_list,
        submitted_by=threat.submitted_by,
        created_at=threat.created_at,
        updated_at=threat.updated_at,
    )


@router.delete("/{threat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_threat(
    threat_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Delete a threat. Admin only."""
    if not threat_service.delete_threat(db, threat_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Threat not found",
        )
