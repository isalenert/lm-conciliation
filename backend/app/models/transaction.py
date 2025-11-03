"""
Model de Transação
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class TransactionSource(enum.Enum):
    BANK = "bank"
    INTERNAL = "internal"

class TransactionStatus(enum.Enum):
    MATCHED = "matched"
    PENDING = "pending"
    MANUAL_MATCH = "manual_match"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    reconciliation_id = Column(Integer, ForeignKey("reconciliations.id"), nullable=False)
    source = Column(SQLEnum(TransactionSource), nullable=False)
    date = Column(Date, nullable=False)
    value = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    matched_with_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    confidence = Column(Float, nullable=True)
    reconciliation = relationship("Reconciliation", back_populates="transactions")
    matched_with = relationship("Transaction", remote_side=[id], uselist=False)
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, source={self.source}, status={self.status})>"
