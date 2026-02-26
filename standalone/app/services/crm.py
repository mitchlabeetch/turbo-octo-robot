"""
CRM Services: Company, Contact, Interaction business logic.

Each service wraps a BaseRepository with entity-specific operations.
Routers call these services instead of touching the DB directly.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.crm import Company, Contact, Interaction
from app.services.base_repository import BaseRepository


class CompanyService:
    """Business logic for Company management."""

    def __init__(self, db: Session, tenant_id: str = "default"):
        self.repo = BaseRepository(Company, db, tenant_id)
        self.db = db

    def get(self, company_id: int) -> Optional[Company]:
        return self.repo.get_by_id(company_id)

    def get_by_name(self, name: str) -> Optional[Company]:
        results = self.repo.list(filters={"name": name}, limit=1)
        return results[0] if results else None

    def get_by_uuid(self, uuid: str) -> Optional[Company]:
        return self.repo.get_by_uuid(uuid)

    def list(self, *, offset: int = 0, limit: int = 50, **filters) -> List[Company]:
        return self.repo.list(offset=offset, limit=limit, filters=filters)

    def count(self, **filters) -> int:
        return self.repo.count(filters=filters)

    def create(self, data: Dict[str, Any]) -> Company:
        # Check for duplicate name within tenant
        existing = self.repo.list(filters={"name": data.get("name")}, limit=1)
        if existing:
            raise ValueError(f"Company '{data['name']}' already exists")
        return self.repo.create(data)

    def update(self, company_id: int, data: Dict[str, Any]) -> Optional[Company]:
        return self.repo.update(company_id, data)

    def delete(self, company_id: int) -> bool:
        return self.repo.delete(company_id)


class ContactService:
    """Business logic for Contact management."""

    def __init__(self, db: Session, tenant_id: str = "default"):
        self.repo = BaseRepository(Contact, db, tenant_id)
        self.db = db

    def get(self, contact_id: int) -> Optional[Contact]:
        return self.repo.get_by_id(contact_id)

    def get_by_uuid(self, uuid: str) -> Optional[Contact]:
        return self.repo.get_by_uuid(uuid)

    def get_by_email(self, email: str) -> Optional[Contact]:
        results = self.repo.list(filters={"email": email}, limit=1)
        return results[0] if results else None

    def list(self, *, offset: int = 0, limit: int = 50, **filters) -> List[Contact]:
        return self.repo.list(offset=offset, limit=limit, filters=filters)

    def count(self, **filters) -> int:
        return self.repo.count(filters=filters)

    def create(self, data: Dict[str, Any]) -> Contact:
        # Check for duplicate email within tenant
        existing = self.get_by_email(data.get("email", ""))
        if existing:
            raise ValueError(f"Contact with email '{data['email']}' already exists")
        return self.repo.create(data)

    def update(self, contact_id: int, data: Dict[str, Any]) -> Optional[Contact]:
        return self.repo.update(contact_id, data)

    def delete(self, contact_id: int) -> bool:
        return self.repo.delete(contact_id)


class InteractionService:
    """Business logic for Interaction logging."""

    def __init__(self, db: Session, tenant_id: str = "default"):
        self.repo = BaseRepository(Interaction, db, tenant_id)
        self.db = db

    def get(self, interaction_id: int) -> Optional[Interaction]:
        return self.repo.get_by_id(interaction_id)

    def list(self, *, offset: int = 0, limit: int = 50, **filters) -> List[Interaction]:
        return self.repo.list(offset=offset, limit=limit, filters=filters)

    def list_by_contact(self, contact_id: int, *, offset: int = 0, limit: int = 50) -> List[Interaction]:
        return self.repo.list(offset=offset, limit=limit, filters={"contact_id": contact_id})

    def list_by_company(self, company_id: int, *, offset: int = 0, limit: int = 50) -> List[Interaction]:
        return self.repo.list(offset=offset, limit=limit, filters={"company_id": company_id})

    def create(self, data: Dict[str, Any]) -> Interaction:
        return self.repo.create(data)

    def delete(self, interaction_id: int) -> bool:
        return self.repo.delete(interaction_id)
