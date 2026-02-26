"""
CRM models: Company, Contact, Interaction.

Migrated from the flat models.py and enhanced with:
  - TimestampMixin (created_at + updated_at)
  - SoftDeleteMixin (is_deleted, deleted_at)
  - TenantMixin (tenant_id for multi-tenancy)
  - UUIDMixin (public-facing UUID)
"""

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin


class Company(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    company_type = Column(String(50), nullable=True)
    sector = Column(String(100), nullable=True, index=True)
    annual_revenue = Column(Integer, nullable=True)
    employee_count = Column(Integer, nullable=True)

    # Relationships
    contacts = relationship("Contact", back_populates="company", lazy="selectin")
    interactions = relationship("Interaction", back_populates="company", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.name}')>"


class Contact(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    job_title = Column(String(100), nullable=True)
    decision_maker = Column(Boolean, default=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)

    # Relationships
    company = relationship("Company", back_populates="contacts")
    interactions = relationship("Interaction", back_populates="contact", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, email='{self.email}')>"


class Interaction(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, UUIDMixin):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    interaction_type = Column(String(50), nullable=False, index=True)
    subject = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    interaction_date = Column(Date, nullable=True)
    metadata_json = Column(Text, nullable=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)

    # Relationships
    contact = relationship("Contact", back_populates="interactions")
    company = relationship("Company", back_populates="interactions")

    def __repr__(self) -> str:
        return f"<Interaction(id={self.id}, type='{self.interaction_type}')>"
