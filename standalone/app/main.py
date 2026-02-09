from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app.routers import auth, companies, contacts, documents, email, interactions, oauth, shares, export, import_, audit, tenants
from app.storage import ensure_storage_dir


app = FastAPI(title="M&A Advisory Standalone API", version="0.1.0")

origins = [o.strip() for o in settings.cors_origins.split(",")] if settings.cors_origins else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
app.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(shares.router, prefix="/shares", tags=["shares"])
app.include_router(email.router, prefix="/email", tags=["email"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
app.include_router(export.router, tags=["export"])
app.include_router(import_.router, tags=["import"])
app.include_router(audit.router)


@app.on_event("startup")
def on_startup() -> None:
    ensure_storage_dir()
    Base.metadata.create_all(bind=engine)
