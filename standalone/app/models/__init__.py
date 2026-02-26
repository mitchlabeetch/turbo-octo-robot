"""
M&A Advisory CRM+ERP — Data Models Package.

All SQLAlchemy ORM models are organized in sub-modules:
  - base:   Shared mixins (timestamps, soft-delete, multi-tenant)
  - crm:    Company, Contact, Interaction
  - docs:   Document, DocumentShare, AccessLog
  - auth:   User, Role
  - deals:  (Phase 2)
  - finance: (Phase 3)
"""

from app.models.base import Base, TimestampMixin, SoftDeleteMixin, TenantMixin
from app.models.crm import Company, Contact, Interaction
from app.models.docs import Document, DocumentShare, AccessLog
from app.models.auth import User
from app.models.deals import (
    Deal, DealStage, DealTeamMember, DealActivity, DealNote,
    BuyerList, BuyerListEntry, Bid,
)
from app.models.finance import (
    Currency, ExchangeRate, FiscalYear, FiscalPeriod,
    Account, JournalEntry, JournalEntryLine,
    Invoice, InvoiceLine, Payment,
    Vendor, Bill, BillLine,
    ExpenseReport, ExpenseItem,
)
from app.models.projects import Project, Task, TimeEntry
from app.models.workflows import (
    WorkflowTemplate, WorkflowState, WorkflowTransition, WorkflowInstance,
)
from app.models.reporting import (
    ReportDefinition, Dashboard, DashboardWidget, Notification,
)
from app.models.integrations import (
    AuditLog, Permission, RolePermission, ApiKey,
    Tag, EntityTag, Address,
    CustomFieldDefinition, CustomFieldValue,
    IntegrationConfig, SyncLog,
)

__all__ = [
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "TenantMixin",
    "Company",
    "Contact",
    "Interaction",
    "Document",
    "DocumentShare",
    "AccessLog",
    "User",
    "Deal",
    "DealStage",
    "DealTeamMember",
    "DealActivity",
    "DealNote",
    "BuyerList",
    "BuyerListEntry",
    "Bid",
    "Currency",
    "ExchangeRate",
    "FiscalYear",
    "FiscalPeriod",
    "Account",
    "JournalEntry",
    "JournalEntryLine",
    "Invoice",
    "InvoiceLine",
    "Payment",
    "Vendor",
    "Bill",
    "BillLine",
    "ExpenseReport",
    "ExpenseItem",
    "Project",
    "Task",
    "TimeEntry",
    "WorkflowTemplate",
    "WorkflowState",
    "WorkflowTransition",
    "WorkflowInstance",
    "ReportDefinition",
    "Dashboard",
    "DashboardWidget",
    "Notification",
    "AuditLog",
    "Permission",
    "RolePermission",
    "ApiKey",
    "Tag",
    "EntityTag",
    "Address",
    "CustomFieldDefinition",
    "CustomFieldValue",
    "IntegrationConfig",
    "SyncLog",
]
