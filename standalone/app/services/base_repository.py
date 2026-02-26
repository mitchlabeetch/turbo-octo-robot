"""
Generic CRUD Repository.

Provides base data access operations that all entity-specific repositories inherit:
  - get_by_id / get_by_uuid
  - list (with pagination, filtering, sorting)
  - create / update / delete (soft-delete)
  - count

All queries automatically scope to tenant_id and exclude soft-deleted records.
"""

from typing import Any, Dict, Generic, List, Optional, Sequence, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic CRUD repository with tenant scoping and soft-delete awareness."""

    def __init__(self, model: Type[T], db: Session, tenant_id: str = "default"):
        self.model = model
        self.db = db
        self.tenant_id = tenant_id

    def _base_query(self):
        """Base query scoped to tenant and excluding soft-deleted records."""
        q = self.db.query(self.model)
        if hasattr(self.model, "tenant_id"):
            q = q.filter(self.model.tenant_id == self.tenant_id)
        if hasattr(self.model, "is_deleted"):
            q = q.filter(self.model.is_deleted == False)  # noqa: E712
        return q

    def get_by_id(self, id: int) -> Optional[T]:
        """Get a single record by integer primary key."""
        return self._base_query().filter(self.model.id == id).first()

    def get_by_uuid(self, uuid: str) -> Optional[T]:
        """Get a single record by public UUID."""
        if not hasattr(self.model, "uuid"):
            raise AttributeError(f"{self.model.__name__} does not have a uuid field")
        return self._base_query().filter(self.model.uuid == uuid).first()

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[T]:
        """List records with pagination, sorting, and filtering."""
        q = self._base_query()

        # Apply simple equality filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    q = q.filter(getattr(self.model, key) == value)

        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            col = getattr(self.model, order_by)
            q = q.order_by(col.desc() if order_desc else col.asc())
        elif hasattr(self.model, "created_at"):
            q = q.order_by(self.model.created_at.desc())

        return q.offset(offset).limit(limit).all()

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records matching filters."""
        q = self._base_query()
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    q = q.filter(getattr(self.model, key) == value)
        return q.count()

    def create(self, data: Dict[str, Any]) -> T:
        """Create a new record."""
        if hasattr(self.model, "tenant_id"):
            data.setdefault("tenant_id", self.tenant_id)
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:
        """Update an existing record by ID."""
        obj = self.get_by_id(id)
        if not obj:
            return None
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int, hard: bool = False) -> bool:
        """Delete a record. Soft-delete by default, hard-delete if specified."""
        obj = self.get_by_id(id)
        if not obj:
            return False
        if hard or not hasattr(obj, "soft_delete"):
            self.db.delete(obj)
        else:
            obj.soft_delete()
        self.db.commit()
        return True
