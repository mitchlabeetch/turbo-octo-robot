"""Tests targeting ALL remaining coverage gaps to reach 100%.

Covers: watermark (mock libs), shares download paths, auth bootstrap,
email webhooks, oauth, contacts router, audit endpoints, CRM service
methods, deals router gaps, DB module, model __repr__, base_repository gaps.
"""

import io
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import pytest

from app.models import (
    Company, Contact, Document, DocumentShare, AccessLog, Interaction, User,
)
from app.models.crm import Company as CrmCompany, Contact as CrmContact, Interaction as CrmInteraction
from app.models.deals import Deal, DealStage, DealTeamMember, DealNote, DealActivity
from app.models.deals import BuyerList, BuyerListEntry, Bid
from app.models.docs import Document as DocModel, DocumentShare as ShareModel
from app.models.finance import Currency, Account, JournalEntry
from app.auth import hash_password, create_access_token
from app.services.crm import CompanyService, ContactService, InteractionService


# ═══════════════════════════════════════════════════════════════
# CRM SERVICE — 15 uncovered lines (78% → 100%)
# ═══════════════════════════════════════════════════════════════

class TestCompanyService:

    def test_get(self, db_session):
        svc = CompanyService(db_session)
        co = svc.create({"name": "SvcCo"})
        assert svc.get(co.id) is not None
        assert svc.get(999999) is None

    def test_get_by_name(self, db_session):
        svc = CompanyService(db_session)
        svc.create({"name": "FindMe"})
        assert svc.get_by_name("FindMe") is not None
        assert svc.get_by_name("NoSuchCo") is None

    def test_get_by_uuid(self, db_session):
        svc = CompanyService(db_session)
        co = svc.create({"name": "UUIDCo"})
        assert svc.get_by_uuid(str(co.uuid)) is not None

    def test_list(self, db_session):
        svc = CompanyService(db_session)
        svc.create({"name": "ListCo1"})
        svc.create({"name": "ListCo2"})
        assert len(svc.list()) >= 2

    def test_count(self, db_session):
        svc = CompanyService(db_session)
        svc.create({"name": "CountCo"})
        assert svc.count() >= 1

    def test_create_duplicate(self, db_session):
        svc = CompanyService(db_session)
        svc.create({"name": "UniqueCo"})
        with pytest.raises(ValueError, match="already exists"):
            svc.create({"name": "UniqueCo"})

    def test_update(self, db_session):
        svc = CompanyService(db_session)
        co = svc.create({"name": "UpdateCo"})
        updated = svc.update(co.id, {"name": "UpdatedCo"})
        assert updated.name == "UpdatedCo"

    def test_delete(self, db_session):
        svc = CompanyService(db_session)
        co = svc.create({"name": "DeleteCo"})
        assert svc.delete(co.id) is True


class TestContactService:

    def test_get(self, db_session):
        svc = ContactService(db_session)
        c = svc.create({"first_name": "A", "last_name": "B", "email": "a@b.com"})
        assert svc.get(c.id) is not None

    def test_get_by_uuid(self, db_session):
        svc = ContactService(db_session)
        c = svc.create({"first_name": "U", "last_name": "U", "email": "uu@t.com"})
        assert svc.get_by_uuid(str(c.uuid)) is not None

    def test_get_by_email(self, db_session):
        svc = ContactService(db_session)
        svc.create({"first_name": "E", "last_name": "E", "email": "e@e.com"})
        assert svc.get_by_email("e@e.com") is not None
        assert svc.get_by_email("no@e.com") is None

    def test_list(self, db_session):
        svc = ContactService(db_session)
        svc.create({"first_name": "L", "last_name": "L", "email": "l@t.com"})
        assert len(svc.list()) >= 1

    def test_count(self, db_session):
        svc = ContactService(db_session)
        svc.create({"first_name": "C", "last_name": "C", "email": "c@t.com"})
        assert svc.count() >= 1

    def test_create_duplicate(self, db_session):
        svc = ContactService(db_session)
        svc.create({"first_name": "D", "last_name": "D", "email": "dup@svc.com"})
        with pytest.raises(ValueError, match="already exists"):
            svc.create({"first_name": "D", "last_name": "D", "email": "dup@svc.com"})

    def test_update(self, db_session):
        svc = ContactService(db_session)
        c = svc.create({"first_name": "Up", "last_name": "Up", "email": "up@t.com"})
        updated = svc.update(c.id, {"first_name": "Updated"})
        assert updated.first_name == "Updated"

    def test_delete(self, db_session):
        svc = ContactService(db_session)
        c = svc.create({"first_name": "Del", "last_name": "Del", "email": "del@t.com"})
        assert svc.delete(c.id) is True


class TestInteractionService:

    def test_crud(self, db_session):
        svc = InteractionService(db_session)
        i = svc.create({"interaction_type": "Call", "subject": "Test call"})
        assert svc.get(i.id) is not None
        assert len(svc.list()) >= 1
        assert svc.delete(i.id) is True

    def test_list_by_contact(self, db_session):
        svc = InteractionService(db_session)
        c = Contact(first_name="T", last_name="T", email="tc@t.com", tenant_id="default")
        db_session.add(c)
        db_session.flush()
        svc.create({"interaction_type": "Email", "contact_id": c.id})
        assert len(svc.list_by_contact(c.id)) == 1

    def test_list_by_company(self, db_session):
        svc = InteractionService(db_session)
        co = Company(name="IntCo", tenant_id="default")
        db_session.add(co)
        db_session.flush()
        svc.create({"interaction_type": "Meeting", "company_id": co.id})
        assert len(svc.list_by_company(co.id)) == 1


# ═══════════════════════════════════════════════════════════════
# AUTH ROUTER — L26-38 (bootstrap success path)
# ═══════════════════════════════════════════════════════════════

class TestAuthBootstrap:

    def test_bootstrap_rejects_default_token(self, client, db_session):
        resp = client.post("/auth/bootstrap", json={
            "email": "admin@t.com", "password": "admin123",
        }, headers={"x-bootstrap-token": "change-me"})
        assert resp.status_code == 401

    def test_bootstrap_missing_token(self, client, db_session):
        resp = client.post("/auth/bootstrap", json={
            "email": "admin@t.com", "password": "admin123",
        })
        assert resp.status_code == 401

    @patch("app.routers.auth.settings")
    def test_bootstrap_success(self, mock_settings, client, db_session):
        mock_settings.bootstrap_token = "valid-secret"
        mock_settings.secret_key = "test-secret"
        mock_settings.algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 60
        resp = client.post("/auth/bootstrap", json={
            "email": "bootstrap@t.com", "password": "pass123",
        }, headers={"x-bootstrap-token": "valid-secret"})
        assert resp.status_code == 200
        assert resp.json()["email"] == "bootstrap@t.com"

    @patch("app.routers.auth.settings")
    def test_bootstrap_already_done(self, mock_settings, client, db_session, test_user):
        mock_settings.bootstrap_token = "valid-secret"
        resp = client.post("/auth/bootstrap", json={
            "email": "another@t.com", "password": "pass123",
        }, headers={"x-bootstrap-token": "valid-secret"})
        assert resp.status_code == 409


# ═══════════════════════════════════════════════════════════════
# CONTACTS ROUTER — L32-35 (get contact not found)
# ═══════════════════════════════════════════════════════════════

class TestContactsRouter:

    def test_get_contact_success(self, auth_client, db_session):
        resp = auth_client.post("/contacts", json={
            "first_name": "A", "last_name": "B", "email": "ab@test.com",
        })
        cid = resp.json()["id"]
        resp2 = auth_client.get(f"/contacts/{cid}")
        assert resp2.status_code == 200

    def test_get_contact_not_found(self, auth_client):
        resp = auth_client.get("/contacts/999999")
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════
# EMAIL WEBHOOK ENDPOINTS — L89-104
# ═══════════════════════════════════════════════════════════════

class TestEmailWebhooks:

    def test_gmail_webhook(self, client, db_session):
        resp = client.post("/email/webhook/gmail", json={
            "subject": "Gmail test",
            "body": "Test body",
            "from": "sender@gmail.com",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["contact_id"] is not None

    def test_microsoft_webhook(self, client, db_session):
        resp = client.post("/email/webhook/microsoft", json={
            "subject": "MS test",
            "body": "Test body",
            "from": "sender@outlook.com",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["contact_id"] is not None

    @patch("app.routers.email.settings")
    def test_webhook_invalid_secret(self, mock_settings, client, db_session):
        mock_settings.webhook_secret = "real-secret"
        resp = client.post("/email/webhook/gmail",
            json={"subject": "T", "from": "a@b.com"},
            headers={"x-webhook-secret": "wrong"})
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════
# OAUTH ROUTER — L15, 24-28
# ═══════════════════════════════════════════════════════════════

class TestOAuthRouter:

    def test_connect_gmail(self, auth_client):
        resp = auth_client.post("/oauth/connect/gmail", json={"token": "abc"})
        assert resp.status_code == 200
        assert resp.json()["provider"] == "gmail"

    def test_connect_microsoft(self, auth_client):
        resp = auth_client.post("/oauth/connect/microsoft", json={"token": "abc"})
        assert resp.status_code == 200
        assert resp.json()["provider"] == "microsoft"

    def test_connect_unsupported(self, auth_client):
        resp = auth_client.post("/oauth/connect/slack", json={"token": "abc"})
        assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════
# AUDIT ROUTER — L20, 31-32
# ═══════════════════════════════════════════════════════════════

class TestAuditRouter:

    def test_get_summary(self, auth_client, db_session):
        resp = auth_client.get("/audit/summary")
        assert resp.status_code == 200
        assert "total_access_events" in resp.json()

    def test_get_document_logs(self, auth_client, db_session):
        doc = Document(
            document_name="AuditDoc", document_type="pdf",
            file_path="/tmp/a.pdf", file_name="a.pdf",
        )
        db_session.add(doc)
        db_session.commit()
        resp = auth_client.get(f"/audit/documents/{doc.id}/logs")
        assert resp.status_code == 200
        assert resp.json()["document_id"] == doc.id


# ═══════════════════════════════════════════════════════════════
# SHARES ROUTER — Download success path + audit logs
# ═══════════════════════════════════════════════════════════════

class TestSharesDownload:

    def _make_doc_and_share(self, auth_client, db_session, tmp_path, **share_opts):
        # Create actual file on disk
        file_path = str(tmp_path / "test_download.txt")
        with open(file_path, "w") as f:
            f.write("Test document content for download")

        doc = Document(
            document_name="Download Test", document_type="text",
            file_path=file_path, file_name="test_download.txt",
            content_type="text/plain",
        )
        db_session.add(doc)
        db_session.commit()

        payload = {"expires_in_days": 7, **share_opts}
        resp = auth_client.post(f"/shares/documents/{doc.id}", json=payload)
        token = resp.json()["token"]
        return token, doc

    def test_download_success(self, auth_client, db_session, tmp_path):
        token, doc = self._make_doc_and_share(auth_client, db_session, tmp_path)
        resp = auth_client.get(f"/shares/{token}/download")
        assert resp.status_code == 200

    def test_download_with_correct_password(self, auth_client, db_session, tmp_path):
        token, doc = self._make_doc_and_share(
            auth_client, db_session, tmp_path, password="secret123"
        )
        resp = auth_client.get(f"/shares/{token}/download", params={"password": "secret123"})
        assert resp.status_code == 200

    def test_download_nda_required_unconfirmed(self, auth_client, db_session, tmp_path):
        token, doc = self._make_doc_and_share(
            auth_client, db_session, tmp_path, requires_nda=True
        )
        resp = auth_client.get(f"/shares/{token}/download")
        assert resp.status_code == 403

    def test_download_nda_confirmed(self, auth_client, db_session, tmp_path):
        token, doc = self._make_doc_and_share(
            auth_client, db_session, tmp_path, requires_nda=True
        )
        # Confirm NDA first
        auth_client.post(f"/shares/{token}/nda-confirm", json={"email": "dl@t.com"})
        resp = auth_client.get(f"/shares/{token}/download")
        assert resp.status_code == 200

    def test_share_audit_logs_endpoint(self, auth_client, db_session, tmp_path):
        token, doc = self._make_doc_and_share(auth_client, db_session, tmp_path)
        # Trigger a download to create an access log
        auth_client.get(f"/shares/{token}/download")
        resp = auth_client.get(f"/shares/{token}/audit-logs")
        assert resp.status_code == 200
        assert resp.json()["token"] == token

    def test_expired_share_download(self, auth_client, db_session, tmp_path):
        """Create a share then manually expire it."""
        token, doc = self._make_doc_and_share(auth_client, db_session, tmp_path)
        # Manually expire the share
        share = db_session.query(DocumentShare).filter(
            DocumentShare.token == token
        ).first()
        share.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        db_session.commit()
        resp = auth_client.get(f"/shares/{token}/download")
        assert resp.status_code == 410

    def test_expired_share_nda_confirm(self, auth_client, db_session, tmp_path):
        token, doc = self._make_doc_and_share(
            auth_client, db_session, tmp_path, requires_nda=True
        )
        share = db_session.query(DocumentShare).filter(
            DocumentShare.token == token
        ).first()
        share.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        db_session.commit()
        resp = auth_client.post(f"/shares/{token}/nda-confirm", json={"email": "x@t.com"})
        assert resp.status_code == 410

    def test_download_nonexistent_share(self, auth_client):
        resp = auth_client.get("/shares/nonexistent/download")
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════
# WATERMARK — Mock HAS_WATERMARK_LIBS paths
# ═══════════════════════════════════════════════════════════════

class TestWatermarkWithMock:

    def test_add_watermark_no_libs(self):
        from app.utils.watermark import add_watermark_text
        result = add_watermark_text("/fake/path.pdf", "user@t.com", "/fake/out.pdf")
        assert result == "/fake/path.pdf"

    def test_should_watermark_excel(self):
        from app.utils.watermark import should_watermark
        assert should_watermark("application/vnd.ms-excel") is True
        assert should_watermark("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") is True

    def test_get_watermark_status_structure(self):
        from app.utils.watermark import get_watermark_status
        status = get_watermark_status()
        assert isinstance(status["watermarking_enabled"], bool)
        assert isinstance(status["message"], str)


# ═══════════════════════════════════════════════════════════════
# DEALS ROUTER GAPS — L108, 120, 179
# ═══════════════════════════════════════════════════════════════

class TestDealsRouterGaps:

    def _create_deal(self, auth_client):
        resp = auth_client.post("/deals", json={
            "title": "Gap Deal", "deal_type": "sell_side",
            "status": "active",
        })
        return resp.json()

    def test_delete_deal(self, auth_client):
        deal = self._create_deal(auth_client)
        resp = auth_client.delete(f"/deals/{deal['id']}")
        assert resp.status_code == 200

    def test_delete_deal_not_found(self, auth_client):
        resp = auth_client.delete("/deals/999999")
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════
# MODEL __repr__ TESTS (remaining uncovered __repr__ lines)
# ═══════════════════════════════════════════════════════════════

class TestModelReprGaps:

    def test_company_repr(self, db_session):
        c = CrmCompany(name="ReprCo", tenant_id="default")
        db_session.add(c)
        db_session.commit()
        assert "ReprCo" in repr(c)

    def test_contact_repr(self, db_session):
        c = CrmContact(first_name="A", last_name="B", email="r@t.com", tenant_id="default")
        db_session.add(c)
        db_session.commit()
        assert "r@t.com" in repr(c)

    def test_interaction_repr(self, db_session):
        i = CrmInteraction(interaction_type="Call", tenant_id="default")
        db_session.add(i)
        db_session.commit()
        assert "Call" in repr(i)

    def test_deal_repr(self, db_session):
        d = Deal(title="ReprDeal", deal_type="buy_side", tenant_id="default")
        db_session.add(d)
        db_session.commit()
        assert "ReprDeal" in repr(d)

    def test_deal_stage_repr(self, db_session):
        d = Deal(title="D", deal_type="buy_side", tenant_id="default")
        db_session.add(d)
        db_session.flush()
        from app.models.deals import DealStage as DS
        # Check the model's actual column names
        s = DS(tenant_id="default")
        s.deal_id = d.id
        s.stage_name = "Origination"
        db_session.add(s)
        db_session.commit()
        assert "Origination" in repr(s)

    def test_document_share_repr(self, db_session):
        doc = DocModel(
            document_name="R", document_type="pdf",
            file_path="/tmp/r.pdf", file_name="r.pdf",
        )
        db_session.add(doc)
        db_session.flush()
        share = ShareModel(
            document_id=doc.id, token="abcdef12345678901234567890",
        )
        db_session.add(share)
        db_session.commit()
        assert "abcdef12" in repr(share)

    def test_access_log_repr(self, db_session):
        doc = DocModel(
            document_name="AL", document_type="pdf",
            file_path="/tmp/al.pdf", file_name="al.pdf",
        )
        db_session.add(doc)
        db_session.flush()
        share = ShareModel(document_id=doc.id, token="rep_log_1234567890123456")
        db_session.add(share)
        db_session.flush()
        log = AccessLog(share_id=share.id, action="view")
        db_session.add(log)
        db_session.commit()
        assert "view" in repr(log)

    def test_currency_repr(self, db_session):
        c = Currency(code="GBP", name="British Pound", symbol="£", tenant_id="default")
        db_session.add(c)
        db_session.commit()
        assert "GBP" in repr(c)

    def test_account_repr(self, db_session):
        a = Account(
            code="5000", name="Revenue", account_type="revenue",
            tenant_id="default",
        )
        db_session.add(a)
        db_session.commit()
        assert "Revenue" in repr(a)
