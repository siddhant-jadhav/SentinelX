"""
SentinelX Configuration
Loads environment variables and provides application settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sentinelx.db")

    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "sentinelx-super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # AlienVault OTX
    OTX_API_KEY: str = os.getenv("OTX_API_KEY", "")
    OTX_BASE_URL: str = "https://otx.alienvault.com/api/v1"

    # Backend
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8003
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8003")

    # App
    APP_NAME: str = "SentinelX"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Default Admin Credentials (for seeding)
    DEFAULT_ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "SentinelX@2024")
    DEFAULT_ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@sentinelx.local")

    # Default User Credentials (for seeding)
    DEFAULT_USER_USERNAME: str = os.getenv("ANALYST_USERNAME", "analyst")
    DEFAULT_USER_PASSWORD: str = os.getenv("ANALYST_PASSWORD", "analyst123")
    DEFAULT_USER_EMAIL: str = os.getenv("ANALYST_EMAIL", "analyst@sentinelx.local")


settings = Settings()
