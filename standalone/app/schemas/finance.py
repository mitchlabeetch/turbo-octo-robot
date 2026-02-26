"""
Financial schemas: API request/response models for the ERP core.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


# ── Currency ─────────────────────────────────────────────────

class CurrencyOut(BaseModel):
    id: int
    code: str
    name: str
    symbol: Optional[str] = None
    decimal_places: int
    is_active: bool
    class Config:
        from_attributes = True


class ExchangeRateCreate(BaseModel):
    from_currency: str
    to_currency: str
    rate: Decimal
    rate_date: date
    source: str = "manual"


class ExchangeRateOut(BaseModel):
    id: int
    from_currency: str
    to_currency: str
    rate: Decimal
    rate_date: date
    source: str
    class Config:
        from_attributes = True


# ── Chart of Accounts ────────────────────────────────────────

class AccountCreate(BaseModel):
    code: str
    name: str
    account_type: str  # asset, liability, equity, revenue, expense
    parent_id: Optional[int] = None
    description: Optional[str] = None
    currency: str = "EUR"
    is_header: bool = False


class AccountOut(BaseModel):
    id: int
    uuid: str
    code: str
    name: str
    account_type: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    currency: str
    is_header: bool
    is_active: bool
    class Config:
        from_attributes = True


# ── Journal Entry ────────────────────────────────────────────

class JournalEntryLineCreate(BaseModel):
    account_id: int
    debit: Decimal = Decimal(0)
    credit: Decimal = Decimal(0)
    currency: str = "EUR"
    exchange_rate: Decimal = Decimal(1)
    description: Optional[str] = None


class JournalEntryCreate(BaseModel):
    entry_date: date
    reference: Optional[str] = None
    memo: Optional[str] = None
    lines: List[JournalEntryLineCreate]


class JournalEntryLineOut(BaseModel):
    id: int
    account_id: int
    debit: Decimal
    credit: Decimal
    currency: str
    exchange_rate: Decimal
    base_debit: Decimal
    base_credit: Decimal
    description: Optional[str] = None
    class Config:
        from_attributes = True


class JournalEntryOut(BaseModel):
    id: int
    uuid: str
    entry_date: date
    reference: Optional[str] = None
    memo: Optional[str] = None
    status: str
    lines: List[JournalEntryLineOut]
    created_at: datetime
    class Config:
        from_attributes = True


# ── Invoice ──────────────────────────────────────────────────

class InvoiceLineCreate(BaseModel):
    description: str
    quantity: Decimal = Decimal(1)
    unit_price: Decimal
    tax_rate: Decimal = Decimal(0)
    account_id: Optional[int] = None


class InvoiceCreate(BaseModel):
    invoice_date: date
    due_date: date
    currency: str = "EUR"
    company_id: Optional[int] = None
    deal_id: Optional[int] = None
    contact_id: Optional[int] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    lines: List[InvoiceLineCreate]


class InvoiceLineOut(BaseModel):
    id: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    line_total: Decimal
    tax_amount: Decimal
    class Config:
        from_attributes = True


class InvoiceOut(BaseModel):
    id: int
    uuid: str
    invoice_number: str
    invoice_date: date
    due_date: date
    status: str
    currency: str
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    company_id: Optional[int] = None
    deal_id: Optional[int] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    lines: List[InvoiceLineOut]
    created_at: datetime
    class Config:
        from_attributes = True


class InvoiceListOut(BaseModel):
    items: List[InvoiceOut]
    total: int
    offset: int
    limit: int


# ── Payment ──────────────────────────────────────────────────

class PaymentCreate(BaseModel):
    payment_date: date
    amount: Decimal
    currency: str = "EUR"
    payment_method: Optional[str] = None
    bank_reference: Optional[str] = None
    notes: Optional[str] = None


class PaymentOut(BaseModel):
    id: int
    uuid: str
    invoice_id: int
    payment_date: date
    amount: Decimal
    currency: str
    payment_method: Optional[str] = None
    bank_reference: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True


# ── Vendor ───────────────────────────────────────────────────

class VendorCreate(BaseModel):
    name: str
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None


class VendorOut(BaseModel):
    id: int
    uuid: str
    name: str
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True


# ── Bill ─────────────────────────────────────────────────────

class BillLineCreate(BaseModel):
    description: str
    quantity: Decimal = Decimal(1)
    unit_price: Decimal
    tax_rate: Decimal = Decimal(0)
    account_id: Optional[int] = None


class BillCreate(BaseModel):
    bill_date: date
    due_date: date
    currency: str = "EUR"
    vendor_id: Optional[int] = None
    deal_id: Optional[int] = None
    bill_number: Optional[str] = None
    notes: Optional[str] = None
    lines: List[BillLineCreate]


class BillOut(BaseModel):
    id: int
    uuid: str
    bill_number: Optional[str] = None
    bill_date: date
    due_date: date
    status: str
    currency: str
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    amount_paid: Decimal
    vendor_id: Optional[int] = None
    deal_id: Optional[int] = None
    created_at: datetime
    class Config:
        from_attributes = True


# ── Expense Report ───────────────────────────────────────────

class ExpenseItemCreate(BaseModel):
    expense_date: date
    category: str
    description: str
    amount: Decimal
    currency: str = "EUR"
    account_id: Optional[int] = None


class ExpenseReportCreate(BaseModel):
    title: str
    deal_id: Optional[int] = None
    currency: str = "EUR"
    items: List[ExpenseItemCreate]


class ExpenseItemOut(BaseModel):
    id: int
    expense_date: date
    category: str
    description: str
    amount: Decimal
    currency: str
    class Config:
        from_attributes = True


class ExpenseReportOut(BaseModel):
    id: int
    uuid: str
    title: str
    status: str
    currency: str
    total: Decimal
    deal_id: Optional[int] = None
    submitter_id: int
    items: List[ExpenseItemOut]
    created_at: datetime
    class Config:
        from_attributes = True
