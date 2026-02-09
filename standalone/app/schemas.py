from datetime import date
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr


class TenantCreate(BaseModel):
    name: str
    slug: str


class TenantOut(TenantCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AccountCreate(BaseModel):
    name: str
    code: str
    account_type: Literal["Asset", "Liability", "Equity", "Revenue", "Expense"]
    description: Optional[str] = None


class AccountOut(AccountCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    invoice_number: str
    customer_name: str
    currency: str
    total_amount_cents: int
    status: Literal["Draft", "Sent", "Paid", "Overdue", "Cancelled"] = "Draft"
    issued_date: Optional[date] = None
    due_date: Optional[date] = None


class InvoiceOut(InvoiceCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TenantSettingsBase(BaseModel):
    brand_name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None


class TenantSettingsCreate(TenantSettingsBase):
    pass


class TenantSettingsOut(TenantSettingsBase):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyCreate(BaseModel):
    name: str
    company_type: Optional[str] = None
    sector: Optional[str] = None
    annual_revenue: Optional[int] = None
    employee_count: Optional[int] = None


class CompanyOut(CompanyCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    job_title: Optional[str] = None
    decision_maker: bool = False
    company_id: Optional[int] = None


class ContactOut(ContactCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InteractionCreate(BaseModel):
    interaction_type: str
    subject: Optional[str] = None
    notes: Optional[str] = None
    interaction_date: Optional[date] = None
    contact_id: Optional[int] = None
    company_id: Optional[int] = None
    metadata_json: Optional[str] = None


class InteractionOut(InteractionCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    document_name: str
    document_type: str
    deal_name: Optional[str] = None
    status: str = "Draft"
    is_confidential: bool = False


class DocumentOut(DocumentCreate):
    id: int
    file_name: str
    file_path: str
    content_type: Optional[str]
    size_bytes: Optional[int]
    version: int
    created_at: datetime

    class Config:
        from_attributes = True


class ShareCreate(BaseModel):
    expires_in_days: Optional[int] = None
    view_only: bool = False
    requires_nda: bool = False
    password: Optional[str] = None


class ShareOut(BaseModel):
    token: str
    expires_at: Optional[datetime]


class ShareInfo(BaseModel):
    """Info about a share (status, NDA requirements, etc.)"""
    token: str
    document_name: str
    view_only: bool
    requires_nda: bool
    nda_confirmed: bool
    expires_at: Optional[datetime]
    expired: bool


class NDAConfirm(BaseModel):
    """Request to confirm NDA for a share"""
    email: EmailStr


class AccessLogOut(BaseModel):
    """Access event log entry"""
    id: int
    action: str
    accessed_at: datetime
    ip_address: Optional[str]
    accessed_by_email: Optional[str]


class AuditSummary(BaseModel):
    """Summary of access activity"""
    total_access_events: int
    total_views: int
    total_downloads: int
    total_nda_confirmations: int
    most_accessed_documents: list


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "user"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class EmailCaptureIn(BaseModel):
    provider: str
    subject: Optional[str] = None
    body: Optional[str] = None
    contact_email: EmailStr
    contact_first_name: Optional[str] = None
    contact_last_name: Optional[str] = None
    company_name: Optional[str] = None
    interaction_date: Optional[date] = None
    metadata_json: Optional[str] = None


class EmailCaptureOut(BaseModel):
    interaction_id: int
    contact_id: int
    company_id: Optional[int]
