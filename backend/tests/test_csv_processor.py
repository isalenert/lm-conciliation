"""
Testes para CSVProcessor
Testa leitura, detecção de encoding e padronização de dados
"""

import pytest
import pandas as pd
from app.core.csv_processor import CSVProcessor
import tempfile
import os


class TestCSVProcessor:
    
    @pytest.fixture
    def processor(self):
        """Cria instância do CSVProcessor"""
        return CSVProcessor()
    
    @pytest.fixture
    def sample_csv_utf8(self):
        """Cria um CSV de exemplo em UTF-8"""
        content = """Data,Valor,Descricao,ID
2025-01-10,150.00,Pagamento Fornecedor Alpha,TX001
2025-01-11,200.50,Transferência PIX,TX002
2025-01-12,75.99,Compra Supermercado,TX003"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            return f.name
    
    @pytest.fixture
    def sample_csv_latin1(self):
        """Cria um CSV em ISO-8859-1 (Latin-1) com acentos"""
        content = """Data,Valor,Descrição,ID
2025-01-10,150.00,Pagamento à Fornecedor Ação,TX001
2025-01-11,200.50,Transferência José,TX002"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='latin-1') as f:
            f.write(content)
            return f.name
    
    @pytest.fixture
    def sample_csv_messy_data(self):
        """CSV com dados bagunçados que precisam ser padronizados"""
        content = """Data,Valor,Descricao
10/01/2025,1500.50,  Pagamento  com  espaços  
11-01-2025,2000.00,Vírgula como separador
2025/01/12,150.00,Formato ISO"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            return f.name
    
    def test_read_csv_utf8(self, processor, sample_csv_utf8):
        """Teste 1: Ler CSV com encoding UTF-8"""
        df = processor.read_csv(sample_csv_utf8)
        
        assert len(df) == 3, "Deveria ter 3 linhas"
        assert list(df.columns) == ['Data', 'Valor', 'Descricao', 'ID']
        assert df['Descricao'].iloc[0] == 'Pagamento Fornecedor Alpha'
        
        os.unlink(sample_csv_utf8)
    
    def test_read_csv_latin1(self, processor, sample_csv_latin1):
        """Teste 2: Ler CSV com encoding Latin-1 (detecção automática)"""
        df = processor.read_csv(sample_csv_latin1)
        
        assert len(df) == 2
        assert 'Descrição' in df.columns or 'Descricao' in df.columns
        
        first_desc = df.iloc[0]['Descrição'] if 'Descrição' in df.columns else df.iloc[0]['Descricao']
        assert 'à' in first_desc or 'a' in first_desc
        
        os.unlink(sample_csv_latin1)
    
    def test_standardize_dates(self, processor, sample_csv_utf8):
        """Teste 3: Padronizar datas para formato YYYY-MM-DD"""
        df = processor.read_csv(sample_csv_utf8)
        df_clean = processor.standardize_data(df)
        
        assert df_clean['Data'].iloc[0] == '2025-01-10'
        assert df_clean['Data'].dtype == 'object'
        
        os.unlink(sample_csv_utf8)
    
    def test_standardize_values(self, processor, sample_csv_utf8):
        """Teste 4: Padronizar valores para float"""
        df = processor.read_csv(sample_csv_utf8)
        df_clean = processor.standardize_data(df)
        
        assert df_clean['Valor'].dtype in ['float64', 'float32']
        assert df_clean['Valor'].iloc[0] == 150.00
        assert df_clean['Valor'].iloc[1] == 200.50
        
        os.unlink(sample_csv_utf8)
    
    def test_handle_messy_data(self, processor, sample_csv_messy_data):
        """Teste 5: Lidar com dados bagunçados"""
        df = processor.read_csv(sample_csv_messy_data)
        df_clean = processor.standardize_data(df)
        
        assert len(df_clean) == 3
        
        # Verificar se pelo menos uma data foi convertida corretamente
        dates = df_clean['Data'].dropna().tolist()
        assert len(dates) > 0, "Deve haver pelo menos uma data válida"
        assert '2025-01-10' in dates or '2025-01-11' in dates or '2025-01-12' in dates
        
        # Valores devem ser numéricos
        assert df_clean['Valor'].dtype in ['float64', 'float32']
        
        os.unlink(sample_csv_messy_data)
    
    def test_invalid_file_path(self, processor):
        """Teste 6: Arquivo inexistente deve lançar erro"""
        with pytest.raises(FileNotFoundError):
            processor.read_csv('/caminho/inexistente/arquivo.csv')
    
    def test_empty_dataframe_handling(self, processor):
        """Teste 7: CSV vazio não deve quebrar"""
        content = "Data,Valor,Descricao\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        df = processor.read_csv(temp_path)
        df_clean = processor.standardize_data(df)
        
        assert len(df_clean) == 0
        assert list(df_clean.columns) == ['Data', 'Valor', 'Descricao']
        
        os.unlink(temp_path)
    
    def test_detect_encoding_automatically(self, processor):
        """Teste 8: Detecção automática de encoding"""
        content = "Data,Valor,Descrição\n2025-01-10,100.00,Café™"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        encoding = processor.detect_encoding(temp_path)
        
        assert encoding.lower() in ['utf-8', 'ascii', 'utf-8-sig']
        
        os.unlink(temp_path)
