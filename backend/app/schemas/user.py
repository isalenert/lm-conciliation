"""
Schemas de usuário
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Schema para criação de usuário"""
    email: EmailStr
    name: str
    password: str


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema de resposta do usuário (sem senha)"""
    id: int
    email: EmailStr
    name: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema de token JWT"""
    access_token: str
    token_type: str
