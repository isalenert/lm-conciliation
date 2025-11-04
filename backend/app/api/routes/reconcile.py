"""
Rotas de conciliação
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import tempfile
import os
import pandas as pd

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.csv_processor import CSVProcessor
from app.core.reconciliation_processor import ReconciliationProcessor
from app.services.reconciliation_service import ReconciliationService
from app.models.user import User
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
    similarity_threshold: float = Form(0.7),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executa conciliação entre dois arquivos e salva no banco
    
    Requer autenticação via token JWT
    """
    
    try:
        print(f"🔍 Conciliação iniciada pelo usuário: {current_user.email}")
        
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
            raise ValueError("Arquivo do banco está vazio")
        if internal_df_clean.empty:
            raise ValueError("Arquivo do sistema interno está vazio")
        
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
        
        # Salvar no banco de dados
        print(f"💾 Salvando conciliação no banco de dados...")
        reconciliation = ReconciliationService.create_reconciliation(
            db=db,
            user_id=current_user.id,
            bank_file_name=bank_file.filename,
            internal_file_name=internal_file.filename,
            results=results
        )
        
        print(f"🎯 Conciliação salva com ID: {reconciliation.id}")
        print(f"✅ Matches: {results['summary']['matched_count']}")
        print(f"⚠️  Pendentes banco: {results['summary']['bank_only_count']}")
        print(f"⚠️  Pendentes sistema: {results['summary']['internal_only_count']}")
        
        # Adicionar ID da conciliação ao resultado
        results['reconciliation_id'] = reconciliation.id
        
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
