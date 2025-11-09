"""
Rotas de histórico de conciliações
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.services.reconciliation_service import ReconciliationService
from app.models.user import User
from pydantic import BaseModel
from datetime import datetime


router = APIRouter()


# Schemas
class ReconciliationListItem(BaseModel):
    id: int
    bank_file_name: str
    internal_file_name: str
    match_rate: float
    matched_count: int
    total_bank_transactions: int
    total_internal_transactions: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserStatistics(BaseModel):
    total_reconciliations: int
    total_transactions: int
    average_match_rate: float
    total_matched: int
    total_pending: int


@router.get("/history", response_model=List[ReconciliationListItem])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna histórico de conciliações do usuário
    
    Requer autenticação
    """
    reconciliations = ReconciliationService.get_user_reconciliations(
        db=db,
        user_id=current_user.id
    )
    
    return reconciliations


@router.get("/history/{reconciliation_id}")
def get_reconciliation_details(
    reconciliation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna detalhes de uma conciliação específica
    """
    from app.models.reconciliation import Reconciliation, ReconciliationMatch
    
    # Buscar conciliação
    reconciliation = db.query(Reconciliation).filter(
        Reconciliation.id == reconciliation_id,
        Reconciliation.user_id == current_user.id
    ).first()
    
    if not reconciliation:
        raise HTTPException(
            status_code=404,
            detail="Conciliação não encontrada"
        )
    
    # Buscar todos os matches desta conciliação
    matches = db.query(ReconciliationMatch).filter(
        ReconciliationMatch.reconciliation_id == reconciliation_id
    ).all()
    
    # Formatar matches
    matched = []
    for match in matches:
        matched.append({
            'bank_transaction': match.bank_transaction_data,
            'internal_transaction': match.internal_transaction_data,
            'confidence': match.confidence,
            'is_manual': match.is_manual
        })
    
    # Reprocessar arquivos para pegar pendências
    import os
    from app.core.csv_processor import CSVProcessor
    
    UPLOAD_DIR = "/tmp/lm-conciliation-uploads"
    bank_path = os.path.join(UPLOAD_DIR, reconciliation.bank_file_name)
    internal_path = os.path.join(UPLOAD_DIR, reconciliation.internal_file_name)
    
    bank_only = []
    internal_only = []
    
    if os.path.exists(bank_path) and os.path.exists(internal_path):
        try:
            # IDs já conciliados
            matched_bank_ids = set()
            matched_internal_ids = set()
            
            for match in matches:
                if match.bank_transaction_data and 'id' in match.bank_transaction_data:
                    matched_bank_ids.add(match.bank_transaction_data['id'])
                if match.internal_transaction_data and 'id' in match.internal_transaction_data:
                    matched_internal_ids.add(match.internal_transaction_data['id'])
            
            # Ler e processar arquivos
            bank_df = CSVProcessor.read_csv(bank_path)
            internal_df = CSVProcessor.read_csv(internal_path)
            
            bank_data = CSVProcessor.process_dataframe(bank_df, 'Data', 'Valor', 'Descricao')
            internal_data = CSVProcessor.process_dataframe(internal_df, 'Data', 'Valor', 'Descricao')
            
            # Filtrar pendentes
            bank_only = [t for t in bank_data if t['id'] not in matched_bank_ids]
            internal_only = [t for t in internal_data if t['id'] not in matched_internal_ids]
            
        except Exception as e:
            print(f"Erro ao processar arquivos: {e}")
    
    return {
        'id': reconciliation.id,
        'bank_file_name': reconciliation.bank_file_name,
        'internal_file_name': reconciliation.internal_file_name,
        'created_at': reconciliation.created_at,
        'matched': matched,
        'bank_only': bank_only,
        'internal_only': internal_only,
        'summary': {
            'total_bank_transactions': reconciliation.total_bank_transactions,
            'total_internal_transactions': reconciliation.total_internal_transactions,
            'matched_count': reconciliation.matched_count,
            'bank_only_count': reconciliation.bank_only_count,
            'internal_only_count': reconciliation.internal_only_count,
            'match_rate': reconciliation.match_rate
        }
    }


@router.get("/statistics", response_model=UserStatistics)
def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas do usuário
    """
    stats = ReconciliationService.get_user_statistics(
        db=db,
        user_id=current_user.id
    )
    
    return stats
