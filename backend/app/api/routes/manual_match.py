"""
Rotas de conciliação manual
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction, TransactionStatus
from app.models.reconciliation import Reconciliation


router = APIRouter()


class ManualMatchRequest(BaseModel):
    reconciliation_id: int
    bank_transaction_id: int
    internal_transaction_id: int


@router.post("/manual-match")
def create_manual_match(
    match_data: ManualMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria um match manual entre duas transações pendentes
    """
    # Verificar se a conciliação pertence ao usuário
    reconciliation = db.query(Reconciliation).filter(
        Reconciliation.id == match_data.reconciliation_id,
        Reconciliation.user_id == current_user.id
    ).first()
    
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Conciliação não encontrada")
    
    # Buscar transações
    bank_trans = db.query(Transaction).filter(
        Transaction.id == match_data.bank_transaction_id,
        Transaction.reconciliation_id == match_data.reconciliation_id,
        Transaction.status == TransactionStatus.PENDING
    ).first()
    
    internal_trans = db.query(Transaction).filter(
        Transaction.id == match_data.internal_transaction_id,
        Transaction.reconciliation_id == match_data.reconciliation_id,
        Transaction.status == TransactionStatus.PENDING
    ).first()
    
    if not bank_trans or not internal_trans:
        raise HTTPException(status_code=404, detail="Transações não encontradas ou já conciliadas")
    
    # Criar match manual
    bank_trans.status = TransactionStatus.MATCHED
    bank_trans.matched_with_id = internal_trans.id
    bank_trans.confidence = 1.0  # Match manual = 100% confiança
    
    internal_trans.status = TransactionStatus.MATCHED
    internal_trans.matched_with_id = bank_trans.id
    internal_trans.confidence = 1.0
    
    # Atualizar contadores da conciliação
    reconciliation.matched_count += 1
    reconciliation.manual_matches_count += 1
    reconciliation.bank_only_count -= 1
    reconciliation.internal_only_count -= 1
    
    # Recalcular match_rate
    total = reconciliation.total_bank_transactions + reconciliation.total_internal_transactions
    reconciliation.match_rate = (reconciliation.matched_count * 2 / total) * 100
    
    db.commit()
    
    return {
        "message": "Match manual criado com sucesso",
        "reconciliation_id": reconciliation.id,
        "new_match_rate": reconciliation.match_rate
    }


@router.get("/reconciliation/{reconciliation_id}/pending")
def get_pending_transactions(
    reconciliation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna transações pendentes de uma conciliação
    """
    # Verificar se a conciliação pertence ao usuário
    reconciliation = db.query(Reconciliation).filter(
        Reconciliation.id == reconciliation_id,
        Reconciliation.user_id == current_user.id
    ).first()
    
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Conciliação não encontrada")
    
    # Buscar transações pendentes
    bank_pending = db.query(Transaction).filter(
        Transaction.reconciliation_id == reconciliation_id,
        Transaction.status == TransactionStatus.PENDING,
        Transaction.source.in_(['bank'])
    ).all()
    
    internal_pending = db.query(Transaction).filter(
        Transaction.reconciliation_id == reconciliation_id,
        Transaction.status == TransactionStatus.PENDING,
        Transaction.source.in_(['internal'])
    ).all()
    
    return {
        "reconciliation_id": reconciliation_id,
        "bank_pending": [
            {
                "id": t.id,
                "date": t.date.isoformat(),
                "value": t.value,
                "description": t.description
            }
            for t in bank_pending
        ],
        "internal_pending": [
            {
                "id": t.id,
                "date": t.date.isoformat(),
                "value": t.value,
                "description": t.description
            }
            for t in internal_pending
        ]
    }
