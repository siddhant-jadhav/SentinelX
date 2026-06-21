"""
SentinelX — Test Configuration
Shared fixtures for backend and frontend tests.
"""
import os
import sys
import pytest

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Override environment for testing
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_sentinelx.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-ci")
os.environ.setdefault("OTX_API_KEY", "")
os.environ.setdefault("BACKEND_URL", "http://localhost:8003")
