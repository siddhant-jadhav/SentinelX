"""
SentinelX Search Router
Search across local database and OTX simultaneously.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import SearchResponse, SearchResult
from backend.services import threat_service
from backend.services import otx_service

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResponse)
def search_indicators(
    q: str = Query(..., min_length=1, description="Search query (IP, domain, URL, hash)"),
    indicator_type: Optional[str] = Query(None, description="Indicator type filter"),
    db: Session = Depends(get_db),
):
    """
    Search for threat indicators across local database and OTX API.
    Returns combined results from both sources.
    """
    # Auto-detect indicator type if not provided
    if not indicator_type:
        indicator_type = _detect_indicator_type(q)

    # Search local database
    local_threats = threat_service.search_threats(db, q, indicator_type)
    local_results = [
        SearchResult(
            indicator=t.indicator,
            indicator_type=t.indicator_type,
            title=t.title,
            severity=t.severity,
            source=t.source,
            description=t.description or "",
            risk_score=t.risk_score,
            reference_url=t.reference_url or "",
            created_at=t.created_at,
            threat_id=t.id,
        )
        for t in local_threats
    ]

    # Search OTX API
    otx_raw = otx_service.search_indicator(indicator_type or "IPv4", q)
    otx_results = [
        SearchResult(
            indicator=r.get("indicator", q),
            indicator_type=r.get("indicator_type", indicator_type or "Unknown"),
            title=r.get("title", "OTX Result"),
            severity=r.get("severity", "Medium"),
            source="OTX",
            description=r.get("description", ""),
            risk_score=r.get("risk_score", 5.0),
            reference_url=r.get("reference_url", ""),
            created_at=None,
        )
        for r in otx_raw
    ]

    return SearchResponse(
        query=q,
        query_type=indicator_type or "Unknown",
        local_results=local_results,
        otx_results=otx_results,
        total_results=len(local_results) + len(otx_results),
    )


def _detect_indicator_type(query: str) -> str:
    """Auto-detect the indicator type based on the query format."""
    import re

    query = query.strip()

    # IPv4 pattern
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', query):
        return "IPv4"

    # IPv6 pattern (simplified)
    if ":" in query and re.match(r'^[0-9a-fA-F:]+$', query):
        return "IPv6"

    # URL pattern
    if query.startswith(("http://", "https://", "ftp://")):
        return "URL"

    # MD5 hash (32 hex chars)
    if re.match(r'^[a-fA-F0-9]{32}$', query):
        return "FileHash-MD5"

    # SHA1 hash (40 hex chars)
    if re.match(r'^[a-fA-F0-9]{40}$', query):
        return "FileHash-SHA1"

    # SHA256 hash (64 hex chars)
    if re.match(r'^[a-fA-F0-9]{64}$', query):
        return "FileHash-SHA256"

    # Email pattern
    if "@" in query and "." in query:
        return "Email"

    # CIDR notation
    if "/" in query and re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$', query):
        return "CIDR"

    # Default to domain
    if "." in query:
        return "Domain"

    return "Hostname"
