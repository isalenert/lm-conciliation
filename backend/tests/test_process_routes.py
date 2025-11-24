"""
Testes para rotas de settings
Requisito: RNF06 - Cobertura OBRIGATÓRIA > 75%
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.core.database import get_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestSettingsBasic:
    """Testes básicos de settings"""
    
    def test_get_settings_requires_auth(self, client):
        """TESTE 1: Settings requer autenticação"""
        response = client.get("/api/settings/")
        assert response.status_code == 401
    
    def test_update_settings_requires_auth(self, client):
        """TESTE 2: Update settings requer autenticação"""
        response = client.put("/api/settings/", json={})
        assert response.status_code == 401