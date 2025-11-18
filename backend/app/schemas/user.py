"""
Schemas de usuário
Requisito: RNF02 - Segurança (validação de senhas fortes)
Requisito: RNF06 - Código testável e manutenível
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """
    Schema para criação de usuário
    Inclui validação de senha forte (mínimo 8 caracteres, letra + número)
    """
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100, description="Nome completo do usuário")
    password: str = Field(..., min_length=8, max_length=100, description="Senha (mín. 8 caracteres)")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Valida força da senha conforme requisitos de segurança
        
        Requisitos:
        - Mínimo 8 caracteres
        - Pelo menos 1 letra
        - Pelo menos 1 número
        
        Args:
            v: Senha a ser validada
            
        Returns:
            str: Senha validada
            
        Raises:
            ValueError: Se a senha não atender aos requisitos
        """
        if len(v) < 8:
            raise ValueError('A senha deve ter no mínimo 8 caracteres')
        
        if not any(c.isalpha() for c in v):
            raise ValueError('A senha deve conter pelo menos uma letra')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('A senha deve conter pelo menos um número')
        
        return v


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Schema de resposta do usuário (sem senha)
    Usado em respostas de API para não expor dados sensíveis
    """
    id: int
    email: EmailStr
    name: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Compatível com SQLAlchemy 2.0


class Token(BaseModel):
    """
    Schema de token JWT
    Usado na resposta de autenticação bem-sucedida
    """
    access_token: str
    token_type: str = "bearer"


class PasswordResetRequest(BaseModel):
    """
    Schema para solicitação de reset de senha
    Requisito: RF06 - Recuperação de senha
    """
    email: EmailStr


class PasswordReset(BaseModel):
    """
    Schema para reset de senha com token
    Requisito: RF06 - Recuperação de senha
    """
    token: str = Field(..., min_length=1, description="Token de recuperação de senha")
    new_password: str = Field(..., min_length=8, max_length=100, description="Nova senha")
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Valida força da nova senha (mesmas regras do cadastro)
        
        Args:
            v: Nova senha a ser validada
            
        Returns:
            str: Senha validada
            
        Raises:
            ValueError: Se a senha não atender aos requisitos
        """
        if len(v) < 8:
            raise ValueError('A senha deve ter no mínimo 8 caracteres')
        
        if not any(c.isalpha() for c in v):
            raise ValueError('A senha deve conter pelo menos uma letra')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('A senha deve conter pelo menos um número')
        
        return v


class UserUpdate(BaseModel):
    """
    Schema para atualização de dados do usuário
    Todos os campos são opcionais
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """
    Schema para alteração de senha (usuário logado)
    Requisito: RNF02 - Segurança
    """
    current_password: str = Field(..., description="Senha atual")
    new_password: str = Field(..., min_length=8, max_length=100, description="Nova senha")
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Valida força da nova senha"""
        if len(v) < 8:
            raise ValueError('A senha deve ter no mínimo 8 caracteres')
        
        if not any(c.isalpha() for c in v):
            raise ValueError('A senha deve conter pelo menos uma letra')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('A senha deve conter pelo menos um número')
        
        return v
    
    @field_validator('new_password')
    @classmethod
    def passwords_must_differ(cls, v: str, info) -> str:
        """Garante que a nova senha seja diferente da atual"""
        if 'current_password' in info.data and v == info.data['current_password']:
            raise ValueError('A nova senha deve ser diferente da senha atual')
        return v