# M&A Advisory Standalone Service

This is the standalone backend for M&A Advisory ERP. It removes Bench/ERPNext dependencies while keeping data portability and open APIs.

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

export DATABASE_URL="sqlite:///./ma_advisory.db"
export STORAGE_DIR="./storage"

uvicorn app.main:app --reload
```

## Quick start (Docker)

```bash
docker compose up --build
```

## Environment variables

- `DATABASE_URL` (default: sqlite file)
- `STORAGE_DIR` (default: ./storage)
- `CORS_ORIGINS` (comma-separated, default: *)
- `SHARE_TOKEN_TTL_DAYS` (default: 14)
- `JWT_SECRET` (default: change-me)
- `JWT_ALGORITHM` (default: HS256)
- `JWT_EXPIRES_MINUTES` (default: 60)
- `WEBHOOK_SECRET` (default: change-me)
- `BOOTSTRAP_TOKEN` (default: change-me)

## Core endpoints

### Data Management
- `POST /companies` - Create company
- `POST /contacts` - Create contact
- `POST /interactions` - Create interaction
- `POST /documents/upload` - Upload document
- `GET /documents/{id}` - Retrieve document
- `POST /shares/documents/{id}` - Create share link
- `GET /shares/{token}` - Download via share token

### Email Integration
- `POST /email/capture` - Manually log email
- `POST /email/webhook/gmail` - Gmail webhook
- `POST /email/webhook/microsoft` - Microsoft webhook

### Export (CSV, JSON, ZIP)
- `GET /export/companies/csv` - Export companies as CSV
- `GET /export/companies/json` - Export companies as JSON
- `GET /export/contacts/csv` - Export contacts as CSV
- `GET /export/contacts/json` - Export contacts as JSON
- `GET /export/documents/csv` - Export document metadata as CSV
- `GET /export/documents/json` - Export document metadata as JSON
- `GET /export/full` - Export complete database as ZIP with attachments

### Import (CSV, JSON)
- `POST /import/companies/csv` - Import companies from CSV
- `POST /import/companies/json` - Import companies from JSON
- `POST /import/contacts/csv` - Import contacts from CSV
- `POST /import/contacts/json` - Import contacts from JSON

### Authentication
- `POST /auth/bootstrap` - Create initial admin (token-gated)
- `POST /auth/register` - Register new user (admin-gated)
- `POST /auth/token` - Login with credentials

### Tenant Provisioning
- `POST /tenants` - Create tenant (admin)
- `GET /tenants` - List tenants (admin)
- `GET /tenants/{tenant_id}` - Retrieve tenant (admin)

### Data Room Features (NDA, Watermarks, Access Logs)
- `POST /shares/documents/{id}` - Create share with NDA/view-only/password options
- `GET /shares/{token}` - Get share info (status, NDA requirements, expiration)
- `POST /shares/{token}/nda-confirm` - Confirm NDA before accessing document
- `GET /shares/{token}/download` - Download document with watermarking and access logging
- `GET /shares/{token}/audit-logs` - View access logs for a share (admin)
- `GET /audit/summary` - Summary of all access activity (admin)
- `GET /audit/documents/{id}/logs` - View all access logs for a document (admin)

## Key Features

### Access Control & Compliance
- **NDA Gating**: Require email confirmation before accessing sensitive documents
- **View-Only Shares**: Restrict downloads while allowing viewing
- **Password Protection**: Optional password on shares for extra security
- **Watermarking**: Automatically adds viewer email and timestamp to PDFs (requires PyPDF2)
- **Access Logging**: Every access attempt is logged with timestamp, IP, user agent
- **Audit Dashboard**: Admin view of all access activity across the platform

### Data Portability
- **Full Export**: Download entire database as ZIP with CSV/JSON + attachments
- **Bulk Import**: Import companies and contacts from CSV/JSON with validation
- **Format Support**: CSV and JSON for compatibility with external tools

## Installation

### Local (Development)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Docker (Production-Ready)

```bash
docker compose up --build
```

### Optional Dependencies

For PDF watermarking support:
```bash
pip install PyPDF2 reportlab
```

## Notes

This is the standalone backend for M&A Advisory ERP. It focuses on:
- **Zero vendor lock-in**: Complete data export/import capabilities
- **Enterprise compliance**: NDA gating, watermarking, access logs
- **Clean APIs**: RESTful endpoints with OpenAPI documentation at `/docs`
- **Scalable architecture**: SQLAlchemy ORM, Pydantic validation, FastAPI performance
