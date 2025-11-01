"""
PDFProcessor - Processador de arquivos PDF
Responsável por extrair texto de PDFs e identificar transações bancárias
"""

import PyPDF2
import pandas as pd
import re
from typing import List, Dict, Optional
from datetime import datetime


class PDFProcessor:
    """Processador de arquivos PDF de extratos bancários"""
    
    def __init__(self):
        # Padrões regex para identificar elementos comuns
        self.patterns = {
            # Formatos de data: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
            'date': r'\b(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})\b',
            
            # Valores monetários: R$ 1.500,00 ou 1.500,00 ou 1500.00
            'value': r'R?\$?\s*[-+]?\s*\d{1,3}(?:[.,]\d{3})*[.,]\d{2}',
            
            # Tipos de transação comuns
            'transaction_types': r'(PIX|TED|DOC|TEF|BOLETO|DEPÓSITO|DEPOSITO|SAQUE|TRANSF|PAGAMENTO|COMPRA|TARIFA)',
        }
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extrai todo o texto de um PDF
        
        Args:
            file_path: Caminho do arquivo PDF
            
        Returns:
            String com o texto extraído
            
        Raises:
            FileNotFoundError: Se arquivo não existe
            ValueError: Se não conseguir ler o PDF
        """
        text = ""
        
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                
                print(f"📄 PDF possui {num_pages} página(s)")
                
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        text += page_text + "\n"
                        print(f"✅ Página {page_num + 1} extraída: {len(page_text)} caracteres")
                    except Exception as e:
                        print(f"⚠️ Erro ao extrair página {page_num + 1}: {e}")
                        continue
                
                if not text.strip():
                    raise ValueError("Nenhum texto foi extraído do PDF. O arquivo pode estar vazio ou ser uma imagem digitalizada.")
                
                return text
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        except Exception as e:
            raise ValueError(f"Erro ao ler PDF: {str(e)}")
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Converte string de data para formato YYYY-MM-DD
        
        Args:
            date_str: String com a data
            
        Returns:
            Data no formato YYYY-MM-DD ou None
        """
        date_formats = [
            '%d/%m/%Y',  # 10/01/2025
            '%d-%m-%Y',  # 10-01-2025
            '%Y-%m-%d',  # 2025-01-10
            '%Y/%m/%d',  # 2025/01/10
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str.strip(), fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def _parse_value(self, value_str: str) -> Optional[float]:
        """
        Converte string de valor monetário para float
        
        Args:
            value_str: String com o valor (ex: "R$ 1.500,00" ou "-150.00")
            
        Returns:
            Valor como float ou None
        """
        try:
            # Remover símbolos
            clean_value = value_str.replace('R$', '').replace('$', '').strip()
            
            # Identificar sinal
            is_negative = clean_value.startswith('-')
            clean_value = clean_value.replace('-', '').replace('+', '').strip()
            
            # Detectar formato (vírgula como decimal ou ponto como decimal)
            if ',' in clean_value and '.' in clean_value:
                # Formato brasileiro: 1.500,00
                clean_value = clean_value.replace('.', '').replace(',', '.')
            elif ',' in clean_value:
                # Apenas vírgula: 1500,00
                clean_value = clean_value.replace(',', '.')
            # Se apenas ponto, já está correto: 1500.00
            
            value = float(clean_value)
            return -value if is_negative else value
            
        except (ValueError, AttributeError):
            return None
    
    def parse_bank_statement(self, text: str) -> pd.DataFrame:
        """
        Converte texto extraído em DataFrame de transações
        
        Args:
            text: Texto do extrato bancário
            
        Returns:
            DataFrame com colunas: Data, Descricao, Valor, Tipo
        """
        if not text or not text.strip():
            return pd.DataFrame(columns=['Data', 'Descricao', 'Valor', 'Tipo'])
        
        transactions = []
        lines = text.split('\n')
        current_date = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Procurar por data na linha
            date_match = re.search(self.patterns['date'], line)
            if date_match:
                date_str = date_match.group(0)
                current_date = self._parse_date(date_str)
            
            # Procurar por valor na linha
            value_matches = re.findall(self.patterns['value'], line)
            
            if value_matches and current_date:
                value_str = value_matches[-1]  # Último valor encontrado
                value = self._parse_value(value_str)
                
                # Extrair descrição (remover data e valor)
                description = line
                description = re.sub(self.patterns['date'], '', description)
                description = re.sub(self.patterns['value'], '', description)
                description = re.sub(r'\s+', ' ', description).strip()
                
                if value is not None and description:
                    # Determinar tipo (débito/crédito)
                    tipo = 'Crédito' if value >= 0 else 'Débito'
                    
                    transactions.append({
                        'Data': current_date,
                        'Descricao': description,
                        'Valor': abs(value),  # Valor sempre positivo
                        'Tipo': tipo
                    })
        
        df = pd.DataFrame(transactions)
        
        if not df.empty:
            print(f"✅ Encontradas {len(df)} transações no PDF")
            # Remover duplicatas
            df = df.drop_duplicates()
        else:
            print("⚠️ Nenhuma transação identificada no PDF")
        
        return df
    
    def get_summary(self, df: pd.DataFrame) -> dict:
        """
        Retorna resumo das transações extraídas
        
        Args:
            df: DataFrame com transações
            
        Returns:
            Dicionário com estatísticas
        """
        if df.empty:
            return {
                'total_transactions': 0,
                'total_debit': 0,
                'total_credit': 0,
                'date_range': None
            }
        
        total_debit = df[df['Tipo'] == 'Débito']['Valor'].sum() if 'Tipo' in df.columns else 0
        total_credit = df[df['Tipo'] == 'Crédito']['Valor'].sum() if 'Tipo' in df.columns else 0
        
        return {
            'total_transactions': len(df),
            'total_debit': float(total_debit),
            'total_credit': float(total_credit),
            'date_range': {
                'start': df['Data'].min() if 'Data' in df.columns else None,
                'end': df['Data'].max() if 'Data' in df.columns else None
            }
        }
