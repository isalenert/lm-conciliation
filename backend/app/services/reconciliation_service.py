"""
Service para gerenciar conciliações no banco de dados
"""

from sqlalchemy.orm import Session
from app.models.reconciliation import Reconciliation, ReconciliationStatus
from app.models.transaction import Transaction, TransactionSource, TransactionStatus
from app.models.user import User
from datetime import datetime
from typing import List, Dict
import pandas as pd


class ReconciliationService:
    """Service para operações de conciliação"""
    
    @staticmethod
    def _parse_date(date_value):
        """
        Converte date_value para date object, tratando vários formatos
        """
        if pd.isna(date_value):
            return None
        
        # Se já for um objeto datetime/Timestamp do pandas
        if isinstance(date_value, (pd.Timestamp, datetime)):
            return date_value.date()
        
        # Se for string, tentar converter
        if isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, '%Y-%m-%d').date()
            except ValueError:
                # Tentar outros formatos
                try:
                    return pd.to_datetime(date_value).date()
                except:
                    return None
        
        return None
    
    @staticmethod
    def _parse_value(value):
        """
        Converte value para float
        """
        if pd.isna(value):
            return 0.0
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def create_reconciliation(
        db: Session,
        user_id: int,
        bank_file_name: str,
        internal_file_name: str,
        results: Dict
    ) -> Reconciliation:
        """
        Cria uma nova conciliação no banco
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            bank_file_name: Nome do arquivo do banco
            internal_file_name: Nome do arquivo interno
            results: Resultado da conciliação (do ReconciliationProcessor)
            
        Returns:
            Objeto Reconciliation salvo
        """
        summary = results['summary']
        
        # Criar reconciliation
        reconciliation = Reconciliation(
            user_id=user_id,
            bank_file_name=bank_file_name,
            internal_file_name=internal_file_name,
            total_bank_transactions=summary['total_bank_transactions'],
            total_internal_transactions=summary['total_internal_transactions'],
            matched_count=summary['matched_count'],
            bank_only_count=summary['bank_only_count'],
            internal_only_count=summary['internal_only_count'],
            match_rate=summary['match_rate'],
            status=ReconciliationStatus.COMPLETED
        )
        
        db.add(reconciliation)
        db.flush()  # Para obter o ID
        
        # Salvar transações conciliadas
        for match in results['matched']:
            bank_trans = match['bank_transaction']
            internal_trans = match['internal_transaction']
            
            # Transação do banco
            bank_transaction = Transaction(
                reconciliation_id=reconciliation.id,
                source=TransactionSource.BANK,
                date=ReconciliationService._parse_date(bank_trans['Data']),
                value=ReconciliationService._parse_value(bank_trans['Valor']),
                description=str(bank_trans['Descricao']),
                status=TransactionStatus.MATCHED,
                confidence=match['confidence']
            )
            db.add(bank_transaction)
            db.flush()
            
            # Transação do sistema interno
            internal_transaction = Transaction(
                reconciliation_id=reconciliation.id,
                source=TransactionSource.INTERNAL,
                date=ReconciliationService._parse_date(internal_trans['Data']),
                value=ReconciliationService._parse_value(internal_trans['Valor']),
                description=str(internal_trans['Descricao']),
                status=TransactionStatus.MATCHED,
                matched_with_id=bank_transaction.id,
                confidence=match['confidence']
            )
            db.add(internal_transaction)
            
            # Atualizar matched_with_id da transação do banco
            bank_transaction.matched_with_id = internal_transaction.id
        
        # Salvar transações pendentes do banco
        for bank_trans in results['bank_only']:
            transaction = Transaction(
                reconciliation_id=reconciliation.id,
                source=TransactionSource.BANK,
                date=ReconciliationService._parse_date(bank_trans['Data']),
                value=ReconciliationService._parse_value(bank_trans['Valor']),
                description=str(bank_trans['Descricao']),
                status=TransactionStatus.PENDING
            )
            db.add(transaction)
        
        # Salvar transações pendentes do sistema
        for internal_trans in results['internal_only']:
            transaction = Transaction(
                reconciliation_id=reconciliation.id,
                source=TransactionSource.INTERNAL,
                date=ReconciliationService._parse_date(internal_trans['Data']),
                value=ReconciliationService._parse_value(internal_trans['Valor']),
                description=str(internal_trans['Descricao']),
                status=TransactionStatus.PENDING
            )
            db.add(transaction)
        
        db.commit()
        db.refresh(reconciliation)
        
        return reconciliation
    
    @staticmethod
    def get_user_reconciliations(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Reconciliation]:
        """
        Busca todas as conciliações de um usuário
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            skip: Quantidade a pular (paginação)
            limit: Limite de resultados
            
        Returns:
            Lista de conciliações
        """
        return db.query(Reconciliation)\
            .filter(Reconciliation.user_id == user_id)\
            .order_by(Reconciliation.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_reconciliation_by_id(
        db: Session,
        reconciliation_id: int,
        user_id: int
    ) -> Reconciliation:
        """
        Busca uma conciliação específica
        
        Args:
            db: Sessão do banco
            reconciliation_id: ID da conciliação
            user_id: ID do usuário (para validar propriedade)
            
        Returns:
            Conciliação ou None
        """
        return db.query(Reconciliation)\
            .filter(
                Reconciliation.id == reconciliation_id,
                Reconciliation.user_id == user_id
            )\
            .first()
    
    @staticmethod
    def get_user_statistics(db: Session, user_id: int) -> Dict:
        """
        Calcula estatísticas do usuário
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            
        Returns:
            Dicionário com estatísticas
        """
        reconciliations = db.query(Reconciliation)\
            .filter(Reconciliation.user_id == user_id)\
            .all()
        
        if not reconciliations:
            return {
                'total_reconciliations': 0,
                'total_transactions': 0,
                'average_match_rate': 0.0,
                'total_matched': 0,
                'total_pending': 0
            }
        
        total_transactions = sum(
            r.total_bank_transactions + r.total_internal_transactions 
            for r in reconciliations
        )
        
        avg_match_rate = sum(r.match_rate for r in reconciliations) / len(reconciliations)
        
        total_matched = sum(r.matched_count for r in reconciliations)
        total_pending = sum(
            r.bank_only_count + r.internal_only_count 
            for r in reconciliations
        )
        
        return {
            'total_reconciliations': len(reconciliations),
            'total_transactions': total_transactions,
            'average_match_rate': round(avg_match_rate, 2),
            'total_matched': total_matched,
            'total_pending': total_pending
        }
