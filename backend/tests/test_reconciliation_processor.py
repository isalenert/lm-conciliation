"""
Testes do Motor de Conciliação
"""
import pytest
from app.core.reconciliation_processor import ReconciliationProcessor


class TestReconciliationProcessor:
    """Testes para o ReconciliationProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Fixture: Instância do processador com valores padrão"""
        return ReconciliationProcessor(
            date_tolerance=1,
            value_tolerance=0.02,
            similarity_threshold=0.7
        )
    
    @pytest.fixture
    def sample_bank_data(self):
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
    def sample_internal_data(self):
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
        assert result['summary']['matched_count'] >= 2  # Pelo menos 2 matches esperados
    
    def test_confidence_calculation(self, processor):
        """Teste 8: Cálculo de confiança"""
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
        
        # Match perfeito deve ter alta confiança
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
            similarity_threshold=0.5  # Threshold mais baixo
        )
        
        bank = [{
            'id': 0,
            'date': '2024-11-01',
            'value': 100.00,
            'description': 'Pagamento Fornecedor'  # Descrição mais completa
        }]
        
        internal = [{
            'id': 0,
            'date': '2024-11-04',  # 3 dias
            'value': 104.00,       # 4%
            'description': 'Fornecedor Pagamento'  # Similar
        }]
        
        result = processor.reconcile(bank, internal)
        
        assert len(result['matched']) == 1
