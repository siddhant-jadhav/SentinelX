"""
SentinelX API Client
HTTP client for communicating with the FastAPI backend.
"""
import os
import httpx
import streamlit as st
from typing import Optional

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8003")
TIMEOUT = 15.0


def _get_headers() -> dict:
    """Get request headers with optional JWT token."""
    headers = {"Content-Type": "application/json"}
    token = st.session_state.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _handle_response(response: httpx.Response) -> dict:
    """Handle API response with error checking."""
    if response.status_code == 204:
        return {"success": True}
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", "Unknown error")
        except Exception:
            detail = response.text
        return {"error": True, "detail": detail, "status_code": response.status_code}
    return response.json()


# ── Auth ─────────────────────────────────────────────────────────

def login(username: str, password: str) -> dict:
    """Authenticate and get JWT token."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                f"{BACKEND_URL}/auth/login",
                json={"username": username, "password": password},
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": f"Connection error: {str(e)}"}


def register(username: str, email: str, password: str) -> dict:
    """Register a new user account."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                f"{BACKEND_URL}/auth/register",
                json={"username": username, "email": email, "password": password},
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": f"Connection error: {str(e)}"}


def get_me() -> dict:
    """Get current user profile."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(
                f"{BACKEND_URL}/auth/me",
                headers=_get_headers(),
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": str(e)}


# ── Threats ──────────────────────────────────────────────────────

def get_threats(
    source: Optional[str] = None,
    severity: Optional[str] = None,
    indicator_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Get paginated list of threats."""
    try:
        params = {"page": page, "limit": limit}
        if source:
            params["source"] = source
        if severity:
            params["severity"] = severity
        if indicator_type:
            params["indicator_type"] = indicator_type
        if status:
            params["status"] = status
        if search:
            params["search"] = search

        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(
                f"{BACKEND_URL}/threats",
                params=params,
                headers=_get_headers(),
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": str(e)}


def get_threat(threat_id: int) -> dict:
    """Get a single threat by ID."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(
                f"{BACKEND_URL}/threats/{threat_id}",
                headers=_get_headers(),
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": str(e)}


def create_threat(data: dict) -> dict:
    """Submit a new threat."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                f"{BACKEND_URL}/threats",
                json=data,
                headers=_get_headers(),
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": str(e)}


def update_threat(threat_id: int, data: dict) -> dict:
    """Update a threat (admin only)."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.put(
                f"{BACKEND_URL}/threats/{threat_id}",
                json=data,
                headers=_get_headers(),
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": str(e)}


def delete_threat(threat_id: int) -> dict:
    """Delete a threat (admin only)."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.delete(
                f"{BACKEND_URL}/threats/{threat_id}",
                headers=_get_headers(),
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": str(e)}


# ── Search ───────────────────────────────────────────────────────

def search_indicators(query: str, indicator_type: Optional[str] = None) -> dict:
    """Search for threat indicators."""
    try:
        params = {"q": query}
        if indicator_type:
            params["indicator_type"] = indicator_type

        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(
                f"{BACKEND_URL}/search",
                params=params,
                headers=_get_headers(),
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": str(e)}


# ── OTX ──────────────────────────────────────────────────────────

def get_otx_latest(limit: int = 20) -> dict:
    """Get latest OTX pulses."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(
                f"{BACKEND_URL}/otx/latest",
                params={"limit": limit},
                headers=_get_headers(),
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": str(e)}


def sync_otx(limit: int = 20) -> dict:
    """Sync OTX pulses to local DB (admin)."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                f"{BACKEND_URL}/otx/sync",
                params={"limit": limit},
                headers=_get_headers(),
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": str(e)}


def get_otx_status() -> dict:
    """Check OTX API connection status."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(f"{BACKEND_URL}/otx/status")
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": str(e)}


# ── Analytics ────────────────────────────────────────────────────

def get_analytics_overview() -> dict:
    """Get analytics overview data."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(
                f"{BACKEND_URL}/analytics/overview",
                headers=_get_headers(),
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": str(e)}


def get_analytics_trends(days: int = 30) -> dict:
    """Get daily threat trends."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(
                f"{BACKEND_URL}/analytics/trends",
                params={"days": days},
                headers=_get_headers(),
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": str(e)}


def get_community_stats() -> dict:
    """Get community statistics."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.get(
                f"{BACKEND_URL}/analytics/community",
                headers=_get_headers(),
            )
            return _handle_response(response)
    except Exception as e:
        return {"error": True, "detail": str(e)}
