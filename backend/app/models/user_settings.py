"""
Model de configurações do usuário
"""

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserSettings(Base):
    """Configurações de conciliação do usuário"""
    
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Tolerâncias padrão
    date_tolerance_days = Column(Integer, default=1, nullable=False)
    value_tolerance = Column(Float, default=0.02, nullable=False)
    similarity_threshold = Column(Float, default=0.7, nullable=False)
    
    # Relacionamento
    user = relationship("User", back_populates="settings")
    
    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id})>"
