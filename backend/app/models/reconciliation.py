"""
Model de Conciliação
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum

class ReconciliationStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Reconciliation(Base):
    __tablename__ = "reconciliations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bank_file_name = Column(String, nullable=False)
    internal_file_name = Column(String, nullable=False)
    total_bank_transactions = Column(Integer, default=0)
    total_internal_transactions = Column(Integer, default=0)
    matched_count = Column(Integer, default=0)
    bank_only_count = Column(Integer, default=0)
    internal_only_count = Column(Integer, default=0)
    manual_matches_count = Column(Integer, default=0)
    match_rate = Column(Float, default=0.0)
    status = Column(SQLEnum(ReconciliationStatus), default=ReconciliationStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User")
    transactions = relationship("Transaction", back_populates="reconciliation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Reconciliation(id={self.id}, match_rate={self.match_rate}%)>"
