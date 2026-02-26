"""
Integration, Audit, and Security models.

Covers: external integrations, audit trail, RBAC, API keys, tags, addresses.
"""

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey,
    Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin


# ═══════════════════════════════════════════════════════════════
# AUDIT TRAIL
# ═══════════════════════════════════════════════════════════════

class AuditLog(Base, TimestampMixin, TenantMixin):
    """Immutable audit trail for all entity changes."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(20), nullable=False, index=True)  # create, update, delete, view, export
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=True, index=True)
    changes_json = Column(Text, nullable=True)  # JSON diff of old → new
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<AuditLog({self.action} {self.entity_type}:{self.entity_id})>"


# ═══════════════════════════════════════════════════════════════
# RBAC (Role-Based Access Control)
# ═══════════════════════════════════════════════════════════════

class Permission(Base, TimestampMixin, TenantMixin):
    """Granular permission definition."""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    codename = Column(String(100), nullable=False, index=True)  # e.g. "deals.create", "invoices.approve"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    module = Column(String(50), nullable=False, index=True)  # deals, finance, projects, admin

    __table_args__ = (
        UniqueConstraint("codename", "tenant_id", name="uq_permission_codename_tenant"),
    )

    def __repr__(self) -> str:
        return f"<Permission({self.codename})>"


class RolePermission(Base, TimestampMixin, TenantMixin):
    """Many-to-many: role ↔ permission."""
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(50), nullable=False, index=True)  # admin, advisor, analyst, read_only
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False, index=True)

    permission = relationship("Permission")

    __table_args__ = (
        UniqueConstraint("role", "permission_id", "tenant_id", name="uq_role_permission"),
    )

    def __repr__(self) -> str:
        return f"<RolePermission(role='{self.role}', perm={self.permission_id})>"


# ═══════════════════════════════════════════════════════════════
# API KEY MANAGEMENT
# ═══════════════════════════════════════════════════════════════

class ApiKey(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """API key for external integrations."""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True)
    scopes = Column(Text, nullable=True)  # JSON array of allowed scopes
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<ApiKey(name='{self.name}')>"


# ═══════════════════════════════════════════════════════════════
# TAGGING & CATEGORIZATION
# ═══════════════════════════════════════════════════════════════

class Tag(Base, TimestampMixin, TenantMixin):
    """Reusable tag for categorizing entities."""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    color = Column(String(7), default="#6B7280")
    category = Column(String(50), nullable=True)  # sector, deal_type, priority, custom

    __table_args__ = (
        UniqueConstraint("name", "tenant_id", name="uq_tag_name_tenant"),
    )

    def __repr__(self) -> str:
        return f"<Tag({self.name})>"


class EntityTag(Base, TimestampMixin, TenantMixin):
    """Polymorphic many-to-many: entity ↔ tag."""
    __tablename__ = "entity_tags"

    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # company, contact, deal, etc.
    entity_id = Column(Integer, nullable=False, index=True)

    tag = relationship("Tag")

    __table_args__ = (
        UniqueConstraint("tag_id", "entity_type", "entity_id", "tenant_id", name="uq_entity_tag"),
    )

    def __repr__(self) -> str:
        return f"<EntityTag(tag={self.tag_id}, {self.entity_type}:{self.entity_id})>"


# ═══════════════════════════════════════════════════════════════
# ADDRESS BOOK
# ═══════════════════════════════════════════════════════════════

class Address(Base, TimestampMixin, TenantMixin, UUIDMixin):
    """Structured address for company/contact/vendor."""
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    address_type = Column(String(20), default="office")  # office, billing, shipping, registered
    line1 = Column(String(255), nullable=False)
    line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(2), nullable=False)  # ISO 3166-1 alpha-2
    is_primary = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<Address({self.city}, {self.country})>"


# ═══════════════════════════════════════════════════════════════
# CUSTOM FIELDS
# ═══════════════════════════════════════════════════════════════

class CustomFieldDefinition(Base, TimestampMixin, TenantMixin):
    """User-defined custom field schema."""
    __tablename__ = "custom_field_definitions"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # company, contact, deal
    field_name = Column(String(100), nullable=False)
    field_type = Column(String(20), nullable=False)  # text, number, date, select, boolean
    options_json = Column(Text, nullable=True)  # For select type: JSON array of options
    is_required = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<CustomFieldDefinition({self.field_name} on {self.entity_type})>"


class CustomFieldValue(Base, TimestampMixin, TenantMixin):
    """Stored value of a custom field on an entity."""
    __tablename__ = "custom_field_values"

    id = Column(Integer, primary_key=True, index=True)
    definition_id = Column(Integer, ForeignKey("custom_field_definitions.id"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    value_text = Column(Text, nullable=True)
    value_number = Column(Integer, nullable=True)
    value_date = Column(DateTime(timezone=True), nullable=True)
    value_boolean = Column(Boolean, nullable=True)

    definition = relationship("CustomFieldDefinition")

    def __repr__(self) -> str:
        return f"<CustomFieldValue(def={self.definition_id}, {self.entity_type}:{self.entity_id})>"


# ═══════════════════════════════════════════════════════════════
# EXTERNAL INTEGRATION SYNC
# ═══════════════════════════════════════════════════════════════

class IntegrationConfig(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """External integration configuration (Pipedrive, HubSpot, etc.)."""
    __tablename__ = "integration_configs"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False, index=True)  # pipedrive, hubspot, salesforce, microsoft
    config_json = Column(Text, nullable=True)  # API keys, tokens, settings (encrypted at rest)
    is_active = Column(Boolean, default=True)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_status = Column(String(20), default="idle")  # idle, running, error

    def __repr__(self) -> str:
        return f"<IntegrationConfig({self.provider}, active={self.is_active})>"


class SyncLog(Base, TimestampMixin, TenantMixin):
    """Log of external sync operations."""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integration_configs.id"), nullable=False, index=True)
    sync_type = Column(String(50), nullable=False)  # full, incremental, webhook
    status = Column(String(20), nullable=False, index=True)  # success, partial, error
    records_synced = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    error_details = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    integration = relationship("IntegrationConfig")

    def __repr__(self) -> str:
        return f"<SyncLog(integration={self.integration_id}, status='{self.status}')>"
