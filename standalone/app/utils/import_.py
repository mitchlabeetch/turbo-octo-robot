"""Import utilities for bulk data import from CSV and JSON formats."""

import csv
import json
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models import Company, Contact, Interaction, Document


class ImportError(Exception):
    """Raised when import validation fails."""
    pass


class ImportResult:
    """Result of an import operation."""
    def __init__(self):
        self.successful = 0
        self.failed = 0
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'successful': self.successful,
            'failed': self.failed,
            'errors': self.errors,
            'warnings': self.warnings
        }


def import_companies_csv(db: Session, csv_content: str) -> ImportResult:
    """Import companies from CSV content."""
    result = ImportResult()
    
    try:
        reader = csv.DictReader(StringIO(csv_content))
        if reader.fieldnames is None:
            raise ImportError("CSV has no headers")
        
        for row_num, row in enumerate(reader, start=2):  # start at 2 (header is 1)
            try:
                # Validate required fields
                if not row.get('name'):
                    result.errors.append(f"Row {row_num}: Missing required field 'name'")
                    result.failed += 1
                    continue
                
                # Check for duplicate
                existing = db.query(Company).filter(Company.name == row['name']).first()
                if existing:
                    result.warnings.append(f"Row {row_num}: Company '{row['name']}' already exists")
                    result.failed += 1
                    continue
                
                # Create company
                company = Company(
                    name=row['name'],
                    company_type=row.get('company_type') or None,
                    sector=row.get('sector') or None,
                    annual_revenue=row.get('annual_revenue') or None,
                    employee_count=row.get('employee_count') or None
                )
                db.add(company)
                result.successful += 1
                
            except Exception as e:
                result.errors.append(f"Row {row_num}: {str(e)}")
                result.failed += 1
        
        db.commit()
    except Exception as e:
        db.rollback()
        result.errors.append(f"CSV parsing error: {str(e)}")
        result.failed += 1
    
    return result


def import_companies_json(db: Session, json_content: str) -> ImportResult:
    """Import companies from JSON content."""
    result = ImportResult()
    
    try:
        data = json.loads(json_content)
        if not isinstance(data, list):
            raise ImportError("JSON must be an array of company objects")
        
        for idx, item in enumerate(data):
            try:
                if not item.get('name'):
                    result.errors.append(f"Item {idx}: Missing required field 'name'")
                    result.failed += 1
                    continue
                
                # Check for duplicate
                existing = db.query(Company).filter(Company.name == item['name']).first()
                if existing:
                    result.warnings.append(f"Item {idx}: Company '{item['name']}' already exists")
                    result.failed += 1
                    continue
                
                company = Company(
                    name=item['name'],
                    company_type=item.get('company_type'),
                    sector=item.get('sector'),
                    annual_revenue=item.get('annual_revenue'),
                    employee_count=item.get('employee_count')
                )
                db.add(company)
                result.successful += 1
                
            except Exception as e:
                result.errors.append(f"Item {idx}: {str(e)}")
                result.failed += 1
        
        db.commit()
    except Exception as e:
        db.rollback()
        result.errors.append(f"JSON parsing error: {str(e)}")
        result.failed += 1
    
    return result


def import_contacts_csv(db: Session, csv_content: str) -> ImportResult:
    """Import contacts from CSV content."""
    result = ImportResult()
    
    try:
        reader = csv.DictReader(StringIO(csv_content))
        if reader.fieldnames is None:
            raise ImportError("CSV has no headers")
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Validate required fields
                if not row.get('email'):
                    result.errors.append(f"Row {row_num}: Missing required field 'email'")
                    result.failed += 1
                    continue
                
                # Check for duplicate
                existing = db.query(Contact).filter(Contact.email == row['email']).first()
                if existing:
                    result.warnings.append(f"Row {row_num}: Contact with email '{row['email']}' already exists")
                    result.failed += 1
                    continue
                
                # Validate company_id if exists
                company_id = row.get('company_id')
                if company_id:
                    company = db.query(Company).filter(Company.id == company_id).first()
                    if not company:
                        result.errors.append(f"Row {row_num}: Company with id {company_id} not found")
                        result.failed += 1
                        continue
                
                contact = Contact(
                    first_name=row.get('first_name') or '',
                    last_name=row.get('last_name') or '',
                    email=row['email'],
                    job_title=row.get('job_title') or None,
                    decision_maker=row.get('decision_maker', 'False').lower() == 'true',
                    company_id=company_id or None
                )
                db.add(contact)
                result.successful += 1
                
            except Exception as e:
                result.errors.append(f"Row {row_num}: {str(e)}")
                result.failed += 1
        
        db.commit()
    except Exception as e:
        db.rollback()
        result.errors.append(f"CSV parsing error: {str(e)}")
        result.failed += 1
    
    return result


def import_contacts_json(db: Session, json_content: str) -> ImportResult:
    """Import contacts from JSON content."""
    result = ImportResult()
    
    try:
        data = json.loads(json_content)
        if not isinstance(data, list):
            raise ImportError("JSON must be an array of contact objects")
        
        for idx, item in enumerate(data):
            try:
                if not item.get('email'):
                    result.errors.append(f"Item {idx}: Missing required field 'email'")
                    result.failed += 1
                    continue
                
                # Check for duplicate
                existing = db.query(Contact).filter(Contact.email == item['email']).first()
                if existing:
                    result.warnings.append(f"Item {idx}: Contact with email '{item['email']}' already exists")
                    result.failed += 1
                    continue
                
                # Validate company_id if exists
                company_id = item.get('company_id')
                if company_id:
                    company = db.query(Company).filter(Company.id == company_id).first()
                    if not company:
                        result.errors.append(f"Item {idx}: Company with id {company_id} not found")
                        result.failed += 1
                        continue
                
                contact = Contact(
                    first_name=item.get('first_name') or '',
                    last_name=item.get('last_name') or '',
                    email=item['email'],
                    job_title=item.get('job_title'),
                    decision_maker=item.get('decision_maker', False),
                    company_id=company_id
                )
                db.add(contact)
                result.successful += 1
                
            except Exception as e:
                result.errors.append(f"Item {idx}: {str(e)}")
                result.failed += 1
        
        db.commit()
    except Exception as e:
        db.rollback()
        result.errors.append(f"JSON parsing error: {str(e)}")
        result.failed += 1
    
    return result
