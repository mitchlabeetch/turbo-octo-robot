from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import Contact
from app.schemas import ContactCreate, ContactOut


router = APIRouter()


@router.post("", response_model=ContactOut)
def create_contact(
    payload: ContactCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user)
):
    existing = db.query(Contact).filter(Contact.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Contact already exists")

    contact = Contact(**payload.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/{contact_id}", response_model=ContactOut)
def get_contact(contact_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact
