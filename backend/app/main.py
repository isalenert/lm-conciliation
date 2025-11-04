"""
Aplicação principal FastAPI
Sistema de Conciliação Bancária - LM Conciliation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Importar rotas
from app.api.routes import upload, reconcile, auth, history

# Criar aplicação
app = FastAPI(
    title="LM Conciliation API",
    description="Sistema de Conciliação Bancária Automatizado",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:80",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(reconcile.router, prefix="/api", tags=["Conciliação"])
app.include_router(history.router, prefix="/api", tags=["Histórico"])


# Endpoint raiz
@app.get("/")
async def root():
    """Endpoint raiz - Health check básico"""
    return {
        "message": "LM Conciliation API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check detalhado"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "lm-conciliation-backend"
    }


# Exception handler global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler para exceções não tratadas"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "detail": str(exc)
        }
    )


# Executar servidor (para desenvolvimento)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
