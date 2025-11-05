"""
Rotas de conciliação manual
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.reconciliation import Reconciliation, ManualMatch, ReconciliationMatch

router = APIRouter()


class ManualMatchCreate(BaseModel):
    reconciliation_id: int
    bank_transaction_id: int
    internal_transaction_id: int


class PendingTransactionsResponse(BaseModel):
    bank_pending: list
    internal_pending: list


@router.get("/reconciliation/{reconciliation_id}/pending", response_model=PendingTransactionsResponse)
def get_pending_transactions(
    reconciliation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna transações pendentes de uma conciliação
    """
    reconciliation = db.query(Reconciliation).filter(
        Reconciliation.id == reconciliation_id,
        Reconciliation.user_id == current_user.id
    ).first()
    
    if not reconciliation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conciliação não encontrada"
        )
    
    # Buscar matches existentes
    existing_matches = db.query(ReconciliationMatch).filter(
        ReconciliationMatch.reconciliation_id == reconciliation_id
    ).all()
    
    # IDs já conciliados
    matched_bank_ids = set()
    matched_internal_ids = set()
    
    for match in existing_matches:
        if match.bank_transaction_data and 'id' in match.bank_transaction_data:
            matched_bank_ids.add(match.bank_transaction_data['id'])
        if match.internal_transaction_data and 'id' in match.internal_transaction_data:
            matched_internal_ids.add(match.internal_transaction_data['id'])
    
    # Retornar pendentes (simplificado - você pode melhorar isso)
    return {
        "bank_pending": [],
        "internal_pending": []
    }


@router.post("/manual-match")
def create_manual_match(
    match_data: ManualMatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria um match manual entre transações
    """
    reconciliation = db.query(Reconciliation).filter(
        Reconciliation.id == match_data.reconciliation_id,
        Reconciliation.user_id == current_user.id
    ).first()
    
    if not reconciliation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conciliação não encontrada"
        )
    
    # Criar match manual
    manual_match = ManualMatch(
        reconciliation_id=match_data.reconciliation_id,
        bank_transaction_id=match_data.bank_transaction_id,
        internal_transaction_id=match_data.internal_transaction_id
    )
    
    db.add(manual_match)
    
    # Atualizar estatísticas da conciliação
    reconciliation.matched_count += 1
    reconciliation.bank_only_count -= 1
    reconciliation.internal_only_count -= 1
    
    # Recalcular match_rate
    total = reconciliation.total_bank_transactions + reconciliation.total_internal_transactions
    if total > 0:
        reconciliation.match_rate = (reconciliation.matched_count * 2 / total) * 100
    
    db.commit()
    
    return {"message": "Match manual criado com sucesso", "match_id": manual_match.id}
