from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from app.auth import require_role
from app.db import get_db
from app.models import Tenant, User
from app.schemas import TenantCreate, TenantOut


router = APIRouter()


@router.post("", response_model=TenantOut)
def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    existing = (
        db.query(Tenant)
        .filter(or_(Tenant.name == payload.name, Tenant.slug == payload.slug))
        .order_by(desc(Tenant.name == payload.name))
        .first()
    )
    if existing:
        if existing.name == payload.name:
            raise HTTPException(status_code=409, detail="Tenant name already exists")
        raise HTTPException(status_code=409, detail="Tenant slug already exists")

    tenant = Tenant(**payload.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("", response_model=list[TenantOut])
def list_tenants(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    return db.query(Tenant).order_by(Tenant.id).all()


@router.get("/{tenant_id}", response_model=TenantOut)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role("admin"))
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant
