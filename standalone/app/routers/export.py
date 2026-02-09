"""Export router for bulk data export."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from io import BytesIO
import json

from ..auth import get_current_user
from ..db import get_db
from ..models import User
from ..utils.export import (
    export_companies_csv,
    export_companies_json,
    export_contacts_csv,
    export_contacts_json,
    export_documents_csv,
    export_documents_json,
    create_zip_export
)
from ..config import settings
from sqlalchemy.orm import Session

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/companies/csv")
def export_companies_csv_endpoint(
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all companies as CSV."""
    csv_content = export_companies_csv(db)
    
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=companies.csv"}
    )


@router.get("/companies/json")
def export_companies_json_endpoint(
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all companies as JSON."""
    data = export_companies_json(db)
    
    return StreamingResponse(
        iter([json.dumps(data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=companies.json"}
    )


@router.get("/contacts/csv")
def export_contacts_csv_endpoint(
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all contacts as CSV."""
    csv_content = export_contacts_csv(db)
    
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=contacts.csv"}
    )


@router.get("/contacts/json")
def export_contacts_json_endpoint(
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all contacts as JSON."""
    data = export_contacts_json(db)
    
    return StreamingResponse(
        iter([json.dumps(data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=contacts.json"}
    )


@router.get("/documents/csv")
def export_documents_csv_endpoint(
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all document metadata as CSV."""
    csv_content = export_documents_csv(db)
    
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=documents.csv"}
    )


@router.get("/documents/json")
def export_documents_json_endpoint(
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all document metadata as JSON."""
    data = export_documents_json(db)
    
    return StreamingResponse(
        iter([json.dumps(data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=documents.json"}
    )


@router.get("/full")
def export_full_zip(
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export complete database as ZIP with CSV/JSON and document attachments."""
    try:
        zip_path = create_zip_export(db, settings.storage_dir)
        return FileResponse(
            zip_path,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={zip_path.split('/')[-1]}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
