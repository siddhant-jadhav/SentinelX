"""
SentinelX Pydantic Schemas
Request/response validation models for the API.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# ── Auth Schemas ─────────────────────────────────────────────────────────────

class UserLogin(BaseModel):
    """Login request body."""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class UserCreate(BaseModel):
    """Registration request body."""
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    """User data returned in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: str
    created_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Threat Schemas ───────────────────────────────────────────────────────────

class ThreatCreate(BaseModel):
    """Create threat request body."""
    title: str = Field(..., min_length=3, max_length=255)
    indicator: str = Field(..., min_length=1, max_length=500)
    indicator_type: str = Field(..., max_length=50)
    severity: str = Field(default="Medium", max_length=20)
    description: Optional[str] = Field(default="", max_length=5000)
    reference_url: Optional[str] = Field(default="", max_length=500)
    tags: Optional[list[str]] = Field(default_factory=list)


class ThreatUpdate(BaseModel):
    """Update threat request body (all fields optional)."""
    title: Optional[str] = Field(default=None, max_length=255)
    indicator: Optional[str] = Field(default=None, max_length=500)
    indicator_type: Optional[str] = Field(default=None, max_length=50)
    severity: Optional[str] = Field(default=None, max_length=20)
    description: Optional[str] = Field(default=None, max_length=5000)
    status: Optional[str] = Field(default=None, max_length=20)
    reference_url: Optional[str] = Field(default=None, max_length=500)
    risk_score: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    tags: Optional[list[str]] = None


class ThreatResponse(BaseModel):
    """Threat data returned in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    indicator: str
    indicator_type: str
    severity: str
    description: Optional[str] = ""
    source: str
    status: str
    reference_url: Optional[str] = ""
    risk_score: float = 5.0
    tags: list[str] = []
    submitted_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ThreatListResponse(BaseModel):
    """Paginated list of threats."""
    threats: list[ThreatResponse]
    total: int
    page: int
    limit: int
    pages: int


# ── Search Schemas ───────────────────────────────────────────────────────────

class SearchResult(BaseModel):
    """Individual search result."""
    indicator: str
    indicator_type: str
    title: str
    severity: str
    source: str
    description: Optional[str] = ""
    risk_score: float = 5.0
    reference_url: Optional[str] = ""
    created_at: Optional[datetime] = None
    threat_id: Optional[int] = None  # Only for local results


class SearchResponse(BaseModel):
    """Combined search response from OTX + local DB."""
    query: str
    query_type: str
    local_results: list[SearchResult]
    otx_results: list[SearchResult]
    total_results: int


# ── Analytics Schemas ────────────────────────────────────────────────────────

class AnalyticsOverview(BaseModel):
    """Overview analytics data."""
    total_threats: int
    otx_count: int
    community_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    pending_count: int
    approved_count: int
    rejected_count: int
    threats_by_type: dict[str, int]
    threats_by_severity: dict[str, int]


class TrendDataPoint(BaseModel):
    """Single data point in a trend chart."""
    date: str
    count: int
    source: Optional[str] = None


class AnalyticsTrends(BaseModel):
    """Trend analytics data."""
    daily_volume: list[TrendDataPoint]
    period_days: int


class CommunityStats(BaseModel):
    """Community contribution statistics."""
    total_submissions: int
    approved_count: int
    rejected_count: int
    pending_count: int
    approval_rate: float
    top_contributors: list[dict]
