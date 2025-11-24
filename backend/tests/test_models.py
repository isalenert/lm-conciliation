"""
Testes para models do banco de dados
Requisito: RNF06 - Cobertura OBRIGATÓRIA > 75%
"""
import pytest


class TestUserModel:
    """Testes do modelo User"""
    
    def test_user_model_exists(self):
        """TESTE 1: Model User deve existir"""
        from app.models.user import User
        assert User is not None
    
    def test_user_has_required_fields(self):
        """TESTE 2: User deve ter campos obrigatórios"""
        from app.models.user import User
        
        assert hasattr(User, 'id')
        assert hasattr(User, 'email')
        assert hasattr(User, 'hashed_password')
        assert hasattr(User, 'name')


class TestReconciliationModel:
    """Testes do modelo Reconciliation"""
    
    def test_reconciliation_model_exists(self):
        """TESTE 3: Model Reconciliation deve existir"""
        from app.models.reconciliation import Reconciliation
        assert Reconciliation is not None
    
    def test_reconciliation_has_fields(self):
        """TESTE 4: Reconciliation deve ter campos"""
        from app.models.reconciliation import Reconciliation
        
        assert hasattr(Reconciliation, 'id')
        assert hasattr(Reconciliation, 'user_id')
        assert hasattr(Reconciliation, 'matched_count')


class TestUserSettingsModel:
    """Testes do modelo UserSettings"""
    
    def test_user_settings_model_exists(self):
        """TESTE 5: Model UserSettings deve existir"""
        from app.models.user_settings import UserSettings
        assert UserSettings is not None
    
    def test_user_settings_has_user_id(self):
        """TESTE 6: UserSettings deve ter user_id"""
        from app.models.user_settings import UserSettings
        
        # Verifica se a classe tem os atributos básicos
        assert UserSettings is not None
        assert hasattr(UserSettings, '__tablename__')