"""
Base model infrastructure: declarative base + shared mixins.

Every model inherits from Base and optionally uses:
  - TimestampMixin  → created_at, updated_at (auto-managed)
  - SoftDeleteMixin → is_deleted, deleted_at (soft-delete support)
  - TenantMixin     → tenant_id (row-level multi-tenancy)
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, event
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Declarative base for all models."""
    pass


class TimestampMixin:
    """Adds created_at and updated_at columns with automatic management."""

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SoftDeleteMixin:
    """Adds soft-delete columns. Records are marked deleted, not removed."""

    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def soft_delete(self) -> None:
        """Mark this record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None


class TenantMixin:
    """Adds tenant_id for row-level multi-tenancy isolation."""

    tenant_id = Column(
        String(36),
        nullable=False,
        index=True,
        default="default",
        doc="UUID of the tenant this row belongs to. All queries must be scoped.",
    )


class UUIDMixin:
    """Adds a public-facing UUID alongside the integer primary key."""

    uuid = Column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        index=True,
        doc="Public-facing identifier. Use this in API responses instead of integer PK.",
    )
