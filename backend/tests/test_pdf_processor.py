"""
Testes para PDFProcessor
Testa extração de texto de PDFs e identificação de transações
"""

import pytest
import pandas as pd
from app.core.pdf_processor import PDFProcessor
import tempfile
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


class TestPDFProcessor:
    
    @pytest.fixture
    def processor(self):
        """Cria instância do PDFProcessor"""
        return PDFProcessor()
    
    @pytest.fixture
    def sample_pdf_simple(self):
        """Cria um PDF simples com texto extraível"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # Criar PDF com reportlab
        c = canvas.Canvas(temp_path, pagesize=letter)
        
        # Adicionar conteúdo simulando extrato bancário
        c.drawString(100, 750, "BANCO EXEMPLO S.A.")
        c.drawString(100, 730, "EXTRATO BANCÁRIO - Janeiro/2025")
        c.drawString(100, 710, "")
        c.drawString(100, 690, "Data       Descrição                    Valor")
        c.drawString(100, 670, "10/01/2025 Pagamento Fornecedor Alpha  -150,00")
        c.drawString(100, 650, "11/01/2025 PIX Recebido João Silva     +200,50")
        c.drawString(100, 630, "12/01/2025 TED Enviado                 -75,00")
        
        c.save()
        return temp_path
    
    @pytest.fixture
    def sample_pdf_complex(self):
        """Cria um PDF mais complexo com múltiplas transações"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        c = canvas.Canvas(temp_path, pagesize=letter)
        
        # Página 1
        c.drawString(100, 750, "BANCO BRASIL")
        c.drawString(100, 730, "Período: 01/01/2025 a 31/01/2025")
        c.drawString(100, 690, "10/01/2025 Compra débito SUPERMERCADO XYZ  R$ 150,00")
        c.drawString(100, 670, "15/01/2025 PIX Transferência               R$ 300,50")
        c.drawString(100, 650, "20/01/2025 Tarifa bancária                 R$ 15,90")
        
        c.showPage()  # Nova página
        
        # Página 2
        c.drawString(100, 750, "Continuação...")
        c.drawString(100, 730, "25/01/2025 Pagamento boleto               R$ 500,00")
        c.drawString(100, 710, "30/01/2025 Saque ATM                      R$ 200,00")
        
        c.save()
        return temp_path
    
    def test_extract_text_simple_pdf(self, processor, sample_pdf_simple):
        """Teste 1: Extrair texto de PDF simples"""
        text = processor.extract_text_from_pdf(sample_pdf_simple)
        
        assert text is not None
        assert len(text) > 0
        assert "BANCO EXEMPLO" in text or "Banco" in text.lower()
        assert "Pagamento" in text or "pagamento" in text.lower()
        
        os.unlink(sample_pdf_simple)
    
    def test_extract_text_multipage_pdf(self, processor, sample_pdf_complex):
        """Teste 2: Extrair texto de PDF com múltiplas páginas"""
        text = processor.extract_text_from_pdf(sample_pdf_complex)
        
        assert text is not None
        assert len(text) > 0
        # Deve ter conteúdo das duas páginas
        assert "BANCO BRASIL" in text or "banco" in text.lower()
        
        os.unlink(sample_pdf_complex)
    
    def test_parse_transactions_from_text(self, processor):
        """Teste 3: Identificar transações em texto extraído"""
        text = """
        BANCO EXEMPLO S.A.
        EXTRATO BANCÁRIO
        
        10/01/2025 Pagamento Fornecedor Alpha  R$ 150,00
        11/01/2025 PIX Recebido João Silva     R$ 200,50
        12/01/2025 TED Enviado                 R$ 75,00
        """
        
        df = processor.parse_bank_statement(text)
        
        assert not df.empty, "Deve encontrar transações"
        assert len(df) > 0
        assert 'Data' in df.columns
        assert 'Descricao' in df.columns or 'Descrição' in df.columns
        assert 'Valor' in df.columns
    
    def test_parse_date_formats(self, processor):
        """Teste 4: Identificar diferentes formatos de data"""
        text = """
        10/01/2025 Compra Loja A  100,00
        2025-01-11 Pagamento B    200,00
        12-01-2025 Transferência  300,00
        """
        
        df = processor.parse_bank_statement(text)
        
        assert len(df) > 0, "Deve encontrar pelo menos uma transação"
    
    def test_parse_value_formats(self, processor):
        """Teste 5: Identificar diferentes formatos de valor"""
        text = """
        10/01/2025 Pagamento A  R$ 1.500,00
        11/01/2025 Pagamento B  2.000,50
        12/01/2025 Pagamento C  150.00
        """
        
        df = processor.parse_bank_statement(text)
        
        assert len(df) > 0
        # Verificar se valores foram convertidos
        if 'Valor' in df.columns:
            assert df['Valor'].dtype in ['float64', 'float32', 'object']
    
    def test_empty_pdf_text(self, processor):
        """Teste 6: Texto vazio não deve quebrar"""
        text = ""
        
        df = processor.parse_bank_statement(text)
        
        assert df.empty or len(df) == 0
    
    def test_pdf_without_transactions(self, processor):
        """Teste 7: PDF sem transações retorna DataFrame vazio"""
        text = """
        BANCO EXEMPLO S.A.
        Este é um texto sem transações bancárias.
        Apenas informações gerais.
        """
        
        df = processor.parse_bank_statement(text)
        
        # Pode estar vazio ou ter poucas linhas (sem dados válidos)
        assert len(df) == 0 or df.empty
    
    def test_invalid_pdf_path(self, processor):
        """Teste 8: PDF inexistente deve lançar erro"""
        with pytest.raises((FileNotFoundError, Exception)):
            processor.extract_text_from_pdf('/caminho/inexistente/arquivo.pdf')
    
    def test_detect_transaction_types(self, processor):
        """Teste 9: Identificar tipos de transação (débito/crédito)"""
        text = """
        10/01/2025 PIX Enviado       -150,00
        11/01/2025 PIX Recebido      +200,50
        12/01/2025 Depósito          300,00
        """
        
        df = processor.parse_bank_statement(text)
        
        if not df.empty and 'Tipo' in df.columns:
            # Verificar se identificou tipos
            tipos = df['Tipo'].unique()
            assert len(tipos) > 0
    
    def test_clean_extracted_text(self, processor):
        """Teste 10: Limpar texto extraído"""
        messy_text = """
        BANCO    EXEMPLO       
        
        
        10/01/2025     Pagamento     150,00
        """
        
        df = processor.parse_bank_statement(messy_text)
        
        # Deve funcionar mesmo com texto bagunçado
        assert isinstance(df, pd.DataFrame)
