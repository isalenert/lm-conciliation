"""
Rotas de conciliação
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List
import os

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.reconciliation import Reconciliation, ReconciliationMatch
from app.core.csv_processor import CSVProcessor
from app.core.reconciliation_processor import ReconciliationProcessor

router = APIRouter()

UPLOAD_DIR = "/tmp/lm-conciliation-uploads"


class ColumnMapping(BaseModel):
    date_col: str
    value_col: str
    desc_col: str


class ReconcileRequest(BaseModel):
    bank_file: str
    internal_file: str
    bank_mapping: ColumnMapping
    internal_mapping: ColumnMapping
    date_tolerance: int = 1
    value_tolerance: float = 0.02
    similarity_threshold: float = 0.7


@router.post("/reconcile")
async def reconcile_transactions(
    request: ReconcileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executa conciliação entre arquivos bancário e interno
    """
    bank_path = os.path.join(UPLOAD_DIR, request.bank_file)
    internal_path = os.path.join(UPLOAD_DIR, request.internal_file)
    
    if not os.path.exists(bank_path) or not os.path.exists(internal_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivos não encontrados"
        )
    
    try:
        # Processar arquivos
        bank_df = CSVProcessor.read_csv(bank_path)
        internal_df = CSVProcessor.read_csv(internal_path)
        
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
        
        # Executar conciliação
        processor = ReconciliationProcessor(
            date_tolerance=request.date_tolerance,
            value_tolerance=request.value_tolerance,
            similarity_threshold=request.similarity_threshold
        )
        
        results = processor.reconcile(bank_data, internal_data)
        
        # Salvar no banco
        reconciliation = Reconciliation(
            user_id=current_user.id,
            bank_file_name=request.bank_file,
            internal_file_name=request.internal_file,
            total_bank_transactions=results['summary']['total_bank_transactions'],
            total_internal_transactions=results['summary']['total_internal_transactions'],
            matched_count=results['summary']['matched_count'],
            bank_only_count=results['summary']['bank_only_count'],
            internal_only_count=results['summary']['internal_only_count'],
            match_rate=results['summary']['match_rate']
        )
        
        db.add(reconciliation)
        db.commit()
        db.refresh(reconciliation)
        
        # Salvar matches
        for match in results['matched']:
            match_record = ReconciliationMatch(
                reconciliation_id=reconciliation.id,
                bank_transaction_data=match['bank_transaction'],
                internal_transaction_data=match['internal_transaction'],
                confidence=match['confidence'],
                is_manual=False
            )
            db.add(match_record)
        
        db.commit()
        
        # Retornar no formato esperado pelo frontend
        return {
            "reconciliation_id": reconciliation.id,
            "summary": results['summary'],
            "matched": results['matched'],
            "bank_only": results['bank_only'],
            "internal_only": results['internal_only']
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na conciliação: {str(e)}"
        )
