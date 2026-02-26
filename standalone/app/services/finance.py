"""
Financial service: Business logic for the ERP core.

Handles: Chart of Accounts, General Ledger (double-entry),
Invoice lifecycle, Payment processing, and accounting integrity.
"""

import itertools
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.finance import (
    Account, Bill, BillLine, Currency, ExchangeRate,
    ExpenseReport, ExpenseItem, FiscalYear, FiscalPeriod,
    Invoice, InvoiceLine, JournalEntry, JournalEntryLine,
    Payment, Vendor,
)
from app.services.base_repository import BaseRepository


# ── Default Chart of Accounts ────────────────────────────────
DEFAULT_ACCOUNTS = [
    # Assets
    {"code": "1000", "name": "Cash and Bank", "account_type": "asset", "is_header": True},
    {"code": "1010", "name": "Checking Account", "account_type": "asset"},
    {"code": "1100", "name": "Accounts Receivable", "account_type": "asset"},
    {"code": "1200", "name": "Prepaid Expenses", "account_type": "asset"},
    # Liabilities
    {"code": "2000", "name": "Current Liabilities", "account_type": "liability", "is_header": True},
    {"code": "2100", "name": "Accounts Payable", "account_type": "liability"},
    {"code": "2200", "name": "Accrued Expenses", "account_type": "liability"},
    {"code": "2300", "name": "Tax Payable", "account_type": "liability"},
    # Equity
    {"code": "3000", "name": "Equity", "account_type": "equity", "is_header": True},
    {"code": "3100", "name": "Retained Earnings", "account_type": "equity"},
    # Revenue
    {"code": "4000", "name": "Revenue", "account_type": "revenue", "is_header": True},
    {"code": "4010", "name": "Advisory Fees", "account_type": "revenue"},
    {"code": "4020", "name": "Retainer Fees", "account_type": "revenue"},
    {"code": "4030", "name": "Success Fees", "account_type": "revenue"},
    {"code": "4090", "name": "Other Revenue", "account_type": "revenue"},
    # Expenses
    {"code": "5000", "name": "Operating Expenses", "account_type": "expense", "is_header": True},
    {"code": "5010", "name": "Salaries & Wages", "account_type": "expense"},
    {"code": "5020", "name": "Professional Services", "account_type": "expense"},
    {"code": "5030", "name": "Travel & Entertainment", "account_type": "expense"},
    {"code": "5040", "name": "Office Expenses", "account_type": "expense"},
    {"code": "5050", "name": "Technology & Software", "account_type": "expense"},
    {"code": "5090", "name": "Miscellaneous Expenses", "account_type": "expense"},
]


class AccountingService:
    """Business logic for chart of accounts and general ledger."""

    def __init__(self, db: Session, tenant_id: str = "default"):
        self.db = db
        self.tenant_id = tenant_id
        self.account_repo = BaseRepository(Account, db, tenant_id)

    # ── Chart of Accounts ────────────────────────────────────

    def seed_default_accounts(self) -> List[Account]:
        """Seed default chart of accounts. Idempotent."""
        existing = self.account_repo.count()
        if existing > 0:
            return self.account_repo.list(limit=100, order_by="code")

        accounts = []
        for a in DEFAULT_ACCOUNTS:
            acct = Account(tenant_id=self.tenant_id, **a)
            self.db.add(acct)
            accounts.append(acct)
        self.db.commit()
        for a in accounts:
            self.db.refresh(a)
        return accounts

    def list_accounts(self, account_type: Optional[str] = None) -> List[Account]:
        filters = {}
        if account_type:
            filters["account_type"] = account_type
        return self.account_repo.list(limit=200, filters=filters, order_by="code")

    def create_account(self, data: Dict[str, Any]) -> Account:
        return self.account_repo.create(data)

    # ── Journal Entries (GL) ─────────────────────────────────

    def create_journal_entry(
        self,
        entry_date: date,
        lines: List[Dict[str, Any]],
        reference: Optional[str] = None,
        memo: Optional[str] = None,
        source_type: Optional[str] = None,
        source_id: Optional[int] = None,
        auto_post: bool = False,
        user_id: Optional[int] = None,
    ) -> JournalEntry:
        """Create a balanced journal entry with lines."""
        # Validate: sum(debits) == sum(credits)
        total_debit = sum(Decimal(str(l.get("debit", 0))) for l in lines)
        total_credit = sum(Decimal(str(l.get("credit", 0))) for l in lines)
        if total_debit != total_credit:
            raise ValueError(
                f"Journal entry out of balance: debits={total_debit}, credits={total_credit}"
            )

        je = JournalEntry(
            entry_date=entry_date,
            reference=reference,
            memo=memo,
            status="posted" if auto_post else "draft",
            source_type=source_type,
            source_id=source_id,
            tenant_id=self.tenant_id,
        )
        if auto_post:
            je.posted_by_id = user_id
            je.posted_at = datetime.now(timezone.utc)

        self.db.add(je)
        self.db.flush()  # Get the ID

        for line_data in lines:
            rate = Decimal(str(line_data.get("exchange_rate", 1)))
            debit = Decimal(str(line_data.get("debit", 0)))
            credit = Decimal(str(line_data.get("credit", 0)))
            jel = JournalEntryLine(
                journal_entry_id=je.id,
                account_id=line_data["account_id"],
                debit=debit,
                credit=credit,
                currency=line_data.get("currency", "EUR"),
                exchange_rate=rate,
                base_debit=debit * rate,
                base_credit=credit * rate,
                description=line_data.get("description"),
                tenant_id=self.tenant_id,
            )
            self.db.add(jel)

        self.db.commit()
        self.db.refresh(je)
        return je

    def post_journal_entry(self, je_id: int, user_id: int) -> JournalEntry:
        """Post a draft journal entry."""
        je = self.db.query(JournalEntry).filter(JournalEntry.id == je_id).first()
        if not je:
            raise ValueError("Journal entry not found")
        if je.status != "draft":
            raise ValueError(f"Cannot post entry in '{je.status}' status")
        je.status = "posted"
        je.posted_by_id = user_id
        je.posted_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(je)
        return je

    def list_journal_entries(self, *, offset: int = 0, limit: int = 50, status: Optional[str] = None) -> List[JournalEntry]:
        q = self.db.query(JournalEntry).filter(
            JournalEntry.tenant_id == self.tenant_id,
            JournalEntry.is_deleted == False,  # noqa: E712
        )
        if status:
            q = q.filter(JournalEntry.status == status)
        return q.order_by(JournalEntry.entry_date.desc()).offset(offset).limit(limit).all()

    def get_account_balance(self, account_id: int) -> Decimal:
        """Get net balance for an account from all posted journal entries."""
        lines = (
            self.db.query(JournalEntryLine)
            .join(JournalEntry)
            .filter(
                JournalEntryLine.account_id == account_id,
                JournalEntryLine.tenant_id == self.tenant_id,
                JournalEntry.status == "posted",
            )
            .all()
        )
        total_debit = sum(l.base_debit or Decimal(0) for l in lines)
        total_credit = sum(l.base_credit or Decimal(0) for l in lines)
        return total_debit - total_credit


class InvoiceService:
    """Business logic for invoicing (Accounts Receivable)."""

    def __init__(self, db: Session, tenant_id: str = "default"):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = BaseRepository(Invoice, db, tenant_id)
        self.accounting = AccountingService(db, tenant_id)

    def _next_invoice_number(self) -> str:
        """Generate sequential invoice number."""
        count = self.repo.count() + 1
        return f"INV-{count:05d}"

    def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Invoice:
        """Create an invoice with lines and compute totals."""
        lines_data = data.pop("lines", [])

        invoice = Invoice(
            invoice_number=self._next_invoice_number(),
            tenant_id=self.tenant_id,
            **data,
        )
        self.db.add(invoice)
        self.db.flush()

        subtotal = Decimal(0)
        tax_total = Decimal(0)
        for ld in lines_data:
            qty = Decimal(str(ld.get("quantity", 1)))
            price = Decimal(str(ld["unit_price"]))
            tax_rate = Decimal(str(ld.get("tax_rate", 0)))
            line_total = qty * price
            tax_amount = line_total * tax_rate / 100
            line = InvoiceLine(
                invoice_id=invoice.id,
                description=ld["description"],
                quantity=qty,
                unit_price=price,
                tax_rate=tax_rate,
                line_total=line_total,
                tax_amount=tax_amount,
                account_id=ld.get("account_id"),
                tenant_id=self.tenant_id,
            )
            self.db.add(line)
            subtotal += line_total
            tax_total += tax_amount

        invoice.subtotal = subtotal
        invoice.tax_amount = tax_total
        invoice.total = subtotal + tax_total
        invoice.balance_due = invoice.total

        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get(self, invoice_id: int) -> Optional[Invoice]:
        return self.repo.get_by_id(invoice_id)

    def list(self, *, offset: int = 0, limit: int = 50, status: Optional[str] = None) -> List[Invoice]:
        filters = {}
        if status:
            filters["status"] = status
        return self.repo.list(offset=offset, limit=limit, filters=filters)

    def count(self, **filters) -> int:
        return self.repo.count(filters=filters)

    def record_payment(self, invoice_id: int, data: Dict[str, Any]) -> Payment:
        """Record a payment against an invoice, update balance."""
        invoice = self.get(invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")

        payment = Payment(
            invoice_id=invoice_id,
            tenant_id=self.tenant_id,
            **data,
        )
        self.db.add(payment)

        amount = Decimal(str(data["amount"]))
        invoice.amount_paid += amount
        invoice.balance_due = invoice.total - invoice.amount_paid

        if invoice.balance_due <= 0:
            invoice.status = "paid"
        else:
            invoice.status = "partially_paid"

        self.db.commit()
        self.db.refresh(payment)
        return payment


class VendorService:
    """Business logic for vendor management and AP."""

    def __init__(self, db: Session, tenant_id: str = "default"):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = BaseRepository(Vendor, db, tenant_id)

    def create(self, data: Dict[str, Any]) -> Vendor:
        return self.repo.create(data)

    def get(self, vendor_id: int) -> Optional[Vendor]:
        return self.repo.get_by_id(vendor_id)

    def list(self, *, offset: int = 0, limit: int = 50) -> List[Vendor]:
        return self.repo.list(offset=offset, limit=limit)

    def create_bill(self, vendor_id: int, data: Dict[str, Any]) -> Bill:
        """Create a vendor bill with lines and compute totals."""
        lines_data = data.pop("lines", [])
        data.pop("vendor_id", None)  # Avoid duplicate kwarg
        bill = Bill(vendor_id=vendor_id, tenant_id=self.tenant_id, **data)
        self.db.add(bill)
        self.db.flush()

        subtotal = Decimal(0)
        tax_total = Decimal(0)
        for ld in lines_data:
            qty = Decimal(str(ld.get("quantity", 1)))
            price = Decimal(str(ld["unit_price"]))
            tax_rate = Decimal(str(ld.get("tax_rate", 0)))
            line_total = qty * price
            line = BillLine(
                bill_id=bill.id,
                description=ld["description"],
                quantity=qty,
                unit_price=price,
                tax_rate=tax_rate,
                line_total=line_total,
                account_id=ld.get("account_id"),
                tenant_id=self.tenant_id,
            )
            self.db.add(line)
            subtotal += line_total
            tax_total += line_total * tax_rate / 100

        bill.subtotal = subtotal
        bill.tax_amount = tax_total
        bill.total = subtotal + tax_total
        self.db.commit()
        self.db.refresh(bill)
        return bill
