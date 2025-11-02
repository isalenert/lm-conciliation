"""
Rotas de conciliação
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import pandas as pd

from app.core.csv_processor import CSVProcessor
from app.core.reconciliation_processor import ReconciliationProcessor
from app.api.models.schemas import ReconciliationResponse, ErrorResponse

router = APIRouter()


@router.post("/reconcile", response_model=ReconciliationResponse)
async def reconcile_files(
    bank_file: UploadFile = File(..., description="Arquivo do banco"),
    internal_file: UploadFile = File(..., description="Arquivo do sistema interno"),
    date_col: str = Form("Data"),
    value_col: str = Form("Valor"),
    desc_col: str = Form("Descricao"),
    id_col: str = Form(None),
    date_tolerance: int = Form(1),
    value_tolerance: float = Form(0.02),
    similarity_threshold: float = Form(0.7)
):
    """
    Executa conciliação entre dois arquivos
    
    **Parâmetros:**
    - bank_file: Arquivo do extrato bancário (CSV)
    - internal_file: Arquivo do sistema interno (CSV)
    - date_col: Nome da coluna de data
    - value_col: Nome da coluna de valor
    - desc_col: Nome da coluna de descrição
    - id_col: Nome da coluna de ID (opcional)
    - date_tolerance: Tolerância em dias (padrão: 1)
    - value_tolerance: Tolerância em valor (padrão: 0.02)
    - similarity_threshold: Threshold de similaridade (padrão: 0.7)
    
    **Retorna:**
    - matched: Lista de transações pareadas
    - bank_only: Transações apenas no banco
    - internal_only: Transações apenas no sistema
    - summary: Estatísticas da conciliação
    """
    
    try:
        print(f"🔍 Iniciando conciliação...")
        print(f"📋 Configuração: date={date_col}, value={value_col}, desc={desc_col}")
        
        # Processar arquivo do banco
        bank_content = await bank_file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_bank:
            tmp_bank.write(bank_content)
            tmp_bank_path = tmp_bank.name
        
        bank_processor = CSVProcessor()
        bank_df = bank_processor.read_csv(tmp_bank_path)
        bank_df_clean = bank_processor.standardize_data(bank_df)
        print(f"✅ Banco: {len(bank_df_clean)} transações processadas")
        
        # Processar arquivo interno
        internal_content = await internal_file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_internal:
            tmp_internal.write(internal_content)
            tmp_internal_path = tmp_internal.name
        
        internal_processor = CSVProcessor()
        internal_df = internal_processor.read_csv(tmp_internal_path)
        internal_df_clean = internal_processor.standardize_data(internal_df)
        print(f"✅ Sistema: {len(internal_df_clean)} transações processadas")
        
        # Limpar arquivos temporários
        os.unlink(tmp_bank_path)
        os.unlink(tmp_internal_path)
        
        # Verificar se DataFrames não estão vazios
        if bank_df_clean.empty:
            raise ValueError("Arquivo do banco está vazio ou não contém dados válidos")
        if internal_df_clean.empty:
            raise ValueError("Arquivo do sistema interno está vazio ou não contém dados válidos")
        
        # Configurar processador de conciliação
        reconciliation_processor = ReconciliationProcessor(
            date_tolerance_days=date_tolerance,
            value_tolerance=value_tolerance,
            similarity_threshold=similarity_threshold
        )
        
        config = {
            'date_col': date_col,
            'value_col': value_col,
            'desc_col': desc_col,
            'id_col': id_col if id_col and id_col != 'null' else None
        }
        
        print(f"🔧 Executando algoritmo de conciliação...")
        
        # Executar conciliação
        results = reconciliation_processor.reconcile(
            bank_df_clean,
            internal_df_clean,
            config
        )
        
        print(f"🎯 Conciliação concluída!")
        print(f"✅ Matches: {results['summary']['matched_count']}")
        print(f"⚠️  Pendentes banco: {results['summary']['bank_only_count']}")
        print(f"⚠️  Pendentes sistema: {results['summary']['internal_only_count']}")
        
        return results
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro na conciliação: {str(e)}"
        )
