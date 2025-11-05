"""
Processador de arquivos CSV
"""
import pandas as pd
import chardet
from typing import Dict, List
from datetime import datetime


class CSVProcessor:
    """Processa arquivos CSV para conciliação"""
    
    @staticmethod
    def detect_encoding(file_path: str) -> str:
        """Detecta encoding do arquivo"""
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding']
    
    @staticmethod
    def read_csv(file_path: str) -> pd.DataFrame:
        """Lê arquivo CSV com detecção automática de encoding"""
        encoding = CSVProcessor.detect_encoding(file_path)
        
        try:
            df = pd.read_csv(file_path, encoding=encoding)
        except:
            # Tentar encoding alternativo
            df = pd.read_csv(file_path, encoding='latin-1')
        
        # Limpar nomes das colunas (remover espaços)
        df.columns = df.columns.str.strip()
        
        return df
    
    @staticmethod
    def normalize_date(date_str) -> str:
        """Normaliza datas para formato padrão YYYY-MM-DD"""
        if pd.isna(date_str):
            return None
        
        # Tentar vários formatos
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%m/%d/%Y',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(str(date_str).strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except:
                continue
        
        return str(date_str)
    
    @staticmethod
    def normalize_value(value) -> float:
        """Normaliza valores monetários"""
        if pd.isna(value):
            return 0.0
        
        # Remover símbolos e converter
        value_str = str(value).replace('R$', '').replace(',', '.').strip()
        
        try:
            return float(value_str)
        except:
            return 0.0
    
    @staticmethod
    def process_dataframe(
        df: pd.DataFrame,
        date_col: str,
        value_col: str,
        desc_col: str
    ) -> List[Dict]:
        """
        Processa DataFrame e retorna lista de dicts
        """
        results = []
        
        for idx, row in df.iterrows():
            try:
                item = {
                    'id': idx,
                    'date': CSVProcessor.normalize_date(row[date_col]),
                    'value': CSVProcessor.normalize_value(row[value_col]),
                    'description': str(row[desc_col]).strip() if pd.notna(row[desc_col]) else '',
                    'original': row.to_dict()
                }
                results.append(item)
            except Exception as e:
                print(f"Erro processando linha {idx}: {e}")
                continue
        
        return results
