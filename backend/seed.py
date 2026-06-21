"""
SentinelX Database Seeding Script
Creates default users and sample threat data on first run.
"""
import json
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from backend.database import SessionLocal, init_db
from backend.models import User, Threat
from backend.auth import hash_password
from backend.config import settings


def seed_database():
    """Seed the database with initial data."""
    init_db()
    db = SessionLocal()

    try:
        _seed_users(db)
        _seed_threats(db)
        print("[SEED] Database seeding completed successfully!")
    except Exception as e:
        print(f"[SEED] Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


def _seed_users(db: Session):
    """Create default admin and analyst accounts."""
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.username == settings.DEFAULT_ADMIN_USERNAME).first()
    if existing_admin:
        print("[SEED] Users already seeded, skipping...")
        return

    admin = User(
        username=settings.DEFAULT_ADMIN_USERNAME,
        email=settings.DEFAULT_ADMIN_EMAIL,
        hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
        role="admin",
    )
    db.add(admin)

    analyst = User(
        username=settings.DEFAULT_USER_USERNAME,
        email=settings.DEFAULT_USER_EMAIL,
        hashed_password=hash_password(settings.DEFAULT_USER_PASSWORD),
        role="user",
    )
    db.add(analyst)

    db.commit()
    print(f"[SEED] Created admin user: {settings.DEFAULT_ADMIN_USERNAME}")
    print(f"[SEED] Created analyst user: {settings.DEFAULT_USER_USERNAME}")


def _seed_threats(db: Session):
    """Create sample threat data."""
    existing = db.query(Threat).count()
    if existing > 0:
        print(f"[SEED] Threats already seeded ({existing} existing), skipping...")
        return

    now = datetime.now(timezone.utc)
    threats_data = [
        # OTX sourced threats
        {
            "title": "APT28 Fancy Bear - Government Sector Targeting",
            "indicator": "185.141.63.120",
            "indicator_type": "IPv4",
            "severity": "Critical",
            "description": "Russian state-sponsored group APT28 (Fancy Bear) conducting espionage campaigns against government entities. Multiple C2 servers identified using custom malware frameworks.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/apt28-fancy-bear",
            "risk_score": 9.8,
            "tags": ["APT28", "nation-state", "espionage", "government"],
            "created_at": now - timedelta(days=1),
        },
        {
            "title": "Conti Ransomware Infrastructure",
            "indicator": "conti-news.onion",
            "indicator_type": "Domain",
            "severity": "Critical",
            "description": "Conti ransomware group infrastructure including leak sites and C2 domains. Active exploitation of ProxyShell and Log4j vulnerabilities for initial access.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/conti-ransomware",
            "risk_score": 9.5,
            "tags": ["ransomware", "Conti", "double-extortion"],
            "created_at": now - timedelta(days=2),
        },
        {
            "title": "Cobalt Strike Team Server Detection",
            "indicator": "45.77.65.211",
            "indicator_type": "IPv4",
            "severity": "High",
            "description": "Detected Cobalt Strike team server with identifiable JARM fingerprint. Beacon configuration indicates targeting of financial sector organizations.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/cobalt-strike-ts",
            "risk_score": 7.8,
            "tags": ["cobalt-strike", "C2", "financial"],
            "created_at": now - timedelta(days=3),
        },
        {
            "title": "TrickBot Banking Trojan C2",
            "indicator": "103.232.55.175",
            "indicator_type": "IPv4",
            "severity": "High",
            "description": "TrickBot banking trojan command and control infrastructure. Module delivery servers for web injects targeting major banking applications.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/trickbot-c2",
            "risk_score": 7.5,
            "tags": ["trojan", "TrickBot", "banking", "botnet"],
            "created_at": now - timedelta(days=4),
        },
        {
            "title": "Log4Shell CVE-2021-44228 Exploitation",
            "indicator": "198.71.233.87",
            "indicator_type": "IPv4",
            "severity": "Critical",
            "description": "Active exploitation of Apache Log4j2 RCE vulnerability (CVE-2021-44228). Scanning infrastructure deploying cryptocurrency miners and reverse shells.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/log4shell",
            "risk_score": 9.9,
            "tags": ["CVE-2021-44228", "Log4Shell", "RCE", "critical"],
            "created_at": now - timedelta(days=5),
        },
        {
            "title": "SolarWinds SUNBURST Backdoor",
            "indicator": "avsvmcloud.com",
            "indicator_type": "Domain",
            "severity": "Critical",
            "description": "Domain used for DNS-based C2 communication by SUNBURST backdoor embedded in trojanized SolarWinds Orion updates. Part of major supply chain compromise.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/sunburst",
            "risk_score": 9.7,
            "tags": ["APT29", "supply-chain", "SolarWinds", "SUNBURST"],
            "created_at": now - timedelta(days=7),
        },
        {
            "title": "Emotet Epoch 5 Infrastructure",
            "indicator": "185.142.236.163",
            "indicator_type": "IPv4",
            "severity": "High",
            "description": "Emotet botnet Epoch 5 C2 server. Delivering Cobalt Strike beacons as secondary payload. Known to facilitate ransomware deployment.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/emotet-e5",
            "risk_score": 8.0,
            "tags": ["Emotet", "botnet", "malware-distribution"],
            "created_at": now - timedelta(days=8),
        },
        {
            "title": "Magecart Skimming Domain",
            "indicator": "cdn-analytics.cloud",
            "indicator_type": "Domain",
            "severity": "Medium",
            "description": "Domain hosting JavaScript payment card skimming code injected into compromised e-commerce websites. Magecart Group 7 attribution.",
            "source": "OTX",
            "status": "Approved",
            "reference_url": "https://otx.alienvault.com/pulse/magecart",
            "risk_score": 6.0,
            "tags": ["magecart", "skimming", "e-commerce", "financial"],
            "created_at": now - timedelta(days=10),
        },
        # Community submitted threats
        {
            "title": "Suspicious Brute Force Source IP",
            "indicator": "92.118.160.50",
            "indicator_type": "IPv4",
            "severity": "Medium",
            "description": "IP address observed conducting SSH brute force attacks against honeypot infrastructure. Over 50,000 login attempts in 24 hours targeting common usernames.",
            "source": "Community",
            "status": "Approved",
            "reference_url": "",
            "risk_score": 5.5,
            "tags": ["brute-force", "SSH", "honeypot"],
            "created_at": now - timedelta(days=1),
            "submitted_by": 2,
        },
        {
            "title": "Phishing Domain - Microsoft Login Clone",
            "indicator": "microsft-secure-login.com",
            "indicator_type": "Domain",
            "severity": "High",
            "description": "Newly registered domain hosting convincing Microsoft 365 login page clone. Credential harvesting via PHP backend with Telegram exfiltration.",
            "source": "Community",
            "status": "Approved",
            "reference_url": "https://urlscan.io/result/example",
            "risk_score": 7.0,
            "tags": ["phishing", "Microsoft365", "credential-theft"],
            "created_at": now - timedelta(days=2),
            "submitted_by": 2,
        },
        {
            "title": "CryptoMiner Binary - XMRig Variant",
            "indicator": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
            "indicator_type": "FileHash-MD5",
            "severity": "Medium",
            "description": "Modified XMRig cryptocurrency miner binary deployed via compromised WordPress sites. Uses process hollowing and persistence via scheduled tasks.",
            "source": "Community",
            "status": "Approved",
            "reference_url": "",
            "risk_score": 5.0,
            "tags": ["cryptominer", "XMRig", "WordPress"],
            "created_at": now - timedelta(days=3),
            "submitted_by": 2,
        },
        {
            "title": "Data Exfiltration C2 Tunnel",
            "indicator": "dns-tunnel.malicious-infra.net",
            "indicator_type": "Domain",
            "severity": "High",
            "description": "Domain used for DNS tunneling-based data exfiltration. Iodine DNS tunnel tool configuration detected in captured network traffic.",
            "source": "Community",
            "status": "Approved",
            "reference_url": "",
            "risk_score": 7.2,
            "tags": ["DNS-tunneling", "exfiltration", "C2"],
            "created_at": now - timedelta(days=4),
            "submitted_by": 2,
        },
        {
            "title": "Malicious PDF Dropper",
            "indicator": "f47ac10b58cc4372a5670e02b2c3d479aabbccdd",
            "indicator_type": "FileHash-SHA1",
            "severity": "Medium",
            "description": "Weaponized PDF file exploiting Adobe Reader vulnerability to drop second-stage RAT payload. Distributed via targeted spear-phishing emails.",
            "source": "Community",
            "status": "Approved",
            "reference_url": "",
            "risk_score": 5.8,
            "tags": ["malicious-document", "PDF", "dropper", "RAT"],
            "created_at": now - timedelta(days=6),
            "submitted_by": 2,
        },
        # Pending community submissions
        {
            "title": "Suspicious C2 Beacon Activity",
            "indicator": "beacon-relay.ddns.net",
            "indicator_type": "Domain",
            "severity": "High",
            "description": "Dynamic DNS domain exhibiting periodic beaconing behavior consistent with C2 communication. Needs further analysis and correlation.",
            "source": "Community",
            "status": "Pending",
            "reference_url": "",
            "risk_score": 6.5,
            "tags": ["C2", "beacon", "DDNS"],
            "created_at": now - timedelta(hours=6),
            "submitted_by": 2,
        },
        {
            "title": "Possible DGA Domain",
            "indicator": "xkr9f2m4p7.com",
            "indicator_type": "Domain",
            "severity": "Medium",
            "description": "Domain matching known DGA (Domain Generation Algorithm) patterns. May be associated with botnet C2 infrastructure.",
            "source": "Community",
            "status": "Pending",
            "reference_url": "",
            "risk_score": 4.5,
            "tags": ["DGA", "botnet", "suspicious"],
            "created_at": now - timedelta(hours=3),
            "submitted_by": 2,
        },
        {
            "title": "Port Scanning Source",
            "indicator": "172.16.254.1",
            "indicator_type": "IPv4",
            "severity": "Low",
            "description": "IP address performing systematic port scans across enterprise network ranges. Likely reconnaissance activity.",
            "source": "Community",
            "status": "Pending",
            "reference_url": "",
            "risk_score": 3.0,
            "tags": ["scanning", "reconnaissance"],
            "created_at": now - timedelta(hours=1),
            "submitted_by": 2,
        },
        # Rejected
        {
            "title": "False Positive - Google DNS",
            "indicator": "8.8.8.8",
            "indicator_type": "IPv4",
            "severity": "Info",
            "description": "Google Public DNS server incorrectly flagged as suspicious. This is a legitimate Google service.",
            "source": "Community",
            "status": "Rejected",
            "reference_url": "",
            "risk_score": 0.5,
            "tags": ["false-positive", "DNS"],
            "created_at": now - timedelta(days=5),
            "submitted_by": 2,
        },
    ]

    for data in threats_data:
        threat = Threat(
            title=data["title"],
            indicator=data["indicator"],
            indicator_type=data["indicator_type"],
            severity=data["severity"],
            description=data["description"],
            source=data["source"],
            status=data["status"],
            reference_url=data.get("reference_url", ""),
            risk_score=data["risk_score"],
            tags=json.dumps(data.get("tags", [])),
            submitted_by=data.get("submitted_by"),
            created_at=data.get("created_at", now),
        )
        db.add(threat)

    db.commit()
    print(f"[SEED] Created {len(threats_data)} sample threats")


if __name__ == "__main__":
    seed_database()
