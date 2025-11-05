"""
Motor de Conciliação - CORE DO SISTEMA
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz


class ReconciliationProcessor:
    """
    Processa conciliação entre transações bancárias e internas
    """
    
    def __init__(
        self,
        date_tolerance: int = 1,
        value_tolerance: float = 0.02,
        similarity_threshold: float = 0.7
    ):
        """
        Args:
            date_tolerance: Dias de diferença aceitos (padrão: 1 dia)
            value_tolerance: % de diferença aceita no valor (padrão: 2%)
            similarity_threshold: Score mínimo de similaridade (0-1)
        """
        self.date_tolerance = date_tolerance
        self.value_tolerance = value_tolerance
        self.similarity_threshold = similarity_threshold
    
    def _parse_date(self, date_str: str) -> datetime:
        """Converte string para datetime"""
        return datetime.strptime(date_str, '%Y-%m-%d')
    
    def _dates_match(self, date1: str, date2: str) -> bool:
        """Verifica se datas estão dentro da tolerância"""
        try:
            d1 = self._parse_date(date1)
            d2 = self._parse_date(date2)
            diff = abs((d1 - d2).days)
            return diff <= self.date_tolerance
        except:
            return False
    
    def _values_match(self, value1: float, value2: float) -> bool:
        """Verifica se valores estão dentro da tolerância"""
        if value1 == 0 or value2 == 0:
            return False
        
        diff_percentage = abs(value1 - value2) / max(value1, value2)
        return diff_percentage <= self.value_tolerance
    
    def _calculate_description_similarity(self, desc1: str, desc2: str) -> float:
        """
        Calcula similaridade entre descrições usando fuzzy matching
        Retorna score de 0 a 1
        """
        if not desc1 or not desc2:
            return 0.0
        
        # Normalizar strings
        desc1 = desc1.lower().strip()
        desc2 = desc2.lower().strip()
        
        # Usar ratio do fuzzywuzzy (0-100, converter para 0-1)
        score = fuzz.token_sort_ratio(desc1, desc2) / 100.0
        
        return score
    
    def _calculate_match_confidence(
        self,
        bank_transaction: Dict,
        internal_transaction: Dict
    ) -> float:
        """
        Calcula confiança do match (0-1)
        
        Pesos:
        - Data exata: 0.3
        - Valor exato: 0.4
        - Descrição similar: 0.3
        """
        confidence = 0.0
        
        # Data
        if bank_transaction['date'] == internal_transaction['date']:
            confidence += 0.3
        elif self._dates_match(bank_transaction['date'], internal_transaction['date']):
            confidence += 0.15
        
        # Valor
        if bank_transaction['value'] == internal_transaction['value']:
            confidence += 0.4
        elif self._values_match(bank_transaction['value'], internal_transaction['value']):
            confidence += 0.2
        
        # Descrição
        desc_similarity = self._calculate_description_similarity(
            bank_transaction['description'],
            internal_transaction['description']
        )
        confidence += desc_similarity * 0.3
        
        return round(confidence, 2)
    
    def reconcile(
        self,
        bank_data: List[Dict],
        internal_data: List[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Executa conciliação
        
        Returns:
            Dict com:
            - matched: lista de matches encontrados
            - bank_only: transações apenas no banco
            - internal_only: transações apenas no sistema interno
            - summary: resumo estatístico
        """
        matched = []
        bank_only = []
        internal_only = []
        
        # Set para rastrear IDs já conciliados
        matched_bank_ids = set()
        matched_internal_ids = set()
        
        # Procurar matches
        for bank_trans in bank_data:
            best_match = None
            best_confidence = 0.0
            
            for internal_trans in internal_data:
                # Pular se já foi conciliado
                if internal_trans['id'] in matched_internal_ids:
                    continue
                
                # Verificar critérios básicos
                if not self._dates_match(bank_trans['date'], internal_trans['date']):
                    continue
                
                if not self._values_match(bank_trans['value'], internal_trans['value']):
                    continue
                
                # Calcular confiança
                confidence = self._calculate_match_confidence(bank_trans, internal_trans)
                
                # Manter melhor match acima do threshold
                if confidence >= self.similarity_threshold and confidence > best_confidence:
                    best_match = internal_trans
                    best_confidence = confidence
            
            # Se encontrou match, adicionar
            if best_match:
                matched.append({
                    'bank_transaction': bank_trans,
                    'internal_transaction': best_match,
                    'confidence': best_confidence
                })
                matched_bank_ids.add(bank_trans['id'])
                matched_internal_ids.add(best_match['id'])
            else:
                bank_only.append(bank_trans)
        
        # Transações internas não conciliadas
        internal_only = [
            trans for trans in internal_data
            if trans['id'] not in matched_internal_ids
        ]
        
        # Calcular estatísticas
        total_bank = len(bank_data)
        total_internal = len(internal_data)
        matched_count = len(matched)
        
        match_rate = 0.0
        if total_bank > 0 or total_internal > 0:
            match_rate = (matched_count * 2) / (total_bank + total_internal) * 100
        
        return {
            'matched': matched,
            'bank_only': bank_only,
            'internal_only': internal_only,
            'summary': {
                'total_bank_transactions': total_bank,
                'total_internal_transactions': total_internal,
                'matched_count': matched_count,
                'bank_only_count': len(bank_only),
                'internal_only_count': len(internal_only),
                'match_rate': round(match_rate, 2)
            }
        }
