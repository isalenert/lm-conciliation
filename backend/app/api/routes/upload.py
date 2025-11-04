"""
Rotas de upload de arquivos
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import tempfile
import os

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.csv_processor import CSVProcessor
from app.models.user import User

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Faz upload de um arquivo e retorna preview das colunas
    
    Requer autenticação
    """
    try:
        # Ler conteúdo do arquivo
        content = await file.read()
        
        # Salvar temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        # Processar CSV
        processor = CSVProcessor()
        df = processor.read_csv(tmp_path)
        df_clean = processor.standardize_data(df)
        
        # Limpar arquivo temporário
        os.unlink(tmp_path)
        
        # Retornar preview
        return {
            "filename": file.filename,
            "columns": df_clean.columns.tolist(),
            "rows": len(df_clean),
            "preview": df_clean.head(5).to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )
