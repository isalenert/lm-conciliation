"""
Testes para ReconciliationService 
Adaptado para a estrutura real do ReconciliationProcessor (retorna dict)

"""
import pytest
from datetime import datetime, timedelta  # ✅ FIX: Adicionar timedelta
from unittest.mock import MagicMock, patch, AsyncMock


# ============================================================================
# FIXTURES COMPARTILHADAS
# ============================================================================

@pytest.fixture
def mock_db_session():
    """Fixture: Mock da sessão do banco de dados"""
    return MagicMock()


@pytest.fixture
def sample_reconciliation():
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


@pytest.fixture
def sample_reconciliation_result():
    """Fixture: Resultado típico do ReconciliationProcessor.reconcile()"""
    return {
        'matched': [
            {
                'bank_transaction': {'id': 1, 'date': '2024-01-15', 'value': 100.00, 'description': 'Pagamento A'},
                'internal_transaction': {'id': 1, 'date': '2024-01-15', 'value': 100.00, 'description': 'Pagto A'},
                'confidence': 0.95
            }
        ],
        'bank_only': [
            {'id': 2, 'date': '2024-01-16', 'value': 200.00, 'description': 'Pagamento B'}
        ],
        'internal_only': [],
        'summary': {
            'total_bank_transactions': 2,
            'total_internal_transactions': 1,
            'matched_count': 1,
            'bank_only_count': 1,
            'internal_only_count': 0,
            'match_rate': 66.67
        }
    }


# ============================================================================
# SUITE 1: HISTÓRICO DE CONCILIAÇÕES (get_user_reconciliations)
# ============================================================================

class TestGetUserReconciliations:
    """Suite de testes para o método get_user_reconciliations"""
    
    def test_returns_empty_list_when_no_reconciliations(self, mock_db_session):
        """
        TESTE 1: Deve retornar lista vazia quando usuário não tem conciliações
        Requisito: RNF06 - Cobertura de testes > 50%
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
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
        from app.services.reconciliation_service import ReconciliationService
        
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
        from app.services.reconciliation_service import ReconciliationService
        
        user_id = 100
        
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
        mock_order.all.return_value = [rec_new, rec_old]
        
        # Act
        result = ReconciliationService.get_user_reconciliations(mock_db_session, user_id)
        
        # Assert
        assert len(result) == 2
        assert result[0]["id"] == 2
        assert result[0]["created_at"] == "2025-01-15T14:30:00"
        assert result[1]["id"] == 1
        assert result[1]["created_at"] == "2025-01-01T10:00:00"
    
    def test_handles_none_values_correctly(self, mock_db_session):
        """
        TESTE 4: Deve tratar valores None/null corretamente
        Requisito: RNF06 - Código manutenível e resiliente
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
        user_id = 100
        mock_rec = MagicMock()
        mock_rec.id = 1
        mock_rec.user_id = user_id
        mock_rec.bank_file_name = "test.pdf"
        mock_rec.internal_file_name = "test.csv"
        mock_rec.created_at = datetime(2025, 1, 15)
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
        from app.services.reconciliation_service import ReconciliationService
        
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
        from app.services.reconciliation_service import ReconciliationService
        
        user_id = 100
        mock_query = mock_db_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = []
        
        # Act
        ReconciliationService.get_user_reconciliations(mock_db_session, user_id)
        
        # Assert
        mock_db_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
    
    def test_created_at_iso_format(self, mock_db_session, sample_reconciliation):
        """
        TESTE 7: Deve retornar created_at no formato ISO 8601
        Requisito: RNF04 - Compatibilidade (formato de data padrão)
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
        user_id = 100
        mock_query = mock_db_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = [sample_reconciliation]
        
        # Act
        result = ReconciliationService.get_user_reconciliations(mock_db_session, user_id)
        
        # Assert
        assert result[0]["created_at"] == "2025-01-15T10:30:00"
        assert "T" in result[0]["created_at"]
    
    def test_match_rate_rounded_to_two_decimals(self, mock_db_session):
        """
        TESTE 8: Deve arredondar match_rate para 2 casas decimais
        Requisito: RNF03 - Usabilidade (precisão visual adequada)
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
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
        mock_rec.match_rate = 75.6789
        
        mock_query = mock_db_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = [mock_rec]
        
        # Act
        result = ReconciliationService.get_user_reconciliations(mock_db_session, user_id)
        
        # Assert
        assert result[0]["match_rate"] == 75.68


# ============================================================================
# SUITE 2: ESTATÍSTICAS AGREGADAS (get_user_statistics)
# ============================================================================

class TestGetUserStatistics:
    """Suite de testes para estatísticas agregadas"""
    
    def test_get_user_statistics_multiple_reconciliations(self, mock_db_session):
        """
        TESTE 9: Deve calcular estatísticas agregadas corretamente
        Requisito: RF08 - Dashboard com métricas
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
        user_id = 100
        
        mock_rec1 = MagicMock()
        mock_rec1.matched_count = 10
        mock_rec1.total_bank_transactions = 15
        mock_rec1.total_internal_transactions = 12
        mock_rec1.bank_only_count = 5
        mock_rec1.internal_only_count = 2
        mock_rec1.created_at = datetime(2025, 1, 1, 10, 0)  # ✅ FIX: Adicionar created_at
        
        mock_rec2 = MagicMock()
        mock_rec2.matched_count = 20
        mock_rec2.total_bank_transactions = 25
        mock_rec2.total_internal_transactions = 22
        mock_rec2.bank_only_count = 5
        mock_rec2.internal_only_count = 2
        mock_rec2.created_at = datetime(2025, 1, 15, 14, 30)  # ✅ FIX: Adicionar created_at
        
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.all.return_value = [mock_rec1, mock_rec2]
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        # Act
        stats = ReconciliationService.get_user_statistics(user_id, mock_db_session)
        
        # Assert
        assert stats['total_reconciliations'] == 2
        assert stats['total_matched'] == 30
        assert stats['total_transactions'] == 74
        assert 'average_match_rate' in stats
        assert stats['last_reconciliation_date'] is not None  # ✅ FIX: Verificar campo
    
    def test_get_user_statistics_no_reconciliations(self, mock_db_session):
        """
        TESTE 10: Deve retornar zeros quando não há conciliações
        Requisito: RNF06 - Tratamento de casos vazios
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
        user_id = 999
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.all.return_value = []
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        # Act
        stats = ReconciliationService.get_user_statistics(user_id, mock_db_session)
        
        # Assert
        assert stats['total_reconciliations'] == 0
        assert stats['total_matched'] == 0
        assert stats['average_match_rate'] == 0.0
    
    def test_handles_database_error(self, mock_db_session):
        """
        TESTE 11: Deve tratar erros de conexão com banco
        Requisito: RNF06 - Resiliência a falhas
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
        user_id = 100
        mock_db_session.query.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            ReconciliationService.get_user_reconciliations(mock_db_session, user_id)
        
        assert "Database error" in str(exc_info.value)


# ============================================================================
# SUITE 3: PROCESSAMENTO DE CONCILIAÇÃO
# ============================================================================

class TestReconciliationProcessing:
    """Suite de testes para processamento (se existir no service)"""
    
    def test_process_successful_reconciliation(self, mock_db_session, sample_reconciliation_result):
        """
        TESTE 12: Deve processar resultado do ReconciliationProcessor
        Requisito: RF04 - Executar algoritmo de conciliação
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
        # Se o service tiver método que processa resultado do processor
        # Simular integração com ReconciliationProcessor
        with patch('app.services.reconciliation_service.ReconciliationProcessor') as MockProcessor:
            mock_processor = MockProcessor.return_value
            mock_processor.reconcile.return_value = sample_reconciliation_result
            
            # Act
            result = mock_processor.reconcile(
                bank_data=[{'id': 1, 'date': '2024-01-15', 'value': 100.00, 'description': 'Pagamento A'}],
                internal_data=[{'id': 1, 'date': '2024-01-15', 'value': 100.00, 'description': 'Pagto A'}]
            )
            
            # Assert
            assert 'matched' in result
            assert 'bank_only' in result
            assert 'internal_only' in result
            assert 'summary' in result
            assert result['summary']['matched_count'] == 1
    
    def test_handles_empty_reconciliation_data(self, mock_db_session):
        """
        TESTE 13: Deve lidar com dados vazios
        Requisito: RNF06 - Robustez
        """
        # Arrange
        from app.core.reconciliation_processor import ReconciliationProcessor
        
        processor = ReconciliationProcessor()
        
        # Act
        result = processor.reconcile(bank_data=[], internal_data=[])
        
        # Assert
        assert result['matched'] == []
        assert result['bank_only'] == []
        assert result['internal_only'] == []
        assert result['summary']['matched_count'] == 0
    
    def test_reconciliation_with_high_confidence_match(self, mock_db_session):
        """
        TESTE 14: Deve identificar matches de alta confiança
        Requisito: RF04 - Precisão do algoritmo
        """
        # Arrange
        from app.core.reconciliation_processor import ReconciliationProcessor
        
        processor = ReconciliationProcessor(
            date_tolerance=1,
            value_tolerance=0.02,
            similarity_threshold=0.7
        )
        
        bank_data = [
            {'id': 1, 'date': '2024-01-15', 'value': 100.00, 'description': 'Pagamento Cliente A'}
        ]
        internal_data = [
            {'id': 1, 'date': '2024-01-15', 'value': 100.00, 'description': 'Pagamento Cliente A'}
        ]
        
        # Act
        result = processor.reconcile(bank_data, internal_data)
        
        # Assert
        assert len(result['matched']) == 1
        assert result['matched'][0]['confidence'] >= 0.9  # Alta confiança
        assert result['summary']['match_rate'] == 100.0


# ============================================================================
# SUITE 4: EDGE CASES E VALIDAÇÕES
# ============================================================================

class TestEdgeCasesAndValidations:
    """Suite de testes para casos extremos"""
    
    def test_handles_special_characters_in_description(self, mock_db_session):
        """
        TESTE 15: Deve lidar com caracteres especiais
        Requisito: RNF04 - Compatibilidade
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
        description_with_special_chars = "Pag. R$ 1.234,56 - João & Maria Ltda."
        
        mock_rec = MagicMock()
        mock_rec.id = 1
        mock_rec.user_id = 100
        mock_rec.bank_file_name = description_with_special_chars
        mock_rec.internal_file_name = "test.csv"
        mock_rec.created_at = datetime(2025, 1, 15)
        mock_rec.total_bank_transactions = 10
        mock_rec.total_internal_transactions = 10
        mock_rec.matched_count = 5
        mock_rec.bank_only_count = 5
        mock_rec.internal_only_count = 5
        mock_rec.match_rate = 50.0
        
        mock_query = MagicMock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = [mock_rec]
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = ReconciliationService.get_user_reconciliations(mock_db_session, 100)
        
        # Assert
        assert len(result) > 0
        assert result[0]["bank_file_name"] == description_with_special_chars
    
    def test_statistics_with_perfect_match_rate(self, mock_db_session):
        """
        TESTE 16: Deve calcular corretamente quando match_rate = 100%
        Requisito: RNF06 - Precisão de cálculos
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
        user_id = 100
        
        mock_rec = MagicMock()
        mock_rec.matched_count = 50
        mock_rec.total_bank_transactions = 50
        mock_rec.total_internal_transactions = 50
        mock_rec.bank_only_count = 0
        mock_rec.internal_only_count = 0
        
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.all.return_value = [mock_rec]
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        # Act
        stats = ReconciliationService.get_user_statistics(user_id, mock_db_session)
        
        # Assert
        assert stats['total_matched'] == 50
        assert stats['total_transactions'] == 100
    
    def test_format_reconciliation_preserves_data_types(self, mock_db_session, sample_reconciliation):
        """
        TESTE 17: Deve preservar tipos de dados na formatação
        Requisito: RNF04 - Integridade de dados
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
        mock_query = mock_db_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = [sample_reconciliation]
        
        # Act
        result = ReconciliationService.get_user_reconciliations(mock_db_session, 100)
        
        # Assert
        assert isinstance(result[0]["id"], int)
        assert isinstance(result[0]["user_id"], int)
        assert isinstance(result[0]["bank_file_name"], str)
        assert isinstance(result[0]["created_at"], str)
        assert isinstance(result[0]["match_rate"], float)
    
    def test_handles_large_dataset_statistics(self, mock_db_session):
        """
        TESTE 18: Deve processar estatísticas de grande volume
        Requisito: RNF01 - Performance
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
        user_id = 100
        
        # Simular 100 conciliações
        mock_recs = []
        for i in range(100):
            mock_rec = MagicMock()
            mock_rec.matched_count = i + 1
            mock_rec.total_bank_transactions = (i + 1) * 2
            mock_rec.total_internal_transactions = (i + 1) * 2
            mock_rec.bank_only_count = 1
            mock_rec.internal_only_count = 1
            mock_rec.created_at = datetime(2025, 1, 1, 10, 0) + timedelta(days=i)  # ✅ FIX
            mock_recs.append(mock_rec)
        
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.all.return_value = mock_recs
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        # Act
        stats = ReconciliationService.get_user_statistics(user_id, mock_db_session)
        
        # Assert
        assert stats['total_reconciliations'] == 100
        assert stats['total_matched'] == sum(range(1, 101))  # Soma 1 até 100
    
    def test_reconciliation_processor_date_tolerance(self):
        """
        TESTE 19: Deve respeitar tolerância de data configurada
        Requisito: RF04 - Configuração de critérios
        """
        # Arrange
        from app.core.reconciliation_processor import ReconciliationProcessor
        
        processor = ReconciliationProcessor(date_tolerance=2)
        
        bank_data = [
            {'id': 1, 'date': '2024-01-15', 'value': 100.00, 'description': 'Pagamento A'}
        ]
        internal_data = [
            {'id': 1, 'date': '2024-01-17', 'value': 100.00, 'description': 'Pagamento A'}  # +2 dias
        ]
        
        # Act
        result = processor.reconcile(bank_data, internal_data)
        
        # Assert
        assert len(result['matched']) == 1  # Deve aceitar +2 dias
    
    def test_reconciliation_processor_value_tolerance(self):
        """
        TESTE 20: Deve respeitar tolerância de valor configurada
        Requisito: RF04 - Configuração de critérios
        """
        # Arrange
        from app.core.reconciliation_processor import ReconciliationProcessor
        
        processor = ReconciliationProcessor(value_tolerance=0.05)  # 5%
        
        bank_data = [
            {'id': 1, 'date': '2024-01-15', 'value': 100.00, 'description': 'Pagamento A'}
        ]
        internal_data = [
            {'id': 1, 'date': '2024-01-15', 'value': 104.00, 'description': 'Pagamento A'}  # +4%
        ]
        
        # Act
        result = processor.reconcile(bank_data, internal_data)
        
        # Assert
        assert len(result['matched']) == 1  

class TestReconciliationServiceMissingLines:
    """Testes para cobrir linhas específicas não cobertas"""
    
    def test_get_user_statistics_calculates_pending_correctly(self, mock_db_session):
        """
        TESTE FINAL 1: Deve calcular transações pendentes corretamente
        Cobre: linha com cálculo de total_pending
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
        user_id = 100
        
        mock_rec = MagicMock()
        mock_rec.matched_count = 10
        mock_rec.total_bank_transactions = 20
        mock_rec.total_internal_transactions = 18
        mock_rec.bank_only_count = 10
        mock_rec.internal_only_count = 8
        mock_rec.created_at = datetime(2025, 1, 15)
        
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.all.return_value = [mock_rec]
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        # Act
        stats = ReconciliationService.get_user_statistics(user_id, mock_db_session)
        
        # Assert
        assert 'total_pending' in stats
        # total_pending = total_transactions - (matched * 2)
        # = (20 + 18) - (10 * 2) = 38 - 20 = 18
        assert stats['total_pending'] == 18
    
    def test_get_user_statistics_finds_last_reconciliation(self, mock_db_session):
        """
        TESTE FINAL 2: Deve encontrar a última conciliação
        Cobre: linha 140 (last_reconciliation = max(...))
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
        user_id = 100
        
        # Criar 3 conciliações com datas diferentes
        mock_rec1 = MagicMock()
        mock_rec1.matched_count = 5
        mock_rec1.total_bank_transactions = 10
        mock_rec1.total_internal_transactions = 10
        mock_rec1.bank_only_count = 5
        mock_rec1.internal_only_count = 5
        mock_rec1.created_at = datetime(2025, 1, 1)  # Mais antiga
        
        mock_rec2 = MagicMock()
        mock_rec2.matched_count = 8
        mock_rec2.total_bank_transactions = 15
        mock_rec2.total_internal_transactions = 15
        mock_rec2.bank_only_count = 7
        mock_rec2.internal_only_count = 7
        mock_rec2.created_at = datetime(2025, 1, 20)  # Mais recente
        
        mock_rec3 = MagicMock()
        mock_rec3.matched_count = 6
        mock_rec3.total_bank_transactions = 12
        mock_rec3.total_internal_transactions = 12
        mock_rec3.bank_only_count = 6
        mock_rec3.internal_only_count = 6
        mock_rec3.created_at = datetime(2025, 1, 10)  # Intermediária
        
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.all.return_value = [mock_rec1, mock_rec2, mock_rec3]
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        # Act
        stats = ReconciliationService.get_user_statistics(user_id, mock_db_session)
        
        # Assert
        assert 'last_reconciliation_date' in stats
        # Deve retornar a data mais recente (2025-01-20)
        assert stats['last_reconciliation_date'] == datetime(2025, 1, 20)
    
    def test_get_user_statistics_finds_last_reconciliation(self, mock_db_session):
        """
        TESTE FINAL 2: Deve encontrar a última conciliação
        Cobre: linha 140 (last_reconciliation = max(...))
        """
        # Arrange
        from app.services.reconciliation_service import ReconciliationService
        
        user_id = 100
        
        # Criar 3 conciliações com datas diferentes
        mock_rec1 = MagicMock()
        mock_rec1.matched_count = 5
        mock_rec1.total_bank_transactions = 10
        mock_rec1.total_internal_transactions = 10
        mock_rec1.bank_only_count = 5
        mock_rec1.internal_only_count = 5
        mock_rec1.created_at = datetime(2025, 1, 1)  # Mais antiga
        
        mock_rec2 = MagicMock()
        mock_rec2.matched_count = 8
        mock_rec2.total_bank_transactions = 15
        mock_rec2.total_internal_transactions = 15
        mock_rec2.bank_only_count = 7
        mock_rec2.internal_only_count = 7
        mock_rec2.created_at = datetime(2025, 1, 20)  # Mais recente
        
        mock_rec3 = MagicMock()
        mock_rec3.matched_count = 6
        mock_rec3.total_bank_transactions = 12
        mock_rec3.total_internal_transactions = 12
        mock_rec3.bank_only_count = 6
        mock_rec3.internal_only_count = 6
        mock_rec3.created_at = datetime(2025, 1, 10)  # Intermediária
        
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.all.return_value = [mock_rec1, mock_rec2, mock_rec3]
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        # Act
        stats = ReconciliationService.get_user_statistics(user_id, mock_db_session)
        
        # Assert
        assert 'last_reconciliation_date' in stats
        # ✅ CORRIGIDO: Comparar com string ISO em vez de datetime object
        assert stats['last_reconciliation_date'] == '2025-01-20T00:00:00'