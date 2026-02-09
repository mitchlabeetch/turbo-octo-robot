"""Audit logging utilities for document access tracking."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import AccessLog, DocumentShare, Document


def log_access(
    db: Session,
    share_id: int,
    action: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    accessed_by_email: Optional[str] = None
) -> AccessLog:
    """Log an access event for a document share."""
    access_log = AccessLog(
        share_id=share_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        accessed_by_email=accessed_by_email
    )
    db.add(access_log)
    db.commit()
    return access_log


def get_share_audit_logs(
    db: Session,
    share_id: int,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get all access logs for a share."""
    logs = db.query(AccessLog).filter(
        AccessLog.share_id == share_id
    ).order_by(AccessLog.accessed_at.desc()).limit(limit).all()
    
    return [
        {
            'id': log.id,
            'action': log.action,
            'accessed_at': log.accessed_at.isoformat() if log.accessed_at else None,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'accessed_by_email': log.accessed_by_email
        }
        for log in logs
    ]


def get_document_audit_logs(
    db: Session,
    document_id: int,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get all access logs for a document across all shares."""
    logs = db.query(AccessLog).join(
        DocumentShare
    ).filter(
        DocumentShare.document_id == document_id
    ).order_by(AccessLog.accessed_at.desc()).limit(limit).all()
    
    return [
        {
            'id': log.id,
            'share_id': log.share_id,
            'action': log.action,
            'accessed_at': log.accessed_at.isoformat() if log.accessed_at else None,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'accessed_by_email': log.accessed_by_email
        }
        for log in logs
    ]


def get_audit_summary(db: Session) -> Dict[str, Any]:
    """Get summary statistics for all access activity."""
    total_logs = db.query(AccessLog).count()
    total_views = db.query(AccessLog).filter(AccessLog.action == 'view').count()
    total_downloads = db.query(AccessLog).filter(AccessLog.action == 'download').count()
    total_nda_confirmations = db.query(AccessLog).filter(AccessLog.action == 'nda_confirm').count()
    
    # Get most accessed shares
    most_accessed = db.query(
        AccessLog.share_id,
        Document.document_name,
        db.func.count(AccessLog.id).label('access_count')
    ).join(
        DocumentShare
    ).join(
        Document
    ).group_by(
        AccessLog.share_id,
        Document.document_name
    ).order_by(
        db.func.count(AccessLog.id).desc()
    ).limit(10).all()
    
    return {
        'total_access_events': total_logs,
        'total_views': total_views,
        'total_downloads': total_downloads,
        'total_nda_confirmations': total_nda_confirmations,
        'most_accessed_documents': [
            {
                'share_id': item[0],
                'document_name': item[1],
                'access_count': item[2]
            }
            for item in most_accessed
        ]
    }
