"""
Testes para rotas de autenticação
Cobertura: Login, Signup, validação de tokens
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.core.security import hash_password

# Banco de dados de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Fixture: Cria banco de dados de teste"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Fixture: Cliente de teste FastAPI"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db_session):
    """Fixture: Usuário de teste no banco"""
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestAuthRoutes:
    """Suite de testes para rotas de autenticação"""
    
    def test_signup_success(self, client, db_session):
        """Testa cadastro de novo usuário com sucesso"""
        # Arrange
        payload = {
            "email": "newuser@example.com",
            "name": "New User",
            "password": "securepass123"
        }
        
        # Act
        response = client.post("/api/auth/signup", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data  # Senha não deve aparecer
    
    def test_signup_duplicate_email(self, client, sample_user):
        """Testa cadastro com email duplicado"""
        # Arrange
        payload = {
            "email": sample_user.email,  # Email já existe
            "name": "Another User",
            "password": "password123"
        }
        
        # Act
        response = client.post("/api/auth/signup", json=payload)
        
        # Assert
        assert response.status_code == 400
        assert "já cadastrado" in response.json()["detail"].lower()
    
    def test_signup_invalid_email(self, client):
        """Testa cadastro com email inválido"""
        # Arrange
        payload = {
            "email": "invalid-email",
            "name": "Test User",
            "password": "password123"
        }
        
        # Act
        response = client.post("/api/auth/signup", json=payload)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_signup_weak_password(self, client):
        """Testa cadastro com senha fraca"""
        # Arrange
        payload = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "123"  # Senha muito curta
        }
        
        # Act
        response = client.post("/api/auth/signup", json=payload)
        
        # Assert
        assert response.status_code in [400, 422]
    
    def test_login_success(self, client, sample_user):
        """Testa login com credenciais corretas"""
        # Arrange
        payload = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        # Act
        response = client.post("/api/auth/login", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, sample_user):
        """Testa login com senha incorreta"""
        # Arrange
        payload = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        # Act
        response = client.post("/api/auth/login", json=payload)
        
        # Assert
        assert response.status_code == 401
        assert "incorreta" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Testa login com usuário inexistente"""
        # Arrange
        payload = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        # Act
        response = client.post("/api/auth/login", json=payload)
        
        # Assert
        assert response.status_code == 401
    
    def test_login_missing_fields(self, client):
        """Testa login sem email ou senha"""
        # Arrange
        payload = {"email": "test@example.com"}  # Falta password
        
        # Act
        response = client.post("/api/auth/login", json=payload)
        
        # Assert
        assert response.status_code == 422
    
    def test_protected_route_without_token(self, client):
        """Testa acesso a rota protegida sem token"""
        # Act
        response = client.get("/api/history")
        
        # Assert
        assert response.status_code == 401
    
    def test_protected_route_with_valid_token(self, client, sample_user):
        """Testa acesso a rota protegida com token válido"""
        # Arrange - Fazer login para obter token
        login_response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        token = login_response.json()["access_token"]
        
        # Act - Usar token em rota protegida
        response = client.get(
            "/api/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_protected_route_with_invalid_token(self, client):
        """Testa acesso com token inválido"""
        # Arrange
        fake_token = "invalid.token.here"
        
        # Act
        response = client.get(
            "/api/history",
            headers={"Authorization": f"Bearer {fake_token}"}
        )
        
        # Assert
        assert response.status_code == 401
    
    def test_token_contains_user_info(self, client, sample_user):
        """Testa se o token JWT contém informações do usuário"""
        # Arrange
        login_response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        token = login_response.json()["access_token"]
        
        # Act - Decodificar token (simplificado)
        import jwt
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Assert
        assert "sub" in decoded or "email" in decoded or "user_id" in decoded