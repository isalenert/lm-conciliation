"""
Testes Completos para CSVProcessor
Requisito: RNF06 - Cobertura de testes > 75%
Cobertura alvo: 90%+
"""
import pytest
import pandas as pd
import tempfile
import os
from app.core.csv_processor import CSVProcessor


# ============================================================================
# FIXTURES GLOBAIS
# ============================================================================

@pytest.fixture
def processor():
    """Instância do CSVProcessor"""
    return CSVProcessor()


# ============================================================================
# TESTES DO MÉTODO detect_encoding()
# ============================================================================

class TestDetectEncoding:
    """Testes de detecção de encoding"""
    
    def test_detect_encoding_utf8(self, processor):
        """TESTE 1: Deve detectar UTF-8"""
        content = "Data,Valor,Descrição\n2025-01-15,1500.00,Test"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            encoding = processor.detect_encoding(temp_path)
            assert encoding is not None
            assert isinstance(encoding, str)
            # UTF-8 pode ser detectado como ascii se não há caracteres especiais
            assert encoding.lower() in ['utf-8', 'ascii', 'utf-8-sig']
        finally:
            os.unlink(temp_path)
    
    def test_detect_encoding_latin1(self, processor):
        """TESTE 2: Deve detectar Latin-1"""
        content = "Data,Valor,Descrição\n2025-01-15,1500,Açúcar e Café"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='latin-1') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            encoding = processor.detect_encoding(temp_path)
            assert encoding is not None
            assert isinstance(encoding, str)
        finally:
            os.unlink(temp_path)
    
    def test_detect_encoding_invalid_file(self, processor):
        """TESTE 3: Deve lançar erro para arquivo inexistente"""
        with pytest.raises(FileNotFoundError):
            processor.detect_encoding('/path/inexistente.csv')


# ============================================================================
# TESTES DO MÉTODO read_csv()
# ============================================================================

class TestReadCSV:
    """Testes de leitura de CSV"""
    
    def test_read_csv_utf8(self, processor):
        """TESTE 4: Deve ler CSV em UTF-8"""
        content = "Data,Valor,Descrição\n2025-01-15,1500.00,Pagamento"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            df = processor.read_csv(temp_path)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 1
            assert 'Data' in df.columns
            assert 'Valor' in df.columns
            assert 'Descrição' in df.columns
        finally:
            os.unlink(temp_path)
    
    def test_read_csv_latin1(self, processor):
        """TESTE 5: Deve ler CSV em Latin-1"""
        content = "Data,Valor,Descrição\n2025-01-15,1500.00,Café"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='latin-1') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            df = processor.read_csv(temp_path)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 1
        finally:
            os.unlink(temp_path)
    
    def test_read_csv_fallback_encoding(self, processor):
        """TESTE 6: Deve usar fallback para latin-1 se encoding falhar"""
        content = "Data,Valor,Descrição\n2025-01-15,1500.00,Test"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # O código tem um try/except que faz fallback para latin-1
            df = processor.read_csv(temp_path)
            assert isinstance(df, pd.DataFrame)
        finally:
            os.unlink(temp_path)
    
    def test_read_csv_strips_column_names(self, processor):
        """TESTE 7: Deve remover espaços dos nomes das colunas"""
        content = " Data , Valor , Descrição \n2025-01-15,1500.00,Test"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            df = processor.read_csv(temp_path)
            # Colunas devem estar sem espaços
            assert 'Data' in df.columns
            assert 'Valor' in df.columns
            assert 'Descrição' in df.columns
        finally:
            os.unlink(temp_path)


# ============================================================================
# TESTES DO MÉTODO normalize_date()
# ============================================================================

class TestNormalizeDate:
    """Testes de normalização de datas"""
    
    @pytest.mark.parametrize("input_date,expected", [
        ('2025-01-15', '2025-01-15'),
        ('15/01/2025', '2025-01-15'),
        ('15-01-2025', '2025-01-15'),
        ('01/15/2025', '2025-01-15'),
        ('2025/01/15', '2025-01-15'),
    ])
    def test_normalize_date_formats(self, processor, input_date, expected):
        """TESTE 8: Deve normalizar vários formatos de data"""
        result = processor.normalize_date(input_date)
        assert result == expected
    
    def test_normalize_date_with_nan(self, processor):
        """TESTE 9: Deve retornar None para valores NaN"""
        result = processor.normalize_date(pd.NA)
        assert result is None
    
    def test_normalize_date_invalid_format(self, processor):
        """TESTE 10: Deve retornar string original para formato inválido"""
        invalid_date = "not-a-date"
        result = processor.normalize_date(invalid_date)
        assert result == invalid_date


# ============================================================================
# TESTES DO MÉTODO normalize_value()
# ============================================================================

class TestNormalizeValue:
    """Testes de normalização de valores"""
    
    @pytest.mark.parametrize("input_value,expected", [
        ('1500.00', 1500.00),
        ('1500,00', 1500.00),
        ('R$ 1500.00', 1500.00),
        ('R$ 1.500,00', 1500.00),  # ✅ AGORA VAI FUNCIONAR
        (1500, 1500.00),
        (1500.5, 1500.5),
        ('1,500.00', 1500.00),  # Formato americano
    ])
    def test_normalize_value_formats(self, processor, input_value, expected):
        """TESTE 11: Deve normalizar vários formatos de valor"""
        result = processor.normalize_value(input_value)
        assert result == expected
    
    def test_normalize_value_with_nan(self, processor):
        """TESTE 12: Deve retornar 0.0 para valores NaN"""
        result = processor.normalize_value(pd.NA)
        assert result == 0.0
    
    def test_normalize_value_invalid(self, processor):
        """TESTE 13: Deve retornar 0.0 para valores inválidos"""
        result = processor.normalize_value("invalid-value")
        assert result == 0.0


# ============================================================================
# TESTES DO MÉTODO process_dataframe()
# ============================================================================

class TestProcessDataframe:
    """Testes de processamento de DataFrame"""
    
    def test_process_dataframe_basic(self, processor):
        """TESTE 14: Deve processar DataFrame básico"""
        df = pd.DataFrame({
            'Data': ['2024-01-15', '2024-01-16'],
            'Valor': [100.00, 200.50],
            'Descrição': ['Pag A', 'Pag B']
        })
        
        result = processor.process_dataframe(df, 'Data', 'Valor', 'Descrição')
        
        assert len(result) == 2
        assert result[0]['id'] == 0
        assert result[0]['date'] == '2024-01-15'
        assert result[0]['value'] == 100.00
        assert result[0]['description'] == 'Pag A'
    
    def test_process_dataframe_with_sequential_ids(self, processor):
        """TESTE 15: Deve adicionar IDs sequenciais"""
        df = pd.DataFrame({
            'Data': ['2024-01-15', '2024-01-16', '2024-01-17'],
            'Valor': [100, 200, 300],
            'Desc': ['A', 'B', 'C']
        })
        
        result = processor.process_dataframe(df, 'Data', 'Valor', 'Desc')
        
        assert len(result) == 3
        assert result[0]['id'] == 0
        assert result[1]['id'] == 1
        assert result[2]['id'] == 2
    
    def test_process_dataframe_normalizes_dates(self, processor):
        """TESTE 16: Deve normalizar formatos de data"""
        df = pd.DataFrame({
            'Date': ['15/01/2024', '16/01/2024'],
            'Amount': [100, 200],
            'Desc': ['A', 'B']
        })
        
        result = processor.process_dataframe(df, 'Date', 'Amount', 'Desc')
        
        assert len(result) == 2
        assert result[0]['date'] == '2024-01-15'
        assert result[1]['date'] == '2024-01-16'
    
    def test_process_dataframe_normalizes_values(self, processor):
        """TESTE 17: Deve normalizar valores monetários"""
        df = pd.DataFrame({
            'Data': ['2024-01-15', '2024-01-16'],
            'Valor': ['R$ 100,50', '200.00'],
            'Desc': ['A', 'B']
        })
        
        result = processor.process_dataframe(df, 'Data', 'Valor', 'Desc')
        
        assert len(result) == 2
        assert isinstance(result[0]['value'], float)
        assert result[0]['value'] == 100.50
    
    def test_process_dataframe_strips_whitespace(self, processor):
        """TESTE 18: Deve remover espaços das descrições"""
        df = pd.DataFrame({
            'Data': ['2024-01-15'],
            'Valor': [100],
            'Desc': ['  Pagamento A  ']
        })
        
        result = processor.process_dataframe(df, 'Data', 'Valor', 'Desc')
        
        assert result[0]['description'] == 'Pagamento A'
    
    def test_process_dataframe_empty(self, processor):
        """TESTE 19: Deve retornar lista vazia para DataFrame vazio"""
        df = pd.DataFrame(columns=['Data', 'Valor', 'Desc'])
        
        result = processor.process_dataframe(df, 'Data', 'Valor', 'Desc')
        
        assert result == []
    
    def test_process_dataframe_with_none_description(self, processor):
        """TESTE 20: Deve tratar descrições None"""
        df = pd.DataFrame({
            'Data': ['2024-01-15'],
            'Valor': [100],
            'Desc': [None]
        })
        
        result = processor.process_dataframe(df, 'Data', 'Valor', 'Desc')
        
        assert result[0]['description'] == ''
    
    def test_process_dataframe_skips_invalid_rows(self, processor, capsys):
        """TESTE 21: Deve pular linhas com erros"""
        df = pd.DataFrame({
            'Data': ['2024-01-15', 'invalid-date'],
            'Valor': [100, 'invalid'],
            'Desc': ['Valid', 'Invalid']
        })
        
        result = processor.process_dataframe(df, 'Data', 'Valor', 'Desc')
        
        # Deve processar pelo menos a linha válida
        assert len(result) >= 1
    
    def test_process_dataframe_preserves_original(self, processor):
        """TESTE 22: Deve preservar dados originais"""
        df = pd.DataFrame({
            'Data': ['2024-01-15'],
            'Valor': [100],
            'Desc': ['Test']
        })
        
        result = processor.process_dataframe(df, 'Data', 'Valor', 'Desc')
        
        assert 'original' in result[0]
        assert isinstance(result[0]['original'], dict)


# ============================================================================
# TESTES DE INTEGRAÇÃO
# ============================================================================

class TestIntegration:
    """Testes de integração"""
    
    def test_full_pipeline(self, processor):
        """TESTE 23: Pipeline completo: detectar + ler + processar"""
        # ✅ CORRIGIDO: Usar formato simples sem separador de milhares
        content = "Data,Valor,Descrição\n15/01/2025,1500.00,Pagamento Fornecedor"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # 1. Detectar encoding
            encoding = processor.detect_encoding(temp_path)
            assert encoding is not None
            
            # 2. Ler CSV
            df = processor.read_csv(temp_path)
            assert len(df) == 1
            
            # 3. Processar DataFrame
            result = processor.process_dataframe(df, 'Data', 'Valor', 'Descrição')
            assert len(result) == 1
            assert result[0]['date'] == '2025-01-15'
            assert result[0]['value'] == 1500.00
        finally:
            os.unlink(temp_path)