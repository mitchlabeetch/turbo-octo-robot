"""Audit dashboard router for admin access activity monitoring."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import require_role
from app.db import get_db
from app.models import User
from app.utils.audit import get_audit_summary, get_document_audit_logs

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/summary")
def get_summary(
    _user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get summary of all access activity (admin only)."""
    return get_audit_summary(db)


@router.get("/documents/{document_id}/logs")
def get_document_logs(
    document_id: int,
    limit: int = 100,
    _user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get all access logs for a document (admin only)."""
    logs = get_document_audit_logs(db, document_id, limit=limit)
    return {"document_id": document_id, "logs": logs, "total": len(logs)}
