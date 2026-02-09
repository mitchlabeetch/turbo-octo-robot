from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import require_role
from app.db import get_db
from app.models import Invoice, User
from app.schemas import InvoiceCreate, InvoiceOut


router = APIRouter()


@router.post("", response_model=InvoiceOut)
def create_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin"))
):
    invoice = Invoice(**payload.model_dump())
    db.add(invoice)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Invoice with this invoice_number already exists"
        )
    db.refresh(invoice)
    return invoice


@router.get("", response_model=list[InvoiceOut])
def list_invoices(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
    limit: int = 100,
    offset: int = 0
):
    return db.query(Invoice).order_by(Invoice.id).offset(offset).limit(limit).all()


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin"))
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice
