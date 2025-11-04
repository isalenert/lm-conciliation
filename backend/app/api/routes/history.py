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
    
    Inclui todas as transações
    """
    reconciliation = ReconciliationService.get_reconciliation_by_id(
        db=db,
        reconciliation_id=reconciliation_id,
        user_id=current_user.id
    )
    
    if not reconciliation:
        raise HTTPException(
            status_code=404,
            detail="Conciliação não encontrada"
        )
    
    # Buscar transações
    matched_transactions = [
        t for t in reconciliation.transactions 
        if t.status.value == 'matched'
    ]
    
    bank_only = [
        t for t in reconciliation.transactions 
        if t.status.value == 'pending' and t.source.value == 'bank'
    ]
    
    internal_only = [
        t for t in reconciliation.transactions 
        if t.status.value == 'pending' and t.source.value == 'internal'
    ]
    
    # Construir pares de matches
    matched_pairs = []
    processed_ids = set()
    
    for transaction in matched_transactions:
        if transaction.id in processed_ids:
            continue
            
        if transaction.matched_with_id:
            matched_with = next(
                (t for t in matched_transactions if t.id == transaction.matched_with_id),
                None
            )
            
            if matched_with:
                if transaction.source.value == 'bank':
                    bank_trans = transaction
                    internal_trans = matched_with
                else:
                    bank_trans = matched_with
                    internal_trans = transaction
                
                matched_pairs.append({
                    'bank_transaction': {
                        'Data': bank_trans.date.isoformat(),
                        'Valor': bank_trans.value,
                        'Descricao': bank_trans.description
                    },
                    'internal_transaction': {
                        'Data': internal_trans.date.isoformat(),
                        'Valor': internal_trans.value,
                        'Descricao': internal_trans.description
                    },
                    'confidence': bank_trans.confidence
                })
                
                processed_ids.add(transaction.id)
                processed_ids.add(matched_with.id)
    
    return {
        'id': reconciliation.id,
        'bank_file_name': reconciliation.bank_file_name,
        'internal_file_name': reconciliation.internal_file_name,
        'created_at': reconciliation.created_at,
        'matched': matched_pairs,
        'bank_only': [
            {
                'Data': t.date.isoformat(),
                'Valor': t.value,
                'Descricao': t.description
            }
            for t in bank_only
        ],
        'internal_only': [
            {
                'Data': t.date.isoformat(),
                'Valor': t.value,
                'Descricao': t.description
            }
            for t in internal_only
        ],
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
