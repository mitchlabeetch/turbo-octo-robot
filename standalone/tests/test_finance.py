"""Tests for the Financial Engine (ERP Core)."""

from datetime import date
from decimal import Decimal

import pytest

from app.services.finance import AccountingService, InvoiceService, VendorService


class TestChartOfAccounts:
    """Verify Chart of Accounts operations."""

    def test_seed_defaults(self, db_session):
        svc = AccountingService(db_session, tenant_id="default")
        accounts = svc.seed_default_accounts()
        assert len(accounts) >= 20  # 22 default accounts

    def test_seed_is_idempotent(self, db_session):
        svc = AccountingService(db_session, tenant_id="default")
        svc.seed_default_accounts()
        accounts = svc.seed_default_accounts()
        assert len(accounts) >= 20

    def test_create_custom_account(self, db_session):
        svc = AccountingService(db_session, tenant_id="default")
        acct = svc.create_account({
            "code": "9999",
            "name": "Test Account",
            "account_type": "expense",
        })
        assert acct.code == "9999"
        assert acct.uuid is not None

    def test_list_by_type(self, db_session):
        svc = AccountingService(db_session, tenant_id="default")
        svc.seed_default_accounts()
        revenue = svc.list_accounts(account_type="revenue")
        assert all(a.account_type == "revenue" for a in revenue)


class TestJournalEntries:
    """Verify General Ledger operations."""

    def _setup(self, db_session):
        svc = AccountingService(db_session, tenant_id="default")
        accounts = svc.seed_default_accounts()
        # Find cash (1010) and revenue (4010)
        cash = next(a for a in accounts if a.code == "1010")
        revenue = next(a for a in accounts if a.code == "4010")
        return svc, cash, revenue

    def test_create_balanced_entry(self, db_session):
        svc, cash, revenue = self._setup(db_session)
        je = svc.create_journal_entry(
            entry_date=date(2026, 1, 15),
            reference="INV-001",
            memo="Advisory fee Q1",
            lines=[
                {"account_id": cash.id, "debit": Decimal("10000"), "credit": Decimal("0")},
                {"account_id": revenue.id, "debit": Decimal("0"), "credit": Decimal("10000")},
            ],
        )
        assert je.id is not None
        assert je.status == "draft"
        assert len(je.lines) == 2

    def test_unbalanced_entry_raises(self, db_session):
        svc, cash, revenue = self._setup(db_session)
        with pytest.raises(ValueError, match="out of balance"):
            svc.create_journal_entry(
                entry_date=date(2026, 1, 15),
                lines=[
                    {"account_id": cash.id, "debit": Decimal("10000"), "credit": Decimal("0")},
                    {"account_id": revenue.id, "debit": Decimal("0"), "credit": Decimal("5000")},
                ],
            )

    def test_post_journal_entry(self, db_session, test_user):
        svc, cash, revenue = self._setup(db_session)
        je = svc.create_journal_entry(
            entry_date=date(2026, 1, 15),
            lines=[
                {"account_id": cash.id, "debit": Decimal("10000"), "credit": Decimal("0")},
                {"account_id": revenue.id, "debit": Decimal("0"), "credit": Decimal("10000")},
            ],
        )
        posted = svc.post_journal_entry(je.id, test_user.id)
        assert posted.status == "posted"
        assert posted.posted_at is not None

    def test_account_balance(self, db_session, test_user):
        svc, cash, revenue = self._setup(db_session)
        je = svc.create_journal_entry(
            entry_date=date(2026, 1, 15),
            auto_post=True,
            user_id=test_user.id,
            lines=[
                {"account_id": cash.id, "debit": Decimal("15000"), "credit": Decimal("0")},
                {"account_id": revenue.id, "debit": Decimal("0"), "credit": Decimal("15000")},
            ],
        )
        cash_balance = svc.get_account_balance(cash.id)
        assert cash_balance == Decimal("15000")
        revenue_balance = svc.get_account_balance(revenue.id)
        assert revenue_balance == Decimal("-15000")  # credit balance = negative


class TestInvoicing:
    """Verify invoice lifecycle."""

    def test_create_invoice_with_lines(self, db_session):
        svc = InvoiceService(db_session, tenant_id="default")
        inv = svc.create({
            "invoice_date": date(2026, 1, 1),
            "due_date": date(2026, 1, 31),
            "lines": [
                {"description": "Advisory retainer", "unit_price": Decimal("5000"), "quantity": Decimal("1")},
                {"description": "Due diligence", "unit_price": Decimal("3000"), "quantity": Decimal("2")},
            ],
        })
        assert inv.invoice_number == "INV-00001"
        assert inv.subtotal == Decimal("11000")
        assert inv.total == Decimal("11000")
        assert inv.balance_due == Decimal("11000")

    def test_invoice_with_tax(self, db_session):
        svc = InvoiceService(db_session, tenant_id="default")
        inv = svc.create({
            "invoice_date": date(2026, 1, 1),
            "due_date": date(2026, 2, 1),
            "lines": [
                {"description": "Service", "unit_price": Decimal("10000"), "tax_rate": Decimal("20")},
            ],
        })
        assert inv.subtotal == Decimal("10000")
        assert inv.tax_amount == Decimal("2000")
        assert inv.total == Decimal("12000")

    def test_record_full_payment(self, db_session):
        svc = InvoiceService(db_session, tenant_id="default")
        inv = svc.create({
            "invoice_date": date(2026, 1, 1),
            "due_date": date(2026, 1, 31),
            "lines": [{"description": "Service", "unit_price": Decimal("5000")}],
        })
        payment = svc.record_payment(inv.id, {
            "payment_date": date(2026, 1, 20),
            "amount": Decimal("5000"),
        })
        assert payment.amount == Decimal("5000")
        # Refresh invoice
        inv = svc.get(inv.id)
        assert inv.status == "paid"
        assert inv.balance_due == Decimal("0")

    def test_partial_payment(self, db_session):
        svc = InvoiceService(db_session, tenant_id="default")
        inv = svc.create({
            "invoice_date": date(2026, 1, 1),
            "due_date": date(2026, 1, 31),
            "lines": [{"description": "Service", "unit_price": Decimal("10000")}],
        })
        svc.record_payment(inv.id, {
            "payment_date": date(2026, 1, 15),
            "amount": Decimal("3000"),
        })
        inv = svc.get(inv.id)
        assert inv.status == "partially_paid"
        assert inv.balance_due == Decimal("7000")


class TestVendorAndBills:
    """Verify AP operations."""

    def test_create_vendor(self, db_session):
        svc = VendorService(db_session, tenant_id="default")
        vendor = svc.create({"name": "Law Firm LLP", "contact_email": "billing@lawfirm.com"})
        assert vendor.uuid is not None
        assert vendor.name == "Law Firm LLP"

    def test_create_bill(self, db_session):
        svc = VendorService(db_session, tenant_id="default")
        vendor = svc.create({"name": "Consulting Inc"})
        bill = svc.create_bill(vendor.id, {
            "bill_date": date(2026, 1, 1),
            "due_date": date(2026, 2, 1),
            "lines": [
                {"description": "Legal review", "unit_price": Decimal("8000")},
                {"description": "Data room setup", "unit_price": Decimal("2000")},
            ],
        })
        assert bill.subtotal == Decimal("10000")
        assert bill.total == Decimal("10000")


class TestFinanceEndpoints:
    """Verify finance REST API."""

    def test_list_accounts(self, auth_client):
        response = auth_client.get("/finance/accounts")
        assert response.status_code == 200
        accounts = response.json()
        assert len(accounts) >= 20

    def test_create_invoice(self, auth_client):
        response = auth_client.post("/finance/invoices", json={
            "invoice_date": "2026-01-01",
            "due_date": "2026-01-31",
            "lines": [
                {"description": "Advisory fee", "unit_price": "5000"},
            ],
        })
        assert response.status_code == 200
        inv = response.json()
        assert inv["invoice_number"] == "INV-00001"
        assert inv["total"] == "5000.00"

    def test_record_payment_api(self, auth_client):
        # Create invoice first
        inv = auth_client.post("/finance/invoices", json={
            "invoice_date": "2026-02-01",
            "due_date": "2026-02-28",
            "lines": [{"description": "Fee", "unit_price": "8000"}],
        }).json()
        # Record payment
        pay = auth_client.post(f"/finance/invoices/{inv['id']}/payments", json={
            "payment_date": "2026-02-15",
            "amount": "8000",
        })
        assert pay.status_code == 200

    def test_create_journal_entry_api(self, auth_client):
        accounts = auth_client.get("/finance/accounts").json()
        cash = next(a for a in accounts if a["code"] == "1010")
        revenue = next(a for a in accounts if a["code"] == "4010")
        response = auth_client.post("/finance/journal-entries", json={
            "entry_date": "2026-01-15",
            "reference": "JE-001",
            "lines": [
                {"account_id": cash["id"], "debit": "10000", "credit": "0"},
                {"account_id": revenue["id"], "debit": "0", "credit": "10000"},
            ],
        })
        assert response.status_code == 200
        assert response.json()["status"] == "draft"

    def test_unbalanced_je_rejected(self, auth_client):
        accounts = auth_client.get("/finance/accounts").json()
        cash = next(a for a in accounts if a["code"] == "1010")
        revenue = next(a for a in accounts if a["code"] == "4010")
        response = auth_client.post("/finance/journal-entries", json={
            "entry_date": "2026-01-15",
            "lines": [
                {"account_id": cash["id"], "debit": "10000", "credit": "0"},
                {"account_id": revenue["id"], "debit": "0", "credit": "5000"},
            ],
        })
        assert response.status_code == 400

    def test_create_vendor_api(self, auth_client):
        response = auth_client.post("/finance/vendors", json={
            "name": "API Vendor",
            "contact_email": "vendor@test.com",
        })
        assert response.status_code == 200
        assert response.json()["name"] == "API Vendor"
