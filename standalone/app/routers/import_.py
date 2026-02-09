"""Import router for bulk data import."""

from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session

from ..auth import get_current_user, require_role
from ..db import get_db
from ..models import User
from ..utils.import_ import (
    import_companies_csv,
    import_companies_json,
    import_contacts_csv,
    import_contacts_json,
    ImportResult
)

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/companies/csv")
async def import_companies_csv_endpoint(
    file: UploadFile = File(...),
    _user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Import companies from CSV file."""
    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
        result = import_companies_csv(db, csv_content)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.post("/companies/json")
async def import_companies_json_endpoint(
    file: UploadFile = File(...),
    _user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Import companies from JSON file."""
    try:
        content = await file.read()
        json_content = content.decode('utf-8')
        result = import_companies_json(db, json_content)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.post("/contacts/csv")
async def import_contacts_csv_endpoint(
    file: UploadFile = File(...),
    _user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Import contacts from CSV file."""
    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
        result = import_contacts_csv(db, csv_content)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.post("/contacts/json")
async def import_contacts_json_endpoint(
    file: UploadFile = File(...),
    _user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Import contacts from JSON file."""
    try:
        content = await file.read()
        json_content = content.decode('utf-8')
        result = import_contacts_json(db, json_content)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")
