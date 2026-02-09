from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import User


router = APIRouter()


def store_oauth_token(db: Session, user: User, provider: str, payload: dict) -> dict:
    # Placeholder storage mechanism. Replace with encrypted storage table.
    # For now, we attach tokens to the user record in a safe future migration.
    return {
        "provider": provider,
        "status": "stored",
        "note": "Implement encrypted token storage table"
    }


@router.post("/connect/{provider}")
def connect_provider(provider: str, payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if provider not in ("gmail", "microsoft"):
        raise HTTPException(status_code=400, detail="Unsupported provider")

    result = store_oauth_token(db, user, provider, payload)
    return result
