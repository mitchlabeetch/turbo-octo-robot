from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    company_type = Column(String(50), nullable=True)
    sector = Column(String(100), nullable=True)
    annual_revenue = Column(Integer, nullable=True)
    employee_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contacts = relationship("Contact", back_populates="company")
    interactions = relationship("Interaction", back_populates="company")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    job_title = Column(String(100), nullable=True)
    decision_maker = Column(Boolean, default=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="contacts")
    interactions = relationship("Interaction", back_populates="contact")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    interaction_type = Column(String(50), nullable=False)
    subject = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    interaction_date = Column(Date, nullable=True)
    metadata_json = Column(Text, nullable=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contact = relationship("Contact", back_populates="interactions")
    company = relationship("Company", back_populates="interactions")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=False)
    deal_name = Column(String(100), nullable=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    version = Column(Integer, default=1)
    status = Column(String(50), default="Draft")
    is_confidential = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    shares = relationship("DocumentShare", back_populates="document")


class DocumentShare(Base):
    __tablename__ = "document_shares"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    token = Column(String(100), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    access_count = Column(Integer, default=0)
    view_only = Column(Boolean, default=False)  # If True, download not allowed, only view
    requires_nda = Column(Boolean, default=False)  # If True, NDA must be confirmed before access
    password_hash = Column(String(255), nullable=True)  # Optional password protection
    nda_confirmed_at = Column(DateTime(timezone=True), nullable=True)  # When NDA was confirmed
    nda_confirmed_by_email = Column(String(255), nullable=True)  # Email of person who confirmed NDA
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="shares")
    access_logs = relationship("AccessLog", back_populates="share")


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    share_id = Column(Integer, ForeignKey("document_shares.id"), nullable=False)
    accessed_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45), nullable=True)  # Supports IPv6
    user_agent = Column(String(500), nullable=True)
    action = Column(String(50), nullable=False)  # 'view', 'download', 'nda_confirm'
    accessed_by_email = Column(String(255), nullable=True)  # Optional email if known

    share = relationship("DocumentShare", back_populates="access_logs")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
