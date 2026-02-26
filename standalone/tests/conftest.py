"""
Test configuration and shared fixtures.

Provides:
  - In-memory SQLite test database
  - Test client with authenticated session
  - Model factories for test data generation
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db import get_db
from app.main import app
from app.models.base import Base
from app.models.auth import User
from app.auth import hash_password, create_access_token


# ── Test Database ────────────────────────────────────────────
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

test_engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="function")
def db_session():
    """Provide a clean database session for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI test client with overridden DB dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session) -> User:
    """Create a test user and return it."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=hash_password("test123"),
        role="admin",
        is_active=True,
        tenant_id="default",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user) -> dict:
    """Return authorization headers for authenticated requests."""
    token = create_access_token(subject=test_user.email, role=test_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def auth_client(client, auth_headers):
    """Convenience: a test client pre-configured with auth headers."""
    client.headers.update(auth_headers)
    return client


# admin_client is an alias: test_user already has role="admin"
admin_client = auth_client


@pytest.fixture(scope="function")
def regular_user(db_session) -> User:
    """Create a non-admin user."""
    user = User(
        email="regular@example.com",
        full_name="Regular User",
        hashed_password=hash_password("pass123"),
        role="user",
        is_active=True,
        tenant_id="default",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def regular_auth_client(client, regular_user):
    """Test client with non-admin user authentication."""
    token = create_access_token(subject=regular_user.email, role=regular_user.role)
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
