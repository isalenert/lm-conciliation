"""
Configurações da aplicação
"""
import os
from typing import List, Set
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configuração do Pydantic v2 (substitui a classe Config antiga)
    model_config = {
        "extra": "allow",  # Permite campos extras do .env
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }
    
    # Aplicação
    APP_NAME: str = "LM Conciliation"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Segurança
    SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv(
            "SECRET_KEY", 
            "lm-conciliation-secret-key-change-in-production-2024"
        )
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas
    
    # Banco de dados
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@lm-postgres-prod:5432/lm_conciliation"
        )
    )
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://lm-conciliation-frontend.s3-website-sa-east-1.amazonaws.com",
        "http://54.94.110.71"
    ]
    
    # Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "/tmp/lm-conciliation-uploads"
    ALLOWED_EXTENSIONS: Set[str] = {".csv", ".pdf", ".xlsx", ".xls"}
    
    # Conciliação
    DEFAULT_DATE_TOLERANCE: int = 1
    DEFAULT_VALUE_TOLERANCE: float = 0.02
    DEFAULT_SIMILARITY_THRESHOLD: float = 0.7
    
    # Email Configuration (SendGrid)
    SENDGRID_API_KEY: str = Field(
        default_factory=lambda: os.getenv("SENDGRID_API_KEY", "")
    )
    SENDER_EMAIL: str = Field(
        default_factory=lambda: os.getenv("SENDER_EMAIL", "noreply@lmconciliation.com")
    )
    SENDER_NAME: str = Field(
        default_factory=lambda: os.getenv("SENDER_NAME", "LM Conciliation")
    )
    FRONTEND_URL: str = Field(
        default_factory=lambda: os.getenv(
            "FRONTEND_URL", 
            "http://lm-conciliation-frontend.s3-website-sa-east-1.amazonaws.com"
        )
    )


# Instância global das configurações
settings = Settings()