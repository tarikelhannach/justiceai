# backend/app/main.py - Aplicación Principal FastAPI

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

# Setup logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración básica para testing
class BasicSettings:
    def __init__(self):
        self.debug = os.getenv('DEBUG', 'true').lower() == 'true'
        self.environment = os.getenv('ENVIRONMENT', 'testing')
        self.allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8080')
        self.allowed_hosts = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')

settings = BasicSettings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    try:
        logger.info("Sistema Judicial Digital iniciado correctamente")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Sistema Judicial Digital cerrando...")

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema Judicial Digital - Marruecos",
    description="Sistema completo de gestión judicial con HSM, OCR, búsqueda semántica y compliance gubernamental",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# CORS configurado para Marruecos - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["🏥 Health"])
async def health_check():
    """
    Health check completo del sistema
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "system": "Sistema Judicial Digital - Marruecos"
    }

# Root endpoint
@app.get("/", tags=["🏛️ System Info"])
async def root():
    """
    Información principal del sistema
    """
    return {
        "system": "Sistema Judicial Digital",
        "country": "🇲🇦 Reino de Marruecos",
        "version": "1.0.0",
        "description": "Sistema completo de digitalización judicial con compliance gubernamental",
        "features": [
            "Gestión de Casos Judiciales",
            "Procesamiento OCR Multi-idioma (AR/FR/ES)",
            "Búsqueda Semántica Avanzada",
            "Firma Digital HSM",
            "Auditoría y Compliance",
            "Escalabilidad Gubernamental",
            "Autenticación de Dos Factores (2FA)",
            "Dashboard de Administración",
            "Monitoreo en Tiempo Real"
        ],
        "api_docs": "/docs" if settings.debug else "Disponible en entorno desarrollo",
        "health": "/health"
    }

# Endpoint de métricas
@app.get("/metrics", tags=["📊 Metrics"])
async def get_metrics():
    """
    Métricas del sistema para monitoreo
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "application": {
            "environment": settings.environment,
            "debug": settings.debug,
            "version": "1.0.0"
        }
    }

# Include routers
from .routes import auth, cases, documents, users

app.include_router(auth.router, prefix="/api")
app.include_router(cases.router, prefix="/api")
app.include_router(documents.router)
app.include_router(users.router, prefix="/api")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Manejador global de excepciones
    """
    logger.error(f"Global exception on {request.url}: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "Error interno del servidor" if not settings.debug else str(exc),
            "path": str(request.url.path),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=settings.debug
    )
