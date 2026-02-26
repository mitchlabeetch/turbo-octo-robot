from __future__ import annotations

import json
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import settings
from app.db import get_db
from app.email_providers import parse_gmail_webhook, parse_microsoft_webhook
from app.models import Company, Contact, Interaction
from app.schemas import EmailCaptureIn, EmailCaptureOut


router = APIRouter()


def get_or_create_company(db: Session, company_name: str | None) -> Company | None:
    if not company_name:
        return None
    company = db.query(Company).filter(Company.name == company_name).first()
    if company:
        return company
    company = Company(name=company_name)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def get_or_create_contact(db: Session, payload: EmailCaptureIn, company_id: int | None) -> Contact:
    contact = db.query(Contact).filter(Contact.email == payload.contact_email).first()
    if contact:
        return contact

    first_name = payload.contact_first_name or payload.contact_email.split("@")[0]
    last_name = payload.contact_last_name or "Contact"
    contact = Contact(
        first_name=first_name,
        last_name=last_name,
        email=payload.contact_email,
        company_id=company_id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def _capture_email(payload: EmailCaptureIn, db: Session) -> EmailCaptureOut:
    company = get_or_create_company(db, payload.company_name)
    contact = get_or_create_contact(db, payload, company.id if company else None)

    interaction = Interaction(
        interaction_type="Email",
        subject=payload.subject,
        notes=payload.body,
        interaction_date=payload.interaction_date,
        metadata_json=payload.metadata_json,
        contact_id=contact.id,
        company_id=company.id if company else None
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    return EmailCaptureOut(
        interaction_id=interaction.id,
        contact_id=contact.id,
        company_id=company.id if company else None
    )


@router.post("/capture", response_model=EmailCaptureOut)
def capture_email(
    payload: EmailCaptureIn,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user)
):
    return _capture_email(payload, db)


@router.post("/webhook/gmail", response_model=EmailCaptureOut)
def gmail_webhook(
    payload: dict,
    db: Session = Depends(get_db),
    x_webhook_secret: str | None = Header(default=None)
):
    if settings.webhook_secret != "change-me" and x_webhook_secret != settings.webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    parsed = parse_gmail_webhook(payload)
    return _capture_email(EmailCaptureIn(**parsed), db)


@router.post("/webhook/microsoft", response_model=EmailCaptureOut)
def microsoft_webhook(
    payload: dict,
    db: Session = Depends(get_db),
    x_webhook_secret: str | None = Header(default=None)
):
    if settings.webhook_secret != "change-me" and x_webhook_secret != settings.webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    parsed = parse_microsoft_webhook(payload)
    return _capture_email(EmailCaptureIn(**parsed), db)
