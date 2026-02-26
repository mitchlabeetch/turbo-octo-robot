"""Tests for base model mixins and infrastructure."""

import uuid
from datetime import datetime

from app.models.base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin
from app.models.crm import Company, Contact, Interaction
from app.models.docs import Document, DocumentShare, AccessLog
from app.models.auth import User


class TestModelMixins:
    """Verify that all models have the expected mixin columns."""

    def test_company_has_timestamps(self, db_session):
        c = Company(name="Test Corp", tenant_id="default")
        db_session.add(c)
        db_session.commit()
        db_session.refresh(c)
        assert c.created_at is not None
        assert c.updated_at is not None

    def test_company_has_soft_delete(self, db_session):
        c = Company(name="Test Corp", tenant_id="default")
        db_session.add(c)
        db_session.commit()
        assert c.is_deleted is False
        c.soft_delete()
        db_session.commit()
        assert c.is_deleted is True
        assert c.deleted_at is not None

    def test_company_restore(self, db_session):
        c = Company(name="Test Corp", tenant_id="default")
        db_session.add(c)
        db_session.commit()
        c.soft_delete()
        db_session.commit()
        c.restore()
        db_session.commit()
        assert c.is_deleted is False
        assert c.deleted_at is None

    def test_company_has_tenant_id(self, db_session):
        c = Company(name="Test Corp", tenant_id="tenant-123")
        db_session.add(c)
        db_session.commit()
        assert c.tenant_id == "tenant-123"

    def test_company_has_uuid(self, db_session):
        c = Company(name="Test Corp", tenant_id="default")
        db_session.add(c)
        db_session.commit()
        assert c.uuid is not None
        # Verify it's a valid UUID
        uuid.UUID(c.uuid)

    def test_contact_has_all_mixins(self, db_session):
        c = Contact(
            first_name="John", last_name="Doe",
            email="john@example.com", tenant_id="default"
        )
        db_session.add(c)
        db_session.commit()
        assert c.created_at is not None
        assert c.uuid is not None
        assert c.is_deleted is False
        assert c.tenant_id == "default"

    def test_user_has_all_mixins(self, db_session):
        u = User(
            email="admin@test.com",
            hashed_password="fakehash",
            role="admin",
            tenant_id="default",
        )
        db_session.add(u)
        db_session.commit()
        assert u.created_at is not None
        assert u.uuid is not None
        assert u.is_deleted is False

    def test_document_share_is_expired(self, db_session):
        d = Document(
            document_name="Test", document_type="pdf",
            file_path="/tmp/test.pdf", file_name="test.pdf",
            tenant_id="default"
        )
        db_session.add(d)
        db_session.commit()
        share = DocumentShare(
            document_id=d.id, token="test-token",
            expires_at=datetime(2020, 1, 1),
            tenant_id="default"
        )
        db_session.add(share)
        db_session.commit()
        assert share.is_expired is True


class TestRelationships:
    """Verify model relationships."""

    def test_company_contacts_relationship(self, db_session):
        company = Company(name="Acme", tenant_id="default")
        db_session.add(company)
        db_session.commit()

        contact = Contact(
            first_name="Jane", last_name="Doe",
            email="jane@acme.com", company_id=company.id,
            tenant_id="default"
        )
        db_session.add(contact)
        db_session.commit()

        db_session.refresh(company)
        assert len(company.contacts) == 1
        assert company.contacts[0].email == "jane@acme.com"

    def test_document_shares_relationship(self, db_session):
        doc = Document(
            document_name="NDA", document_type="pdf",
            file_path="/tmp/nda.pdf", file_name="nda.pdf",
            tenant_id="default"
        )
        db_session.add(doc)
        db_session.commit()

        share = DocumentShare(
            document_id=doc.id, token="share-1",
            tenant_id="default"
        )
        db_session.add(share)
        db_session.commit()

        db_session.refresh(doc)
        assert len(doc.shares) == 1
