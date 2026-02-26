from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from app.config import settings


def generate_share_token() -> str:
    return secrets.token_urlsafe(32)


def share_expiry(expires_in_days: int | None) -> datetime | None:
    days = expires_in_days if expires_in_days is not None else settings.share_token_ttl_days
    if days <= 0:
        return None
    return datetime.now(timezone.utc) + timedelta(days=days)
