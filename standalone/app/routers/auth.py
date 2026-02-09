from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, require_role, verify_password
from app.config import settings
from app.db import get_db
from app.models import User
from app.schemas import TokenOut, UserCreate, UserOut


router = APIRouter()


@router.post("/bootstrap", response_model=UserOut)
def bootstrap_admin(
    payload: UserCreate,
    db: Session = Depends(get_db),
    x_bootstrap_token: str | None = Header(default=None)
):
    if settings.bootstrap_token == "change-me" or x_bootstrap_token != settings.bootstrap_token:
        raise HTTPException(status_code=401, detail="Invalid bootstrap token")

    if db.query(User).count() > 0:
        raise HTTPException(status_code=409, detail="Bootstrap already completed")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        role="admin",
        hashed_password=hash_password(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/register", response_model=UserOut)
def register_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_role("admin"))
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=hash_password(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token", response_model=TokenOut)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.email, user.role)
    return TokenOut(access_token=token)
