"""
Teste de conexão com banco
"""

from app.core.database import SessionLocal, init_db
from app.models import User

# Inicializar (se necessário)
init_db()

# Testar criação de usuário
db = SessionLocal()

test_user = User(
    email="test@example.com",
    name="Test User",
    password_hash="hash_temporario"
)

db.add(test_user)
db.commit()
db.refresh(test_user)

print(f"✅ Usuário criado: {test_user}")

# Buscar usuário
user = db.query(User).filter(User.email == "test@example.com").first()
print(f"✅ Usuário encontrado: {user}")

db.close()
print("\n🎉 BANCO DE DADOS FUNCIONANDO PERFEITAMENTE!")
