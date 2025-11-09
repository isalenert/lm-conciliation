"""
Rotas de recuperação de senha com envio de email real
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import timedelta
import jwt

from app.core.database import get_db
from app.core.security import hash_password, create_access_token, SECRET_KEY, ALGORITHM
from app.models.user import User
from app.services.email_service import email_service


router = APIRouter()


class PasswordResetRequest(BaseModel):
    """Schema para solicitar reset de senha"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema para confirmar reset com token"""
    token: str
    new_password: str


@router.post("/forgot-password")
def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Solicita reset de senha - ENVIA EMAIL REAL
    
    Segurança: Sempre retorna mesma mensagem para não revelar
    se o email existe no sistema
    """
    
    # Mensagem padrão de segurança
    standard_response = {
        "message": "Se o email existir em nossa base, você receberá as instruções de reset."
    }
    
    # Buscar usuário
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        print(f"⚠️ Tentativa de reset para email não cadastrado: {request.email}")
        return standard_response
    
    # Gerar token JWT com expiração de 1 hora
    reset_token = create_access_token(
        data={
            "sub": user.email,
            "type": "password_reset"
        },
        expires_delta=timedelta(hours=1)
    )
    
    # Enviar email
    try:
        email_sent = email_service.send_reset_password_email(
            to_email=user.email,
            reset_token=reset_token
        )
        
        if email_sent:
            print(f"✅ Email de reset enviado para {user.email}")
        else:
            print(f"⚠️ Falha ao enviar email para {user.email}")
            
    except Exception as e:
        print(f"❌ Erro ao processar reset: {str(e)}")
    
    # SEMPRE retornar mesma mensagem (segurança)
    return standard_response


@router.post("/reset-password")
def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reseta senha usando token JWT recebido por email
    """
    
    try:
        # Decodificar token JWT
        payload = jwt.decode(
            request.token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        # Extrair dados
        email = payload.get("sub")
        token_type = payload.get("type")
        
        # Verificar tipo de token
        if token_type != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido"
            )
        
        # Buscar usuário
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Validar senha
        if len(request.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha deve ter no mínimo 6 caracteres"
            )
        
        # Atualizar senha
        user.hashed_password = hash_password(request.new_password)
        db.commit()
        
        print(f"✅ Senha resetada com sucesso para {user.email}")
        
        return {
            "message": "Senha redefinida com sucesso! Você já pode fazer login."
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado. Solicite um novo reset de senha."
        )
        
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido"
        )
        
    except Exception as e:
        print(f"❌ Erro ao resetar senha: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar solicitação"
        )
