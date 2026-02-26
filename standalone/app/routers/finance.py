"""
Finance router: REST API for the ERP financial engine.

Endpoints cover: Chart of Accounts, Journal Entries (GL),
Invoices (AR), Payments, Vendors, Bills (AP).
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import User
from app.schemas.finance import (
    AccountCreate, AccountOut,
    BillCreate, BillOut,
    ExchangeRateCreate, ExchangeRateOut,
    InvoiceCreate, InvoiceListOut, InvoiceOut,
    JournalEntryCreate, JournalEntryOut,
    PaymentCreate, PaymentOut,
    VendorCreate, VendorOut,
)
from app.services.finance import AccountingService, InvoiceService, VendorService

router = APIRouter()


def _acct_svc(db: Session = Depends(get_db)) -> AccountingService:
    return AccountingService(db, tenant_id="default")


def _inv_svc(db: Session = Depends(get_db)) -> InvoiceService:
    return InvoiceService(db, tenant_id="default")


def _vendor_svc(db: Session = Depends(get_db)) -> VendorService:
    return VendorService(db, tenant_id="default")


# ── Chart of Accounts ────────────────────────────────────────

@router.get("/accounts", response_model=List[AccountOut])
def list_accounts(
    account_type: Optional[str] = None,
    svc: AccountingService = Depends(_acct_svc),
    _user: User = Depends(get_current_user),
):
    """List chart of accounts. Auto-seeds defaults if empty."""
    svc.seed_default_accounts()
    return svc.list_accounts(account_type=account_type)


@router.post("/accounts", response_model=AccountOut)
def create_account(
    payload: AccountCreate,
    svc: AccountingService = Depends(_acct_svc),
    _user: User = Depends(get_current_user),
):
    """Create a new account in the chart of accounts."""
    return svc.create_account(payload.model_dump())


# ── Journal Entries ──────────────────────────────────────────

@router.post("/journal-entries", response_model=JournalEntryOut)
def create_journal_entry(
    payload: JournalEntryCreate,
    svc: AccountingService = Depends(_acct_svc),
    user: User = Depends(get_current_user),
):
    """Create a new journal entry. Validates that debits == credits."""
    try:
        lines = [l.model_dump() for l in payload.lines]
        return svc.create_journal_entry(
            entry_date=payload.entry_date,
            lines=lines,
            reference=payload.reference,
            memo=payload.memo,
            user_id=user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/journal-entries", response_model=List[JournalEntryOut])
def list_journal_entries(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    svc: AccountingService = Depends(_acct_svc),
    _user: User = Depends(get_current_user),
):
    """List journal entries with optional status filter."""
    return svc.list_journal_entries(offset=offset, limit=limit, status=status)


@router.post("/journal-entries/{je_id}/post", response_model=JournalEntryOut)
def post_journal_entry(
    je_id: int,
    svc: AccountingService = Depends(_acct_svc),
    user: User = Depends(get_current_user),
):
    """Post a draft journal entry."""
    try:
        return svc.post_journal_entry(je_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Invoices ─────────────────────────────────────────────────

@router.post("/invoices", response_model=InvoiceOut)
def create_invoice(
    payload: InvoiceCreate,
    svc: InvoiceService = Depends(_inv_svc),
    user: User = Depends(get_current_user),
):
    """Create a new invoice with line items."""
    data = payload.model_dump()
    data["lines"] = [l.model_dump() for l in payload.lines]
    return svc.create(data, user_id=user.id)


@router.get("/invoices", response_model=InvoiceListOut)
def list_invoices(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    svc: InvoiceService = Depends(_inv_svc),
    _user: User = Depends(get_current_user),
):
    """List invoices with pagination and status filter."""
    invoices = svc.list(offset=offset, limit=limit, status=status)
    total = svc.count()
    return InvoiceListOut(items=invoices, total=total, offset=offset, limit=limit)


@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)
def get_invoice(
    invoice_id: int,
    svc: InvoiceService = Depends(_inv_svc),
    _user: User = Depends(get_current_user),
):
    """Get a single invoice by ID."""
    inv = svc.get(invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


@router.post("/invoices/{invoice_id}/payments", response_model=PaymentOut)
def record_payment(
    invoice_id: int,
    payload: PaymentCreate,
    svc: InvoiceService = Depends(_inv_svc),
    _user: User = Depends(get_current_user),
):
    """Record a payment against an invoice."""
    try:
        return svc.record_payment(invoice_id, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Vendors ──────────────────────────────────────────────────

@router.post("/vendors", response_model=VendorOut)
def create_vendor(
    payload: VendorCreate,
    svc: VendorService = Depends(_vendor_svc),
    _user: User = Depends(get_current_user),
):
    """Create a new vendor."""
    return svc.create(payload.model_dump())


@router.get("/vendors", response_model=List[VendorOut])
def list_vendors(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    svc: VendorService = Depends(_vendor_svc),
    _user: User = Depends(get_current_user),
):
    """List vendors."""
    return svc.list(offset=offset, limit=limit)


@router.post("/vendors/{vendor_id}/bills", response_model=BillOut)
def create_bill(
    vendor_id: int,
    payload: BillCreate,
    svc: VendorService = Depends(_vendor_svc),
    _user: User = Depends(get_current_user),
):
    """Create a vendor bill with line items."""
    data = payload.model_dump()
    data["lines"] = [l.model_dump() for l in payload.lines]
    return svc.create_bill(vendor_id, data)
