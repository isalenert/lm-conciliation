"""
Schemas Pydantic para validação de dados
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ========== SCHEMAS DE UPLOAD ==========

class FileUploadResponse(BaseModel):
    """Resposta do upload de arquivo"""
    filename: str
    columns: List[str]
    row_count: int
    preview: List[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "banco_janeiro.csv",
                "columns": ["Data", "Valor", "Descricao"],
                "row_count": 342,
                "preview": [
                    {"Data": "2025-01-10", "Valor": 150.00, "Descricao": "Pagamento"}
                ]
            }
        }


class PDFUploadResponse(BaseModel):
    """Resposta do upload de PDF"""
    filename: str
    text_length: int
    transactions_count: int
    preview_text: str
    preview_data: List[Dict[str, Any]]


# ========== SCHEMAS DE CONCILIAÇÃO ==========

class ReconciliationRequest(BaseModel):
    """Requisição de conciliação"""
    date_col: str = Field(default="Data", description="Nome da coluna de data")
    value_col: str = Field(default="Valor", description="Nome da coluna de valor")
    desc_col: str = Field(default="Descricao", description="Nome da coluna de descrição")
    id_col: Optional[str] = Field(default=None, description="Nome da coluna de ID")
    date_tolerance: int = Field(default=1, ge=0, le=7, description="Tolerância em dias")
    value_tolerance: float = Field(default=0.02, ge=0, le=1, description="Tolerância em valor")
    similarity_threshold: float = Field(default=0.7, ge=0, le=1, description="Threshold de similaridade")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date_col": "Data",
                "value_col": "Valor",
                "desc_col": "Descricao",
                "date_tolerance": 1,
                "value_tolerance": 0.02,
                "similarity_threshold": 0.7
            }
        }


class TransactionMatch(BaseModel):
    """Transação pareada"""
    bank_transaction: Dict[str, Any]
    internal_transaction: Dict[str, Any]
    confidence: float


class ReconciliationSummary(BaseModel):
    """Resumo da conciliação"""
    total_bank_transactions: int
    total_internal_transactions: int
    matched_count: int
    bank_only_count: int
    internal_only_count: int
    match_rate: float


class ReconciliationResponse(BaseModel):
    """Resposta completa da conciliação"""
    matched: List[TransactionMatch]
    bank_only: List[Dict[str, Any]]
    internal_only: List[Dict[str, Any]]
    summary: ReconciliationSummary
    
    class Config:
        json_schema_extra = {
            "example": {
                "matched": [],
                "bank_only": [],
                "internal_only": [],
                "summary": {
                    "total_bank_transactions": 100,
                    "total_internal_transactions": 98,
                    "matched_count": 95,
                    "bank_only_count": 5,
                    "internal_only_count": 3,
                    "match_rate": 95.0
                }
            }
        }


# ========== SCHEMAS DE ERRO ==========

class ErrorResponse(BaseModel):
    """Resposta de erro padrão"""
    error: str
    detail: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Arquivo inválido",
                "detail": "Formato não suportado. Use CSV ou PDF."
            }
        }
