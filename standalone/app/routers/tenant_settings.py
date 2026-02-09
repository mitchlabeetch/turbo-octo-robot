from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_role
from app.db import get_db
from app.models import Tenant, TenantSettings, User
from app.schemas import TenantSettingsCreate, TenantSettingsOut


router = APIRouter()


@router.get("/tenants/{tenant_id}/settings", response_model=TenantSettingsOut)
def get_tenant_settings(
    tenant_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin"))
):
    tenant_exists = db.query(Tenant.id).filter(Tenant.id == tenant_id).first()
    if not tenant_exists:
        raise HTTPException(status_code=404, detail="Tenant not found")
    settings = db.query(TenantSettings).filter(TenantSettings.tenant_id == tenant_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Tenant settings not found")
    return settings


@router.put("/tenants/{tenant_id}/settings", response_model=TenantSettingsOut)
def upsert_tenant_settings(
    tenant_id: int,
    payload: TenantSettingsCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin"))
):
    tenant_exists = db.query(Tenant.id).filter(Tenant.id == tenant_id).first()
    if not tenant_exists:
        raise HTTPException(status_code=404, detail="Tenant not found")

    settings = db.query(TenantSettings).filter(TenantSettings.tenant_id == tenant_id).first()
    data = payload.model_dump(exclude_unset=True)
    if settings:
        for key, value in data.items():
            setattr(settings, key, value)
    else:
        settings = TenantSettings(tenant_id=tenant_id, **data)
        db.add(settings)

    db.commit()
    db.refresh(settings)
    return settings
