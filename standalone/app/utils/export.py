"""Export utilities for bulk data export in CSV and JSON formats."""

import csv
import json
import os
import shutil
import tempfile
from io import StringIO
from pathlib import Path
from typing import Any, List, Dict
from datetime import datetime

from sqlalchemy.orm import Session
from ..models import Company, Contact, Interaction, Document, DocumentShare


def export_companies_csv(db: Session) -> str:
    """Export all companies as CSV string."""
    companies = db.query(Company).all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'id', 'name', 'company_type', 'sector', 'annual_revenue',
        'employee_count', 'created_at'
    ])
    
    for company in companies:
        writer.writerow([
            company.id,
            company.name,
            company.company_type or '',
            company.sector or '',
            company.annual_revenue or '',
            company.employee_count or '',
            company.created_at.isoformat() if company.created_at else ''
        ])
    
    return output.getvalue()


def export_companies_json(db: Session) -> List[Dict[str, Any]]:
    """Export all companies as JSON list."""
    companies = db.query(Company).all()
    
    result = []
    for company in companies:
        result.append({
            'id': company.id,
            'name': company.name,
            'company_type': company.company_type,
            'sector': company.sector,
            'annual_revenue': company.annual_revenue,
            'employee_count': company.employee_count,
            'created_at': company.created_at.isoformat() if company.created_at else None
        })
    
    return result


def export_contacts_csv(db: Session) -> str:
    """Export all contacts as CSV string."""
    contacts = db.query(Contact).all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'id', 'first_name', 'last_name', 'email', 'job_title',
        'decision_maker', 'company_id', 'created_at'
    ])
    
    for contact in contacts:
        writer.writerow([
            contact.id,
            contact.first_name or '',
            contact.last_name or '',
            contact.email or '',
            contact.job_title or '',
            contact.decision_maker or False,
            contact.company_id or '',
            contact.created_at.isoformat() if contact.created_at else ''
        ])
    
    return output.getvalue()


def export_contacts_json(db: Session) -> List[Dict[str, Any]]:
    """Export all contacts as JSON list."""
    contacts = db.query(Contact).all()
    
    result = []
    for contact in contacts:
        result.append({
            'id': contact.id,
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'email': contact.email,
            'job_title': contact.job_title,
            'decision_maker': contact.decision_maker,
            'company_id': contact.company_id,
            'created_at': contact.created_at.isoformat() if contact.created_at else None
        })
    
    return result


def export_documents_csv(db: Session) -> str:
    """Export all documents as CSV string (metadata only)."""
    documents = db.query(Document).all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'id', 'document_name', 'document_type', 'deal_name', 'file_name',
        'content_type', 'size_bytes', 'version', 'status', 'is_confidential', 'created_at'
    ])
    
    for doc in documents:
        writer.writerow([
            doc.id,
            doc.document_name or '',
            doc.document_type or '',
            doc.deal_name or '',
            doc.file_name or '',
            doc.content_type or '',
            doc.size_bytes or '',
            doc.version or '',
            doc.status or '',
            doc.is_confidential or False,
            doc.created_at.isoformat() if doc.created_at else ''
        ])
    
    return output.getvalue()


def export_documents_json(db: Session) -> List[Dict[str, Any]]:
    """Export all documents as JSON list (metadata only)."""
    documents = db.query(Document).all()
    
    result = []
    for doc in documents:
        result.append({
            'id': doc.id,
            'document_name': doc.document_name,
            'document_type': doc.document_type,
            'deal_name': doc.deal_name,
            'file_name': doc.file_name,
            'content_type': doc.content_type,
            'size_bytes': doc.size_bytes,
            'version': doc.version,
            'status': doc.status,
            'is_confidential': doc.is_confidential,
            'created_at': doc.created_at.isoformat() if doc.created_at else None
        })
    
    return result


def create_zip_export(db: Session, storage_dir: str) -> str:
    """Create complete export zip with CSV/JSON and document attachments."""
    temp_dir = tempfile.mkdtemp()
    try:
        # Create data subdirectory
        data_dir = Path(temp_dir) / 'data'
        data_dir.mkdir(exist_ok=True)
        
        # Export CSVs
        with open(data_dir / 'companies.csv', 'w') as f:
            f.write(export_companies_csv(db))
        with open(data_dir / 'contacts.csv', 'w') as f:
            f.write(export_contacts_csv(db))
        with open(data_dir / 'documents.csv', 'w') as f:
            f.write(export_documents_csv(db))
        
        # Export JSONs
        with open(data_dir / 'companies.json', 'w') as f:
            json.dump(export_companies_json(db), f, indent=2)
        with open(data_dir / 'contacts.json', 'w') as f:
            json.dump(export_contacts_json(db), f, indent=2)
        with open(data_dir / 'documents.json', 'w') as f:
            json.dump(export_documents_json(db), f, indent=2)
        
        # Copy document files
        docs_dir = Path(temp_dir) / 'documents'
        docs_dir.mkdir(exist_ok=True)
        
        documents = db.query(Document).all()
        for doc in documents:
            if doc.file_path:
                src = Path(storage_dir) / doc.file_path
                if src.exists():
                    dest = docs_dir / f"{doc.id}_{doc.file_name}"
                    shutil.copy2(src, dest)
        
        # Create metadata
        metadata = {
            'export_date': datetime.now().isoformat(),
            'total_companies': db.query(Company).count(),
            'total_contacts': db.query(Contact).count(),
            'total_documents': db.query(Document).count(),
            'total_interactions': db.query(Interaction).count()
        }
        with open(Path(temp_dir) / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create zip
        zip_path = Path(temp_dir).parent / f"ma_advisory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.make_archive(str(zip_path), 'zip', temp_dir)
        
        return str(zip_path) + '.zip'
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
