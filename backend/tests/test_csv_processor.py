"""
Testes para o processador de CSV
"""
import pytest
import tempfile
import os
from app.core.csv_processor import CSVProcessor


class TestCSVProcessor:
    
    @pytest.fixture
    def processor(self):
        """Fixture do processador CSV"""
        return CSVProcessor()
    
    @pytest.fixture
    def sample_csv_utf8(self):
        """Fixture CSV UTF-8"""
        content = """Data,Valor,Descricao
01/01/2024,100.50,Pagamento 1
02/01/2024,200.75,Pagamento 2
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        yield temp_path
        os.unlink(temp_path)
    
    @pytest.fixture
    def sample_csv_latin1(self):
        """Fixture CSV Latin-1"""
        content = "Data,Valor,Descrição\n01/01/2024,100.50,Pagamento 1\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='latin-1') as f:
            f.write(content)
            temp_path = f.name
        
        yield temp_path
        os.unlink(temp_path)
    
    @pytest.fixture
    def sample_csv_messy_data(self):
        """Fixture CSV com dados bagunçados"""
        content = """Data,Valor,Descricao
01/01/2024,R$ 100,50,Pix recebido
02-01-2024,"1.234,56",Transferência
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        yield temp_path
        os.unlink(temp_path)
    
    def test_read_csv_utf8(self, processor, sample_csv_utf8):
        """Teste 1: Ler CSV com encoding UTF-8"""
        df = processor.read_csv(sample_csv_utf8)
        
        assert df is not None
        assert len(df) == 2
        assert 'Data' in df.columns
        assert 'Valor' in df.columns
    
    def test_read_csv_latin1(self, processor, sample_csv_latin1):
        """Teste 2: Ler CSV com encoding Latin-1"""
        df = processor.read_csv(sample_csv_latin1)
        
        assert df is not None
        assert len(df) == 1
        assert 'Data' in df.columns
    
    def test_standardize_dates(self, processor, sample_csv_utf8):
        """Teste 3: Verificar leitura de datas"""
        df = processor.read_csv(sample_csv_utf8)
        
        # Testar que leu o arquivo e tem a coluna Data
        assert 'Data' in df.columns
        assert len(df) > 0
        
        # Testar normalização de data
        date_normalized = processor.normalize_date('01/01/2024')
        assert date_normalized == '2024-01-01'
    
    def test_standardize_values(self, processor, sample_csv_utf8):
        """Teste 4: Verificar normalização de valores"""
        df = processor.read_csv(sample_csv_utf8)
        
        # Testar que leu o arquivo e tem a coluna Valor
        assert 'Valor' in df.columns
        assert len(df) > 0
        
        # Testar normalização de valor
        value_normalized = processor.normalize_value('100.50')
        assert value_normalized == 100.50
    
    def test_handle_messy_data(self, processor, sample_csv_messy_data):
        """Teste 5: Lidar com dados bagunçados"""
        df = processor.read_csv(sample_csv_messy_data)
        
        # Testar que conseguiu ler mesmo com dados bagunçados
        assert len(df) > 0
        assert 'Data' in df.columns
        
        # Testar process_dataframe com colunas existentes
        result = processor.process_dataframe(df, 'Data', 'Valor', 'Descricao')
        assert isinstance(result, list)
    
    def test_invalid_file_path(self, processor):
        """Teste 6: Arquivo inexistente deve lançar erro"""
        with pytest.raises(Exception):
            processor.read_csv('/caminho/inexistente/arquivo.csv')
    
    def test_empty_dataframe_handling(self, processor):
        """Teste 7: CSV vazio não deve quebrar"""
        content = "Data,Valor,Descricao\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        df = processor.read_csv(temp_path)
        
        # Testar que leu o CSV mesmo vazio (só headers)
        assert len(df) == 0
        assert 'Data' in df.columns
        assert 'Valor' in df.columns
        assert 'Descricao' in df.columns
        
        os.unlink(temp_path)
    
    def test_detect_encoding_automatically(self, processor, sample_csv_utf8):
        """Teste 8: Detecção automática de encoding"""
        encoding = processor.detect_encoding(sample_csv_utf8)
        
        assert encoding is not None
        assert isinstance(encoding, str)
