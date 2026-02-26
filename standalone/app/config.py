"""
Application configuration.

Settings are loaded from environment variables (with .env file support via pydantic-settings).
Groups: database, auth/JWT, storage, CORS, features, and environment.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Environment ──────────────────────────────────────────
    environment: str = "development"  # development | staging | production
    debug: bool = False
    sql_echo: bool = False  # Log all SQL queries (dev only)

    # ── Database ─────────────────────────────────────────────
    database_url: str = "sqlite:///./ma_advisory.db"

    # ── Authentication / JWT ─────────────────────────────────
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60

    # ── Document Storage ─────────────────────────────────────
    storage_dir: str = "./storage"

    # ── CORS ─────────────────────────────────────────────────
    cors_origins: str = "*"

    # ── Share links ──────────────────────────────────────────
    share_token_ttl_days: int = 14

    # ── Webhooks ─────────────────────────────────────────────
    webhook_secret: str = "change-me"
    bootstrap_token: str = "change-me"

    # ── Celery / Task Queue ──────────────────────────────────
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # ── Feature Flags ────────────────────────────────────────
    feature_deals_enabled: bool = True
    feature_finance_enabled: bool = False
    feature_hr_enabled: bool = False
    feature_workflows_enabled: bool = False

    # ── Multi-Tenancy ────────────────────────────────────────
    default_tenant_id: str = "default"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
