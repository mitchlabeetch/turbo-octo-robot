"""Document sharing router with NDA gating and access logging."""

from datetime import datetime, timezone
from typing import Optional
import tempfile
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_role
from app.db import get_db
from app.models import Document, DocumentShare, AccessLog
from app.schemas import ShareCreate, ShareOut, ShareInfo, NDAConfirm, AccessLogOut, AuditSummary
from app.security import generate_share_token, share_expiry
from app.utils.watermark import add_watermark_text, should_watermark
from app.utils.audit import log_access, get_share_audit_logs, get_document_audit_logs, get_audit_summary
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/documents/{document_id}", response_model=ShareOut)
def create_share(
    document_id: int,
    payload: ShareCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user)
):
    """Create a secure share link for a document with optional NDA and view-only restrictions."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    token = generate_share_token()
    expiry = share_expiry(payload.expires_in_days)
    
    # Hash password if provided
    password_hash = None
    if payload.password:
        password_hash = pwd_context.hash(payload.password)
    
    share = DocumentShare(
        document_id=doc.id,
        token=token,
        expires_at=expiry,
        view_only=payload.view_only,
        requires_nda=payload.requires_nda,
        password_hash=password_hash
    )

    db.add(share)
    db.commit()
    db.refresh(share)
    return ShareOut(token=share.token, expires_at=share.expires_at)


@router.get("/{token}", response_model=ShareInfo)
def get_share_info(token: str, db: Session = Depends(get_db)):
    """Get information about a share (status, NDA requirements)."""
    share = db.query(DocumentShare).filter(DocumentShare.token == token).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")

    expired = False
    if share.expires_at and share.expires_at < datetime.now(timezone.utc):
        expired = True

    doc = db.query(Document).filter(Document.id == share.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return ShareInfo(
        token=share.token,
        document_name=doc.document_name,
        view_only=share.view_only,
        requires_nda=share.requires_nda,
        nda_confirmed=share.nda_confirmed_at is not None,
        expires_at=share.expires_at,
        expired=expired
    )


@router.post("/{token}/nda-confirm")
def confirm_nda(
    token: str,
    payload: NDAConfirm,
    db: Session = Depends(get_db)
):
    """Confirm NDA for a share before accessing document."""
    share = db.query(DocumentShare).filter(DocumentShare.token == token).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")

    if not share.requires_nda:
        raise HTTPException(status_code=400, detail="NDA not required for this share")

    if share.expires_at and share.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Share expired")

    # Mark NDA as confirmed
    share.nda_confirmed_at = datetime.now(timezone.utc)
    share.nda_confirmed_by_email = payload.email
    db.add(share)
    db.commit()
    
    # Log NDA confirmation
    log_access(
        db,
        share_id=share.id,
        action="nda_confirm",
        accessed_by_email=payload.email
    )

    return {"status": "NDA confirmed"}


@router.get("/{token}/download")
def download_share(
    token: str,
    password: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Download document from share link with optional password protection, watermarking, and access logging."""
    share = db.query(DocumentShare).filter(DocumentShare.token == token).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")

    if share.expires_at and share.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Share expired")

    # Check NDA confirmation if required
    if share.requires_nda and not share.nda_confirmed_at:
        raise HTTPException(
            status_code=403,
            detail="NDA confirmation required. Please confirm NDA before downloading."
        )

    # Check password if required
    if share.password_hash:
        if not password:
            raise HTTPException(status_code=403, detail="Password required")
        if not pwd_context.verify(password, share.password_hash):
            raise HTTPException(status_code=403, detail="Invalid password")

    # Check if view-only
    if share.view_only:
        raise HTTPException(
            status_code=403,
            detail="This share is view-only. Download not allowed."
        )

    doc = db.query(Document).filter(Document.id == share.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Log access
    client_ip = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None
    log_access(
        db,
        share_id=share.id,
        action="download",
        ip_address=client_ip,
        user_agent=user_agent,
        accessed_by_email=share.nda_confirmed_by_email
    )

    # Update access count
    share.access_count += 1
    db.commit()

    # Apply watermarking if applicable
    file_to_return = doc.file_path
    if should_watermark(doc.content_type or "") and share.nda_confirmed_by_email:
        try:
            watermarked_path = tempfile.NamedTemporaryFile(
                suffix=f"_{os.path.basename(doc.file_path)}",
                delete=False
            ).name
            file_to_return = add_watermark_text(
                doc.file_path,
                share.nda_confirmed_by_email,
                watermarked_path
            )
        except Exception:
            # If watermarking fails, serve original
            file_to_return = doc.file_path

    return FileResponse(
        path=file_to_return,
        filename=doc.file_name,
        media_type=doc.content_type or "application/octet-stream"
    )


@router.get("/{token}/audit-logs")
def get_share_logs(
    token: str,
    db: Session = Depends(get_db),
    _user=Depends(require_role("admin"))
):
    """Get all access logs for a share (admin only)."""
    share = db.query(DocumentShare).filter(DocumentShare.token == token).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")

    logs = get_share_audit_logs(db, share.id)
    return {"token": token, "logs": logs}

