"""
Testes para rotas de autenticação
Requisito: RNF06 - Cobertura de testes > 50%
Requisito: RNF02 - Segurança (JWT, bcrypt, validação de senhas)
Requisito: RNF09 - Testabilidade (testes isolados com fixtures)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.core.security import hash_password


# Configuração do banco de dados de teste
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Cria banco de dados de teste limpo para cada teste"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Cliente de teste FastAPI com banco isolado"""
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(client):
    """Cria usuário de teste no banco"""
    db = TestingSessionLocal()
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=hash_password("TestPassword123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


class TestAuthRoutes:
    """Suite de testes para rotas de autenticação"""
    
    def test_signup_success(self, client):
        """
        TESTE 1: Deve criar usuário com dados válidos
        Requisito: RF01 - Sistema de autenticação
        """
        # Arrange
        payload = {
            "email": "newuser@example.com",
            "name": "New User",
            "password": "StrongPass123"
        }
        
        # Act
        response = client.post("/api/auth/signup", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        # ✅ API retorna apenas dados do usuário, não token no signup
        assert "email" in data
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_signup_duplicate_email(self, client, sample_user):
        """
        TESTE 2: Deve rejeitar cadastro com email duplicado
        Requisito: RNF02 - Segurança (unicidade de email)
        """
        # Arrange
        payload = {
            "email": "test@example.com",
            "name": "Duplicate User",
            "password": "AnotherPass123"
        }
        
        # Act
        response = client.post("/api/auth/signup", json=payload)
        
        # Assert
        assert response.status_code in [400, 409]
        assert "email" in response.json()["detail"].lower()
    
    def test_signup_invalid_email(self, client):
        """
        TESTE 3: Deve rejeitar email inválido
        Requisito: RNF02 - Validação de input (Pydantic)
        """
        # Arrange
        payload = {
            "email": "invalid-email",
            "name": "Invalid User",
            "password": "ValidPass123"
        }
        
        # Act
        response = client.post("/api/auth/signup", json=payload)
        
        # Assert
        assert response.status_code == 422
    
    def test_signup_weak_password(self, client):
        """
        TESTE 4: Deve rejeitar senha fraca
        Requisito: RNF02 - Segurança (senhas fortes obrigatórias)
        """
        # Arrange
        payload = {
            "email": "weakpass@example.com",
            "name": "Weak User",
            "password": "123"
        }
        
        # Act
        response = client.post("/api/auth/signup", json=payload)
        
        # Assert
        assert response.status_code in [400, 422]
        error_message = str(response.json()).lower()
        assert any(keyword in error_message for keyword in [
            "senha", "password", "caracteres", "mínimo", "minimum"
        ])
    
    def test_login_success(self, client, sample_user):
        """
        TESTE 5: Deve autenticar com credenciais corretas
        Requisito: RF01 - Login com JWT
        """
        # Arrange
        payload = {
            "email": "test@example.com",
            "password": "TestPassword123"
        }
        
        # Act
        response = client.post("/api/auth/login", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        # ✅ API não retorna objeto user no login, apenas token
    
    def test_login_wrong_password(self, client, sample_user):
        """
        TESTE 6: Deve rejeitar senha incorreta
        Requisito: RNF02 - Segurança (validação de credenciais)
        """
        # Arrange
        payload = {
            "email": "test@example.com",
            "password": "WrongPassword123"
        }
        
        # Act
        response = client.post("/api/auth/login", json=payload)
        
        # Assert
        assert response.status_code == 401
        detail = response.json()["detail"].lower()
        assert any(word in detail for word in [
            "incorreta", "incorreto", "incorretos", "invalid", "wrong"
        ])
    
    def test_login_nonexistent_user(self, client):
        """
        TESTE 7: Deve rejeitar usuário inexistente
        Requisito: RNF02 - Segurança
        """
        # Arrange
        payload = {
            "email": "nonexistent@example.com",
            "password": "AnyPassword123"
        }
        
        # Act
        response = client.post("/api/auth/login", json=payload)
        
        # Assert
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_login_missing_fields(self, client):
        """
        TESTE 8: Deve rejeitar requisição sem campos obrigatórios
        Requisito: RNF02 - Validação de input
        """
        # Arrange
        payload = {
            "email": "test@example.com"
        }
        
        # Act
        response = client.post("/api/auth/login", json=payload)
        
        # Assert
        assert response.status_code == 422
    
    def test_protected_route_without_token(self, client):
        """
        TESTE 9: Deve rejeitar acesso sem token JWT
        Requisito: RNF02 - Segurança (autenticação obrigatória)
        """
        # Arrange & Act
        response = client.get("/api/auth/me")
        
        # Assert
        assert response.status_code == 401
    
    def test_protected_route_with_valid_token(self, client, sample_user):
        """
        TESTE 10: Deve permitir acesso com token válido
        Requisito: RNF02 - Autenticação JWT funcional
        """
        # Arrange
        login_response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123"
        })
        token = login_response.json()["access_token"]
        
        # Act
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
    
    def test_protected_route_with_invalid_token(self, client):
        """
        TESTE 11: Deve rejeitar token inválido
        Requisito: RNF02 - Validação de JWT
        """
        # Arrange
        fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.signature"
        
        # Act
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {fake_token}"}
        )
        
        # Assert
        assert response.status_code in [401, 403]
    
    def test_token_contains_user_info(self, client, sample_user):
        """
        TESTE 12: Token JWT deve ser válido e permitir acesso a /me
        Requisito: RNF02 - Payload JWT com dados necessários
        """
        # Arrange & Act: Login
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123"
        })
        
        # Assert: Token gerado
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        
        # Act: Usar token para acessar dados do usuário
        token = data["access_token"]
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert: Dados do usuário retornados
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["email"] == "test@example.com"
        assert user_data["name"] == "Test User"
        assert "id" in user_data
        assert "password" not in user_data
        assert "hashed_password" not in user_data