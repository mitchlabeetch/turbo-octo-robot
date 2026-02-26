"""
Project & Time Tracking service.
"""

from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.projects import Project, Task, TimeEntry
from app.services.base_repository import BaseRepository


class ProjectService:
    """Business logic for project and task management."""

    def __init__(self, db: Session, tenant_id: str = "default"):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = BaseRepository(Project, db, tenant_id)
        self.task_repo = BaseRepository(Task, db, tenant_id)

    def create_project(self, data: Dict[str, Any]) -> Project:
        return self.repo.create(data)

    def get_project(self, project_id: int) -> Optional[Project]:
        return self.repo.get_by_id(project_id)

    def list_projects(self, *, offset: int = 0, limit: int = 50, status: Optional[str] = None) -> List[Project]:
        filters = {}
        if status:
            filters["status"] = status
        return self.repo.list(offset=offset, limit=limit, filters=filters)

    def create_task(self, project_id: int, data: Dict[str, Any]) -> Task:
        data["project_id"] = project_id
        return self.task_repo.create(data)

    def update_task(self, task_id: int, data: Dict[str, Any]) -> Optional[Task]:
        return self.task_repo.update(task_id, data)

    def log_time(self, data: Dict[str, Any]) -> TimeEntry:
        entry = TimeEntry(tenant_id=self.tenant_id, **data)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        # Update actual_hours on the task
        if entry.task_id:
            task = self.task_repo.get_by_id(entry.task_id)
            if task:
                task.actual_hours = (task.actual_hours or 0) + entry.hours
                self.db.commit()
        return entry

    def get_timesheet(self, user_id: int, start_date: date, end_date: date) -> List[TimeEntry]:
        return (
            self.db.query(TimeEntry)
            .filter(
                TimeEntry.user_id == user_id,
                TimeEntry.tenant_id == self.tenant_id,
                TimeEntry.date >= start_date,
                TimeEntry.date <= end_date,
            )
            .order_by(TimeEntry.date.desc())
            .all()
        )
