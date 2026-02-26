"""Tests for import utilities and import router endpoints.

Covers: import_companies_csv, import_companies_json,
import_contacts_csv, import_contacts_json, ImportResult,
and all 4 import router endpoints.
"""

import io
import json
import pytest
from unittest.mock import MagicMock

from app.models import Company, Contact
from app.utils.import_ import (
    ImportResult,
    import_companies_csv, import_companies_json,
    import_contacts_csv, import_contacts_json,
)


# ═══════════════════════════════════════════════════════════════
# ImportResult
# ═══════════════════════════════════════════════════════════════

class TestImportResult:

    def test_initial_state(self):
        r = ImportResult()
        assert r.successful == 0
        assert r.failed == 0
        assert r.errors == []
        assert r.warnings == []

    def test_to_dict(self):
        r = ImportResult()
        r.successful = 3
        r.failed = 1
        r.errors = ["Row 2: bad"]
        r.warnings = ["Row 3: dup"]
        d = r.to_dict()
        assert d == {
            "successful": 3, "failed": 1,
            "errors": ["Row 2: bad"], "warnings": ["Row 3: dup"],
        }


# ═══════════════════════════════════════════════════════════════
# import_companies_csv
# ═══════════════════════════════════════════════════════════════

class TestImportCompaniesCsv:

    def test_valid_csv(self, db_session):
        csv = "name,company_type,sector\nAcme Inc,buyer,tech\nGlobex,seller,finance\n"
        result = import_companies_csv(db_session, csv)
        assert result.successful == 2
        assert result.failed == 0
        assert db_session.query(Company).count() >= 2

    def test_missing_name(self, db_session):
        csv = "name,company_type\n,buyer\n"
        result = import_companies_csv(db_session, csv)
        assert result.failed == 1
        assert "Missing required field 'name'" in result.errors[0]

    def test_duplicate_company(self, db_session):
        db_session.add(Company(name="DupCo", tenant_id="default"))
        db_session.commit()
        csv = "name\nDupCo\n"
        result = import_companies_csv(db_session, csv)
        assert result.failed == 1
        assert "already exists" in result.warnings[0]

    def test_malformed_csv(self, db_session):
        result = import_companies_csv(db_session, "")
        # Empty CSV – no headers, no rows
        assert result.successful == 0

    def test_csv_with_extra_fields(self, db_session):
        csv = "name,company_type,sector,annual_revenue,employee_count\nTestCo,buyer,tech,1000000,50\n"
        result = import_companies_csv(db_session, csv)
        assert result.successful == 1


# ═══════════════════════════════════════════════════════════════
# import_companies_json
# ═══════════════════════════════════════════════════════════════

class TestImportCompaniesJson:

    def test_valid_json(self, db_session):
        data = json.dumps([
            {"name": "JSON Co A", "company_type": "buyer"},
            {"name": "JSON Co B", "sector": "tech"},
        ])
        result = import_companies_json(db_session, data)
        assert result.successful == 2
        assert result.failed == 0

    def test_not_array(self, db_session):
        result = import_companies_json(db_session, '{"name": "single"}')
        assert result.failed == 1
        assert "array" in result.errors[0].lower() or "JSON" in result.errors[0]

    def test_missing_name(self, db_session):
        data = json.dumps([{"company_type": "buyer"}])
        result = import_companies_json(db_session, data)
        assert result.failed == 1
        assert "Missing required field 'name'" in result.errors[0]

    def test_duplicate_company(self, db_session):
        db_session.add(Company(name="ExistCo", tenant_id="default"))
        db_session.commit()
        data = json.dumps([{"name": "ExistCo"}])
        result = import_companies_json(db_session, data)
        assert result.failed == 1
        assert "already exists" in result.warnings[0]

    def test_invalid_json(self, db_session):
        result = import_companies_json(db_session, "not json at all")
        assert result.failed == 1
        assert "JSON parsing error" in result.errors[0]


# ═══════════════════════════════════════════════════════════════
# import_contacts_csv
# ═══════════════════════════════════════════════════════════════

class TestImportContactsCsv:

    def test_valid_csv(self, db_session):
        csv = "first_name,last_name,email,job_title,decision_maker\nAlice,Smith,alice@test.com,CEO,true\n"
        result = import_contacts_csv(db_session, csv)
        assert result.successful == 1

    def test_missing_email(self, db_session):
        csv = "first_name,last_name,email\nBob,Jones,\n"
        result = import_contacts_csv(db_session, csv)
        assert result.failed == 1
        assert "Missing required field 'email'" in result.errors[0]

    def test_duplicate_contact(self, db_session):
        db_session.add(Contact(
            first_name="Dup", last_name="Contact",
            email="dup@test.com", tenant_id="default",
        ))
        db_session.commit()
        csv = "first_name,last_name,email\nDup,Contact,dup@test.com\n"
        result = import_contacts_csv(db_session, csv)
        assert result.failed == 1
        assert "already exists" in result.warnings[0]

    def test_invalid_company_id(self, db_session):
        csv = "first_name,last_name,email,company_id\nTest,User,test@inv.com,99999\n"
        result = import_contacts_csv(db_session, csv)
        assert result.failed == 1
        assert "not found" in result.errors[0]

    def test_valid_company_id(self, db_session):
        co = Company(name="ValidCo", tenant_id="default")
        db_session.add(co)
        db_session.commit()
        csv = f"first_name,last_name,email,company_id\nTest,User,test@valid.com,{co.id}\n"
        result = import_contacts_csv(db_session, csv)
        assert result.successful == 1

    def test_no_headers(self, db_session):
        result = import_contacts_csv(db_session, "")
        assert result.successful == 0


# ═══════════════════════════════════════════════════════════════
# import_contacts_json
# ═══════════════════════════════════════════════════════════════

class TestImportContactsJson:

    def test_valid_json(self, db_session):
        data = json.dumps([
            {"first_name": "A", "last_name": "B", "email": "a@b.com"},
        ])
        result = import_contacts_json(db_session, data)
        assert result.successful == 1

    def test_not_array(self, db_session):
        result = import_contacts_json(db_session, '{"email": "single@t.com"}')
        assert result.failed == 1

    def test_missing_email(self, db_session):
        data = json.dumps([{"first_name": "No Email"}])
        result = import_contacts_json(db_session, data)
        assert result.failed == 1

    def test_duplicate_contact(self, db_session):
        db_session.add(Contact(
            first_name="Dup", last_name="J", email="dup2@t.com", tenant_id="default",
        ))
        db_session.commit()
        data = json.dumps([{"email": "dup2@t.com"}])
        result = import_contacts_json(db_session, data)
        assert result.failed == 1

    def test_invalid_company_id(self, db_session):
        data = json.dumps([{"email": "x@t.com", "company_id": 99999}])
        result = import_contacts_json(db_session, data)
        assert result.failed == 1
        assert "not found" in result.errors[0]

    def test_invalid_json(self, db_session):
        result = import_contacts_json(db_session, "{{bad json")
        assert result.failed == 1

    def test_with_all_fields(self, db_session):
        data = json.dumps([{
            "first_name": "Full", "last_name": "Contact",
            "email": "full@t.com", "job_title": "CTO",
            "decision_maker": True,
        }])
        result = import_contacts_json(db_session, data)
        assert result.successful == 1


# ═══════════════════════════════════════════════════════════════
# Import Router Endpoints
# ═══════════════════════════════════════════════════════════════

class TestImportEndpoints:

    def _make_upload(self, content: str, filename: str = "data.csv"):
        return {"file": (filename, io.BytesIO(content.encode()), "text/csv")}

    def test_import_companies_csv_endpoint(self, admin_client):
        files = self._make_upload("name,company_type\nImport Co,buyer\n")
        resp = admin_client.post("/import/companies/csv", files=files)
        assert resp.status_code == 200
        assert resp.json()["successful"] == 1

    def test_import_companies_json_endpoint(self, admin_client):
        content = json.dumps([{"name": "Import JSON Co"}])
        files = {"file": ("data.json", io.BytesIO(content.encode()), "application/json")}
        resp = admin_client.post("/import/companies/json", files=files)
        assert resp.status_code == 200
        assert resp.json()["successful"] == 1

    def test_import_contacts_csv_endpoint(self, admin_client):
        files = self._make_upload("first_name,last_name,email\nA,B,imp@t.com\n")
        resp = admin_client.post("/import/contacts/csv", files=files)
        assert resp.status_code == 200
        assert resp.json()["successful"] == 1

    def test_import_contacts_json_endpoint(self, admin_client):
        content = json.dumps([{"email": "impj@t.com", "first_name": "I"}])
        files = {"file": ("data.json", io.BytesIO(content.encode()), "application/json")}
        resp = admin_client.post("/import/contacts/json", files=files)
        assert resp.status_code == 200
        assert resp.json()["successful"] == 1
