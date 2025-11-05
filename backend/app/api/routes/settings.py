"""
Rotas de configurações do usuário
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.user_settings import UserSettings


router = APIRouter()


class SettingsUpdate(BaseModel):
    date_tolerance_days: int
    value_tolerance: float
    similarity_threshold: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "date_tolerance_days": 2,
                "value_tolerance": 0.05,
                "similarity_threshold": 0.75
            }
        }


class SettingsResponse(BaseModel):
    date_tolerance_days: int
    value_tolerance: float
    similarity_threshold: float
    
    class Config:
        from_attributes = True


@router.get("/settings", response_model=SettingsResponse)
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna configurações do usuário
    """
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    # Se não existir, criar com valores padrão
    if not settings:
        settings = UserSettings(
            user_id=current_user.id,
            date_tolerance_days=1,
            value_tolerance=0.02,
            similarity_threshold=0.7
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("/settings", response_model=SettingsResponse)
def update_settings(
    settings_data: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza configurações do usuário
    """
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    settings.date_tolerance_days = settings_data.date_tolerance_days
    settings.value_tolerance = settings_data.value_tolerance
    settings.similarity_threshold = settings_data.similarity_threshold
    
    db.commit()
    db.refresh(settings)
    
    return settings
