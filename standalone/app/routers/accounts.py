from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import require_role
from app.db import get_db
from app.models import Account, User
from app.schemas import AccountCreate, AccountOut


router = APIRouter()


@router.post("", response_model=AccountOut)
def create_account(
    payload: AccountCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin"))
):
    account = Account(**payload.model_dump())
    db.add(account)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Account with this name or code already exists"
        )
    db.refresh(account)
    return account


@router.get("", response_model=list[AccountOut])
def list_accounts(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
    limit: int = 100,
    offset: int = 0
):
    return db.query(Account).order_by(Account.id).offset(offset).limit(limit).all()


@router.get("/{account_id}", response_model=AccountOut)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin"))
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
