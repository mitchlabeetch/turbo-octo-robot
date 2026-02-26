"""
Deal service: Business logic for deal lifecycle management.

Handles: CRUD, stage transitions, pipeline views, activity logging,
buyer lists, bids, team management, and deal notes.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.deals import (
    Bid, BuyerList, BuyerListEntry, Deal, DealActivity,
    DealNote, DealStage, DealTeamMember,
)
from app.services.base_repository import BaseRepository


# ── Default M&A Deal Stages ─────────────────────────────────
DEFAULT_STAGES = [
    {"name": "Origination", "display_order": 1, "default_probability": 0.05, "color": "#6B7280"},
    {"name": "Preliminary Assessment", "display_order": 2, "default_probability": 0.10, "color": "#8B5CF6"},
    {"name": "Engagement Letter", "display_order": 3, "default_probability": 0.20, "color": "#3B82F6"},
    {"name": "Preparation", "display_order": 4, "default_probability": 0.30, "color": "#06B6D4"},
    {"name": "Marketing", "display_order": 5, "default_probability": 0.40, "color": "#10B981"},
    {"name": "Buyer Screening", "display_order": 6, "default_probability": 0.50, "color": "#84CC16"},
    {"name": "Indicative Offers", "display_order": 7, "default_probability": 0.60, "color": "#EAB308"},
    {"name": "Due Diligence", "display_order": 8, "default_probability": 0.70, "color": "#F59E0B"},
    {"name": "Binding Offers", "display_order": 9, "default_probability": 0.80, "color": "#F97316"},
    {"name": "Negotiation", "display_order": 10, "default_probability": 0.90, "color": "#EF4444"},
    {"name": "Closing", "display_order": 11, "default_probability": 0.95, "color": "#DC2626"},
    {"name": "Post-Closing", "display_order": 12, "default_probability": 1.0, "color": "#059669", "is_won": True},
]


class DealService:
    """Business logic for Deal management and pipeline operations."""

    def __init__(self, db: Session, tenant_id: str = "default"):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = BaseRepository(Deal, db, tenant_id)

    # ── CRUD ─────────────────────────────────────────────────

    def get(self, deal_id: int) -> Optional[Deal]:
        return self.repo.get_by_id(deal_id)

    def get_by_uuid(self, uuid: str) -> Optional[Deal]:
        return self.repo.get_by_uuid(uuid)

    def list(
        self, *,
        offset: int = 0, limit: int = 50,
        stage_id: Optional[int] = None,
        deal_type: Optional[str] = None,
        priority: Optional[str] = None,
        sector: Optional[str] = None,
        owner_user_id: Optional[int] = None,
    ) -> List[Deal]:
        filters = {}
        if stage_id is not None:
            filters["stage_id"] = stage_id
        if deal_type:
            filters["deal_type"] = deal_type
        if priority:
            filters["priority"] = priority
        if sector:
            filters["sector"] = sector
        if owner_user_id is not None:
            filters["owner_user_id"] = owner_user_id
        return self.repo.list(offset=offset, limit=limit, filters=filters)

    def count(self, **filters) -> int:
        return self.repo.count(filters=filters)

    def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Deal:
        deal = self.repo.create(data)
        self._log_activity(deal.id, user_id, "deal_created", f"Deal '{deal.title}' created")
        return deal

    def update(self, deal_id: int, data: Dict[str, Any], user_id: Optional[int] = None) -> Optional[Deal]:
        old_deal = self.get(deal_id)
        if not old_deal:
            return None

        # Track stage changes for activity log
        old_stage_id = old_deal.stage_id
        deal = self.repo.update(deal_id, data)

        if deal and data.get("stage_id") and data["stage_id"] != old_stage_id:
            self._log_activity(
                deal_id, user_id, "stage_change",
                f"Stage changed",
                old_value=str(old_stage_id),
                new_value=str(data["stage_id"]),
            )
        return deal

    def delete(self, deal_id: int) -> bool:
        return self.repo.delete(deal_id)

    # ── Pipeline View ────────────────────────────────────────

    def get_pipeline_view(self) -> List[Dict]:
        """Build Kanban-style pipeline data grouped by stage."""
        stages = (
            self.db.query(DealStage)
            .filter(DealStage.tenant_id == self.tenant_id)
            .order_by(DealStage.display_order)
            .all()
        )
        result = []
        for stage in stages:
            deals = (
                self.db.query(Deal)
                .filter(
                    Deal.tenant_id == self.tenant_id,
                    Deal.stage_id == stage.id,
                    Deal.is_deleted == False,  # noqa: E712
                )
                .order_by(Deal.updated_at.desc())
                .all()
            )
            total_value = sum(
                d.target_value or Decimal(0) for d in deals
            )
            result.append({
                "stage": stage,
                "deals": deals,
                "total_value": total_value,
                "deal_count": len(deals),
            })
        return result

    # ── Notes ────────────────────────────────────────────────

    def add_note(self, deal_id: int, author_id: int, content: str, is_pinned: bool = False) -> DealNote:
        note = DealNote(
            deal_id=deal_id, author_id=author_id,
            content=content, is_pinned=is_pinned,
            tenant_id=self.tenant_id,
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        self._log_activity(deal_id, author_id, "note_added", "Note added")
        return note

    def get_notes(self, deal_id: int) -> List[DealNote]:
        return (
            self.db.query(DealNote)
            .filter(
                DealNote.deal_id == deal_id,
                DealNote.tenant_id == self.tenant_id,
                DealNote.is_deleted == False,  # noqa: E712
            )
            .order_by(DealNote.created_at.desc())
            .all()
        )

    # ── Team ─────────────────────────────────────────────────

    def add_team_member(self, deal_id: int, user_id: int, role: str, allocation_pct: float = 100.0) -> DealTeamMember:
        member = DealTeamMember(
            deal_id=deal_id, user_id=user_id,
            role=role, allocation_pct=allocation_pct,
            tenant_id=self.tenant_id,
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def get_team(self, deal_id: int) -> List[DealTeamMember]:
        return (
            self.db.query(DealTeamMember)
            .filter(
                DealTeamMember.deal_id == deal_id,
                DealTeamMember.tenant_id == self.tenant_id,
            )
            .all()
        )

    def remove_team_member(self, member_id: int) -> bool:
        member = self.db.query(DealTeamMember).filter(DealTeamMember.id == member_id).first()
        if not member:
            return False
        self.db.delete(member)
        self.db.commit()
        return True

    # ── Buyer Lists ──────────────────────────────────────────

    def create_buyer_list(self, deal_id: int, data: Dict[str, Any]) -> BuyerList:
        bl = BuyerList(deal_id=deal_id, tenant_id=self.tenant_id, **data)
        self.db.add(bl)
        self.db.commit()
        self.db.refresh(bl)
        return bl

    def add_buyer_list_entry(self, buyer_list_id: int, data: Dict[str, Any]) -> BuyerListEntry:
        entry = BuyerListEntry(buyer_list_id=buyer_list_id, tenant_id=self.tenant_id, **data)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_buyer_lists(self, deal_id: int) -> List[BuyerList]:
        return (
            self.db.query(BuyerList)
            .filter(
                BuyerList.deal_id == deal_id,
                BuyerList.tenant_id == self.tenant_id,
                BuyerList.is_deleted == False,  # noqa: E712
            )
            .all()
        )

    # ── Bids ─────────────────────────────────────────────────

    def add_bid(self, deal_id: int, data: Dict[str, Any], user_id: Optional[int] = None) -> Bid:
        bid = Bid(deal_id=deal_id, tenant_id=self.tenant_id, **data)
        bid.submitted_at = datetime.now(timezone.utc)
        self.db.add(bid)
        self.db.commit()
        self.db.refresh(bid)
        self._log_activity(deal_id, user_id, "bid_received", f"{data.get('bid_type', 'unknown')} bid received")
        return bid

    def get_bids(self, deal_id: int) -> List[Bid]:
        return (
            self.db.query(Bid)
            .filter(
                Bid.deal_id == deal_id,
                Bid.tenant_id == self.tenant_id,
                Bid.is_deleted == False,  # noqa: E712
            )
            .order_by(Bid.submitted_at.desc())
            .all()
        )

    # ── Activity Log ─────────────────────────────────────────

    def get_activities(self, deal_id: int, limit: int = 50) -> List[DealActivity]:
        return (
            self.db.query(DealActivity)
            .filter(
                DealActivity.deal_id == deal_id,
                DealActivity.tenant_id == self.tenant_id,
            )
            .order_by(DealActivity.created_at.desc())
            .limit(limit)
            .all()
        )

    def _log_activity(
        self,
        deal_id: int,
        user_id: Optional[int],
        activity_type: str,
        description: str,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
    ) -> None:
        """Create an activity log entry for a deal event."""
        activity = DealActivity(
            deal_id=deal_id,
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            old_value=old_value,
            new_value=new_value,
            tenant_id=self.tenant_id,
        )
        self.db.add(activity)
        self.db.commit()


def seed_default_stages(db: Session, tenant_id: str = "default") -> List[DealStage]:
    """Seed the default M&A deal stages for a tenant. Idempotent."""
    existing = db.query(DealStage).filter(DealStage.tenant_id == tenant_id).count()
    if existing > 0:
        return db.query(DealStage).filter(DealStage.tenant_id == tenant_id).order_by(DealStage.display_order).all()

    stages = []
    for s in DEFAULT_STAGES:
        stage = DealStage(tenant_id=tenant_id, **s)
        db.add(stage)
        stages.append(stage)
    db.commit()
    for s in stages:
        db.refresh(s)
    return stages
