from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import Document
from app.schemas import DocumentOut
from app.storage import save_upload


router = APIRouter()


@router.post("/upload", response_model=DocumentOut)
def upload_document(
    document_name: str = Form(...),
    document_type: str = Form(...),
    deal_name: str | None = Form(None),
    status: str = Form("Draft"),
    is_confidential: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user)
):
    file_path, size_bytes = save_upload(file, prefix="doc")

    doc = Document(
        document_name=document_name,
        document_type=document_type,
        deal_name=deal_name,
        file_path=file_path,
        file_name=file.filename,
        content_type=file.content_type,
        size_bytes=size_bytes,
        version=1,
        status=status,
        is_confidential=is_confidential
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
