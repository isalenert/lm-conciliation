"""
Serviço de reconciliação
"""
from typing import List, Dict, Any
from datetime import datetime

from app.models.reconciliation import Reconciliation, ReconciliationMatch
from app.core.reconciliation_processor import ReconciliationProcessor


class ReconciliationService:
    """Serviço para processar conciliações"""
    
    @staticmethod
    def process_reconciliation(
        bank_data: List[Dict],
        internal_data: List[Dict],
        date_col: str,
        value_col: str,
        desc_col: str,
        id_col: str = None,
        date_tolerance: int = 1,
        value_tolerance: float = 0.02,
        similarity_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Processa a conciliação entre dados bancários e internos
        
        Returns:
            Dict com resultados da conciliação
        """
        processor = ReconciliationProcessor(
            date_tolerance=date_tolerance,
            value_tolerance=value_tolerance,
            similarity_threshold=similarity_threshold
        )
        
        results = processor.reconcile(
            bank_data=bank_data,
            internal_data=internal_data,
            date_col=date_col,
            value_col=value_col,
            desc_col=desc_col,
            id_col=id_col
        )
        
        return results
    
    @staticmethod
    def save_reconciliation_to_db(
        db,
        user_id: int,
        bank_file_name: str,
        internal_file_name: str,
        results: Dict[str, Any]
    ) -> Reconciliation:
        """
        Salva resultado da conciliação no banco
        """
        reconciliation = Reconciliation(
            user_id=user_id,
            bank_file_name=bank_file_name,
            internal_file_name=internal_file_name,
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
        
        return reconciliation
