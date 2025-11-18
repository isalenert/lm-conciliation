"""
Testes para rotas de upload
Cobertura: Upload de CSV e PDF
"""
import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.core.security import hash_password, create_access_token

# Banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_upload.db"
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
def auth_token(db_session):
    """Fixture: Token de autenticação válido"""
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    token = create_access_token({"sub": user.email})
    return token, user


@pytest.fixture
def csv_file():
    """Fixture: Arquivo CSV de teste"""
    content = """Data,Valor,Descrição
2025-01-15,1500.00,Pagamento Fornecedor
2025-01-16,2300.50,Recebimento Cliente"""
    
    return io.BytesIO(content.encode('utf-8'))


@pytest.fixture
def pdf_file():
    """Fixture: Arquivo PDF de teste"""
    from reportlab.pdfgen import canvas
    import io
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, "EXTRATO BANCÁRIO")
    c.drawString(100, 730, "15/01/2025  1.500,00  Pagamento")
    c.save()
    buffer.seek(0)
    
    return buffer


class TestUploadRoutes:
    """Suite de testes para rotas de upload"""
    
    def test_upload_csv_success(self, client, auth_token, csv_file):
        """Testa upload de CSV com sucesso"""
        # Arrange
        token, user = auth_token
        files = {"file": ("test.csv", csv_file, "text/csv")}
        
        # Act
        response = client.post(
            "/api/upload/csv",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data or "columns" in data or "preview" in data
    
    def test_upload_csv_without_auth(self, client, csv_file):
        """Testa upload sem autenticação"""
        # Arrange
        files = {"file": ("test.csv", csv_file, "text/csv")}
        
        # Act
        response = client.post("/api/upload/csv", files=files)
        
        # Assert
        assert response.status_code == 401
    
    def test_upload_invalid_file_type(self, client, auth_token):
        """Testa upload de tipo de arquivo inválido"""
        # Arrange
        token, user = auth_token
        invalid_file = io.BytesIO(b"not a csv or pdf")
        files = {"file": ("test.txt", invalid_file, "text/plain")}
        
        # Act
        response = client.post(
            "/api/upload/csv",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code in [400, 422, 500]
    
    def test_upload_empty_file(self, client, auth_token):
        """Testa upload de arquivo vazio"""
        # Arrange
        token, user = auth_token
        empty_file = io.BytesIO(b"")
        files = {"file": ("empty.csv", empty_file, "text/csv")}
        
        # Act
        response = client.post(
            "/api/upload/csv",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code in [400, 422, 500]
    
    def test_upload_pdf_success(self, client, auth_token, pdf_file):
        """Testa upload de PDF com sucesso"""
        # Arrange
        token, user = auth_token
        files = {"file": ("test.pdf", pdf_file, "application/pdf")}
        
        # Act
        response = client.post(
            "/api/upload/pdf",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data or "text" in data or "transactions" in data
    
    def test_upload_large_file(self, client, auth_token):
        """Testa upload de arquivo grande"""
        # Arrange
        token, user = auth_token
        # Criar CSV grande (simulado)
        large_content = "Data,Valor,Descrição\n" + "\n".join(
            [f"2025-01-{i:02d},{i*100},{i}" for i in range(1, 100)]
        )
        large_file = io.BytesIO(large_content.encode('utf-8'))
        files = {"file": ("large.csv", large_file, "text/csv")}
        
        # Act
        response = client.post(
            "/api/upload/csv",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_upload_csv_with_special_characters(self, client, auth_token):
        """Testa upload de CSV com caracteres especiais"""
        # Arrange
        token, user = auth_token
        content = """Data,Valor,Descrição
2025-01-15,1500.00,Café & Açúcar - Fornecedor José"""
        csv_file = io.BytesIO(content.encode('utf-8'))
        files = {"file": ("special.csv", csv_file, "text/csv")}
        
        # Act
        response = client.post(
            "/api/upload/csv",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_upload_returns_preview(self, client, auth_token, csv_file):
        """Testa se o upload retorna preview dos dados"""
        # Arrange
        token, user = auth_token
        files = {"file": ("test.csv", csv_file, "text/csv")}
        
        # Act
        response = client.post(
            "/api/upload/csv",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        # Verificar se tem informações úteis
        assert any(key in data for key in ["preview", "columns", "rows", "data"])