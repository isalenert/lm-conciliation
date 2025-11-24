"""
Testes para o endpoint /upload
Cobertura: Validações, Upload, Listagem e Segurança

"""
import pytest
import os
import tempfile
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock, mock_open
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.core.deps import get_current_user, get_db

client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_current_user():
    """Simula usuário autenticado"""
    user = Mock()
    user.id = 1
    user.email = "test@example.com"
    return user


@pytest.fixture
def mock_db():
    """Mock da sessão de banco de dados"""
    return MagicMock()


@pytest.fixture
def override_get_current_user(mock_current_user):
    """Override da dependência de autenticação"""
    def _get_current_user_override():
        return mock_current_user
    
    app.dependency_overrides[get_current_user] = _get_current_user_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def override_get_db(mock_db):
    """Override da dependência de banco de dados"""
    def _get_db_override():
        yield mock_db
    
    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def valid_csv_file():
    """Arquivo CSV válido"""
    csv_content = b"date,amount,description\n2024-01-15,100.00,Payment A"
    return ("transactions.csv", BytesIO(csv_content), "text/csv")


@pytest.fixture
def valid_pdf_file():
    """Arquivo PDF válido (simplificado)"""
    pdf_content = b"%PDF-1.4\n%fake pdf content"
    return ("statement.pdf", BytesIO(pdf_content), "application/pdf")


@pytest.fixture
def mock_upload_dir():
    """Mock do diretório de upload"""
    with patch("app.api.routes.upload.UPLOAD_DIR", "/tmp/test-uploads"):
        yield "/tmp/test-uploads"


# ============================================================================
# SUITE 1: VALIDAÇÃO DE ARQUIVOS
# ============================================================================

class TestUploadValidation:
    """Testes de validação de arquivos"""
    
    def test_upload_csv_files_success(
        self, override_get_current_user, override_get_db,
        valid_csv_file, mock_upload_dir
    ):
        """
        TESTE 1: Deve aceitar upload de 2 arquivos CSV
        Requisito: RF01 - Upload de arquivos
        """
        # Arrange
        csv_file_1 = valid_csv_file
        csv_file_2 = ("internal.csv", BytesIO(b"date,value\n2024-01-15,100"), "text/csv")
        
        with patch("app.api.routes.upload.os.makedirs"), \
             patch("builtins.open", mock_open()), \
             patch("app.api.routes.upload.shutil.copyfileobj"):
            
            # Act
            response = client.post(
                "/api/upload",
                files={
                    "bank_file": csv_file_1,
                    "internal_file": csv_file_2
                }
            )
            
            # Assert
            assert response.status_code == 200
            result = response.json()
            assert "message" in result
            assert "bank_file" in result
            assert "internal_file" in result
            assert result["bank_file"].endswith(".csv")
            assert result["internal_file"].endswith(".csv")
    
    def test_upload_pdf_files_success(
        self, override_get_current_user, override_get_db,
        valid_pdf_file, mock_upload_dir
    ):
        """
        TESTE 2: Deve aceitar upload de 2 arquivos PDF
        Requisito: RF01 - Upload de arquivos
        """
        # Arrange
        pdf_file_1 = valid_pdf_file
        pdf_file_2 = ("internal.pdf", BytesIO(b"%PDF-1.4\ncontent"), "application/pdf")
        
        with patch("app.api.routes.upload.os.makedirs"), \
             patch("builtins.open", mock_open()), \
             patch("app.api.routes.upload.shutil.copyfileobj"):
            
            # Act
            response = client.post(
                "/api/upload",
                files={
                    "bank_file": pdf_file_1,
                    "internal_file": pdf_file_2
                }
            )
            
            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["bank_file"].endswith(".pdf")
            assert result["internal_file"].endswith(".pdf")
    
    def test_upload_mixed_formats_success(
        self, override_get_current_user, override_get_db,
        valid_csv_file, valid_pdf_file, mock_upload_dir
    ):
        """
        TESTE 3: Deve aceitar upload de CSV + PDF
        Requisito: RF01 - Suportar múltiplos formatos
        """
        # Arrange
        with patch("app.api.routes.upload.os.makedirs"), \
             patch("builtins.open", mock_open()), \
             patch("app.api.routes.upload.shutil.copyfileobj"):
            
            # Act
            response = client.post(
                "/api/upload",
                files={
                    "bank_file": valid_csv_file,
                    "internal_file": valid_pdf_file
                }
            )
            
            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["bank_file"].endswith(".csv")
            assert result["internal_file"].endswith(".pdf")
    
    def test_upload_reject_invalid_extension(
        self, override_get_current_user, override_get_db
    ):
        """
        TESTE 4: Deve rejeitar arquivo com extensão inválida
        Requisito: RNF02 - Segurança (validação de tipos)
        """
        # Arrange
        invalid_file = ("malware.exe", BytesIO(b"fake exe"), "application/x-msdownload")
        valid_file = ("valid.csv", BytesIO(b"data"), "text/csv")
        
        # Act
        response = client.post(
            "/api/upload",
            files={
                "bank_file": invalid_file,
                "internal_file": valid_file
            }
        )
        
        # Assert
        assert response.status_code == 400
        assert "não suportado" in response.json()["detail"].lower()
    
    def test_upload_reject_zip_file(
        self, override_get_current_user, override_get_db
    ):
        """
        TESTE 5: Deve rejeitar arquivo ZIP
        Requisito: RNF02 - Segurança
        """
        # Arrange
        zip_file = ("archive.zip", BytesIO(b"PK\x03\x04"), "application/zip")
        valid_file = ("valid.csv", BytesIO(b"data"), "text/csv")
        
        # Act
        response = client.post(
            "/api/upload",
            files={
                "bank_file": zip_file,
                "internal_file": valid_file
            }
        )
        
        # Assert
        assert response.status_code == 400
    
    def test_upload_case_insensitive_extension(
        self, override_get_current_user, override_get_db, mock_upload_dir
    ):
        """
        TESTE 6: Deve aceitar extensões em maiúscula (.CSV, .PDF)
        Requisito: RNF03 - Usabilidade
        """
        # Arrange
        csv_uppercase = ("file.CSV", BytesIO(b"data"), "text/csv")
        pdf_uppercase = ("file.PDF", BytesIO(b"%PDF"), "application/pdf")
        
        with patch("app.api.routes.upload.os.makedirs"), \
             patch("builtins.open", mock_open()), \
             patch("app.api.routes.upload.shutil.copyfileobj"):
            
            # Act
            response = client.post(
                "/api/upload",
                files={
                    "bank_file": csv_uppercase,
                    "internal_file": pdf_uppercase
                }
            )
            
            # Assert
            assert response.status_code == 200


# ============================================================================
# SUITE 2: AUTENTICAÇÃO
# ============================================================================

class TestUploadAuthentication:
    """Testes de autenticação"""
    
    def test_upload_without_authentication(self, valid_csv_file):
        """
        TESTE 7: Deve rejeitar upload sem token
        Requisito: RNF02 - Segurança
        """
        # Act
        response = client.post(
            "/api/upload",
            files={
                "bank_file": valid_csv_file,
                "internal_file": valid_csv_file
            }
        )
        
        # Assert
        assert response.status_code == 401
    
    def test_upload_with_invalid_token(self, valid_csv_file):
        """
        TESTE 8: Deve rejeitar token inválido
        Requisito: RNF02 - Segurança
        """
        # Arrange
        headers = {"Authorization": "Bearer invalid-token-123"}
        
        # Act
        response = client.post(
            "/api/upload",
            files={
                "bank_file": valid_csv_file,
                "internal_file": valid_csv_file
            },
            headers=headers
        )
        
        # Assert
        assert response.status_code == 401


# ============================================================================
# SUITE 3: ARMAZENAMENTO E NOMEAÇÃO
# ============================================================================

class TestUploadStorage:
    """Testes de armazenamento de arquivos"""
    
    def test_upload_creates_unique_filenames(
        self, override_get_current_user, override_get_db,
        mock_current_user, valid_csv_file, mock_upload_dir
    ):
        """
        TESTE 9: Deve criar nomes únicos com user_id e timestamp
        Requisito: RNF02 - Isolamento de dados por usuário
        """
        # Arrange
        mock_current_user.id = 42
        
        with patch("app.api.routes.upload.os.makedirs"), \
             patch("builtins.open", mock_open()), \
             patch("app.api.routes.upload.shutil.copyfileobj"), \
             patch("app.api.routes.upload.datetime") as mock_datetime:
            
            mock_datetime.now.return_value.strftime.return_value = "20250115_143000"
            
            # Act
            response = client.post(
                "/api/upload",
                files={
                    "bank_file": valid_csv_file,
                    "internal_file": valid_csv_file
                }
            )
            
            # Assert
            assert response.status_code == 200
            result = response.json()
            assert "bank_42_20250115_143000" in result["bank_file"]
            assert "internal_42_20250115_143000" in result["internal_file"]
    
    def test_upload_saves_to_correct_directory(
        self, override_get_current_user, override_get_db,
        valid_csv_file, mock_upload_dir
    ):
        """
        TESTE 10: Deve salvar arquivos no diretório correto
        Requisito: RNF04 - Organização de arquivos
        """
        # Arrange
        with patch("app.api.routes.upload.os.makedirs") as mock_makedirs, \
             patch("builtins.open", mock_open()), \
             patch("app.api.routes.upload.shutil.copyfileobj"):
            
            # Act
            response = client.post(
                "/api/upload",
                files={
                    "bank_file": valid_csv_file,
                    "internal_file": valid_csv_file
                }
            )
            
            # Assert
            assert response.status_code == 200
            result = response.json()
            assert mock_upload_dir in result["bank_path"]
            assert mock_upload_dir in result["internal_path"]
    
    def test_upload_directory_path_included_in_response(
        self, override_get_current_user, override_get_db,
        valid_csv_file, mock_upload_dir
    ):
        """
        TESTE 11: Deve incluir paths completos na resposta
        Requisito: RNF04 - Completude da API
        """
        # Arrange
        with patch("app.api.routes.upload.os.makedirs"), \
             patch("builtins.open", mock_open()), \
             patch("app.api.routes.upload.shutil.copyfileobj"):
            
            # Act
            response = client.post(
                "/api/upload",
                files={
                    "bank_file": valid_csv_file,
                    "internal_file": valid_csv_file
                }
            )
            
            # Assert
            assert response.status_code == 200
            result = response.json()
            assert "bank_path" in result
            assert "internal_path" in result
            assert os.path.isabs(result["bank_path"])  # Path absoluto
            assert os.path.isabs(result["internal_path"])


# ============================================================================
# SUITE 4: LISTAGEM DE ARQUIVOS
# ============================================================================

class TestListUploads:
    """Testes do endpoint GET /uploads"""
    
    def test_list_uploads_returns_user_files_only(
        self, override_get_current_user, override_get_db, mock_current_user
    ):
        """
        TESTE 12: Deve listar apenas arquivos do usuário autenticado
        Requisito: RNF02 - Isolamento de dados
        """
        # Arrange
        mock_current_user.id = 1
        
        mock_files = [
            "bank_1_20250115_143000.csv",
            "internal_1_20250115_143000.csv",
            "bank_2_20250115_143000.csv",  # Outro usuário
            "internal_2_20250115_143000.csv"  # Outro usuário
        ]
        
        with patch("app.api.routes.upload.os.listdir", return_value=mock_files):
            # Act
            response = client.get("/api/uploads")
            
            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["count"] == 2
            assert all("_1_" in f for f in result["files"])
    
    def test_list_uploads_empty_directory(
        self, override_get_current_user, override_get_db
    ):
        """
        TESTE 13: Deve retornar lista vazia quando não há arquivos
        Requisito: RNF06 - Casos extremos
        """
        # Arrange
        with patch("app.api.routes.upload.os.listdir", return_value=[]):
            # Act
            response = client.get("/api/uploads")
            
            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["count"] == 0
            assert result["files"] == []
    
    def test_list_uploads_requires_authentication(self):
        """
        TESTE 14: Deve rejeitar listagem sem autenticação
        Requisito: RNF02 - Segurança
        """
        # Act
        response = client.get("/api/uploads")
        
        # Assert
        assert response.status_code == 401
    
    def test_list_uploads_filters_by_user_id(
        self, override_get_current_user, override_get_db, mock_current_user
    ):
        """
        TESTE 15: Deve filtrar arquivos pelo user_id
        Requisito: RNF02 - Isolamento de dados
        """
        # Arrange
        mock_current_user.id = 42
        
        mock_files = [
            "bank_42_20250115_143000.csv",
            "internal_42_20250115_143000.pdf",
            "bank_1_20250115_143000.csv",
            "random_file.txt"
        ]
        
        with patch("app.api.routes.upload.os.listdir", return_value=mock_files):
            # Act
            response = client.get("/api/uploads")
            
            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["count"] == 2
            assert all("_42_" in f for f in result["files"])


# ============================================================================
# SUITE 5: VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS
# ============================================================================

class TestUploadRequiredFields:
    """Testes de campos obrigatórios"""
    
    def test_upload_missing_bank_file(
        self, override_get_current_user, override_get_db, valid_csv_file
    ):
        """
        TESTE 16: Deve rejeitar upload sem bank_file
        Requisito: RNF06 - Validação de entrada
        """
        # Act
        response = client.post(
            "/api/upload",
            files={
                "internal_file": valid_csv_file
            }
        )
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_upload_missing_internal_file(
        self, override_get_current_user, override_get_db, valid_csv_file
    ):
        """
        TESTE 17: Deve rejeitar upload sem internal_file
        Requisito: RNF06 - Validação de entrada
        """
        # Act
        response = client.post(
            "/api/upload",
            files={
                "bank_file": valid_csv_file
            }
        )
        
        # Assert
        assert response.status_code == 422


# ============================================================================
# SUITE 6: CASOS ESPECIAIS
# ============================================================================

class TestUploadEdgeCases:
    """Testes de casos especiais"""
    
    def test_upload_file_with_special_characters(
        self, override_get_current_user, override_get_db, mock_upload_dir
    ):
        """
        TESTE 18: Deve lidar com nomes de arquivo com caracteres especiais
        Requisito: RNF04 - Compatibilidade
        """
        # Arrange
        special_file = ("relatório_2024.csv", BytesIO(b"data"), "text/csv")
        
        with patch("app.api.routes.upload.os.makedirs"), \
             patch("builtins.open", mock_open()), \
             patch("app.api.routes.upload.shutil.copyfileobj"):
            
            # Act
            response = client.post(
                "/api/upload",
                files={
                    "bank_file": special_file,
                    "internal_file": special_file
                }
            )
            
            # Assert
            assert response.status_code == 200
    
    def test_upload_returns_complete_response(
        self, override_get_current_user, override_get_db,
        valid_csv_file, mock_upload_dir
    ):
        """
        TESTE 19: Deve retornar resposta completa com todos os campos
        Requisito: RNF04 - Completude da API
        """
        # Arrange
        with patch("app.api.routes.upload.os.makedirs"), \
             patch("builtins.open", mock_open()), \
             patch("app.api.routes.upload.shutil.copyfileobj"):
            
            # Act
            response = client.post(
                "/api/upload",
                files={
                    "bank_file": valid_csv_file,
                    "internal_file": valid_csv_file
                }
            )
            
            # Assert
            assert response.status_code == 200
            result = response.json()
            
            # Verificar todos os campos esperados
            assert "message" in result
            assert "bank_file" in result
            assert "internal_file" in result
            assert "bank_path" in result
            assert "internal_path" in result
            
            # Verificar tipos
            assert isinstance(result["message"], str)
            assert isinstance(result["bank_file"], str)
            assert isinstance(result["internal_file"], str)
    
    def test_upload_preserves_file_extension(
        self, override_get_current_user, override_get_db, mock_upload_dir
    ):
        """
        TESTE 20: Deve preservar a extensão original do arquivo
        Requisito: RNF04 - Integridade de dados
        """
        # Arrange
        csv_file = ("data.csv", BytesIO(b"data"), "text/csv")
        pdf_file = ("report.pdf", BytesIO(b"%PDF"), "application/pdf")
        
        with patch("app.api.routes.upload.os.makedirs"), \
             patch("builtins.open", mock_open()), \
             patch("app.api.routes.upload.shutil.copyfileobj"):
            
            # Act
            response = client.post(
                "/api/upload",
                files={
                    "bank_file": csv_file,
                    "internal_file": pdf_file
                }
            )
            
            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["bank_file"].endswith(".csv")
            assert result["internal_file"].endswith(".pdf")