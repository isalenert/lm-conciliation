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
        """
        Args:
            date_tolerance_days: Diferença máxima em dias (ex: ±1 dia)
            value_tolerance: Diferença máxima em valor (ex: ±R$ 0,01)
            similarity_threshold: % mínima de similaridade (0.8 = 80%)
        """
        self.date_tolerance_days = date_tolerance_days
        self.value_tolerance = value_tolerance
        self.similarity_threshold = similarity_threshold
    
    def reconcile(self, 
                  bank_df: pd.DataFrame, 
                  internal_df: pd.DataFrame,
                  config: Dict) -> Dict:
        """Executa a conciliação entre dois DataFrames"""
        
        # Extrair nomes das colunas
        date_col = config.get('date_col', 'Data')
        value_col = config.get('value_col', 'Valor')
        desc_col = config.get('desc_col', 'Descricao')
        
        # Validar se as colunas existem
        self._validate_columns(bank_df, internal_df, date_col, value_col, desc_col)
        
        # Normalizar dados
        bank_norm = self._normalize_dataframe(bank_df.copy(), date_col, value_col)
        internal_norm = self._normalize_dataframe(internal_df.copy(), date_col, value_col)
        
        # Executar o pareamento
        matches = []
        bank_remaining = bank_norm.copy()
        internal_remaining = internal_norm.copy()
        
        # Iterar sobre transações do banco
        for bank_idx, bank_row in bank_remaining.iterrows():
            best_match = None
            best_score = 0
            
            # Buscar melhor match no sistema interno
            for internal_idx, internal_row in internal_remaining.iterrows():
                score = self._calculate_match_score(
                    bank_row, internal_row, 
                    date_col, value_col, desc_col
                )
                
                if score > best_score:
                    best_score = score
                    best_match = (internal_idx, internal_row)
            
            # Se encontrou um match acima do threshold
            if best_match and best_score >= self.similarity_threshold:
                internal_idx, internal_row = best_match
                
                matches.append({
                    'bank_transaction': bank_row.to_dict(),
                    'internal_transaction': internal_row.to_dict(),
                    'confidence': best_score
                })
                
                # Remover das pendentes
                bank_remaining = bank_remaining.drop(bank_idx)
                internal_remaining = internal_remaining.drop(internal_idx)
        
        # Montar resultado
        return {
            'matched': matches,
            'bank_only': bank_remaining.to_dict('records'),
            'internal_only': internal_remaining.to_dict('records'),
            'summary': {
                'total_bank_transactions': len(bank_df),
                'total_internal_transactions': len(internal_df),
                'matched_count': len(matches),
                'bank_only_count': len(bank_remaining),
                'internal_only_count': len(internal_remaining),
                'match_rate': len(matches) / max(len(bank_df), 1) * 100
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
        """
        Calcula score de similaridade entre duas transações
        
        MUDANÇA: Agora aceita valores dentro da tolerância e usa token_set_ratio
        para melhor matching de descrições
        """
        
        # 1. Validar data (com tolerância)
        date_diff = abs((row1[date_col] - row2[date_col]).days)
        if date_diff > self.date_tolerance_days:
            return 0.0
        
        # 2. Validar valor (com tolerância) - CORRIGIDO
        value_diff = abs(row1[value_col] - row2[value_col])
        if value_diff > self.value_tolerance:
            return 0.0
        
        # 3. Calcular similaridade da descrição - MELHORADO
        desc1 = str(row1[desc_col]).upper().strip()
        desc2 = str(row2[desc_col]).upper().strip()
        
        # Usar token_set_ratio para melhor matching de descrições
        # Isso ignora ordem das palavras e palavras extras
        description_similarity = fuzz.token_set_ratio(desc1, desc2) / 100.0
        
        # Se data e valor batem (dentro da tolerância), considerar o match
        # mesmo que a descrição não seja 100% similar
        if date_diff <= self.date_tolerance_days and value_diff <= self.value_tolerance:
            # Reduzir threshold efetivo quando data e valor batem
            return description_similarity
        
        return description_similarity
