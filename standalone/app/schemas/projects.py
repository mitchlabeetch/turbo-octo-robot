"""
Project management Pydantic schemas.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    assignee_id: Optional[int] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None


class TaskOut(BaseModel):
    id: int
    uuid: str
    project_id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assignee_id: Optional[int] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    actual_hours: float
    created_at: datetime
    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    deal_id: Optional[int] = None
    owner_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    currency: str = "EUR"


class ProjectOut(BaseModel):
    id: int
    uuid: str
    name: str
    description: Optional[str] = None
    status: str
    deal_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    currency: str
    tasks: List[TaskOut] = []
    created_at: datetime
    class Config:
        from_attributes = True


class TimeEntryCreate(BaseModel):
    task_id: Optional[int] = None
    deal_id: Optional[int] = None
    user_id: int
    date: date
    hours: float
    description: Optional[str] = None
    billable: bool = True
    hourly_rate: Optional[Decimal] = None


class TimeEntryOut(BaseModel):
    id: int
    task_id: Optional[int] = None
    deal_id: Optional[int] = None
    user_id: int
    date: date
    hours: float
    description: Optional[str] = None
    billable: bool
    hourly_rate: Optional[Decimal] = None
    created_at: datetime
    class Config:
        from_attributes = True
