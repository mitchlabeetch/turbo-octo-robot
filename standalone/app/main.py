"""
M&A Advisory CRM+ERP — Application Entry Point.

Configures FastAPI application with:
  - CORS middleware
  - Exception handlers
  - Router registration
  - Startup event (storage + DB init)
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db import Base, engine
from app.routers import (
    audit,
    auth,
    companies,
    contacts,
    deals,
    documents,
    email,
    export,
    finance,
    import_,
    interactions,
    oauth,
    projects,
    shares,
)
from app.storage import ensure_storage_dir

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ma_advisory")


# ── Lifespan ─────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Starting M&A Advisory CRM+ERP (env=%s)", settings.environment)
    ensure_storage_dir()

    # In development, create tables directly. In production, use Alembic.
    if settings.environment == "development":
        Base.metadata.create_all(bind=engine)
        logger.info("Development mode: auto-created database tables")

    yield

    # Shutdown
    logger.info("Shutting down M&A Advisory CRM+ERP")


# ── App ──────────────────────────────────────────────────────
app = FastAPI(
    title="M&A Advisory CRM+ERP API",
    version="1.0.0",
    description=(
        "White-label CRM+ERP platform for M&A advisory firms.\n\n"
        "## Modules\n"
        "- **CRM**: Companies, Contacts, Interactions — the relationship graph\n"
        "- **Deals**: Full M&A deal pipeline with 12-stage lifecycle\n"
        "- **Finance**: Chart of Accounts, General Ledger, Invoicing, AP\n"
        "- **Projects**: Task management and billable time tracking\n"
        "- **Documents**: Secure document management with version control\n"
        "- **Auth**: JWT authentication with role-based access control"
    ),
    contact={"name": "Alecia M&A Advisory", "url": "https://alecia.markets"},
    license_info={"name": "Proprietary", "identifier": "LicenseRef-Proprietary"},
    openapi_tags=[
        {"name": "auth", "description": "Authentication, registration, and token management"},
        {"name": "companies", "description": "Company management and CRM records"},
        {"name": "contacts", "description": "Contact management and deduplication"},
        {"name": "deals", "description": "M&A deal pipeline, buyer lists, bids, and activities"},
        {"name": "finance", "description": "Chart of Accounts, General Ledger, Invoicing, AP"},
        {"name": "projects", "description": "Project management, tasks, and time tracking"},
        {"name": "documents", "description": "Secure document upload and management"},
        {"name": "interactions", "description": "Interaction logging (meetings, calls, emails)"},
    ],
    lifespan=lifespan,
)

# CORS
origins = [o.strip() for o in settings.cors_origins.split(",")] if settings.cors_origins else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception Handlers ───────────────────────────────────────
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Convert service-layer ValueErrors to 400 responses."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# ── Routers ──────────────────────────────────────────────────
app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
app.include_router(deals.router, prefix="/deals", tags=["deals"])
app.include_router(finance.router, prefix="/finance", tags=["finance"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(shares.router, prefix="/shares", tags=["shares"])
app.include_router(email.router, prefix="/email", tags=["email"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
app.include_router(export.router, tags=["export"])
app.include_router(import_.router, tags=["import"])
app.include_router(audit.router)


# ── Health Check ─────────────────────────────────────────────
@app.get("/health", tags=["system"])
def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment,
    }
