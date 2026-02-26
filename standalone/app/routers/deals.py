"""
Deal management router: Full REST API for M&A deal lifecycle.

Endpoints cover: deal CRUD, pipeline view, stage transitions,
notes, team management, buyer lists, bids, and activity log.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import User
from app.schemas.deals import (
    BidCreate, BidOut, BuyerListCreate, BuyerListEntryCreate, BuyerListEntryOut,
    BuyerListOut, DealActivityOut, DealCreate, DealListOut, DealNoteCreate,
    DealNoteOut, DealOut, DealStageOut, DealTeamMemberCreate, DealTeamMemberOut,
    DealUpdate, PipelineStageView,
)
from app.services.deals import DealService, seed_default_stages

router = APIRouter()


def _deal_svc(db: Session = Depends(get_db)) -> DealService:
    return DealService(db, tenant_id="default")


# ── Stages ───────────────────────────────────────────────────

@router.get("/stages", response_model=List[DealStageOut])
def list_stages(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    """List all deal stages. Auto-seeds defaults if none exist."""
    return seed_default_stages(db, tenant_id="default")


# ── Pipeline View ────────────────────────────────────────────

@router.get("/pipeline", response_model=List[PipelineStageView])
def get_pipeline(
    svc: DealService = Depends(_deal_svc),
    _user: User = Depends(get_current_user),
):
    """Get Kanban-style pipeline view with deals grouped by stage."""
    return svc.get_pipeline_view()


# ── Deal CRUD ────────────────────────────────────────────────

@router.post("", response_model=DealOut)
def create_deal(
    payload: DealCreate,
    svc: DealService = Depends(_deal_svc),
    user: User = Depends(get_current_user),
):
    """Create a new deal."""
    data = payload.model_dump(exclude_none=True)
    return svc.create(data, user_id=user.id)


@router.get("", response_model=DealListOut)
def list_deals(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    stage_id: Optional[int] = None,
    deal_type: Optional[str] = None,
    priority: Optional[str] = None,
    sector: Optional[str] = None,
    svc: DealService = Depends(_deal_svc),
    _user: User = Depends(get_current_user),
):
    """List deals with filtering and pagination."""
    deals = svc.list(
        offset=offset, limit=limit,
        stage_id=stage_id, deal_type=deal_type,
        priority=priority, sector=sector,
    )
    total = svc.count()
    return DealListOut(items=deals, total=total, offset=offset, limit=limit)


@router.get("/{deal_id}", response_model=DealOut)
def get_deal(
    deal_id: int,
    svc: DealService = Depends(_deal_svc),
    _user: User = Depends(get_current_user),
):
    """Get a single deal by ID."""
    deal = svc.get(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.patch("/{deal_id}", response_model=DealOut)
def update_deal(
    deal_id: int,
    payload: DealUpdate,
    svc: DealService = Depends(_deal_svc),
    user: User = Depends(get_current_user),
):
    """Update a deal (partial update)."""
    data = payload.model_dump(exclude_none=True)
    deal = svc.update(deal_id, data, user_id=user.id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.delete("/{deal_id}")
def delete_deal(
    deal_id: int,
    svc: DealService = Depends(_deal_svc),
    _user: User = Depends(get_current_user),
):
    """Soft-delete a deal."""
    if not svc.delete(deal_id):
        raise HTTPException(status_code=404, detail="Deal not found")
    return {"status": "deleted"}


# ── Notes ────────────────────────────────────────────────────

@router.post("/{deal_id}/notes", response_model=DealNoteOut)
def add_note(
    deal_id: int,
    payload: DealNoteCreate,
    svc: DealService = Depends(_deal_svc),
    user: User = Depends(get_current_user),
):
    """Add a note to a deal."""
    return svc.add_note(deal_id, user.id, payload.content, payload.is_pinned)


@router.get("/{deal_id}/notes", response_model=List[DealNoteOut])
def list_notes(
    deal_id: int,
    svc: DealService = Depends(_deal_svc),
    _user: User = Depends(get_current_user),
):
    """List all notes for a deal."""
    return svc.get_notes(deal_id)


# ── Team ─────────────────────────────────────────────────────

@router.post("/{deal_id}/team", response_model=DealTeamMemberOut)
def add_team_member(
    deal_id: int,
    payload: DealTeamMemberCreate,
    svc: DealService = Depends(_deal_svc),
    _user: User = Depends(get_current_user),
):
    """Assign a team member to a deal."""
    return svc.add_team_member(deal_id, payload.user_id, payload.role, payload.allocation_pct)


@router.get("/{deal_id}/team", response_model=List[DealTeamMemberOut])
def list_team(
    deal_id: int,
    svc: DealService = Depends(_deal_svc),
    _user: User = Depends(get_current_user),
):
    """List all team members for a deal."""
    return svc.get_team(deal_id)


@router.delete("/{deal_id}/team/{member_id}")
def remove_team_member(
    deal_id: int,
    member_id: int,
    svc: DealService = Depends(_deal_svc),
    _user: User = Depends(get_current_user),
):
    """Remove a team member from a deal."""
    if not svc.remove_team_member(member_id):
        raise HTTPException(status_code=404, detail="Team member not found")
    return {"status": "removed"}


# ── Buyer Lists ──────────────────────────────────────────────

@router.post("/{deal_id}/buyer-lists", response_model=BuyerListOut)
def create_buyer_list(
    deal_id: int,
    payload: BuyerListCreate,
    svc: DealService = Depends(_deal_svc),
    _user: User = Depends(get_current_user),
):
    """Create a buyer/seller list for a deal."""
    return svc.create_buyer_list(deal_id, payload.model_dump())


@router.get("/{deal_id}/buyer-lists", response_model=List[BuyerListOut])
def list_buyer_lists(
    deal_id: int,
    svc: DealService = Depends(_deal_svc),
    _user: User = Depends(get_current_user),
):
    """List all buyer/seller lists for a deal."""
    return svc.get_buyer_lists(deal_id)


@router.post("/{deal_id}/buyer-lists/{list_id}/entries", response_model=BuyerListEntryOut)
def add_buyer_list_entry(
    deal_id: int,
    list_id: int,
    payload: BuyerListEntryCreate,
    svc: DealService = Depends(_deal_svc),
    _user: User = Depends(get_current_user),
):
    """Add an entry to a buyer/seller list."""
    return svc.add_buyer_list_entry(list_id, payload.model_dump(exclude_none=True))


# ── Bids ─────────────────────────────────────────────────────

@router.post("/{deal_id}/bids", response_model=BidOut)
def add_bid(
    deal_id: int,
    payload: BidCreate,
    svc: DealService = Depends(_deal_svc),
    user: User = Depends(get_current_user),
):
    """Record a bid on a deal."""
    return svc.add_bid(deal_id, payload.model_dump(exclude_none=True), user_id=user.id)


@router.get("/{deal_id}/bids", response_model=List[BidOut])
def list_bids(
    deal_id: int,
    svc: DealService = Depends(_deal_svc),
    _user: User = Depends(get_current_user),
):
    """List all bids for a deal."""
    return svc.get_bids(deal_id)


# ── Activity Log ─────────────────────────────────────────────

@router.get("/{deal_id}/activities", response_model=List[DealActivityOut])
def list_activities(
    deal_id: int,
    limit: int = Query(50, ge=1, le=200),
    svc: DealService = Depends(_deal_svc),
    _user: User = Depends(get_current_user),
):
    """Get the activity log for a deal."""
    return svc.get_activities(deal_id, limit=limit)
