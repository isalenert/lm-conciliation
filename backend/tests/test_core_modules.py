"""
Testes para módulos core auxiliares
Requisito: RNF06 - Cobertura OBRIGATÓRIA > 75%
"""
import pytest
from app.core.config import settings


class TestConfig:
    """Testes de configuração"""
    
    def test_settings_exist(self):
        """TESTE 1: Settings devem existir"""
        assert settings is not None
        assert hasattr(settings, 'DATABASE_URL')
    
    def test_secret_key_exists(self):
        """TESTE 2: Secret key deve existir"""
        assert hasattr(settings, 'SECRET_KEY')
        assert len(settings.SECRET_KEY) > 0
    
    def test_algorithm_config(self):
        """TESTE 3: Algoritmo JWT configurado"""
        assert hasattr(settings, 'ALGORITHM')
        assert settings.ALGORITHM == 'HS256'


class TestSecurity:
    """Testes adicionais de segurança"""
    
    def test_hash_password_deterministic(self):
        """TESTE 4: Hash deve ser consistente"""
        from app.core.security import hash_password, verify_password
        
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
    
    def test_verify_password_wrong(self):
        """TESTE 5: Senha errada não deve verificar"""
        from app.core.security import hash_password, verify_password
        
        password = "TestPassword123"
        wrong = "WrongPassword456"
        hashed = hash_password(password)
        
        assert not verify_password(wrong, hashed)
    
    def test_create_token_returns_string(self):
        """TESTE 6: Token deve ser uma string"""
        from app.core.security import create_access_token
        
        token = create_access_token(data={"sub": "test@example.com"})
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT tem pontos


class TestDeps:
    """Testes de dependências"""
    
    def test_get_db_generator(self):
        """TESTE 7: get_db é um generator"""
        from app.core.deps import get_db
        import inspect
        
        assert inspect.isgeneratorfunction(get_db)


class TestDatabase:
    """Testes do módulo database"""
    
    def test_base_exists(self):
        """TESTE 8: Base do SQLAlchemy existe"""
        from app.core.database import Base
        
        assert Base is not None
    
    def test_session_local_exists(self):
        """TESTE 9: SessionLocal existe"""
        from app.core.database import SessionLocal
        
        assert SessionLocal is not None