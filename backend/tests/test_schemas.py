"""
Testes para schemas/validações Pydantic
Requisito: RNF06 - Cobertura OBRIGATÓRIA > 75%
"""
import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserLogin, UserResponse


class TestUserSchemas:
    """Testes de validação de schemas de usuário"""
    
    def test_user_create_valid(self):
        """TESTE 1: Criar usuário com dados válidos"""
        user = UserCreate(
            email="test@example.com",
            password="StrongPass123!",
            name="Test User"
        )
        assert user.email == "test@example.com"
        assert user.name == "Test User"
    
    def test_user_create_invalid_email(self):
        """TESTE 2: Rejeitar email inválido"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="invalid-email",
                password="StrongPass123!",
                name="Test"
            )
    
    def test_user_login_valid(self):
        """TESTE 3: Login com dados válidos"""
        login = UserLogin(
            email="test@example.com",
            password="password123"
        )
        assert login.email == "test@example.com"
    
    def test_user_login_missing_fields(self):
        """TESTE 4: Login requer todos os campos"""
        with pytest.raises(ValidationError):
            UserLogin(email="test@example.com")
    
    def test_user_response_structure(self):
        """TESTE 5: Estrutura de resposta do usuário"""
        from datetime import datetime
        user_response = UserResponse(
            id=1,
            email="test@example.com",
            name="Test User",
            created_at=datetime.now()
        )
        assert user_response.id == 1
        assert user_response.email == "test@example.com"