"""
Motor de Conciliação - ReconciliationProcessor
Desenvolvido com TDD (Test-Driven Development)
"""

import pandas as pd
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
from typing import Dict


class ReconciliationProcessor:
    """Processador principal de conciliação bancária"""
    
    def __init__(self, 
                 date_tolerance_days: int = 1,
                 value_tolerance: float = 0.01,
                 similarity_threshold: float = 0.8):
        self.date_tolerance_days = date_tolerance_days
        self.value_tolerance = value_tolerance
        self.similarity_threshold = similarity_threshold
    
    def reconcile(self, 
                  bank_df: pd.DataFrame, 
                  internal_df: pd.DataFrame,
                  config: Dict) -> Dict:
        """Executa a conciliação entre dois DataFrames"""
        
        date_col = config.get('date_col', 'Data')
        value_col = config.get('value_col', 'Valor')
        desc_col = config.get('desc_col', 'Descricao')
        
        self._validate_columns(bank_df, internal_df, date_col, value_col, desc_col)
        
        bank_norm = self._normalize_dataframe(bank_df.copy(), date_col, value_col)
        internal_norm = self._normalize_dataframe(internal_df.copy(), date_col, value_col)
        
        matches = []
        bank_remaining = bank_norm.copy()
        internal_remaining = internal_norm.copy()
        bank_indices_to_remove = []
        internal_indices_to_remove = []
        
        for bank_idx, bank_row in bank_norm.iterrows():
            if bank_idx in bank_indices_to_remove:
                continue
                
            best_match = None
            best_score = 0
            best_internal_idx = None
            
            for internal_idx, internal_row in internal_norm.iterrows():
                if internal_idx in internal_indices_to_remove:
                    continue
                    
                score = self._calculate_match_score(
                    bank_row, internal_row, 
                    date_col, value_col, desc_col
                )
                
                if score > best_score:
                    best_score = score
                    best_match = internal_row
                    best_internal_idx = internal_idx
            
            if best_match is not None and best_score >= self.similarity_threshold:
                matches.append({
                    'bank_transaction': bank_row.to_dict(),
                    'internal_transaction': best_match.to_dict(),
                    'confidence': best_score
                })
                
                bank_indices_to_remove.append(bank_idx)
                internal_indices_to_remove.append(best_internal_idx)
        
        bank_remaining = bank_norm.drop(bank_indices_to_remove)
        internal_remaining = internal_norm.drop(internal_indices_to_remove)
        
        # CORREÇÃO: Calcular taxa de match corretamente
        # Taxa de match = transações conciliadas / total de transações do banco
        # (O banco é a fonte de verdade - queremos saber quantas do banco foram encontradas)
        total_bank = len(bank_df)
        total_internal = len(internal_df)
        matched_count = len(matches)
        
        # Taxa baseada no arquivo do banco (referência)
        match_rate = (matched_count / total_bank * 100) if total_bank > 0 else 0
        
        return {
            'matched': matches,
            'bank_only': bank_remaining.to_dict('records'),
            'internal_only': internal_remaining.to_dict('records'),
            'summary': {
                'total_bank_transactions': total_bank,
                'total_internal_transactions': total_internal,
                'matched_count': matched_count,
                'bank_only_count': len(bank_remaining),
                'internal_only_count': len(internal_remaining),
                'match_rate': round(match_rate, 2)  # Arredondado para 2 casas
            }
        }
    
    def _validate_columns(self, bank_df, internal_df, date_col, value_col, desc_col):
        """Valida se as colunas existem nos DataFrames"""
        for col in [date_col, value_col, desc_col]:
            if col not in bank_df.columns:
                raise ValueError(
                    f"Coluna '{col}' não encontrada no arquivo do banco. "
                    f"Colunas disponíveis: {list(bank_df.columns)}"
                )
            if col not in internal_df.columns:
                raise ValueError(
                    f"Coluna '{col}' não encontrada no arquivo interno. "
                    f"Colunas disponíveis: {list(internal_df.columns)}"
                )
    
    def _normalize_dataframe(self, df, date_col, value_col):
        """Normaliza datas e valores para comparação"""
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
        return df
    
    def _calculate_match_score(self, row1, row2, date_col, value_col, desc_col):
        """Calcula score de similaridade entre duas transações"""
        
        try:
            date_diff = abs((row1[date_col] - row2[date_col]).days)
            if date_diff > self.date_tolerance_days:
                return 0.0
        except:
            return 0.0
        
        try:
            val1 = float(row1[value_col])
            val2 = float(row2[value_col])
            value_diff = abs(round(val1, 2) - round(val2, 2))
            
            if value_diff > self.value_tolerance + 0.001:
                return 0.0
        except:
            return 0.0
        
        try:
            desc1 = str(row1[desc_col]).upper().strip()
            desc2 = str(row2[desc_col]).upper().strip()
            
            description_similarity = fuzz.token_set_ratio(desc1, desc2) / 100.0
            
            return description_similarity
        except:
            return 0.0
