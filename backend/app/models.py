"""
Modelos do banco de dados
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Reconciliation(Base):
    __tablename__ = "reconciliations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    bank_filename = Column(String, nullable=False)
    internal_filename = Column(String, nullable=False)
    matched_count = Column(Integer, default=0)
    pending_bank_count = Column(Integer, default=0)
    pending_internal_count = Column(Integer, default=0)
    total_transactions = Column(Integer, default=0)
    match_rate = Column(Float, default=0.0)
    config = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)
    date_tolerance_days = Column(Integer, default=1)
    value_tolerance = Column(Float, default=0.02)
    similarity_threshold = Column(Float, default=0.7)
