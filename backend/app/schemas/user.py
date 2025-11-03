"""
Schemas de usuário para validação de dados
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ========== SCHEMAS DE INPUT ==========

class UserCreate(BaseModel):
    """Schema para criação de usuário"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "João Silva",
                "password": "senha123456"
            }
        }


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "senha123456"
            }
        }


# ========== SCHEMAS DE OUTPUT ==========

class UserResponse(BaseModel):
    """Schema de resposta de usuário (sem senha)"""
    id: int
    email: str
    name: str
    is_2fa_enabled: bool
    is_email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "name": "João Silva",
                "is_2fa_enabled": False,
                "is_email_verified": False,
                "created_at": "2025-11-03T10:30:00"
            }
        }


class Token(BaseModel):
    """Schema de token JWT"""
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """Dados extraídos do token"""
    email: Optional[str] = None
