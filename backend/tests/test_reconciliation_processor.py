"""Testes para o ReconciliationProcessor - TDD"""

import pytest
import pandas as pd
from app.core.reconciliation_processor import ReconciliationProcessor


class TestReconciliationProcessor:
    
    @pytest.fixture
    def processor(self):
        """Cria uma instância do processador"""
        return ReconciliationProcessor(
            date_tolerance_days=1,
            value_tolerance=0.02,  # 2 centavos (mais realista)
            similarity_threshold=0.70  # 70% de similaridade
        )
    
    def test_exact_match_all_fields(self, processor):
        """Teste 1: Match perfeito - tudo idêntico"""
        bank_data = pd.DataFrame([{
            "Data": "2025-01-10",
            "Valor": 150.00,
            "Descricao": "Pagamento Fornecedor Alpha"
        }])
        
        internal_data = pd.DataFrame([{
            "Data": "2025-01-10",
            "Valor": 150.00,
            "Descricao": "Pagamento Fornecedor Alpha"
        }])
        
        config = {'date_col': 'Data', 'value_col': 'Valor', 'desc_col': 'Descricao'}
        results = processor.reconcile(bank_data, internal_data, config)
        
        assert results['summary']['matched_count'] == 1
        assert len(results['bank_only']) == 0
        assert len(results['internal_only']) == 0
    
    def test_fuzzy_description_matching(self, processor):
        """Teste 2: Descrições similares mas não idênticas"""
        bank_data = pd.DataFrame([{
            "Data": "2025-01-10",
            "Valor": 150.00,
            "Descricao": "PAGAMENTO FORNECEDOR ALPHA"
        }])
        
        internal_data = pd.DataFrame([{
            "Data": "2025-01-10",
            "Valor": 150.00,
            "Descricao": "Pagto Fornecedor Alpha"
        }])
        
        config = {'date_col': 'Data', 'value_col': 'Valor', 'desc_col': 'Descricao'}
        results = processor.reconcile(bank_data, internal_data, config)
        
        assert results['summary']['matched_count'] == 1
    
    def test_date_tolerance_one_day(self, processor):
        """Teste 3: Tolerância de ±1 dia"""
        bank_data = pd.DataFrame([{
            "Data": "2025-01-10",
            "Valor": 100.00,
            "Descricao": "Transferência"
        }])
        
        internal_data = pd.DataFrame([{
            "Data": "2025-01-11",  # 1 dia depois
            "Valor": 100.00,
            "Descricao": "Transferência"
        }])
        
        config = {'date_col': 'Data', 'value_col': 'Valor', 'desc_col': 'Descricao'}
        results = processor.reconcile(bank_data, internal_data, config)
        
        assert results['summary']['matched_count'] == 1
    
    def test_value_tolerance_two_cents(self, processor):
        """Teste 4: Tolerância de valor (2 centavos)"""
        bank_data = pd.DataFrame([{
            "Data": "2025-01-10",
            "Valor": 100.00,
            "Descricao": "Pagamento Boleto"
        }])
        
        internal_data = pd.DataFrame([{
            "Data": "2025-01-10",
            "Valor": 100.02,  # 2 centavos a mais
            "Descricao": "Pagamento Boleto"
        }])
        
        config = {'date_col': 'Data', 'value_col': 'Valor', 'desc_col': 'Descricao'}
        results = processor.reconcile(bank_data, internal_data, config)
        
        assert results['summary']['matched_count'] == 1
    
    def test_bank_only_transactions(self, processor):
        """Teste 5: Transação existe apenas no banco"""
        bank_data = pd.DataFrame([
            {"Data": "2025-01-10", "Valor": 100.00, "Descricao": "PIX Cliente A"},
            {"Data": "2025-01-11", "Valor": 200.00, "Descricao": "TED Cliente B"}
        ])
        
        internal_data = pd.DataFrame([
            {"Data": "2025-01-10", "Valor": 100.00, "Descricao": "PIX Cliente A"}
            # TED não está registrado no sistema!
        ])
        
        config = {'date_col': 'Data', 'value_col': 'Valor', 'desc_col': 'Descricao'}
        results = processor.reconcile(bank_data, internal_data, config)
        
        assert results['summary']['matched_count'] == 1
        assert len(results['bank_only']) == 1
        assert results['bank_only'][0]['Descricao'] == 'TED Cliente B'
    
    def test_internal_only_transactions(self, processor):
        """Teste 6: Transação existe apenas no sistema interno"""
        bank_data = pd.DataFrame([
            {"Data": "2025-01-10", "Valor": 100.00, "Descricao": "PIX Cliente A"}
        ])
        
        internal_data = pd.DataFrame([
            {"Data": "2025-01-10", "Valor": 100.00, "Descricao": "PIX Cliente A"},
            {"Data": "2025-01-12", "Valor": 300.00, "Descricao": "Venda Produto X"}
            # Venda não apareceu no banco ainda!
        ])
        
        config = {'date_col': 'Data', 'value_col': 'Valor', 'desc_col': 'Descricao'}
        results = processor.reconcile(bank_data, internal_data, config)
        
        assert results['summary']['matched_count'] == 1
        assert len(results['internal_only']) == 1
    
    def test_no_matches_different_periods(self, processor):
        """Teste 7: Arquivos de períodos diferentes - sem matches"""
        bank_data = pd.DataFrame([
            {"Data": "2025-01-10", "Valor": 100.00, "Descricao": "Compra Janeiro"}
        ])
        
        internal_data = pd.DataFrame([
            {"Data": "2025-02-15", "Valor": 200.00, "Descricao": "Venda Fevereiro"}
        ])
        
        config = {'date_col': 'Data', 'value_col': 'Valor', 'desc_col': 'Descricao'}
        results = processor.reconcile(bank_data, internal_data, config)
        
        assert results['summary']['matched_count'] == 0
        assert len(results['bank_only']) == 1
        assert len(results['internal_only']) == 1
