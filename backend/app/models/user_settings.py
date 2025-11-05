"""
Model de configurações do usuário
"""
from sqlalchemy import Column, Integer, Float, ForeignKey
from app.core.database import Base

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    date_tolerance_days = Column(Integer, default=1, nullable=False)
    value_tolerance = Column(Float, default=0.02, nullable=False)
    similarity_threshold = Column(Float, default=0.7, nullable=False)
