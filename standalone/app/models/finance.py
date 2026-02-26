"""
Financial models: The ERP core.

Covers: multi-currency, chart of accounts, general ledger,
invoicing, payments, accounts payable, and tax.
"""

from datetime import date

from sqlalchemy import (
    Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin


# ═══════════════════════════════════════════════════════════════
# MULTI-CURRENCY
# ═══════════════════════════════════════════════════════════════

class Currency(Base, TimestampMixin, TenantMixin):
    """Supported currencies with metadata."""
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), nullable=False, index=True)  # ISO 4217
    name = Column(String(100), nullable=False)
    symbol = Column(String(10), nullable=True)
    decimal_places = Column(Integer, default=2)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("code", "tenant_id", name="uq_currency_code_tenant"),
    )

    def __repr__(self) -> str:
        return f"<Currency({self.code})>"


class ExchangeRate(Base, TimestampMixin, TenantMixin):
    """Historical exchange rates for currency conversion."""
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    from_currency = Column(String(3), nullable=False, index=True)
    to_currency = Column(String(3), nullable=False, index=True)
    rate = Column(Numeric(precision=18, scale=8), nullable=False)
    rate_date = Column(Date, nullable=False, index=True)
    source = Column(String(50), default="manual")  # manual, ecb, openexchangerates

    __table_args__ = (
        UniqueConstraint("from_currency", "to_currency", "rate_date", "tenant_id",
                         name="uq_exchange_rate"),
    )

    def __repr__(self) -> str:
        return f"<ExchangeRate({self.from_currency}/{self.to_currency}={self.rate} on {self.rate_date})>"


# ═══════════════════════════════════════════════════════════════
# CHART OF ACCOUNTS & GENERAL LEDGER
# ═══════════════════════════════════════════════════════════════

class FiscalYear(Base, TimestampMixin, TenantMixin):
    """Fiscal year definition."""
    __tablename__ = "fiscal_years"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)  # e.g. "FY 2026"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_closed = Column(Boolean, default=False)

    periods = relationship("FiscalPeriod", back_populates="fiscal_year", lazy="selectin")

    def __repr__(self) -> str:
        return f"<FiscalYear({self.name})>"


class FiscalPeriod(Base, TimestampMixin, TenantMixin):
    """Monthly/quarterly period within a fiscal year."""
    __tablename__ = "fiscal_periods"

    id = Column(Integer, primary_key=True, index=True)
    fiscal_year_id = Column(Integer, ForeignKey("fiscal_years.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)  # e.g. "January 2026"
    period_number = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_closed = Column(Boolean, default=False)

    fiscal_year = relationship("FiscalYear", back_populates="periods")

    def __repr__(self) -> str:
        return f"<FiscalPeriod({self.name})>"


class Account(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """Chart of accounts entry."""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), nullable=False, index=True)  # e.g. "1000", "4010"
    name = Column(String(255), nullable=False)
    account_type = Column(String(20), nullable=False, index=True)  # asset, liability, equity, revenue, expense
    parent_id = Column(Integer, ForeignKey("accounts.id"), nullable=True, index=True)
    description = Column(Text, nullable=True)
    currency = Column(String(3), default="EUR")
    is_header = Column(Boolean, default=False)  # Group header (non-postable)
    is_active = Column(Boolean, default=True)

    parent = relationship("Account", remote_side="Account.id", lazy="joined")

    __table_args__ = (
        UniqueConstraint("code", "tenant_id", name="uq_account_code_tenant"),
        CheckConstraint(
            "account_type IN ('asset', 'liability', 'equity', 'revenue', 'expense')",
            name="ck_account_type",
        ),
    )

    def __repr__(self) -> str:
        return f"<Account({self.code} - {self.name})>"


class JournalEntry(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """General ledger journal entry header."""
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    entry_date = Column(Date, nullable=False, index=True)
    reference = Column(String(100), nullable=True, index=True)
    memo = Column(Text, nullable=True)
    status = Column(String(20), default="draft", index=True)  # draft, posted, void
    fiscal_period_id = Column(Integer, ForeignKey("fiscal_periods.id"), nullable=True, index=True)
    posted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    source_type = Column(String(50), nullable=True)  # manual, invoice, payment, fx_revaluation
    source_id = Column(Integer, nullable=True)  # ID of the originating record

    lines = relationship("JournalEntryLine", back_populates="journal_entry", lazy="selectin", cascade="all, delete-orphan")
    posted_by = relationship("User")

    def __repr__(self) -> str:
        return f"<JournalEntry(id={self.id}, date={self.entry_date}, status='{self.status}')>"


class JournalEntryLine(Base, TimestampMixin, TenantMixin):
    """Individual debit/credit line within a journal entry."""
    __tablename__ = "journal_entry_lines"

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    debit = Column(Numeric(precision=18, scale=2), default=0)
    credit = Column(Numeric(precision=18, scale=2), default=0)
    currency = Column(String(3), default="EUR")
    exchange_rate = Column(Numeric(precision=18, scale=8), default=1)
    base_debit = Column(Numeric(precision=18, scale=2), default=0)  # In base currency
    base_credit = Column(Numeric(precision=18, scale=2), default=0)
    description = Column(String(500), nullable=True)

    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account")

    __table_args__ = (
        CheckConstraint(
            "(debit >= 0 AND credit = 0) OR (credit >= 0 AND debit = 0)",
            name="ck_debit_or_credit",
        ),
    )

    def __repr__(self) -> str:
        return f"<JournalEntryLine(account={self.account_id}, dr={self.debit}, cr={self.credit})>"


# ═══════════════════════════════════════════════════════════════
# ACCOUNTS RECEIVABLE & INVOICING
# ═══════════════════════════════════════════════════════════════

class Invoice(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """Sales invoice issued to a client."""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), nullable=False, index=True)
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), default="draft", index=True)  # draft, sent, paid, partially_paid, overdue, void
    currency = Column(String(3), default="EUR")
    exchange_rate = Column(Numeric(precision=18, scale=8), default=1)

    # Amounts (computed from lines)
    subtotal = Column(Numeric(precision=18, scale=2), default=0)
    tax_amount = Column(Numeric(precision=18, scale=2), default=0)
    total = Column(Numeric(precision=18, scale=2), default=0)
    amount_paid = Column(Numeric(precision=18, scale=2), default=0)
    balance_due = Column(Numeric(precision=18, scale=2), default=0)

    # Relations
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    payment_terms = Column(String(100), nullable=True)  # e.g. "Net 30"

    # GL linkage
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)

    lines = relationship("InvoiceLine", back_populates="invoice", lazy="selectin", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", lazy="selectin")
    company = relationship("Company")
    deal = relationship("Deal")

    def __repr__(self) -> str:
        return f"<Invoice({self.invoice_number}, {self.status}, {self.total} {self.currency})>"


class InvoiceLine(Base, TimestampMixin, TenantMixin):
    """Individual line item on an invoice."""
    __tablename__ = "invoice_lines"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(precision=10, scale=2), default=1)
    unit_price = Column(Numeric(precision=18, scale=2), nullable=False)
    tax_rate = Column(Numeric(precision=5, scale=2), default=0)  # Percentage
    line_total = Column(Numeric(precision=18, scale=2), nullable=False)
    tax_amount = Column(Numeric(precision=18, scale=2), default=0)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    invoice = relationship("Invoice", back_populates="lines")
    account = relationship("Account")

    def __repr__(self) -> str:
        return f"<InvoiceLine(inv={self.invoice_id}, total={self.line_total})>"


class Payment(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """Payment received against an invoice."""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    payment_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    currency = Column(String(3), default="EUR")
    exchange_rate = Column(Numeric(precision=18, scale=8), default=1)
    payment_method = Column(String(50), nullable=True)  # bank_transfer, check, card, cash
    bank_reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # GL linkage
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)

    invoice = relationship("Invoice", back_populates="payments")

    def __repr__(self) -> str:
        return f"<Payment(inv={self.invoice_id}, amount={self.amount} {self.currency})>"


# ═══════════════════════════════════════════════════════════════
# ACCOUNTS PAYABLE
# ═══════════════════════════════════════════════════════════════

class Vendor(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """Vendor/supplier registry."""
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    contact_email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    tax_id = Column(String(50), nullable=True)
    payment_terms = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    bills = relationship("Bill", back_populates="vendor", lazy="noload")

    def __repr__(self) -> str:
        return f"<Vendor({self.name})>"


class Bill(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """Vendor bill / expense."""
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    bill_number = Column(String(50), nullable=True, index=True)
    bill_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False)
    status = Column(String(20), default="draft", index=True)  # draft, approved, paid, overdue, void
    currency = Column(String(3), default="EUR")
    subtotal = Column(Numeric(precision=18, scale=2), default=0)
    tax_amount = Column(Numeric(precision=18, scale=2), default=0)
    total = Column(Numeric(precision=18, scale=2), default=0)
    amount_paid = Column(Numeric(precision=18, scale=2), default=0)

    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True, index=True)
    notes = Column(Text, nullable=True)

    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)

    vendor = relationship("Vendor", back_populates="bills")
    lines = relationship("BillLine", back_populates="bill", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Bill({self.bill_number}, {self.status}, {self.total} {self.currency})>"


class BillLine(Base, TimestampMixin, TenantMixin):
    """Line item on a vendor bill."""
    __tablename__ = "bill_lines"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(precision=10, scale=2), default=1)
    unit_price = Column(Numeric(precision=18, scale=2), nullable=False)
    tax_rate = Column(Numeric(precision=5, scale=2), default=0)
    line_total = Column(Numeric(precision=18, scale=2), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    bill = relationship("Bill", back_populates="lines")
    account = relationship("Account")

    def __repr__(self) -> str:
        return f"<BillLine(bill={self.bill_id}, total={self.line_total})>"


class ExpenseReport(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    """Employee expense submission."""
    __tablename__ = "expense_reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    submitter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True, index=True)
    status = Column(String(20), default="draft", index=True)  # draft, submitted, approved, rejected, reimbursed
    currency = Column(String(3), default="EUR")
    total = Column(Numeric(precision=14, scale=2), default=0)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    submitter = relationship("User", foreign_keys=[submitter_id])
    items = relationship("ExpenseItem", back_populates="expense_report", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ExpenseReport({self.title}, {self.status})>"


class ExpenseItem(Base, TimestampMixin, TenantMixin):
    """Individual expense line item with receipt."""
    __tablename__ = "expense_items"

    id = Column(Integer, primary_key=True, index=True)
    expense_report_id = Column(Integer, ForeignKey("expense_reports.id"), nullable=False, index=True)
    expense_date = Column(Date, nullable=False)
    category = Column(String(50), nullable=False)  # travel, meals, office, professional_fees
    description = Column(String(500), nullable=False)
    amount = Column(Numeric(precision=14, scale=2), nullable=False)
    currency = Column(String(3), default="EUR")
    receipt_path = Column(String(500), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    expense_report = relationship("ExpenseReport", back_populates="items")
    account = relationship("Account")

    def __repr__(self) -> str:
        return f"<ExpenseItem({self.category}, {self.amount})>"
