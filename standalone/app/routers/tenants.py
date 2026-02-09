from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_role
from app.db import get_db
from app.models import Tenant
from app.schemas import TenantCreate, TenantOut


router = APIRouter()


@router.post("", response_model=TenantOut)
def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_role("admin"))
):
    existing_name = db.query(Tenant).filter(Tenant.name == payload.name).first()
    if existing_name:
        raise HTTPException(status_code=409, detail="Tenant name already exists")

    existing_slug = db.query(Tenant).filter(Tenant.slug == payload.slug).first()
    if existing_slug:
        raise HTTPException(status_code=409, detail="Tenant slug already exists")

    tenant = Tenant(**payload.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("", response_model=list[TenantOut])
def list_tenants(db: Session = Depends(get_db), _admin=Depends(require_role("admin"))):
    return db.query(Tenant).order_by(Tenant.id).all()


@router.get("/{tenant_id}", response_model=TenantOut)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_role("admin"))
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant
