"""
Project management router.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import User
from app.schemas.projects import (
    ProjectCreate, ProjectOut, TaskCreate, TaskOut,
    TimeEntryCreate, TimeEntryOut,
)
from app.services.projects import ProjectService

router = APIRouter()


def _svc(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db, tenant_id="default")


@router.post("", response_model=ProjectOut)
def create_project(
    payload: ProjectCreate,
    svc: ProjectService = Depends(_svc),
    _user: User = Depends(get_current_user),
):
    return svc.create_project(payload.model_dump(exclude_none=True))


@router.get("", response_model=List[ProjectOut])
def list_projects(
    status: Optional[str] = None,
    svc: ProjectService = Depends(_svc),
    _user: User = Depends(get_current_user),
):
    return svc.list_projects(status=status)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    svc: ProjectService = Depends(_svc),
    _user: User = Depends(get_current_user),
):
    p = svc.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p


@router.post("/{project_id}/tasks", response_model=TaskOut)
def create_task(
    project_id: int,
    payload: TaskCreate,
    svc: ProjectService = Depends(_svc),
    _user: User = Depends(get_current_user),
):
    return svc.create_task(project_id, payload.model_dump(exclude_none=True))


@router.post("/time-entries", response_model=TimeEntryOut)
def log_time(
    payload: TimeEntryCreate,
    svc: ProjectService = Depends(_svc),
    _user: User = Depends(get_current_user),
):
    return svc.log_time(payload.model_dump())
