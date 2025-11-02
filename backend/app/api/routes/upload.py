"""
Rotas de upload de arquivos
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os

from app.core.csv_processor import CSVProcessor
from app.core.pdf_processor import PDFProcessor
from app.api.models.schemas import FileUploadResponse, PDFUploadResponse, ErrorResponse

router = APIRouter()


@router.post("/upload/csv", response_model=FileUploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload e processamento de arquivo CSV
    
    - Aceita arquivos .csv
    - Detecta encoding automaticamente
    - Retorna preview dos dados
    """
    
    # Validar extensão
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Formato inválido. Apenas arquivos .csv são aceitos."
        )
    
    # Validar tamanho (5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=413,
            detail="Arquivo muito grande. Tamanho máximo: 5MB"
        )
    
    try:
        # Salvar temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Processar
        processor = CSVProcessor()
        df = processor.read_csv(tmp_path)
        df_clean = processor.standardize_data(df)
        
        # Limpar arquivo temporário
        os.unlink(tmp_path)
        
        # Preparar resposta
        preview = df_clean.head(5).to_dict('records')
        
        # Converter timestamps para string
        for row in preview:
            for key, value in row.items():
                if pd.isna(value):
                    row[key] = None
                elif isinstance(value, (pd.Timestamp, datetime)):
                    row[key] = value.strftime('%Y-%m-%d')
        
        return FileUploadResponse(
            filename=file.filename,
            columns=list(df_clean.columns),
            row_count=len(df_clean),
            preview=preview
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )


@router.post("/upload/pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload e processamento de arquivo PDF
    
    - Aceita arquivos .pdf
    - Extrai texto e identifica transações
    - Retorna preview dos dados
    """
    
    # Validar extensão
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Formato inválido. Apenas arquivos .pdf são aceitos."
        )
    
    # Validar tamanho (5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Arquivo muito grande. Tamanho máximo: 5MB"
        )
    
    try:
        # Salvar temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Processar
        processor = PDFProcessor()
        text = processor.extract_text_from_pdf(tmp_path)
        df = processor.parse_bank_statement(text)
        
        # Limpar arquivo temporário
        os.unlink(tmp_path)
        
        # Preparar resposta
        preview_text = text[:300] + "..." if len(text) > 300 else text
        preview_data = df.head(5).to_dict('records') if not df.empty else []
        
        return PDFUploadResponse(
            filename=file.filename,
            text_length=len(text),
            transactions_count=len(df),
            preview_text=preview_text,
            preview_data=preview_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Erro ao processar PDF: {str(e)}"
        )


# Imports necessários
import pandas as pd
from datetime import datetime
