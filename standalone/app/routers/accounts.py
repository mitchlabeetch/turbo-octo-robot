from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_

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
    existing = db.query(Account).filter(
        or_(Account.name == payload.name, Account.code == payload.code)
    ).limit(2).all()
    has_name = False
    has_code = False
    for account in existing:
        if account.name == payload.name:
            has_name = True
        if account.code == payload.code:
            has_code = True
    if has_name or has_code:
        if has_name and has_code:
            detail = "Account name and code already exist"
        elif has_name:
            detail = "Account name already exists"
        else:
            detail = "Account code already exists"
        raise HTTPException(status_code=409, detail=detail)
    account = Account(**payload.model_dump())
    db.add(account)
    # IntegrityError still protects against race conditions on unique constraints.
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Account already exists")
    db.refresh(account)
    return account


@router.get("", response_model=list[AccountOut])
def list_accounts(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
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
