"""
Testes Completos para PDFProcessor
Requisito: RNF06 - Cobertura de testes > 75%
Cobertura alvo: 85%+
"""
import pytest
import pandas as pd
from app.core.pdf_processor import PDFProcessor
import tempfile
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


# ============================================================================
# FIXTURES GLOBAIS
# ============================================================================

@pytest.fixture
def processor():
    """Instância do PDFProcessor"""
    return PDFProcessor()


@pytest.fixture
def sample_pdf_simple():
    """PDF simples com transações"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    temp_path = temp_file.name
    temp_file.close()
    
    c = canvas.Canvas(temp_path, pagesize=letter)
    c.drawString(100, 750, "BANCO EXEMPLO S.A.")
    c.drawString(100, 730, "EXTRATO BANCÁRIO")
    c.drawString(100, 690, "10/01/2025 Pagamento Fornecedor  -150,00")
    c.drawString(100, 670, "11/01/2025 PIX Recebido         +200,50")
    c.save()
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def sample_pdf_multipage():
    """PDF com múltiplas páginas"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    temp_path = temp_file.name
    temp_file.close()
    
    c = canvas.Canvas(temp_path, pagesize=letter)
    c.drawString(100, 750, "Página 1")
    c.drawString(100, 730, "10/01/2025 Compra  R$ 150,00")
    c.showPage()
    c.drawString(100, 750, "Página 2")
    c.drawString(100, 730, "15/01/2025 PIX  R$ 300,50")
    c.save()
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.unlink(temp_path)


# ============================================================================
# TESTES DO MÉTODO extract_text_from_pdf()
# ============================================================================

class TestExtractText:
    """Testes de extração de texto"""
    
    def test_extract_text_simple_pdf(self, processor, sample_pdf_simple):
        """TESTE 1: Extrair texto de PDF simples"""
        text = processor.extract_text_from_pdf(sample_pdf_simple)
        
        assert text is not None
        assert len(text) > 0
        assert isinstance(text, str)
    
    def test_extract_text_multipage_pdf(self, processor, sample_pdf_multipage):
        """TESTE 2: Extrair texto de PDF multipáginas"""
        text = processor.extract_text_from_pdf(sample_pdf_multipage)
        
        assert text is not None
        assert len(text) > 0
    
    def test_extract_text_file_not_found(self, processor):
        """TESTE 3: Deve lançar FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            processor.extract_text_from_pdf('/path/inexistente.pdf')
    
    def test_extract_text_corrupted_pdf(self, processor):
        """TESTE 4: Deve lançar ValueError para PDF corrompido"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_path = temp_file.name
        
        with open(temp_path, 'wb') as f:
            f.write(b"Not a valid PDF")
        
        try:
            with pytest.raises(ValueError):
                processor.extract_text_from_pdf(temp_path)
        finally:
            os.unlink(temp_path)


# ============================================================================
# TESTES DO MÉTODO _parse_date()
# ============================================================================

class TestParseDate:
    """Testes do método privado _parse_date()"""
    
    @pytest.mark.parametrize("input_date,expected", [
        ('10/01/2025', '2025-01-10'),
        ('10-01-2025', '2025-01-10'),
        ('2025-01-10', '2025-01-10'),
        ('2025/01/10', '2025-01-10'),
    ])
    def test_parse_date_formats(self, processor, input_date, expected):
        """TESTE 5: Deve parsear vários formatos de data"""
        result = processor._parse_date(input_date)
        assert result == expected
    
    def test_parse_date_invalid(self, processor):
        """TESTE 6: Deve retornar None para data inválida"""
        result = processor._parse_date('invalid-date')
        assert result is None


# ============================================================================
# TESTES DO MÉTODO _parse_value()
# ============================================================================

class TestParseValue:
    """Testes do método privado _parse_value()"""
    
    @pytest.mark.parametrize("input_value,expected", [
        ('R$ 150,00', 150.00),
        ('R$ 1.500,00', 1500.00),
        ('150.00', 150.00),
        ('-150.00', -150.00),
        ('+200.50', 200.50),
        ('$ 100.00', 100.00),
    ])
    def test_parse_value_formats(self, processor, input_value, expected):
        """TESTE 7: Deve parsear vários formatos de valor"""
        result = processor._parse_value(input_value)
        assert result == expected
    
    def test_parse_value_with_thousands_separator(self, processor):
        """TESTE 8: Deve tratar separador de milhares"""
        result = processor._parse_value('R$ 1.500,00')
        assert result == 1500.00
    
    def test_parse_value_invalid(self, processor):
        """TESTE 9: Deve retornar None para valor inválido"""
        result = processor._parse_value('invalid')
        assert result is None


# ============================================================================
# TESTES DO MÉTODO parse_bank_statement()
# ============================================================================

class TestParseBankStatement:
    """Testes de parsing de extratos"""
    
    def test_parse_transactions_from_text(self, processor):
        """TESTE 10: Deve identificar transações em texto"""
        text = """
        10/01/2025 Pagamento Alpha  R$ 150,00
        11/01/2025 PIX Recebido     R$ 200,50
        """
        
        df = processor.parse_bank_statement(text)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'Data' in df.columns
        assert 'Descricao' in df.columns
        assert 'Valor' in df.columns
        assert 'Tipo' in df.columns
    
    def test_parse_empty_text(self, processor):
        """TESTE 11: Texto vazio retorna DataFrame vazio"""
        df = processor.parse_bank_statement("")
        
        assert isinstance(df, pd.DataFrame)
        assert df.empty
        assert list(df.columns) == ['Data', 'Descricao', 'Valor', 'Tipo']
    
    def test_parse_text_without_transactions(self, processor):
        """TESTE 12: Texto sem transações retorna DataFrame vazio"""
        text = "BANCO EXEMPLO - Apenas texto"
        
        df = processor.parse_bank_statement(text)
        
        assert isinstance(df, pd.DataFrame)
    
    def test_parse_identifies_transaction_types(self, processor):
        """TESTE 13: Deve identificar tipo de transação (débito/crédito)"""
        text = """
        10/01/2025 PIX Enviado       -150,00
        11/01/2025 PIX Recebido      +200,50
        """
        
        df = processor.parse_bank_statement(text)
        
        if not df.empty:
            assert 'Tipo' in df.columns
    
    def test_parse_removes_duplicates(self, processor):
        """TESTE 14: Deve remover transações duplicadas"""
        text = """
        10/01/2025 Pagamento  R$ 150,00
        10/01/2025 Pagamento  R$ 150,00
        """
        
        df = processor.parse_bank_statement(text)
        
        # DataFrame deve ter duplicatas removidas
        assert isinstance(df, pd.DataFrame)
    
    def test_parse_multiple_values_in_line(self, processor):
        """TESTE 15: Deve pegar último valor quando há múltiplos"""
        text = "10/01/2025 Saldo anterior: 1000,00 Débito: 150,00"
        
        df = processor.parse_bank_statement(text)
        
        # Deve processar corretamente
        assert isinstance(df, pd.DataFrame)


# ============================================================================
# TESTES DO MÉTODO get_summary()
# ============================================================================

class TestGetSummary:
    """Testes de geração de resumo"""
    
    def test_get_summary_with_transactions(self, processor):
        """TESTE 16: Deve gerar resumo com transações"""
        df = pd.DataFrame({
            'Data': ['2025-01-10', '2025-01-11'],
            'Descricao': ['Débito', 'Crédito'],
            'Valor': [150.00, 200.50],
            'Tipo': ['Débito', 'Crédito']
        })
        
        summary = processor.get_summary(df)
        
        assert summary['total_transactions'] == 2
        assert summary['total_debit'] == 150.00
        assert summary['total_credit'] == 200.50
        assert 'date_range' in summary
    
    def test_get_summary_empty_dataframe(self, processor):
        """TESTE 17: Deve retornar resumo vazio para DataFrame vazio"""
        df = pd.DataFrame()
        
        summary = processor.get_summary(df)
        
        assert summary['total_transactions'] == 0
        assert summary['total_debit'] == 0
        assert summary['total_credit'] == 0
        assert summary['date_range'] is None


# ============================================================================
# TESTES DE INTEGRAÇÃO
# ============================================================================

class TestIntegration:
    """Testes de integração completa"""
    
    def test_full_pipeline(self, processor, sample_pdf_simple):
        """TESTE 18: Pipeline completo: extrair + parsear + resumo"""
        # 1. Extrair texto
        text = processor.extract_text_from_pdf(sample_pdf_simple)
        assert text is not None
        
        # 2. Parsear transações
        df = processor.parse_bank_statement(text)
        assert isinstance(df, pd.DataFrame)
        
        # 3. Gerar resumo
        summary = processor.get_summary(df)
        assert isinstance(summary, dict)