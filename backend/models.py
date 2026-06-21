"""
SentinelX ORM Models
SQLAlchemy models for threats and users tables.
"""
import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from backend.database import Base


class Threat(Base):
    """Threat intelligence indicator model."""
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    indicator = Column(String(500), nullable=False, index=True)
    indicator_type = Column(
        String(50), nullable=False, index=True,
        comment="IPv4, IPv6, Domain, URL, FileHash-MD5, FileHash-SHA1, FileHash-SHA256, Email, Hostname, CIDR"
    )
    severity = Column(
        String(20), nullable=False, default="Medium", index=True,
        comment="Critical, High, Medium, Low, Info"
    )
    description = Column(Text, nullable=True, default="")
    source = Column(
        String(20), nullable=False, default="Community", index=True,
        comment="OTX or Community"
    )
    status = Column(
        String(20), nullable=False, default="Pending", index=True,
        comment="Pending, Approved, Rejected"
    )
    reference_url = Column(String(500), nullable=True, default="")
    risk_score = Column(Float, nullable=False, default=5.0, comment="0.0 to 10.0")
    tags = Column(Text, nullable=True, default="[]", comment="JSON-encoded list of tags")
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    submitter = relationship("User", back_populates="submitted_threats")

    @property
    def tags_list(self) -> list[str]:
        """Parse JSON tags field into a Python list."""
        try:
            return json.loads(self.tags) if self.tags else []
        except (json.JSONDecodeError, TypeError):
            return []

    @tags_list.setter
    def tags_list(self, value: list[str]):
        self.tags = json.dumps(value)

    def to_dict(self) -> dict:
        """Convert model to dictionary for API responses."""
        return {
            "id": self.id,
            "title": self.title,
            "indicator": self.indicator,
            "indicator_type": self.indicator_type,
            "severity": self.severity,
            "description": self.description,
            "source": self.source,
            "status": self.status,
            "reference_url": self.reference_url,
            "risk_score": self.risk_score,
            "tags": self.tags_list,
            "submitted_by": self.submitted_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class User(Base):
    """User account model for authentication and role-based access."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        String(20), nullable=False, default="user",
        comment="admin or user"
    )
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    submitted_threats = relationship("Threat", back_populates="submitter")

    def to_dict(self) -> dict:
        """Convert model to dictionary (excluding password)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
