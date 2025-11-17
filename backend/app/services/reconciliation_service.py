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
    
    @staticmethod
    def get_user_statistics(user_id: int, db) -> Dict[str, Any]:
        """
        Calcula estatísticas agregadas do usuário
        
        Args:
            user_id: ID do usuário
            db: Sessão do banco de dados
            
        Returns:
            Dict com estatísticas do usuário:
            - total_reconciliations: Total de conciliações realizadas
            - total_transactions: Total de transações processadas
            - total_matched: Total de transações conciliadas
            - total_pending: Total de transações pendentes
            - average_match_rate: Taxa média de acerto (%)
            - last_reconciliation_date: Data da última conciliação
        """
        from sqlalchemy import func
        
        # Buscar todas as conciliações do usuário
        reconciliations = db.query(Reconciliation).filter(
            Reconciliation.user_id == user_id
        ).all()
        
        if not reconciliations:
            return {
                "total_reconciliations": 0,
                "total_transactions": 0,
                "total_matched": 0,
                "total_pending": 0,
                "average_match_rate": 0.0,
                "last_reconciliation_date": None
            }
        
        # Calcular estatísticas agregadas
        total_reconciliations = len(reconciliations)
        total_matches = sum(r.matched_count or 0 for r in reconciliations)
        total_bank = sum(r.total_bank_transactions or 0 for r in reconciliations)
        total_internal = sum(r.total_internal_transactions or 0 for r in reconciliations)
        
        # Calcular totais
        total_transactions = total_bank + total_internal
        total_pending = total_transactions - (total_matches * 2)
        
        # Calcular taxa média ponderada
        if total_transactions > 0:
            average_match_rate = (total_matches * 2 / total_transactions) * 100
        else:
            average_match_rate = 0.0
        
        # Última conciliação
        last_reconciliation = max(reconciliations, key=lambda r: r.created_at)
        
        return {
            "total_reconciliations": total_reconciliations,
            "total_transactions": total_transactions,
            "total_matched": total_matches,
            "total_pending": total_pending,
            "average_match_rate": round(average_match_rate, 2),
            "last_reconciliation_date": last_reconciliation.created_at.isoformat()
        }
    
    @staticmethod
    def get_user_reconciliations(db, user_id: int) -> List[Dict[str, Any]]:
        """
        Retorna todas as conciliações de um usuário, ordenadas por data (mais recentes primeiro).
        
        Requisitos atendidos:
        - RF08: Visualizar histórico de conciliações
        - RNF06: Código manutenível com docstrings
        
        Args:
            db: Sessão do banco de dados SQLAlchemy
            user_id: ID do usuário autenticado
            
        Returns:
            List[Dict]: Lista de conciliações formatadas para JSON
            
        Exemplo:
            >>> reconciliations = ReconciliationService.get_user_reconciliations(db, 1)
            >>> print(reconciliations[0]['bank_file_name'])
            'extrato_janeiro.pdf'
        """
        # Buscar conciliações do usuário (ordenadas por data decrescente)
        reconciliations = db.query(Reconciliation).filter(
            Reconciliation.user_id == user_id
        ).order_by(Reconciliation.created_at.desc()).all()
        
        # Formatar para JSON (tratando valores None)
        return [
            {
                "id": rec.id,
                "user_id": rec.user_id,
                "bank_file_name": rec.bank_file_name,
                "internal_file_name": rec.internal_file_name,
                "created_at": rec.created_at.isoformat() if rec.created_at else None,
                "total_bank_transactions": rec.total_bank_transactions or 0,
                "total_internal_transactions": rec.total_internal_transactions or 0,
                "matched_count": rec.matched_count or 0,
                "bank_only_count": rec.bank_only_count or 0,
                "internal_only_count": rec.internal_only_count or 0,
                "match_rate": round(rec.match_rate or 0.0, 2)
            }
            for rec in reconciliations
        ]