"""
Database engine and session management.

Provides:
  - engine: SQLAlchemy engine with connection pooling
  - SessionLocal: session factory
  - get_db: FastAPI dependency for request-scoped sessions
  - Base: imported from models.base for Alembic awareness
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.base import Base  # noqa: F401 — re-export for Alembic

# Connection pool configuration for production PostgreSQL.
# SQLite uses check_same_thread=False for dev convenience.
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.sql_echo,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """FastAPI dependency: yield a request-scoped session, auto-close on finish."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
