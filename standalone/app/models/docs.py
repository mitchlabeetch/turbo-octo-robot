"""
Document management models: Document, DocumentShare, AccessLog.

Migrated from flat models.py with full mixin support.
"""

import os
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin


class Document(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String(255), nullable=False, index=True)
    document_type = Column(String(100), nullable=False, index=True)
    deal_name = Column(String(100), nullable=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    version = Column(Integer, default=1)
    status = Column(String(50), default="Draft", index=True)
    is_confidential = Column(Boolean, default=False)

    # Relationships
    shares = relationship("DocumentShare", back_populates="document", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, name='{self.document_name}')>"


class DocumentShare(Base, TimestampMixin, TenantMixin, UUIDMixin):
    __tablename__ = "document_shares"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    token = Column(String(100), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    access_count = Column(Integer, default=0)
    view_only = Column(Boolean, default=False)
    requires_nda = Column(Boolean, default=False)
    password_hash = Column(String(255), nullable=True)
    nda_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    nda_confirmed_by_email = Column(String(255), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="shares")
    access_logs = relationship("AccessLog", back_populates="share", lazy="selectin")

    @property
    def is_expired(self) -> bool:
        """Check if this share link has expired."""
        if self.expires_at is None:
            return False
        now = datetime.now(timezone.utc)
        # Handle timezone-naive datetimes (e.g. SQLite)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return expires < now

    def __repr__(self) -> str:
        return f"<DocumentShare(id={self.id}, token='{self.token[:8]}...')>"


class AccessLog(Base, TimestampMixin, TenantMixin):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    share_id = Column(Integer, ForeignKey("document_shares.id"), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    action = Column(String(50), nullable=False, index=True)
    accessed_by_email = Column(String(255), nullable=True)

    # Relationships
    share = relationship("DocumentShare", back_populates="access_logs")

    def __repr__(self) -> str:
        return f"<AccessLog(id={self.id}, action='{self.action}')>"
