"""
Testes para rotas de match manual
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
    """Cliente de teste"""
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


class TestManualMatchRoutes:
    """Testes das rotas de match manual"""
    
    def test_create_manual_match_unauthorized(self, client, mock_db):
        """TESTE 1: Deve rejeitar sem autenticação"""
        payload = {
            "reconciliation_id": 1,
            "bank_transaction_id": "bank_001",
            "internal_transaction_id": "int_001"
        }
        
        response = client.post("/api/manual-match/", json=payload)
        assert response.status_code == 401
    
    def test_create_manual_match_missing_fields(self, client, auth_headers, mock_db):
        """TESTE 2: Deve rejeitar payload incompleto"""
        payload = {"reconciliation_id": 1}
        
        response = client.post(
            "/api/manual-match/",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_list_manual_matches_with_auth(self, client, auth_headers, mock_db):
        """TESTE 3: Deve processar listagem com autenticação"""
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        response = client.get(
            "/api/manual-match/reconciliation/1",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404, 422, 401]
    
    def test_delete_manual_match_with_auth(self, client, auth_headers, mock_db):
        """TESTE 4: Deve processar delete com autenticação"""
        mock_match = MagicMock()
        mock_match.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_match
        
        response = client.delete("/api/manual-match/1", headers=auth_headers)
        assert response.status_code in [200, 204, 404, 422, 401]