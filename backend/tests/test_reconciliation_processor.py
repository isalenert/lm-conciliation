"""
Testes TDD para o Motor de Conciliação (CORE DO SISTEMA)
Requisito: RNF06 - Cobertura de testes > 75%
Requisito: RF03 - Conciliação automática com fuzzy matching
Requisito: RNF09 - TDD demonstrado no core business
"""
import pytest
from datetime import datetime
from app.core.reconciliation_processor import ReconciliationProcessor


# ============================================================================
# FIXTURES GLOBAIS
# ============================================================================

@pytest.fixture
def processor():
    """Fixture: Instância padrão do processador"""
    return ReconciliationProcessor(
        date_tolerance=1,
        value_tolerance=0.02,
        similarity_threshold=0.7
    )


@pytest.fixture
def sample_bank_data():
    """Fixture: Dados bancários de exemplo"""
    return [
        {
            'id': 0,
            'date': '2024-11-01',
            'value': 150.00,
            'description': 'Pagamento Fornecedor A'
        },
        {
            'id': 1,
            'date': '2024-11-02',
            'value': 200.50,
            'description': 'Pagamento Fornecedor B'
        },
        {
            'id': 2,
            'date': '2024-11-05',
            'value': 99.99,
            'description': 'Compra Material'
        }
    ]


@pytest.fixture
def sample_internal_data():
    """Fixture: Dados internos de exemplo"""
    return [
        {
            'id': 0,
            'date': '2024-11-01',
            'value': 150.00,
            'description': 'Fornecedor A - Nota 001'
        },
        {
            'id': 1,
            'date': '2024-11-02',
            'value': 200.50,
            'description': 'Fornecedor B - Nota 002'
        },
        {
            'id': 2,
            'date': '2024-11-10',
            'value': 500.00,
            'description': 'Fornecedor C - Nota 003'
        }
    ]


# ============================================================================
# TESTES PRINCIPAIS
# ============================================================================

class TestReconciliationProcessor:
    """Testes para o ReconciliationProcessor"""
    
    def test_exact_match(self, processor):
        """Teste 1: Match exato - mesma data, valor e descrição similar"""
        bank = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Pagamento Fornecedor'
        }]
        
        internal = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Fornecedor - Nota 001'
        }]
        
        result = processor.reconcile(bank, internal)
        
        assert len(result['matched']) == 1
        assert len(result['bank_only']) == 0
        assert len(result['internal_only']) == 0
        assert result['summary']['match_rate'] == 100.0
    
    def test_date_tolerance(self, processor):
        """Teste 2: Match com diferença de 1 dia (dentro da tolerância)"""
        bank = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Pagamento'
        }]
        
        internal = [{
            'id': 0,
            'date': '2024-11-02',  # 1 dia de diferença
            'value': 100.00,
            'description': 'Pagamento'
        }]
        
        result = processor.reconcile(bank, internal)
        
        assert len(result['matched']) == 1
    
    def test_value_tolerance(self, processor):
        """Teste 3: Match com pequena diferença no valor (2%)"""
        bank = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Pagamento'
        }]
        
        internal = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 101.50,  # 1.5% de diferença
            'description': 'Pagamento'
        }]
        
        result = processor.reconcile(bank, internal)
        
        assert len(result['matched']) == 1
    
    def test_no_match_date_outside_tolerance(self, processor):
        """Teste 4: Sem match - diferença de data maior que tolerância"""
        bank = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Pagamento'
        }]
        
        internal = [{
            'id': 0,
            'date': '2024-11-05',  # 4 dias de diferença
            'value': 100.00,
            'description': 'Pagamento'
        }]
        
        result = processor.reconcile(bank, internal)
        
        assert len(result['matched']) == 0
        assert len(result['bank_only']) == 1
        assert len(result['internal_only']) == 1
    
    def test_no_match_value_outside_tolerance(self, processor):
        """Teste 5: Sem match - diferença de valor maior que tolerância"""
        bank = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Pagamento'
        }]
        
        internal = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 150.00,  # 50% de diferença
            'description': 'Pagamento'
        }]
        
        result = processor.reconcile(bank, internal)
        
        assert len(result['matched']) == 0
    
    def test_fuzzy_description_matching(self, processor):
        """Teste 6: Match com descrições similares mas não idênticas"""
        bank = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Pagamento Fornecedor ABC Ltda'
        }]
        
        internal = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Fornecedor ABC - Nota Fiscal 123'
        }]
        
        result = processor.reconcile(bank, internal)
        
        assert len(result['matched']) == 1
        assert result['matched'][0]['confidence'] > 0.7
    
    def test_multiple_transactions(self, processor, sample_bank_data, sample_internal_data):
        """Teste 7: Múltiplas transações"""
        result = processor.reconcile(sample_bank_data, sample_internal_data)
        
        assert result['summary']['total_bank_transactions'] == 3
        assert result['summary']['total_internal_transactions'] == 3
        assert result['summary']['matched_count'] >= 2
    
    def test_confidence_calculation(self, processor):
        """Teste 8: Cálculo de confiança - match perfeito"""
        bank = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Pagamento'
        }]
        
        internal = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Pagamento'
        }]
        
        result = processor.reconcile(bank, internal)
        
        assert result['matched'][0]['confidence'] >= 0.9
    
    def test_empty_data(self, processor):
        """Teste 9: Dados vazios"""
        result = processor.reconcile([], [])
        
        assert len(result['matched']) == 0
        assert len(result['bank_only']) == 0
        assert len(result['internal_only']) == 0
        assert result['summary']['match_rate'] == 0.0
    
    def test_bank_only_transactions(self, processor):
        """Teste 10: Transações apenas no banco"""
        bank = [
            {'id': 0, 'date': '2024-11-01', 'value': 100.00, 'description': 'Pag 1'},
            {'id': 1, 'date': '2024-11-02', 'value': 200.00, 'description': 'Pag 2'}
        ]
        
        internal = []
        
        result = processor.reconcile(bank, internal)
        
        assert len(result['bank_only']) == 2
        assert len(result['internal_only']) == 0
        assert result['summary']['match_rate'] == 0.0
    
    def test_internal_only_transactions(self, processor):
        """Teste 11: Transações apenas no sistema interno"""
        bank = []
        
        internal = [
            {'id': 0, 'date': '2024-11-01', 'value': 100.00, 'description': 'Pag 1'},
            {'id': 1, 'date': '2024-11-02', 'value': 200.00, 'description': 'Pag 2'}
        ]
        
        result = processor.reconcile(bank, internal)
        
        assert len(result['bank_only']) == 0
        assert len(result['internal_only']) == 2
    
    def test_custom_tolerance_parameters(self):
        """Teste 12: Parâmetros personalizados de tolerância"""
        processor = ReconciliationProcessor(
            date_tolerance=3,
            value_tolerance=0.05,
            similarity_threshold=0.5
        )
        
        bank = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Pagamento Fornecedor'
        }]
        
        internal = [{
            'id': 0,
            'date': '2024-11-04',  # 3 dias
            'value': 104.00,       # 4%
            'description': 'Fornecedor Pagamento'
        }]
        
        result = processor.reconcile(bank, internal)
        
        assert len(result['matched']) == 1


# ============================================================================
# TESTES DE MÉTODOS AUXILIARES (COBERTURA COMPLETA)
# ============================================================================

class TestAuxiliaryMethods:
    """Testes dos métodos auxiliares para máxima cobertura"""
    
    def test_parse_date_valid(self, processor):
        """TESTE 13: Deve parsear data válida"""
        date_str = '2024-11-01'
        result = processor._parse_date(date_str)
        
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 11
        assert result.day == 1
    
    def test_dates_match_exact(self, processor):
        """TESTE 14: Datas idênticas devem dar match"""
        assert processor._dates_match('2024-11-01', '2024-11-01') is True
    
    def test_dates_match_within_tolerance_reverse(self, processor):
        """TESTE 15: Match com data invertida (date2 < date1)"""
        # Testa abs() no cálculo de diferença
        assert processor._dates_match('2024-11-02', '2024-11-01') is True
    
    def test_values_match_exact(self, processor):
        """TESTE 16: Valores idênticos devem dar match"""
        assert processor._values_match(100.00, 100.00) is True
    
    def test_values_match_reverse_order(self, processor):
        """TESTE 17: Deve funcionar independente da ordem (value2 > value1)"""
        # Testa max(value1, value2) no denominador
        assert processor._values_match(100.00, 101.00) is True
    
    def test_description_similarity_identical(self, processor):
        """TESTE 18: Descrições idênticas = score 1.0"""
        score = processor._calculate_description_similarity(
            'Pagamento Fornecedor',
            'Pagamento Fornecedor'
        )
        assert score == 1.0
    
    def test_description_similarity_case_insensitive(self, processor):
        """TESTE 19: Deve ignorar maiúsculas/minúsculas"""
        score = processor._calculate_description_similarity(
            'PAGAMENTO FORNECEDOR',
            'pagamento fornecedor'
        )
        assert score == 1.0
    
    def test_description_similarity_with_whitespace(self, processor):
        """TESTE 20: Deve ignorar espaços extras"""
        score = processor._calculate_description_similarity(
            '  Pagamento  ',
            'Pagamento'
        )
        assert score == 1.0
    
    def test_calculate_match_confidence_perfect(self, processor):
        """TESTE 21: Match perfeito = confiança 1.0"""
        bank = {
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Pagamento'
        }
        internal = {
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Pagamento'
        }
        
        confidence = processor._calculate_match_confidence(bank, internal)
        assert confidence == 1.0
    
    def test_calculate_match_confidence_date_only_tolerance(self, processor):
        """TESTE 22: Data dentro da tolerância (não exata) = 0.15"""
        bank = {
            'date': '2024-11-01',
            'value': 200.00,  # Valor diferente
            'description': 'A'
        }
        internal = {
            'date': '2024-11-02',  # 1 dia diferença
            'value': 100.00,
            'description': 'B'
        }
        
        confidence = processor._calculate_match_confidence(bank, internal)
        # 0.15 (data parcial) + 0 (valor) + ~0 (descrição)
        assert 0.10 <= confidence <= 0.20
    
    def test_calculate_match_confidence_value_only_tolerance(self, processor):
        """TESTE 23: Valor dentro da tolerância (não exato) = 0.20"""
        bank = {
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'A'
        }
        internal = {
            'date': '2024-11-10',  # Data fora da tolerância
            'value': 101.50,  # 1.5% diferença
            'description': 'B'
        }
        
        confidence = processor._calculate_match_confidence(bank, internal)
        # 0 (data) + 0.20 (valor parcial) + ~0 (descrição)
        assert 0.15 <= confidence <= 0.25


# ============================================================================
# TESTES DE EDGE CASES
# ============================================================================

class TestReconciliationProcessorEdgeCases:
    """Testes de casos extremos"""
    
    def test_reconcile_with_zero_values(self, processor):
        """TESTE 24: Deve rejeitar transações com valor zero"""
        bank_data = [
            {'id': 1, 'date': '2024-01-15', 'value': 0, 'description': 'Zero'}
        ]
        internal_data = [
            {'id': 1, 'date': '2024-01-15', 'value': 0, 'description': 'Zero'}
        ]
        
        result = processor.reconcile(bank_data, internal_data)
        
        # Valores zero não dão match
        assert len(result['matched']) == 0
        assert len(result['bank_only']) == 1
        assert len(result['internal_only']) == 1
    
    def test_reconcile_with_empty_description(self, processor):
        """TESTE 25: Deve lidar com descrições vazias"""
        bank_data = [
            {'id': 1, 'date': '2024-01-15', 'value': 100, 'description': ''}
        ]
        internal_data = [
            {'id': 1, 'date': '2024-01-15', 'value': 100, 'description': ''}
        ]
        
        result = processor.reconcile(bank_data, internal_data)
        
        # Deve processar mas com confiança baixa
        assert isinstance(result, dict)
        assert 'matched' in result
    
    def test_reconcile_with_none_description(self, processor):
        """TESTE 26: Deve lidar com descrições None"""
        bank_data = [
            {'id': 1, 'date': '2024-01-15', 'value': 100, 'description': None}
        ]
        internal_data = [
            {'id': 1, 'date': '2024-01-15', 'value': 100, 'description': None}
        ]
        
        result = processor.reconcile(bank_data, internal_data)
        
        assert isinstance(result, dict)
    
    def test_reconcile_with_invalid_date_format(self, processor):
        """TESTE 27: Deve lidar com formato de data inválido"""
        bank_data = [
            {'id': 1, 'date': 'invalid', 'value': 100, 'description': 'Test'}
        ]
        internal_data = [
            {'id': 1, 'date': '2024-01-15', 'value': 100, 'description': 'Test'}
        ]
        
        result = processor.reconcile(bank_data, internal_data)
        
        # Não deve crashar
        assert isinstance(result, dict)
        assert len(result['matched']) == 0
    
    def test_best_match_selection_multiple_candidates(self, processor):
        """TESTE 28: Deve selecionar o MELHOR match entre múltiplos candidatos"""
        bank = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Pagamento Fornecedor ABC'
        }]
        
        internal = [
            {
                'id': 0,
                'date': '2024-11-01',
                'value': 100.00,
                'description': 'Pagamento Fornecedor ABC'  # Match perfeito
            },
            {
                'id': 1,
                'date': '2024-11-02',
                'value': 101.00,
                'description': 'Pagamento Forn ABC'  # Match parcial
            }
        ]
        
        result = processor.reconcile(bank, internal)
        
        # Deve escolher o match com maior confiança (id=0)
        assert len(result['matched']) == 1
        assert result['matched'][0]['internal_transaction']['id'] == 0
        assert result['matched'][0]['confidence'] == 1.0
    
    def test_already_matched_transactions_skipped(self, processor):
        """TESTE 29: Transações já conciliadas não devem ser reutilizadas"""
        bank = [
            {'id': 0, 'date': '2024-11-01', 'value': 100.00, 'description': 'Pag A'},
            {'id': 1, 'date': '2024-11-01', 'value': 100.00, 'description': 'Pag A'}
        ]
        
        internal = [
            {'id': 0, 'date': '2024-11-01', 'value': 100.00, 'description': 'Pag A'}
        ]
        
        result = processor.reconcile(bank, internal)
        
        # Apenas 1 match (primeiro banco com único interno)
        assert len(result['matched']) == 1
        assert len(result['bank_only']) == 1