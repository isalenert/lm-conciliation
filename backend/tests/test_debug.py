"""Teste de debug para entender o problema da tolerância de valor"""

import pandas as pd
from app.core.reconciliation_processor import ReconciliationProcessor

# Criar processador
processor = ReconciliationProcessor(
    date_tolerance_days=1,
    value_tolerance=0.01,
    similarity_threshold=0.7
)

# Dados do teste
bank_data = pd.DataFrame([{
    "Data": "2025-01-10",
    "Valor": 100.00,
    "Descricao": "Pagamento"
}])

internal_data = pd.DataFrame([{
    "Data": "2025-01-10",
    "Valor": 100.01,
    "Descricao": "Pagamento"
}])

config = {
    'date_col': 'Data',
    'value_col': 'Valor',
    'desc_col': 'Descricao'
}

# Executar conciliação
results = processor.reconcile(bank_data, internal_data, config)

# Mostrar resultados
print("\n�� RESULTADOS DA CONCILIAÇÃO:")
print(f"Matched: {results['summary']['matched_count']}")
print(f"Bank only: {results['summary']['bank_only_count']}")
print(f"Internal only: {results['summary']['internal_only_count']}")

# Verificar diferença de valor
diff = abs(100.00 - 100.01)
print(f"\n💰 DIFERENÇA DE VALOR: {diff}")
print(f"Tolerância configurada: {processor.value_tolerance}")
print(f"Dentro da tolerância? {diff <= processor.value_tolerance}")
