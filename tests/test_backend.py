"""
SentinelX — Backend Test Suite
Tests for FastAPI API endpoints, authentication, and data models.
"""
import pytest


# ═══════════════════════════════════════════════════════════════
# Health & Root Endpoints
# ═══════════════════════════════════════════════════════════════

class TestHealthEndpoints:
    """Test API health and root endpoints."""

    def test_root_endpoint(self, api_client):
        """Root endpoint returns app info."""
        response = api_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "SentinelX"
        assert data["status"] == "operational"
        assert "version" in data

    def test_health_endpoint(self, api_client):
        """Health endpoint returns healthy status."""
        response = api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["otx_integration"] in ["live", "demo"]


# ═══════════════════════════════════════════════════════════════
# Authentication
# ═══════════════════════════════════════════════════════════════

class TestAuthentication:
    """Test authentication endpoints."""

    def test_register_user(self, api_client):
        """Register a new user."""
        response = api_client.post("/auth/register", json={
            "username": "testuser",
            "email": "test@sentinelx.local",
            "password": "TestPass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == "testuser"

    def test_register_duplicate_user(self, api_client):
        """Duplicate registration returns error."""
        # First registration
        api_client.post("/auth/register", json={
            "username": "duplicate_user",
            "email": "dup@sentinelx.local",
            "password": "TestPass123",
        })
        # Second attempt
        response = api_client.post("/auth/register", json={
            "username": "duplicate_user",
            "email": "dup2@sentinelx.local",
            "password": "TestPass123",
        })
        assert response.status_code >= 400

    def test_login_success(self, api_client):
        """Login with valid credentials."""
        # Register first
        api_client.post("/auth/register", json={
            "username": "loginuser",
            "email": "login@sentinelx.local",
            "password": "LoginPass123",
        })
        # Login
        response = api_client.post("/auth/login", json={
            "username": "loginuser",
            "password": "LoginPass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == "loginuser"

    def test_login_invalid_password(self, api_client):
        """Login with wrong password fails."""
        api_client.post("/auth/register", json={
            "username": "wrongpass_user",
            "email": "wrong@sentinelx.local",
            "password": "CorrectPass123",
        })
        response = api_client.post("/auth/login", json={
            "username": "wrongpass_user",
            "password": "WrongPassword",
        })
        assert response.status_code >= 400

    def test_login_nonexistent_user(self, api_client):
        """Login with non-existent user fails."""
        response = api_client.post("/auth/login", json={
            "username": "ghost_user",
            "password": "anything",
        })
        assert response.status_code >= 400

    def test_get_me_authenticated(self, api_client):
        """Get current user profile with valid token."""
        # Register & login
        reg = api_client.post("/auth/register", json={
            "username": "meuser",
            "email": "me@sentinelx.local",
            "password": "MePass123",
        })
        token = reg.json()["access_token"]

        response = api_client.get("/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        assert response.json()["username"] == "meuser"

    def test_get_me_unauthenticated(self, api_client):
        """Get profile without token fails."""
        response = api_client.get("/auth/me")
        assert response.status_code >= 400


# ═══════════════════════════════════════════════════════════════
# Threats CRUD
# ═══════════════════════════════════════════════════════════════

class TestThreats:
    """Test threat endpoints."""

    def _auth_headers(self, api_client, username="threatuser"):
        """Helper: register/login and return auth headers."""
        api_client.post("/auth/register", json={
            "username": username,
            "email": f"{username}@sentinelx.local",
            "password": "ThreatPass123",
        })
        login = api_client.post("/auth/login", json={
            "username": username,
            "password": "ThreatPass123",
        })
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_list_threats_empty(self, api_client):
        """List threats returns paginated response."""
        response = api_client.get("/threats")
        assert response.status_code == 200
        data = response.json()
        assert "threats" in data
        assert "total" in data
        assert "pages" in data
        assert isinstance(data["threats"], list)

    def test_create_threat(self, api_client):
        """Create a new threat with auth."""
        headers = self._auth_headers(api_client, "creator_user")
        response = api_client.post("/threats", json={
            "title": "Test Threat",
            "indicator": "192.168.1.100",
            "indicator_type": "IPv4",
            "severity": "Medium",
            "description": "Test threat from CI pipeline.",
            "reference_url": "",
            "tags": ["test", "ci"],
        }, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Threat"
        assert data["indicator"] == "192.168.1.100"
        assert data["status"] == "Pending"

    def test_create_threat_unauthenticated(self, api_client):
        """Create threat without auth fails."""
        response = api_client.post("/threats", json={
            "title": "Unauthorized Threat",
            "indicator": "10.0.0.1",
            "indicator_type": "IPv4",
            "severity": "Low",
            "description": "Should fail.",
        })
        assert response.status_code >= 400

    def test_list_threats_with_filters(self, api_client):
        """List threats with query parameters."""
        response = api_client.get("/threats", params={
            "severity": "Medium",
            "source": "Community",
            "page": 1,
            "limit": 5,
        })
        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════
# Analytics
# ═══════════════════════════════════════════════════════════════

class TestAnalytics:
    """Test analytics endpoints."""

    def test_analytics_overview(self, api_client):
        """Analytics overview returns expected fields."""
        response = api_client.get("/analytics/overview")
        assert response.status_code == 200
        data = response.json()
        assert "total_threats" in data
        assert "threats_by_severity" in data
        assert "threats_by_type" in data

    def test_analytics_trends(self, api_client):
        """Analytics trends returns daily volume."""
        response = api_client.get("/analytics/trends", params={"days": 7})
        assert response.status_code == 200
        data = response.json()
        assert "daily_volume" in data

    def test_community_stats(self, api_client):
        """Community stats endpoint responds."""
        response = api_client.get("/analytics/community")
        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════
# OTX Integration
# ═══════════════════════════════════════════════════════════════

class TestOTXIntegration:
    """Test OTX integration endpoints."""

    def test_otx_status(self, api_client):
        """OTX status endpoint responds."""
        response = api_client.get("/otx/status")
        assert response.status_code == 200
        data = response.json()
        assert "mode" in data
        assert data["mode"] in ["live", "demo"]

    def test_otx_latest(self, api_client):
        """OTX latest pulses returns data."""
        response = api_client.get("/otx/latest", params={"limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert "pulses" in data


# ═══════════════════════════════════════════════════════════════
# Search
# ═══════════════════════════════════════════════════════════════

class TestSearch:
    """Test search endpoint."""

    def test_search_indicator(self, api_client):
        """Search returns structured results."""
        response = api_client.get("/search", params={"q": "192.168.1.1"})
        assert response.status_code == 200
        data = response.json()
        assert "total_results" in data
        assert "query_type" in data
        assert "local_results" in data


# ═══════════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════════

class TestModels:
    """Test database models."""

    def test_user_model(self, db_session):
        """User model creates correctly."""
        from backend.models import User
        from backend.auth import hash_password

        user = User(
            username="model_test_user",
            email="model@test.local",
            hashed_password=hash_password("test123"),
            role="user",
        )
        db_session.add(user)
        db_session.flush()

        assert user.id is not None
        assert user.username == "model_test_user"
        assert user.role == "user"

    def test_threat_model(self, db_session):
        """Threat model creates correctly."""
        import json
        from backend.models import Threat

        threat = Threat(
            title="Model Test Threat",
            indicator="10.10.10.10",
            indicator_type="IPv4",
            severity="High",
            description="Testing model creation.",
            source="Community",
            status="Pending",
            risk_score=7.5,
            tags=json.dumps(["test"]),
        )
        db_session.add(threat)
        db_session.flush()

        assert threat.id is not None
        assert threat.title == "Model Test Threat"
        assert threat.severity == "High"


# ═══════════════════════════════════════════════════════════════
# Auth Utilities
# ═══════════════════════════════════════════════════════════════

class TestAuthUtils:
    """Test authentication utility functions."""

    def test_hash_password(self):
        """Password hashing produces valid bcrypt hash."""
        from backend.auth import hash_password
        hashed = hash_password("testpassword")
        assert hashed.startswith("$2")
        assert len(hashed) > 50

    def test_verify_password(self):
        """Password verification works correctly."""
        from backend.auth import hash_password, verify_password
        hashed = hash_password("correctpassword")
        assert verify_password("correctpassword", hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_create_access_token(self):
        """JWT token creation returns a string."""
        from backend.auth import create_access_token
        token = create_access_token(data={"sub": "testuser"})
        assert isinstance(token, str)
        assert len(token) > 20
