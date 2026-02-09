from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import Interaction
from app.schemas import InteractionCreate, InteractionOut


router = APIRouter()


@router.post("", response_model=InteractionOut)
def create_interaction(
    payload: InteractionCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user)
):
    interaction = Interaction(**payload.model_dump())
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction
