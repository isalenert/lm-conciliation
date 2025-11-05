"""
Rotas de processamento de arquivos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List
import os

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.core.csv_processor import CSVProcessor

router = APIRouter()

UPLOAD_DIR = "/tmp/lm-conciliation-uploads"


class ColumnMapping(BaseModel):
    """Schema para mapeamento de colunas"""
    date_col: str
    value_col: str
    desc_col: str


class ProcessRequest(BaseModel):
    """Request para processar arquivos"""
    bank_file: str
    internal_file: str
    bank_mapping: ColumnMapping
    internal_mapping: ColumnMapping


@router.post("/process/preview")
async def preview_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Preview das primeiras linhas do arquivo CSV
    Retorna colunas disponíveis e 5 primeiras linhas
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    # Verificar se é arquivo do usuário
    if not filename.startswith(f"bank_{current_user.id}_") and \
       not filename.startswith(f"internal_{current_user.id}_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este arquivo"
        )
    
    try:
        df = CSVProcessor.read_csv(file_path)
        
        return {
            "filename": filename,
            "columns": df.columns.tolist(),
            "rows": df.head(5).to_dict('records'),
            "total_rows": len(df)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )


@router.post("/process")
async def process_files(
    request: ProcessRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Processa arquivos e prepara dados para conciliação
    """
    bank_path = os.path.join(UPLOAD_DIR, request.bank_file)
    internal_path = os.path.join(UPLOAD_DIR, request.internal_file)
    
    # Validações
    if not os.path.exists(bank_path) or not os.path.exists(internal_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivos não encontrados"
        )
    
    try:
        # Ler CSVs
        bank_df = CSVProcessor.read_csv(bank_path)
        internal_df = CSVProcessor.read_csv(internal_path)
        
        # Processar dados
        bank_data = CSVProcessor.process_dataframe(
            bank_df,
            request.bank_mapping.date_col,
            request.bank_mapping.value_col,
            request.bank_mapping.desc_col
        )
        
        internal_data = CSVProcessor.process_dataframe(
            internal_df,
            request.internal_mapping.date_col,
            request.internal_mapping.value_col,
            request.internal_mapping.desc_col
        )
        
        return {
            "message": "Arquivos processados com sucesso",
            "bank_transactions": len(bank_data),
            "internal_transactions": len(internal_data),
            "bank_data": bank_data[:10],  # Primeiros 10 para preview
            "internal_data": internal_data[:10]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar: {str(e)}"
        )
