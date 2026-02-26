"""
Deal management Pydantic schemas for API request/response validation.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


# ── Deal Stage Schemas ───────────────────────────────────────

class DealStageOut(BaseModel):
    id: int
    name: str
    display_order: int
    description: Optional[str] = None
    default_probability: float
    color: str
    is_won: bool
    is_lost: bool

    class Config:
        from_attributes = True


# ── Deal Schemas ─────────────────────────────────────────────

class DealCreate(BaseModel):
    title: str
    deal_type: str
    description: Optional[str] = None
    reference_code: Optional[str] = None
    stage_id: Optional[int] = None
    probability: float = 0.0
    priority: str = "medium"
    target_value: Optional[Decimal] = None
    currency: str = "EUR"
    retainer_fee: Optional[Decimal] = None
    success_fee_pct: Optional[float] = None
    expected_revenue: Optional[Decimal] = None
    expected_close_date: Optional[date] = None
    engagement_start_date: Optional[date] = None
    company_id: Optional[int] = None
    lead_contact_id: Optional[int] = None
    owner_user_id: Optional[int] = None
    sector: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None


class DealUpdate(BaseModel):
    title: Optional[str] = None
    deal_type: Optional[str] = None
    description: Optional[str] = None
    stage_id: Optional[int] = None
    probability: Optional[float] = None
    priority: Optional[str] = None
    target_value: Optional[Decimal] = None
    currency: Optional[str] = None
    retainer_fee: Optional[Decimal] = None
    success_fee_pct: Optional[float] = None
    expected_revenue: Optional[Decimal] = None
    expected_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    engagement_start_date: Optional[date] = None
    company_id: Optional[int] = None
    lead_contact_id: Optional[int] = None
    owner_user_id: Optional[int] = None
    sector: Optional[str] = None
    source: Optional[str] = None
    loss_reason: Optional[str] = None
    notes: Optional[str] = None


class DealOut(BaseModel):
    id: int
    uuid: str
    title: str
    deal_type: str
    description: Optional[str] = None
    reference_code: Optional[str] = None
    stage: Optional[DealStageOut] = None
    probability: float
    priority: str
    target_value: Optional[Decimal] = None
    currency: str
    retainer_fee: Optional[Decimal] = None
    success_fee_pct: Optional[float] = None
    expected_revenue: Optional[Decimal] = None
    expected_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    engagement_start_date: Optional[date] = None
    company_id: Optional[int] = None
    lead_contact_id: Optional[int] = None
    owner_user_id: Optional[int] = None
    sector: Optional[str] = None
    source: Optional[str] = None
    loss_reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DealListOut(BaseModel):
    items: List[DealOut]
    total: int
    offset: int
    limit: int


# ── Deal Note Schemas ────────────────────────────────────────

class DealNoteCreate(BaseModel):
    content: str
    is_pinned: bool = False


class DealNoteOut(BaseModel):
    id: int
    uuid: str
    deal_id: int
    author_id: int
    content: str
    is_pinned: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Deal Activity Schemas ────────────────────────────────────

class DealActivityOut(BaseModel):
    id: int
    deal_id: int
    user_id: Optional[int] = None
    activity_type: str
    description: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Team Member Schemas ──────────────────────────────────────

class DealTeamMemberCreate(BaseModel):
    user_id: int
    role: str
    allocation_pct: float = 100.0


class DealTeamMemberOut(BaseModel):
    id: int
    deal_id: int
    user_id: int
    role: str
    allocation_pct: float
    created_at: datetime

    class Config:
        from_attributes = True


# ── Buyer List Schemas ───────────────────────────────────────

class BuyerListCreate(BaseModel):
    name: str
    list_type: str
    description: Optional[str] = None


class BuyerListOut(BaseModel):
    id: int
    uuid: str
    deal_id: int
    name: str
    list_type: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BuyerListEntryCreate(BaseModel):
    company_id: Optional[int] = None
    contact_id: Optional[int] = None
    status: str = "identified"
    priority: str = "medium"
    notes: Optional[str] = None


class BuyerListEntryOut(BaseModel):
    id: int
    buyer_list_id: int
    company_id: Optional[int] = None
    contact_id: Optional[int] = None
    status: str
    priority: str
    notes: Optional[str] = None
    contacted_at: Optional[datetime] = None
    response_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Bid Schemas ──────────────────────────────────────────────

class BidCreate(BaseModel):
    bid_type: str
    bidder_company_id: Optional[int] = None
    amount: Optional[Decimal] = None
    currency: str = "EUR"
    conditions: Optional[str] = None
    notes: Optional[str] = None


class BidOut(BaseModel):
    id: int
    uuid: str
    deal_id: int
    bidder_company_id: Optional[int] = None
    bid_type: str
    amount: Optional[Decimal] = None
    currency: str
    submitted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    status: str
    conditions: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Pipeline View ────────────────────────────────────────────

class PipelineStageView(BaseModel):
    """Kanban-style pipeline view data for a single stage."""
    stage: DealStageOut
    deals: List[DealOut]
    total_value: Decimal
    deal_count: int
