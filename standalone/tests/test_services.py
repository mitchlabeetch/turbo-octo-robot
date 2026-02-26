"""Tests for the base repository pattern and CRM services."""

import pytest

from app.models.crm import Company, Contact
from app.services.base_repository import BaseRepository
from app.services.crm import CompanyService, ContactService, InteractionService


class TestBaseRepository:
    """Verify generic CRUD operations."""

    def test_create_and_get(self, db_session):
        repo = BaseRepository(Company, db_session, tenant_id="default")
        company = repo.create({"name": "TestCo"})
        assert company.id is not None
        fetched = repo.get_by_id(company.id)
        assert fetched is not None
        assert fetched.name == "TestCo"

    def test_list_with_pagination(self, db_session):
        repo = BaseRepository(Company, db_session, tenant_id="default")
        for i in range(5):
            repo.create({"name": f"Co-{i}"})
        all_items = repo.list(offset=0, limit=10)
        assert len(all_items) == 5
        page = repo.list(offset=0, limit=2)
        assert len(page) == 2

    def test_tenant_isolation(self, db_session):
        repo_a = BaseRepository(Company, db_session, tenant_id="tenant-a")
        repo_b = BaseRepository(Company, db_session, tenant_id="tenant-b")
        repo_a.create({"name": "A-Corp"})
        repo_b.create({"name": "B-Corp"})
        assert repo_a.count() == 1
        assert repo_b.count() == 1
        assert repo_a.list()[0].name == "A-Corp"
        assert repo_b.list()[0].name == "B-Corp"

    def test_soft_delete(self, db_session):
        repo = BaseRepository(Company, db_session, tenant_id="default")
        company = repo.create({"name": "DeleteMe"})
        assert repo.count() == 1
        repo.delete(company.id)
        assert repo.count() == 0  # Soft-deleted, excluded from queries

    def test_hard_delete(self, db_session):
        repo = BaseRepository(Company, db_session, tenant_id="default")
        company = repo.create({"name": "HardDelete"})
        repo.delete(company.id, hard=True)
        # Verify truly gone from DB
        result = db_session.query(Company).filter(Company.id == company.id).first()
        assert result is None

    def test_update(self, db_session):
        repo = BaseRepository(Company, db_session, tenant_id="default")
        company = repo.create({"name": "Old Name"})
        updated = repo.update(company.id, {"name": "New Name"})
        assert updated.name == "New Name"

    def test_get_by_uuid(self, db_session):
        repo = BaseRepository(Company, db_session, tenant_id="default")
        company = repo.create({"name": "UUID Test"})
        fetched = repo.get_by_uuid(company.uuid)
        assert fetched is not None
        assert fetched.id == company.id

    def test_count_with_filters(self, db_session):
        repo = BaseRepository(Company, db_session, tenant_id="default")
        repo.create({"name": "Tech Co", "sector": "Technology"})
        repo.create({"name": "Finance Co", "sector": "Finance"})
        repo.create({"name": "Another Tech", "sector": "Technology"})
        assert repo.count(filters={"sector": "Technology"}) == 2
        assert repo.count(filters={"sector": "Finance"}) == 1


class TestCompanyService:
    """Verify CompanyService business logic."""

    def test_create_company(self, db_session):
        svc = CompanyService(db_session, tenant_id="default")
        company = svc.create({"name": "New Corp"})
        assert company.name == "New Corp"

    def test_duplicate_company_raises(self, db_session):
        svc = CompanyService(db_session, tenant_id="default")
        svc.create({"name": "Unique"})
        with pytest.raises(ValueError, match="already exists"):
            svc.create({"name": "Unique"})

    def test_list_companies(self, db_session):
        svc = CompanyService(db_session, tenant_id="default")
        svc.create({"name": "A"})
        svc.create({"name": "B"})
        assert len(svc.list()) == 2


class TestContactService:
    """Verify ContactService business logic."""

    def test_create_contact(self, db_session):
        svc = ContactService(db_session, tenant_id="default")
        contact = svc.create({
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com"
        })
        assert contact.email == "john@example.com"

    def test_duplicate_email_raises(self, db_session):
        svc = ContactService(db_session, tenant_id="default")
        svc.create({"first_name": "A", "last_name": "B", "email": "dup@example.com"})
        with pytest.raises(ValueError, match="already exists"):
            svc.create({"first_name": "C", "last_name": "D", "email": "dup@example.com"})

    def test_get_by_email(self, db_session):
        svc = ContactService(db_session, tenant_id="default")
        svc.create({"first_name": "Find", "last_name": "Me", "email": "find@test.com"})
        found = svc.get_by_email("find@test.com")
        assert found is not None
        assert found.first_name == "Find"
