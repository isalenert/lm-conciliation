"""
Rotas de upload de arquivos
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()

UPLOAD_DIR = "/tmp/lm-conciliation-uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_files(
    bank_file: UploadFile = File(...),
    internal_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload de arquivos bancário e interno para conciliação
    
    Aceita: CSV e PDF
    """
    # Validar extensões
    allowed_extensions = [".csv", ".pdf"]
    
    def validate_file(file: UploadFile):
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato não suportado: {ext}. Use CSV ou PDF"
            )
        return ext
    
    bank_ext = validate_file(bank_file)
    internal_ext = validate_file(internal_file)
    
    # Criar nomes únicos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bank_filename = f"bank_{current_user.id}_{timestamp}{bank_ext}"
    internal_filename = f"internal_{current_user.id}_{timestamp}{internal_ext}"
    
    bank_path = os.path.join(UPLOAD_DIR, bank_filename)
    internal_path = os.path.join(UPLOAD_DIR, internal_filename)
    
    # Salvar arquivos
    with open(bank_path, "wb") as buffer:
        shutil.copyfileobj(bank_file.file, buffer)
    
    with open(internal_path, "wb") as buffer:
        shutil.copyfileobj(internal_file.file, buffer)
    
    return {
        "message": "Arquivos enviados com sucesso",
        "bank_file": bank_filename,
        "internal_file": internal_filename,
        "bank_path": bank_path,
        "internal_path": internal_path
    }


@router.get("/uploads")
async def list_uploads(
    current_user: User = Depends(get_current_user)
):
    """Lista uploads do usuário"""
    user_files = [
        f for f in os.listdir(UPLOAD_DIR)
        if f.startswith(f"bank_{current_user.id}_") or f.startswith(f"internal_{current_user.id}_")
    ]
    
    return {
        "files": user_files,
        "count": len(user_files)
    }
