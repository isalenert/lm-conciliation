"""
CSVProcessor - Processador de arquivos CSV
Responsável por ler, detectar encoding e padronizar dados
"""

import pandas as pd
import chardet
from typing import Optional
from datetime import datetime


class CSVProcessor:
    """Processador de arquivos CSV com detecção automática de encoding"""
    
    def __init__(self):
        self.supported_encodings = ['utf-8', 'iso-8859-1', 'latin-1', 'cp1252']
        # Formatos comuns de data no Brasil
        self.date_formats = [
            '%Y-%m-%d',  # 2025-01-10
            '%d/%m/%Y',  # 10/01/2025
            '%d-%m-%Y',  # 10-01-2025
            '%Y/%m/%d',  # 2025/01/10
            '%m/%d/%Y',  # 01/10/2025 (formato americano)
        ]
    
    def detect_encoding(self, file_path: str) -> str:
        """
        Detecta o encoding do arquivo usando chardet
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Nome do encoding detectado (ex: 'utf-8')
        """
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Ler primeiros 10KB
            result = chardet.detect(raw_data)
            return result['encoding']
    
    def read_csv(self, file_path: str, encoding: Optional[str] = None) -> pd.DataFrame:
        """
        Lê arquivo CSV com detecção automática de encoding
        
        Args:
            file_path: Caminho do arquivo
            encoding: Encoding específico (opcional)
            
        Returns:
            DataFrame com os dados do CSV
            
        Raises:
            FileNotFoundError: Se arquivo não existe
        """
        if encoding is None:
            encoding = self.detect_encoding(file_path)
            print(f"📝 Encoding detectado: {encoding}")
        
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            print(f"✅ CSV lido com sucesso: {len(df)} linhas, {len(df.columns)} colunas")
            return df
        except UnicodeDecodeError:
            # Tentar com outros encodings
            for enc in self.supported_encodings:
                if enc != encoding:
                    try:
                        df = pd.read_csv(file_path, encoding=enc)
                        print(f"✅ CSV lido com encoding alternativo: {enc}")
                        return df
                    except UnicodeDecodeError:
                        continue
            
            raise ValueError(
                f"Não foi possível ler o arquivo com nenhum encoding suportado. "
                f"Tentados: {', '.join(self.supported_encodings)}"
            )
    
    def _parse_date_flexible(self, date_str):
        """
        Tenta parsear uma data em múltiplos formatos
        
        Args:
            date_str: String com a data
            
        Returns:
            String no formato YYYY-MM-DD ou None se falhar
        """
        if pd.isna(date_str) or date_str == '' or str(date_str).strip() == '':
            return None
        
        date_str = str(date_str).strip()
        
        # Tentar cada formato
        for fmt in self.date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Se nenhum formato funcionou, tentar com pandas (mais flexível)
        try:
            parsed_date = pd.to_datetime(date_str, dayfirst=True)
            return parsed_date.strftime('%Y-%m-%d')
        except:
            return None
    
    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Padroniza datas e valores do DataFrame
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame com dados padronizados
        """
        df_clean = df.copy()
        
        # 1. Padronizar colunas de data
        date_columns = [col for col in df.columns 
                       if 'data' in col.lower() or 'date' in col.lower()]
        
        for col in date_columns:
            try:
                # Aplicar parse flexível em cada valor
                df_clean[col] = df_clean[col].apply(self._parse_date_flexible)
                print(f"✅ Coluna '{col}' padronizada para YYYY-MM-DD")
            except Exception as e:
                print(f"⚠️ Não foi possível padronizar coluna de data '{col}': {e}")
        
        # 2. Padronizar colunas de valor
        value_columns = [col for col in df.columns 
                        if 'valor' in col.lower() or 'value' in col.lower() 
                        or 'amount' in col.lower() or 'preco' in col.lower()]
        
        for col in value_columns:
            try:
                # Remover símbolos de moeda e converter para float
                if df_clean[col].dtype == 'object':
                    # Remover R$, $, espaços
                    df_clean[col] = df_clean[col].astype(str).str.replace('R$', '', regex=False)
                    df_clean[col] = df_clean[col].str.replace('$', '', regex=False)
                    df_clean[col] = df_clean[col].str.strip()
                    
                    # Substituir vírgula por ponto (decimal brasileiro → internacional)
                    df_clean[col] = df_clean[col].str.replace('.', '', regex=False)  # Remover separador de milhar
                    df_clean[col] = df_clean[col].str.replace(',', '.', regex=False)  # Vírgula → ponto
                
                # Converter para numérico
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                print(f"✅ Coluna '{col}' padronizada para numérico")
            except Exception as e:
                print(f"⚠️ Não foi possível padronizar coluna de valor '{col}': {e}")
        
        # 3. Remover espaços extras em colunas de texto
        text_columns = df_clean.select_dtypes(include=['object']).columns
        for col in text_columns:
            if col not in date_columns:  # Já processamos datas
                df_clean[col] = df_clean[col].astype(str).str.strip()
                df_clean[col] = df_clean[col].str.replace(r'\s+', ' ', regex=True)  # Múltiplos espaços → um espaço
        
        return df_clean
    
    def get_summary(self, df: pd.DataFrame) -> dict:
        """
        Retorna resumo dos dados do CSV
        
        Args:
            df: DataFrame
            
        Returns:
            Dicionário com estatísticas
        """
        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB",
            'dtypes': df.dtypes.astype(str).to_dict()
        }
