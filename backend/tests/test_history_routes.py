"""
Testes para rotas de histórico de conciliações
Requisito: RNF06 - Cobertura de testes > 75%
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
from app.core.security import create_access_token


@pytest.fixture
def mock_db():
    """Mock do banco de dados"""
    db = MagicMock(spec=Session)
    return db


@pytest.fixture
def client(mock_db):
    """Cliente de teste com autenticação mockada"""
    def override_get_db():
        yield mock_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()


@pytest.fixture
def auth_token():
    """Token de autenticação válido"""
    return create_access_token(data={"sub": "test@example.com", "user_id": 1})


@pytest.fixture
def auth_headers(auth_token):
    """Headers com autenticação"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestHistoryRoutes:
    """Testes das rotas de histórico"""
    
    def test_list_reconciliations_unauthorized(self, client, mock_db):
        """TESTE 1: Deve rejeitar requisição sem autenticação"""
        response = client.get("/api/history/reconciliations")
        assert response.status_code == 401
    
    def test_get_statistics_requires_auth(self, client, mock_db):
        """TESTE 2: Deve exigir autenticação para estatísticas"""
        response = client.get("/api/history/statistics")
        assert response.status_code == 401
    
    def test_get_reconciliation_not_found(self, client, auth_headers, mock_db):
        """TESTE 3: Deve retornar 404 para conciliação inexistente"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        response = client.get("/api/history/reconciliations/999", headers=auth_headers)
        assert response.status_code == 404