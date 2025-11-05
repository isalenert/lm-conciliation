"""
Models de reconciliação
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class Reconciliation(Base):
    __tablename__ = "reconciliations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    bank_file_name = Column(String)
    internal_file_name = Column(String)
    total_bank_transactions = Column(Integer)
    total_internal_transactions = Column(Integer)
    matched_count = Column(Integer)
    bank_only_count = Column(Integer)
    internal_only_count = Column(Integer)
    match_rate = Column(Float)


class ReconciliationMatch(Base):
    __tablename__ = "reconciliation_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    reconciliation_id = Column(Integer, ForeignKey("reconciliations.id", ondelete="CASCADE"), nullable=False)
    bank_transaction_data = Column(JSON)
    internal_transaction_data = Column(JSON)
    confidence = Column(Float)
    is_manual = Column(Boolean, default=False)


class ManualMatch(Base):
    __tablename__ = "manual_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    reconciliation_id = Column(Integer, ForeignKey("reconciliations.id", ondelete="CASCADE"), nullable=False)
    bank_transaction_id = Column(Integer)
    internal_transaction_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
