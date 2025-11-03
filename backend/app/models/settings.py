"""
Model de Configurações do Usuário
"""

from sqlalchemy import Column, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    date_tolerance = Column(Integer, default=1)
    value_tolerance = Column(Float, default=0.02)
    similarity_threshold = Column(Float, default=0.7)
    default_mapping = Column(JSON, nullable=True)
    user = relationship("User")
    
    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id})>"
