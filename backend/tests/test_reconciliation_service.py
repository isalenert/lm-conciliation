"""
Testes para ReconciliationService
Seguindo requisitos do RFC: TDD com 50%+ coverage
Meta: 30 testes, coverage > 50%
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from app.services.reconciliation_service import ReconciliationService


class TestGetUserReconciliations:
    """Suite de testes para o método get_user_reconciliations"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Fixture: Mock da sessão do banco de dados"""
        return MagicMock()
    
    @pytest.fixture
    def sample_reconciliation(self):
        """Fixture: Dados de amostra de uma conciliação"""
        mock_rec = MagicMock()
        mock_rec.id = 1
        mock_rec.user_id = 100
        mock_rec.bank_file_name = "extrato_janeiro.pdf"
        mock_rec.internal_file_name = "relatorio_janeiro.csv"
        mock_rec.created_at = datetime(2025, 1, 15, 10, 30)
        mock_rec.total_bank_transactions = 20
        mock_rec.total_internal_transactions = 18
        mock_rec.matched_count = 15
        mock_rec.bank_only_count = 5
        mock_rec.internal_only_count = 3
        mock_rec.match_rate = 78.95
        return mock_rec
    
    def test_returns_empty_list_when_no_reconciliations(self, mock_db_session):
        """
        TESTE 1: Deve retornar lista vazia quando usuário não tem conciliações
        Requisito: RNF06 - Cobertura de testes > 50%
        """
        # Arrange
        user_id = 999
        mock_query = mock_db_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = []
        
        # Act
        result = ReconciliationService.get_user_reconciliations(mock_db_session, user_id)
        
        # Assert
        assert result == []
        assert isinstance(result, list)
    
    def test_returns_formatted_list_with_all_fields(self, mock_db_session, sample_reconciliation):
        """
        TESTE 2: Deve retornar lista formatada com todos os campos corretos
        Requisito: RF08 - Visualizar histórico de conciliações
        """
        # Arrange
        user_id = 100
        mock_query = mock_db_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = [sample_reconciliation]
        
        # Act
        result = ReconciliationService.get_user_reconciliations(mock_db_session, user_id)
        
        # Assert
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["user_id"] == 100
        assert result[0]["bank_file_name"] == "extrato_janeiro.pdf"
        assert result[0]["internal_file_name"] == "relatorio_janeiro.csv"
        assert result[0]["total_bank_transactions"] == 20
        assert result[0]["total_internal_transactions"] == 18
        assert result[0]["matched_count"] == 15
        assert result[0]["bank_only_count"] == 5
        assert result[0]["internal_only_count"] == 3
        assert result[0]["match_rate"] == 78.95
    
    def test_orders_by_created_at_descending(self, mock_db_session):
        """
        TESTE 3: Deve ordenar resultados por data (mais recentes primeiro)
        Requisito: RF08 - Histórico ordenado cronologicamente
        """
        # Arrange
        user_id = 100
        
        # Criar 2 conciliações com datas diferentes
        rec_old = MagicMock()
        rec_old.id = 1
        rec_old.user_id = user_id
        rec_old.created_at = datetime(2025, 1, 1, 10, 0)
        rec_old.bank_file_name = "old.pdf"
        rec_old.internal_file_name = "old.csv"
        rec_old.total_bank_transactions = 10
        rec_old.total_internal_transactions = 10
        rec_old.matched_count = 5
        rec_old.bank_only_count = 5
        rec_old.internal_only_count = 5
        rec_old.match_rate = 50.0
        
        rec_new = MagicMock()
        rec_new.id = 2
        rec_new.user_id = user_id
        rec_new.created_at = datetime(2025, 1, 15, 14, 30)
        rec_new.bank_file_name = "new.pdf"
        rec_new.internal_file_name = "new.csv"
        rec_new.total_bank_transactions = 20
        rec_new.total_internal_transactions = 20
        rec_new.matched_count = 15
        rec_new.bank_only_count = 5
        rec_new.internal_only_count = 5
        rec_new.match_rate = 75.0
        
        mock_query = mock_db_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = [rec_new, rec_old]  # Mais recente primeiro
        
        # Act
        result = ReconciliationService.get_user_reconciliations(mock_db_session, user_id)
        
        # Assert
        assert len(result) == 2
        assert result[0]["id"] == 2  # Mais recente
        assert result[0]["created_at"] == "2025-01-15T14:30:00"
        assert result[1]["id"] == 1  # Mais antiga
        assert result[1]["created_at"] == "2025-01-01T10:00:00"
    
    def test_handles_none_values_correctly(self, mock_db_session):
        """
        TESTE 4: Deve tratar valores None/null corretamente
        Requisito: RNF06 - Código manutenível e resiliente
        """
        # Arrange
        user_id = 100
        mock_rec = MagicMock()
        mock_rec.id = 1
        mock_rec.user_id = user_id
        mock_rec.bank_file_name = "test.pdf"
        mock_rec.internal_file_name = "test.csv"
        mock_rec.created_at = datetime(2025, 1, 15)
        # Simular valores None do banco
        mock_rec.total_bank_transactions = None
        mock_rec.total_internal_transactions = None
        mock_rec.matched_count = None
        mock_rec.bank_only_count = None
        mock_rec.internal_only_count = None
        mock_rec.match_rate = None
        
        mock_query = mock_db_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = [mock_rec]
        
        # Act
        result = ReconciliationService.get_user_reconciliations(mock_db_session, user_id)
        
        # Assert
        assert result[0]["total_bank_transactions"] == 0
        assert result[0]["total_internal_transactions"] == 0
        assert result[0]["matched_count"] == 0
        assert result[0]["bank_only_count"] == 0
        assert result[0]["internal_only_count"] == 0
        assert result[0]["match_rate"] == 0.0
    
    def test_returns_multiple_reconciliations(self, mock_db_session):
        """
        TESTE 5: Deve retornar múltiplas conciliações corretamente
        Requisito: RNF01 - Performance (processar múltiplos registros)
        """
        # Arrange
        user_id = 100
        mock_recs = []
        for i in range(5):
            mock_rec = MagicMock()
            mock_rec.id = i + 1
            mock_rec.user_id = user_id
            mock_rec.bank_file_name = f"extrato_{i}.pdf"
            mock_rec.internal_file_name = f"relatorio_{i}.csv"
            mock_rec.created_at = datetime(2025, 1, i + 1)
            mock_rec.total_bank_transactions = 10 * (i + 1)
            mock_rec.total_internal_transactions = 10 * (i + 1)
            mock_rec.matched_count = 5 * (i + 1)
            mock_rec.bank_only_count = 2 * (i + 1)
            mock_rec.internal_only_count = 3 * (i + 1)
            mock_rec.match_rate = 50.0 + (i * 5)
            mock_recs.append(mock_rec)
        
        mock_query = mock_db_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = mock_recs
        
        # Act
        result = ReconciliationService.get_user_reconciliations(mock_db_session, user_id)
        
        # Assert
        assert len(result) == 5
        assert result[0]["id"] == 1
        assert result[4]["id"] == 5
    
    def test_filters_by_user_id_correctly(self, mock_db_session):
        """
        TESTE 6: Deve filtrar corretamente por user_id
        Requisito: RNF02 - Segurança (isolamento de dados por usuário)
        """
        # Arrange
        user_id = 100
        mock_query = mock_db_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = []
        
        # Act
        ReconciliationService.get_user_reconciliations(mock_db_session, user_id)
        
        # Assert
        # Verificar que query foi chamado com o modelo correto
        from app.models.reconciliation import Reconciliation
        mock_db_session.query.assert_called_once()
        
        # Verificar que filter foi chamado
        mock_query.filter.assert_called_once()
    
    def test_created_at_iso_format(self, mock_db_session, sample_reconciliation):
        """
        TESTE 7: Deve retornar created_at no formato ISO 8601
        Requisito: RNF04 - Compatibilidade (formato de data padrão)
        """
        # Arrange
        user_id = 100
        mock_query = mock_db_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = [sample_reconciliation]
        
        # Act
        result = ReconciliationService.get_user_reconciliations(mock_db_session, user_id)
        
        # Assert
        assert result[0]["created_at"] == "2025-01-15T10:30:00"
        assert "T" in result[0]["created_at"]  # Formato ISO
    
    def test_match_rate_rounded_to_two_decimals(self, mock_db_session):
        """
        TESTE 8: Deve arredondar match_rate para 2 casas decimais
        Requisito: RNF03 - Usabilidade (precisão visual adequada)
        """
        # Arrange
        user_id = 100
        mock_rec = MagicMock()
        mock_rec.id = 1
        mock_rec.user_id = user_id
        mock_rec.bank_file_name = "test.pdf"
        mock_rec.internal_file_name = "test.csv"
        mock_rec.created_at = datetime(2025, 1, 15)
        mock_rec.total_bank_transactions = 100
        mock_rec.total_internal_transactions = 100
        mock_rec.matched_count = 75
        mock_rec.bank_only_count = 25
        mock_rec.internal_only_count = 25
        mock_rec.match_rate = 75.6789  # Valor com muitas casas decimais
        
        mock_query = mock_db_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = [mock_rec]
        
        # Act
        result = ReconciliationService.get_user_reconciliations(mock_db_session, user_id)
        
        # Assert
        assert result[0]["match_rate"] == 75.68  # Arredondado para 2 casas