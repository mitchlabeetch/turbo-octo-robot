"""
Deal management models: Deal lifecycle, pipeline stages, buyer lists, bids.

The Deal is the central entity of the M&A workflow. Each deal moves through
a configurable 12-stage lifecycle from origination to post-closing.
"""

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum, Float, ForeignKey,
    Integer, Numeric, String, Text,
)
from sqlalchemy.orm import relationship

from app.models.base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin


class DealStage(Base, TimestampMixin, TenantMixin):
    """Configurable deal stage definitions. Seeded with M&A-standard stages."""
    __tablename__ = "deal_stages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=True)
    default_probability = Column(Float, default=0.0)
    color = Column(String(7), default="#6B7280")  # Hex color for Kanban
    is_won = Column(Boolean, default=False)
    is_lost = Column(Boolean, default=False)

    deals = relationship("Deal", back_populates="stage", lazy="noload")

    def __repr__(self) -> str:
        return f"<DealStage(id={self.id}, name='{self.name}')>"


class Deal(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """
    Core deal entity representing an M&A mandate/engagement.

    Tracks the full lifecycle from origination through post-closing,
    with financial metrics, team assignments, and activity history.
    """
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)

    # ── Identity ─────────────────────────────────────────────
    title = Column(String(255), nullable=False, index=True)
    deal_type = Column(String(50), nullable=False, index=True)  # sell-side, buy-side, fundraise, restructuring
    description = Column(Text, nullable=True)
    reference_code = Column(String(50), unique=True, nullable=True, index=True)  # e.g. "MA-2026-042"

    # ── Pipeline ─────────────────────────────────────────────
    stage_id = Column(Integer, ForeignKey("deal_stages.id"), nullable=True, index=True)
    probability = Column(Float, default=0.0)  # 0.0 to 1.0
    priority = Column(String(20), default="medium", index=True)  # low, medium, high, critical

    # ── Financials ───────────────────────────────────────────
    target_value = Column(Numeric(precision=18, scale=2), nullable=True)
    currency = Column(String(3), default="EUR")
    retainer_fee = Column(Numeric(precision=12, scale=2), nullable=True)
    success_fee_pct = Column(Float, nullable=True)  # Lehman scale or custom %
    expected_revenue = Column(Numeric(precision=14, scale=2), nullable=True)

    # ── Dates ────────────────────────────────────────────────
    expected_close_date = Column(Date, nullable=True, index=True)
    actual_close_date = Column(Date, nullable=True)
    engagement_start_date = Column(Date, nullable=True)

    # ── Relations ────────────────────────────────────────────
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    lead_contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # ── Metadata ─────────────────────────────────────────────
    sector = Column(String(100), nullable=True, index=True)
    source = Column(String(100), nullable=True)  # referral, direct, repeat client
    loss_reason = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    # ── Relationships ────────────────────────────────────────
    stage = relationship("DealStage", back_populates="deals", lazy="joined")
    company = relationship("Company", lazy="joined")
    lead_contact = relationship("Contact", lazy="joined")
    owner = relationship("User", lazy="joined")
    team_members = relationship("DealTeamMember", back_populates="deal", lazy="selectin", cascade="all, delete-orphan")
    activities = relationship("DealActivity", back_populates="deal", lazy="noload", cascade="all, delete-orphan")
    notes_list = relationship("DealNote", back_populates="deal", lazy="noload", cascade="all, delete-orphan")
    buyer_lists = relationship("BuyerList", back_populates="deal", lazy="noload", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Deal(id={self.id}, title='{self.title}', stage='{self.stage_id}')>"


class DealTeamMember(Base, TimestampMixin, TenantMixin):
    """Tracks team member assignments and roles within a deal."""
    __tablename__ = "deal_team_members"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # lead_advisor, analyst, associate, support
    allocation_pct = Column(Float, default=100.0)  # % of time allocated

    deal = relationship("Deal", back_populates="team_members")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<DealTeamMember(deal={self.deal_id}, user={self.user_id}, role='{self.role}')>"


class DealActivity(Base, TimestampMixin, TenantMixin):
    """Automated activity log for deal lifecycle events."""
    __tablename__ = "deal_activities"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    activity_type = Column(String(50), nullable=False, index=True)  # stage_change, note_added, document_uploaded, etc.
    description = Column(Text, nullable=False)
    old_value = Column(String(255), nullable=True)
    new_value = Column(String(255), nullable=True)

    deal = relationship("Deal", back_populates="activities")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<DealActivity(deal={self.deal_id}, type='{self.activity_type}')>"


class DealNote(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """Internal deal notes with @mention support."""
    __tablename__ = "deal_notes"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    mentioned_user_ids = Column(Text, nullable=True)  # JSON array of user IDs

    deal = relationship("Deal", back_populates="notes_list")
    author = relationship("User")

    def __repr__(self) -> str:
        return f"<DealNote(deal={self.deal_id}, author={self.author_id})>"


class BuyerList(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """Target buyer/seller list for a deal."""
    __tablename__ = "buyer_lists"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    list_type = Column(String(50), nullable=False, index=True)  # buyers, sellers, investors
    description = Column(Text, nullable=True)

    deal = relationship("Deal", back_populates="buyer_lists")
    entries = relationship("BuyerListEntry", back_populates="buyer_list", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<BuyerList(deal={self.deal_id}, name='{self.name}')>"


class BuyerListEntry(Base, TimestampMixin, TenantMixin):
    """Individual entry in a buyer/seller list."""
    __tablename__ = "buyer_list_entries"

    id = Column(Integer, primary_key=True, index=True)
    buyer_list_id = Column(Integer, ForeignKey("buyer_lists.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True)
    status = Column(String(50), default="identified", index=True)  # identified, contacted, interested, passed, nda_signed, bid_submitted
    priority = Column(String(20), default="medium")
    notes = Column(Text, nullable=True)
    contacted_at = Column(DateTime(timezone=True), nullable=True)
    response_at = Column(DateTime(timezone=True), nullable=True)

    buyer_list = relationship("BuyerList", back_populates="entries")
    company = relationship("Company")
    contact = relationship("Contact")

    def __repr__(self) -> str:
        return f"<BuyerListEntry(list={self.buyer_list_id}, status='{self.status}')>"


class Bid(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """Tracks indicative and binding bids on a deal."""
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False, index=True)
    bidder_company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    bid_type = Column(String(50), nullable=False, index=True)  # indicative, binding, revised
    amount = Column(Numeric(precision=18, scale=2), nullable=True)
    currency = Column(String(3), default="EUR")
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="pending", index=True)  # pending, accepted, rejected, withdrawn, expired
    conditions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    deal = relationship("Deal")
    bidder = relationship("Company")

    def __repr__(self) -> str:
        return f"<Bid(deal={self.deal_id}, type='{self.bid_type}', amount={self.amount})>"
