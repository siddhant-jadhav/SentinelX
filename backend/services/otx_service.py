"""
SentinelX OTX Integration Service
Handles communication with AlienVault OTX API for threat intelligence data.
Uses httpx for HTTP requests with caching to minimize API calls.
"""
import json
import time
from datetime import datetime, timezone
from typing import Optional

import httpx

from backend.config import settings

# Simple in-memory cache
_cache: dict[str, dict] = {}
CACHE_TTL = 300  # 5 minutes


def _get_cached(key: str) -> Optional[dict]:
    """Get cached data if still valid."""
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry["timestamp"] < CACHE_TTL:
            return entry["data"]
        del _cache[key]
    return None


def _set_cache(key: str, data):
    """Store data in cache."""
    _cache[key] = {"data": data, "timestamp": time.time()}


def _otx_headers() -> dict:
    """Get OTX API request headers."""
    headers = {"Accept": "application/json"}
    if settings.OTX_API_KEY:
        headers["X-OTX-API-KEY"] = settings.OTX_API_KEY
    return headers


def is_otx_available() -> bool:
    """Check if OTX API key is configured."""
    return bool(settings.OTX_API_KEY and settings.OTX_API_KEY.strip())


def get_latest_pulses(limit: int = 20) -> list[dict]:
    """
    Fetch latest threat pulses from OTX.
    Falls back to demo data if no API key is configured.
    """
    if not is_otx_available():
        return _get_demo_pulses()

    cache_key = f"latest_pulses_{limit}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        url = f"{settings.OTX_BASE_URL}/pulses/subscribed"
        params = {"limit": limit, "page": 1}

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_otx_headers(), params=params)
            response.raise_for_status()
            data = response.json()

        pulses = data.get("results", [])
        normalized = [_normalize_pulse(p) for p in pulses]
        _set_cache(cache_key, normalized)
        return normalized

    except Exception as e:
        print(f"[OTX] Error fetching pulses: {e}")
        return _get_demo_pulses()


def search_indicator(indicator_type: str, indicator_value: str) -> list[dict]:
    """
    Search OTX for a specific indicator (IP, domain, URL, file hash).

    Args:
        indicator_type: One of IPv4, Domain, URL, FileHash-MD5, FileHash-SHA256
        indicator_value: The actual indicator value to search.

    Returns:
        List of normalized threat results from OTX.
    """
    if not is_otx_available():
        return _get_demo_search_results(indicator_type, indicator_value)

    cache_key = f"search_{indicator_type}_{indicator_value}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    # Map indicator types to OTX API endpoints
    type_map = {
        "IPv4": f"indicators/IPv4/{indicator_value}/general",
        "IPv6": f"indicators/IPv6/{indicator_value}/general",
        "Domain": f"indicators/domain/{indicator_value}/general",
        "Hostname": f"indicators/hostname/{indicator_value}/general",
        "URL": f"indicators/url/{indicator_value}/general",
        "FileHash-MD5": f"indicators/file/{indicator_value}/general",
        "FileHash-SHA1": f"indicators/file/{indicator_value}/general",
        "FileHash-SHA256": f"indicators/file/{indicator_value}/general",
    }

    endpoint = type_map.get(indicator_type)
    if not endpoint:
        return []

    try:
        url = f"{settings.OTX_BASE_URL}/{endpoint}"

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_otx_headers())
            response.raise_for_status()
            data = response.json()

        results = _normalize_indicator_result(data, indicator_type, indicator_value)
        _set_cache(cache_key, results)
        return results

    except Exception as e:
        print(f"[OTX] Error searching indicator: {e}")
        return _get_demo_search_results(indicator_type, indicator_value)


def get_pulse_details(pulse_id: str) -> Optional[dict]:
    """Fetch full details for a specific OTX pulse."""
    if not is_otx_available():
        return None

    cache_key = f"pulse_{pulse_id}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        url = f"{settings.OTX_BASE_URL}/pulses/{pulse_id}"

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=_otx_headers())
            response.raise_for_status()
            data = response.json()

        result = _normalize_pulse(data)
        _set_cache(cache_key, result)
        return result

    except Exception as e:
        print(f"[OTX] Error fetching pulse {pulse_id}: {e}")
        return None


def _normalize_pulse(pulse: dict) -> dict:
    """Normalize an OTX pulse to our standard threat format."""
    indicators = pulse.get("indicators", [])
    indicator_value = indicators[0]["indicator"] if indicators else pulse.get("name", "N/A")
    indicator_type = indicators[0]["type"] if indicators else "Unknown"

    # Calculate severity from pulse metadata
    adversary = pulse.get("adversary", "")
    tlp = pulse.get("tlp", "white")
    severity = _calculate_severity_from_pulse(pulse)

    tags = pulse.get("tags", [])
    if isinstance(tags, list):
        tags = tags[:10]  # Limit tags
    else:
        tags = []

    return {
        "title": pulse.get("name", "Unknown Threat"),
        "indicator": indicator_value,
        "indicator_type": indicator_type,
        "severity": severity,
        "description": pulse.get("description", "")[:2000],
        "source": "OTX",
        "status": "Approved",
        "reference_url": f"https://otx.alienvault.com/pulse/{pulse.get('id', '')}",
        "risk_score": _severity_to_score(severity),
        "tags": tags,
        "created_at": pulse.get("created", datetime.now(timezone.utc).isoformat()),
        "pulse_id": pulse.get("id", ""),
        "indicator_count": len(indicators),
    }


def _normalize_indicator_result(data: dict, indicator_type: str, indicator_value: str) -> list[dict]:
    """Normalize OTX indicator search results."""
    results = []

    # Extract pulse references
    pulse_info = data.get("pulse_info", {})
    pulses = pulse_info.get("pulses", [])

    if pulses:
        for pulse in pulses[:10]:
            results.append({
                "title": pulse.get("name", "OTX Indicator Match"),
                "indicator": indicator_value,
                "indicator_type": indicator_type,
                "severity": _calculate_severity_from_pulse(pulse),
                "description": pulse.get("description", "")[:1000],
                "source": "OTX",
                "reference_url": f"https://otx.alienvault.com/pulse/{pulse.get('id', '')}",
                "risk_score": _severity_to_score(_calculate_severity_from_pulse(pulse)),
                "tags": pulse.get("tags", [])[:5],
                "created_at": pulse.get("created"),
            })
    else:
        # Single result from general endpoint
        results.append({
            "title": f"OTX Analysis: {indicator_value}",
            "indicator": indicator_value,
            "indicator_type": indicator_type,
            "severity": "Info",
            "description": f"OTX general analysis for {indicator_type}: {indicator_value}",
            "source": "OTX",
            "reference_url": "",
            "risk_score": 2.0,
            "tags": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    return results


def _calculate_severity_from_pulse(pulse: dict) -> str:
    """Estimate severity based on pulse metadata."""
    tags = [t.lower() for t in pulse.get("tags", [])] if pulse.get("tags") else []
    adversary = (pulse.get("adversary") or "").lower()
    name = (pulse.get("name") or "").lower()
    description = (pulse.get("description") or "").lower()

    combined = " ".join(tags + [adversary, name, description])

    critical_keywords = ["apt", "ransomware", "zero-day", "0day", "critical", "exploit", "rce", "remote code execution"]
    high_keywords = ["malware", "trojan", "backdoor", "c2", "command and control", "botnet", "high"]
    medium_keywords = ["phishing", "suspicious", "medium", "spam", "scan"]
    low_keywords = ["low", "informational", "benign"]

    if any(k in combined for k in critical_keywords):
        return "Critical"
    elif any(k in combined for k in high_keywords):
        return "High"
    elif any(k in combined for k in medium_keywords):
        return "Medium"
    elif any(k in combined for k in low_keywords):
        return "Low"
    return "Medium"


def _severity_to_score(severity: str) -> float:
    """Convert severity label to numeric risk score."""
    return {
        "Critical": 9.5,
        "High": 7.5,
        "Medium": 5.0,
        "Low": 3.0,
        "Info": 1.0,
    }.get(severity, 5.0)


# ── Demo / Mock Data ────────────────────────────────────────────────────────

def _get_demo_pulses() -> list[dict]:
    """Return realistic demo pulses when OTX API is unavailable."""
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "title": "APT29 Cozy Bear - SolarWinds Supply Chain Attack",
            "indicator": "154.35.175.225",
            "indicator_type": "IPv4",
            "severity": "Critical",
            "description": "Advanced persistent threat group APT29 (Cozy Bear) linked to supply chain compromise of SolarWinds Orion platform. Multiple C2 domains and IP addresses identified.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/demo-apt29",
            "risk_score": 9.8,
            "tags": ["APT29", "supply-chain", "SolarWinds", "nation-state"],
            "created_at": now,
            "pulse_id": "demo-apt29",
            "indicator_count": 47,
        },
        {
            "title": "LockBit 3.0 Ransomware Campaign",
            "indicator": "lockbit3-decryptor.onion",
            "indicator_type": "Domain",
            "severity": "Critical",
            "description": "Latest LockBit 3.0 ransomware strain targeting critical infrastructure. Indicators include ransomware binary hashes and C2 infrastructure.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/demo-lockbit",
            "risk_score": 9.5,
            "tags": ["ransomware", "LockBit", "critical-infrastructure"],
            "created_at": now,
            "pulse_id": "demo-lockbit",
            "indicator_count": 23,
        },
        {
            "title": "Emotet Botnet Resurgence 2024",
            "indicator": "185.142.236.163",
            "indicator_type": "IPv4",
            "severity": "High",
            "description": "Emotet botnet showing renewed activity with updated delivery mechanisms. New C2 servers identified across multiple geographies.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/demo-emotet",
            "risk_score": 8.0,
            "tags": ["botnet", "Emotet", "malware", "banking-trojan"],
            "created_at": now,
            "pulse_id": "demo-emotet",
            "indicator_count": 56,
        },
        {
            "title": "Lazarus Group Cryptocurrency Exchange Targeting",
            "indicator": "exchange-update.serveftp.com",
            "indicator_type": "Domain",
            "severity": "Critical",
            "description": "North Korean threat actor Lazarus Group targeting cryptocurrency exchanges with spear-phishing and watering hole attacks.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/demo-lazarus",
            "risk_score": 9.2,
            "tags": ["APT", "Lazarus", "cryptocurrency", "nation-state"],
            "created_at": now,
            "pulse_id": "demo-lazarus",
            "indicator_count": 31,
        },
        {
            "title": "QakBot Malware Distribution Network",
            "indicator": "e3b0c44298fc1c149afbf4c8996fb924",
            "indicator_type": "FileHash-MD5",
            "severity": "High",
            "description": "QakBot (aka QBot) malware distribution network using thread-hijacking email campaigns with malicious document attachments.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/demo-qakbot",
            "risk_score": 7.8,
            "tags": ["malware", "QakBot", "email", "trojan"],
            "created_at": now,
            "pulse_id": "demo-qakbot",
            "indicator_count": 89,
        },
        {
            "title": "Cobalt Strike Beacon Infrastructure",
            "indicator": "45.77.65.211",
            "indicator_type": "IPv4",
            "severity": "High",
            "description": "Identified Cobalt Strike team servers used in post-exploitation activities. Multiple beacon configurations extracted.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/demo-cobaltstrike",
            "risk_score": 7.5,
            "tags": ["cobalt-strike", "C2", "post-exploitation"],
            "created_at": now,
            "pulse_id": "demo-cobaltstrike",
            "indicator_count": 15,
        },
        {
            "title": "Log4Shell Exploitation Attempts",
            "indicator": "198.71.233.87",
            "indicator_type": "IPv4",
            "severity": "Critical",
            "description": "Ongoing exploitation attempts of CVE-2021-44228 (Log4Shell) vulnerability. New exploitation payloads and scanning infrastructure detected.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/demo-log4shell",
            "risk_score": 9.9,
            "tags": ["CVE-2021-44228", "Log4Shell", "RCE", "critical"],
            "created_at": now,
            "pulse_id": "demo-log4shell",
            "indicator_count": 200,
        },
        {
            "title": "AgentTesla Keylogger Campaign",
            "indicator": "mail.secure-login-portal.com",
            "indicator_type": "Domain",
            "severity": "Medium",
            "description": "AgentTesla keylogger distributed via phishing emails impersonating shipping companies. Exfiltration via SMTP and FTP.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/demo-agenttesla",
            "risk_score": 5.5,
            "tags": ["keylogger", "phishing", "AgentTesla", "infostealer"],
            "created_at": now,
            "pulse_id": "demo-agenttesla",
            "indicator_count": 12,
        },
        {
            "title": "DDoS Amplification Source IPs",
            "indicator": "203.0.113.50",
            "indicator_type": "IPv4",
            "severity": "Medium",
            "description": "IP addresses identified as sources of DNS and NTP amplification DDoS attacks targeting financial institutions.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/demo-ddos",
            "risk_score": 5.0,
            "tags": ["DDoS", "amplification", "DNS", "financial"],
            "created_at": now,
            "pulse_id": "demo-ddos",
            "indicator_count": 340,
        },
        {
            "title": "Phishing Kit - Microsoft 365 Credential Harvesting",
            "indicator": "https://login-microsft365.web.app/signin",
            "indicator_type": "URL",
            "severity": "Medium",
            "description": "Phishing kit hosted on Firebase/web.app infrastructure targeting Microsoft 365 credentials. Evasion techniques include CAPTCHA and geographic filtering.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/demo-phishing365",
            "risk_score": 6.0,
            "tags": ["phishing", "Microsoft365", "credential-harvesting"],
            "created_at": now,
            "pulse_id": "demo-phishing365",
            "indicator_count": 8,
        },
    ]


def _get_demo_search_results(indicator_type: str, indicator_value: str) -> list[dict]:
    """Return demo search results."""
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "title": f"OTX Analysis: {indicator_value}",
            "indicator": indicator_value,
            "indicator_type": indicator_type,
            "severity": "Medium",
            "description": f"Demo analysis result for {indicator_type} indicator: {indicator_value}. In production, this would contain real OTX threat intelligence data.",
            "source": "OTX",
            "reference_url": f"https://otx.alienvault.com/indicator/{indicator_type}/{indicator_value}",
            "risk_score": 5.0,
            "tags": ["demo", indicator_type.lower()],
            "created_at": now,
        }
    ]
