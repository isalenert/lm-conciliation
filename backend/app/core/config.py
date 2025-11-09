import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Aplicação
    APP_NAME: str = "LM Conciliation"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "lm-conciliation-secret-key-change-in-production-2024")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas
    
    # Banco de dados
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@lm-postgres-prod:5432/lm_conciliation"
    )
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://lm-conciliation-frontend.s3-website-sa-east-1.amazonaws.com",
        "http://54.94.110.71"
    ]
    
    # Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "/tmp/lm-conciliation-uploads"
    ALLOWED_EXTENSIONS: set = {".csv", ".pdf", ".xlsx", ".xls"}
    
    # Conciliação
    DEFAULT_DATE_TOLERANCE: int = 1
    DEFAULT_VALUE_TOLERANCE: float = 0.02
    DEFAULT_SIMILARITY_THRESHOLD: float = 0.7
    
    # Email Configuration (SendGrid)
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "noreply@lmconciliation.com")
    SENDER_NAME: str = os.getenv("SENDER_NAME", "LM Conciliation")
    FRONTEND_URL: str = os.getenv(
        "FRONTEND_URL", 
        "http://lm-conciliation-frontend.s3-website-sa-east-1.amazonaws.com"

    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global das configurações
settings = Settings()
