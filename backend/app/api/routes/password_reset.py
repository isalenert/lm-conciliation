"""
Rotas de recuperação de senha
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import secrets

from app.core.database import get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User


router = APIRouter()


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


# Armazenar tokens temporariamente (em produção, use Redis)
reset_tokens = {}


@router.post("/forgot-password")
def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Solicita reset de senha (envia email com token)
    
    NOTA: Em produção, enviar email real com SendGrid/AWS SES
    Para desenvolvimento, retornamos o token diretamente
    """
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Por segurança, não revelar se email existe
        return {
            "message": "Se o email existir, você receberá instruções para resetar a senha"
        }
    
    # Gerar token único
    token = secrets.token_urlsafe(32)
    
    # Armazenar token com expiração de 1 hora
    reset_tokens[token] = {
        "user_id": user.id,
        "expires_at": datetime.utcnow() + timedelta(hours=1)
    }
    
    # TODO: Em produção, enviar email
    # send_email(user.email, f"Reset token: {token}")
    
    # Para desenvolvimento, retornar token
    return {
        "message": "Token de reset gerado (em produção seria enviado por email)",
        "token": token,  # REMOVER EM PRODUÇÃO
        "reset_url": f"http://localhost:5173/reset-password?token={token}"
    }


@router.post("/reset-password")
def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reseta a senha usando o token
    """
    # Verificar se token existe
    if request.token not in reset_tokens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado"
        )
    
    token_data = reset_tokens[request.token]
    
    # Verificar se token expirou
    if datetime.utcnow() > token_data["expires_at"]:
        del reset_tokens[request.token]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado"
        )
    
    # Buscar usuário
    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Atualizar senha
    user.password_hash = hash_password(request.new_password)
    db.commit()
    
    # Remover token usado
    del reset_tokens[request.token]
    
    return {
        "message": "Senha alterada com sucesso"
    }
