"""
Testes para o endpoint /reconcile
Cobertura: Validações, Autenticação, Processamento e Erros

"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.core.deps import get_current_user, get_db

# Cliente de teste
client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_current_user():
    """Simula usuário autenticado"""
    user = Mock()
    user.id = 1
    user.email = "test@example.com"
    return user


@pytest.fixture
def mock_db():
    """Mock da sessão de banco de dados"""
    db = MagicMock()
    return db


@pytest.fixture
def override_get_current_user(mock_current_user):
    """Override da dependência de autenticação"""
    def _get_current_user_override():
        return mock_current_user
    
    app.dependency_overrides[get_current_user] = _get_current_user_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def override_get_db(mock_db):
    """Override da dependência de banco de dados"""
    def _get_db_override():
        yield mock_db
    
    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def valid_reconcile_request():
    """Payload válido para conciliação"""
    return {
        "bank_file": "bank_statement.csv",
        "internal_file": "internal_report.csv",
        "bank_mapping": {
            "date_col": "Data",
            "value_col": "Valor",
            "desc_col": "Descrição"
        },
        "internal_mapping": {
            "date_col": "Data",
            "value_col": "Valor",
            "desc_col": "Descrição"
        },
        "date_tolerance": 1,
        "value_tolerance": 0.02,
        "similarity_threshold": 0.7
    }


@pytest.fixture
def mock_reconciliation_result():
    """Resultado típico do ReconciliationProcessor"""
    return {
        'matched': [
            {
                'bank_transaction': {
                    'id': 1,
                    'date': '2024-01-15',
                    'value': 100.00,
                    'description': 'Pagamento A'
                },
                'internal_transaction': {
                    'id': 1,
                    'date': '2024-01-15',
                    'value': 100.00,
                    'description': 'Pagto A'
                },
                'confidence': 0.95
            }
        ],
        'bank_only': [],
        'internal_only': [],
        'summary': {
            'total_bank_transactions': 1,
            'total_internal_transactions': 1,
            'matched_count': 1,
            'bank_only_count': 0,
            'internal_only_count': 0,
            'match_rate': 100.0
        }
    }


@pytest.fixture
def mock_csv_data():
    """Dados processados de CSV"""
    return [
        {
            'id': 1,
            'date': '2024-01-15',
            'value': 100.00,
            'description': 'Pagamento A'
        }
    ]


# ============================================================================
# SUITE 1: VALIDAÇÕES DE PAYLOAD
# ============================================================================

class TestReconcileValidations:
    """Testes de validação de entrada"""
    
    def test_reconcile_missing_bank_file(self, override_get_current_user):
        """
        TESTE 1: Deve rejeitar requisição sem bank_file
        Requisito: RNF06 - Validação de entrada
        """
        # Arrange
        payload = {
            "internal_file": "internal.csv",
            "bank_mapping": {"date_col": "Data", "value_col": "Valor", "desc_col": "Desc"},
            "internal_mapping": {"date_col": "Data", "value_col": "Valor", "desc_col": "Desc"}
        }
        
        # Act
        response = client.post("/api/reconcile", json=payload)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_reconcile_missing_internal_file(self, override_get_current_user):
        """
        TESTE 2: Deve rejeitar requisição sem internal_file
        Requisito: RNF06 - Validação de entrada
        """
        # Arrange
        payload = {
            "bank_file": "bank.csv",
            "bank_mapping": {"date_col": "Data", "value_col": "Valor", "desc_col": "Desc"},
            "internal_mapping": {"date_col": "Data", "value_col": "Valor", "desc_col": "Desc"}
        }
        
        # Act
        response = client.post("/api/reconcile", json=payload)
        
        # Assert
        assert response.status_code == 422
    
    def test_reconcile_missing_column_mapping(self, override_get_current_user):
        """
        TESTE 3: Deve rejeitar requisição sem mapeamento de colunas
        Requisito: RNF06 - Validação de entrada
        """
        # Arrange
        payload = {
            "bank_file": "bank.csv",
            "internal_file": "internal.csv"
        }
        
        # Act
        response = client.post("/api/reconcile", json=payload)
        
        # Assert
        assert response.status_code == 422
    
    def test_reconcile_custom_tolerance_values(
        self, override_get_current_user, override_get_db, valid_reconcile_request
    ):
        """
        TESTE 4: Deve aceitar tolerâncias customizadas
        Requisito: RF04 - Configuração de critérios
        """
        # Arrange
        valid_reconcile_request["date_tolerance"] = 5
        valid_reconcile_request["value_tolerance"] = 0.10
        valid_reconcile_request["similarity_threshold"] = 0.85
        
        with patch("app.api.routes.reconcile.os.path.exists", return_value=True), \
             patch("app.api.routes.reconcile.CSVProcessor.read_csv"), \
             patch("app.api.routes.reconcile.CSVProcessor.process_dataframe", return_value=[]), \
             patch("app.api.routes.reconcile.ReconciliationProcessor") as MockProcessor:
            
            mock_processor = MockProcessor.return_value
            mock_processor.reconcile.return_value = {
                'matched': [], 'bank_only': [], 'internal_only': [],
                'summary': {
                    'total_bank_transactions': 0, 'total_internal_transactions': 0,
                    'matched_count': 0, 'bank_only_count': 0, 'internal_only_count': 0,
                    'match_rate': 0.0
                }
            }
            
            # Act
            response = client.post("/api/reconcile", json=valid_reconcile_request)
            
            # Assert
            assert response.status_code == 200
            MockProcessor.assert_called_once_with(
                date_tolerance=5,
                value_tolerance=0.10,
                similarity_threshold=0.85
            )


# ============================================================================
# SUITE 2: AUTENTICAÇÃO
# ============================================================================

class TestReconcileAuthentication:
    """Testes de autenticação"""
    
    def test_reconcile_without_authentication(self, valid_reconcile_request):
        """
        TESTE 5: Deve rejeitar requisição sem token
        Requisito: RNF02 - Segurança
        """
        # Act
        response = client.post("/api/reconcile", json=valid_reconcile_request)
        
        # Assert
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()
    
    def test_reconcile_with_invalid_token(self, valid_reconcile_request):
        """
        TESTE 6: Deve rejeitar token inválido
        Requisito: RNF02 - Segurança
        """
        # Arrange
        headers = {"Authorization": "Bearer invalid-token-123"}
        
        # Act
        response = client.post("/api/reconcile", json=valid_reconcile_request, headers=headers)
        
        # Assert
        assert response.status_code == 401


# ============================================================================
# SUITE 3: VERIFICAÇÃO DE ARQUIVOS
# ============================================================================

class TestReconcileFileValidation:
    """Testes de validação de arquivos"""
    
    def test_reconcile_bank_file_not_found(
        self, override_get_current_user, override_get_db, valid_reconcile_request
    ):
        """
        TESTE 7: Deve retornar erro quando arquivo bancário não existe
        Requisito: RNF06 - Tratamento de erros
        """
        # Arrange
        with patch("app.api.routes.reconcile.os.path.exists", return_value=False):
            # Act
            response = client.post("/api/reconcile", json=valid_reconcile_request)
            
            # Assert
            assert response.status_code == 404
            assert "não encontrados" in response.json()["detail"].lower()
    
    def test_reconcile_constructs_correct_file_paths(
        self, override_get_current_user, override_get_db, valid_reconcile_request
    ):
        """
        TESTE 8: Deve construir paths corretos para os arquivos
        Requisito: RNF04 - Integridade de dados
        """
        # Arrange
        with patch("app.api.routes.reconcile.os.path.exists") as mock_exists, \
             patch("app.api.routes.reconcile.CSVProcessor.read_csv"), \
             patch("app.api.routes.reconcile.CSVProcessor.process_dataframe", return_value=[]), \
             patch("app.api.routes.reconcile.ReconciliationProcessor") as MockProcessor:
            
            mock_exists.return_value = True
            mock_processor = MockProcessor.return_value
            mock_processor.reconcile.return_value = {
                'matched': [], 'bank_only': [], 'internal_only': [],
                'summary': {
                    'total_bank_transactions': 0, 'total_internal_transactions': 0,
                    'matched_count': 0, 'bank_only_count': 0, 'internal_only_count': 0,
                    'match_rate': 0.0
                }
            }
            
            # Act
            client.post("/api/reconcile", json=valid_reconcile_request)
            
            # Assert
            assert mock_exists.call_count >= 2
            calls = [str(call) for call in mock_exists.call_args_list]
            assert any("bank_statement.csv" in str(call) for call in calls)
            assert any("internal_report.csv" in str(call) for call in calls)


# ============================================================================
# SUITE 4: PROCESSAMENTO COMPLETO
# ============================================================================

class TestReconcileProcessing:
    """Testes do fluxo completo de processamento"""
    
    def test_reconcile_successful_processing(
        self, override_get_current_user, override_get_db, 
        valid_reconcile_request, mock_reconciliation_result, mock_csv_data
    ):
        """
        TESTE 9: Deve processar conciliação com sucesso
        Requisito: RF04 - Executar algoritmo de conciliação
        """
        # Arrange
        with patch("app.api.routes.reconcile.os.path.exists", return_value=True), \
             patch("app.api.routes.reconcile.CSVProcessor.read_csv"), \
             patch("app.api.routes.reconcile.CSVProcessor.process_dataframe", return_value=mock_csv_data), \
             patch("app.api.routes.reconcile.ReconciliationProcessor") as MockProcessor:
            
            mock_processor = MockProcessor.return_value
            mock_processor.reconcile.return_value = mock_reconciliation_result
            
            # Act
            response = client.post("/api/reconcile", json=valid_reconcile_request)
            
            # Assert
            assert response.status_code == 200
            result = response.json()
            assert "reconciliation_id" in result
            assert "summary" in result
            assert result["summary"]["matched_count"] == 1
            assert result["summary"]["match_rate"] == 100.0
    
    def test_reconcile_saves_to_database(
        self, override_get_current_user, override_get_db, mock_db,
        valid_reconcile_request, mock_reconciliation_result, mock_csv_data
    ):
        """
        TESTE 10: Deve salvar conciliação no banco de dados
        Requisito: RF08 - Persistir histórico
        """
        # Arrange
        with patch("app.api.routes.reconcile.os.path.exists", return_value=True), \
             patch("app.api.routes.reconcile.CSVProcessor.read_csv"), \
             patch("app.api.routes.reconcile.CSVProcessor.process_dataframe", return_value=mock_csv_data), \
             patch("app.api.routes.reconcile.ReconciliationProcessor") as MockProcessor:
            
            mock_processor = MockProcessor.return_value
            mock_processor.reconcile.return_value = mock_reconciliation_result
            
            # Act
            response = client.post("/api/reconcile", json=valid_reconcile_request)
            
            # Assert
            assert response.status_code == 200
            mock_db.add.assert_called()
            mock_db.commit.assert_called()
    
    def test_reconcile_returns_correct_format(
        self, override_get_current_user, override_get_db, mock_db,
        valid_reconcile_request, mock_reconciliation_result, mock_csv_data
    ):
        """
        TESTE 11: Deve retornar resposta no formato esperado pelo frontend
        Requisito: RNF04 - Compatibilidade
        """
        # Arrange
        # Configurar mock do refresh para adicionar ID
        def mock_refresh(obj):
            obj.id = 123
        
        mock_db.refresh.side_effect = mock_refresh
        
        with patch("app.api.routes.reconcile.os.path.exists", return_value=True), \
             patch("app.api.routes.reconcile.CSVProcessor.read_csv"), \
             patch("app.api.routes.reconcile.CSVProcessor.process_dataframe", return_value=mock_csv_data), \
             patch("app.api.routes.reconcile.ReconciliationProcessor") as MockProcessor:
            
            mock_processor = MockProcessor.return_value
            mock_processor.reconcile.return_value = mock_reconciliation_result
            
            # Act
            response = client.post("/api/reconcile", json=valid_reconcile_request)
            
            # Assert
            assert response.status_code == 200
            result = response.json()
            
            assert "reconciliation_id" in result
            assert "summary" in result
            assert "matched" in result
            assert "bank_only" in result
            assert "internal_only" in result
            
            assert isinstance(result["reconciliation_id"], int)
            assert result["reconciliation_id"] == 123
            assert isinstance(result["matched"], list)
            assert isinstance(result["summary"], dict)


# ============================================================================
# SUITE 5: TRATAMENTO DE ERROS
# ============================================================================

class TestReconcileErrorHandling:
    """Testes de tratamento de erros"""
    
    def test_reconcile_handles_csv_processing_error(
        self, override_get_current_user, override_get_db, valid_reconcile_request
    ):
        """
        TESTE 12: Deve tratar erro ao processar CSV
        Requisito: RNF06 - Resiliência a falhas
        """
        # Arrange
        with patch("app.api.routes.reconcile.os.path.exists", return_value=True), \
             patch("app.api.routes.reconcile.CSVProcessor.read_csv", side_effect=Exception("CSV corrupto")):
            
            # Act
            response = client.post("/api/reconcile", json=valid_reconcile_request)
            
            # Assert
            assert response.status_code == 500
            assert "erro na conciliação" in response.json()["detail"].lower()
    
    def test_reconcile_handles_processor_error(
        self, override_get_current_user, override_get_db,
        valid_reconcile_request, mock_csv_data
    ):
        """
        TESTE 13: Deve tratar erro no processamento de conciliação
        Requisito: RNF06 - Resiliência a falhas
        """
        # Arrange
        with patch("app.api.routes.reconcile.os.path.exists", return_value=True), \
             patch("app.api.routes.reconcile.CSVProcessor.read_csv"), \
             patch("app.api.routes.reconcile.CSVProcessor.process_dataframe", return_value=mock_csv_data), \
             patch("app.api.routes.reconcile.ReconciliationProcessor") as MockProcessor:
            
            mock_processor = MockProcessor.return_value
            mock_processor.reconcile.side_effect = Exception("Erro no algoritmo")
            
            # Act
            response = client.post("/api/reconcile", json=valid_reconcile_request)
            
            # Assert
            assert response.status_code == 500
    
    def test_reconcile_handles_database_error(
        self, override_get_current_user, override_get_db, mock_db,
        valid_reconcile_request, mock_reconciliation_result, mock_csv_data
    ):
        """
        TESTE 14: Deve tratar erro ao salvar no banco
        Requisito: RNF06 - Resiliência a falhas
        """
        # Arrange
        mock_db.commit.side_effect = Exception("Database connection lost")
        
        with patch("app.api.routes.reconcile.os.path.exists", return_value=True), \
             patch("app.api.routes.reconcile.CSVProcessor.read_csv"), \
             patch("app.api.routes.reconcile.CSVProcessor.process_dataframe", return_value=mock_csv_data), \
             patch("app.api.routes.reconcile.ReconciliationProcessor") as MockProcessor:
            
            mock_processor = MockProcessor.return_value
            mock_processor.reconcile.return_value = mock_reconciliation_result
            
            # Act
            response = client.post("/api/reconcile", json=valid_reconcile_request)
            
            # Assert
            assert response.status_code == 500


# ============================================================================
# SUITE 6: INTEGRAÇÃO COM COMPONENTES
# ============================================================================

class TestReconcileIntegration:
    """Testes de integração entre componentes"""
    
    def test_reconcile_uses_correct_column_mappings(
        self, override_get_current_user, override_get_db,
        valid_reconcile_request, mock_csv_data
    ):
        """
        TESTE 15: Deve usar mapeamentos de colunas corretos
        Requisito: RF03 - Mapear colunas
        """
        # Arrange
        with patch("app.api.routes.reconcile.os.path.exists", return_value=True), \
             patch("app.api.routes.reconcile.CSVProcessor.read_csv"), \
             patch("app.api.routes.reconcile.CSVProcessor.process_dataframe") as mock_process, \
             patch("app.api.routes.reconcile.ReconciliationProcessor") as MockProcessor:
            
            mock_process.return_value = mock_csv_data
            mock_processor = MockProcessor.return_value
            mock_processor.reconcile.return_value = {
                'matched': [], 'bank_only': [], 'internal_only': [],
                'summary': {
                    'total_bank_transactions': 0, 'total_internal_transactions': 0,
                    'matched_count': 0, 'bank_only_count': 0, 'internal_only_count': 0,
                    'match_rate': 0.0
                }
            }
            
            # Act
            client.post("/api/reconcile", json=valid_reconcile_request)
            
            # Assert
            assert mock_process.call_count == 2
            
            first_call_args = mock_process.call_args_list[0][0]
            assert first_call_args[1] == "Data"
            assert first_call_args[2] == "Valor"
            assert first_call_args[3] == "Descrição"
    
    def test_reconcile_associates_with_correct_user(
        self, override_get_current_user, override_get_db, mock_current_user, mock_db,
        valid_reconcile_request, mock_reconciliation_result, mock_csv_data
    ):
        """
        TESTE 16: Deve associar conciliação ao usuário correto
        Requisito: RNF02 - Isolamento de dados por usuário
        """
        # Arrange
        mock_current_user.id = 42
        
        with patch("app.api.routes.reconcile.os.path.exists", return_value=True), \
             patch("app.api.routes.reconcile.CSVProcessor.read_csv"), \
             patch("app.api.routes.reconcile.CSVProcessor.process_dataframe", return_value=mock_csv_data), \
             patch("app.api.routes.reconcile.ReconciliationProcessor") as MockProcessor:
            
            mock_processor = MockProcessor.return_value
            mock_processor.reconcile.return_value = mock_reconciliation_result
            
            # Act
            response = client.post("/api/reconcile", json=valid_reconcile_request)
            
            # Assert
            assert response.status_code == 200
            added_obj = mock_db.add.call_args_list[0][0][0]
            assert hasattr(added_obj, 'user_id')
            assert added_obj.user_id == 42