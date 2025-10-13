# backend/app/main.py - Aplicación Principal FastAPI

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

# Imports locales
try:
    from .config import settings
    from .database import engine, SessionLocal, check_db_health
    from .models import Base
    from .security.rate_limiter import RateLimitMiddleware
    from .monitoring.error_detector import RealTimeErrorDetector
except ImportError as e:
    logging.error(f"Import error: {e}")
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    try:
        # Crear tablas si no existen
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Inicializar detector de errores
        error_detector = RealTimeErrorDetector()
        app.state.error_detector = error_detector
        
        # Iniciar monitoreo en background
        import asyncio
        asyncio.create_task(error_detector.monitor_system_health())
        
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

# CORS configurado para Marruecos
allowed_origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security middleware
allowed_hosts = settings.allowed_hosts.split(",")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Import y registrar routes
try:
    from .routes import auth, cases, documents, search, audit, hsm
    
    # Registrar routers con prefijos específicos
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["🔐 Authentication"])
    app.include_router(cases.router, prefix="/api/v1/cases", tags=["📁 Case Management"])
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["📄 Document Processing"])
    app.include_router(search.router, prefix="/api/v1/search", tags=["🔍 Search & Discovery"])
    app.include_router(audit.router, prefix="/api/v1/audit", tags=["📊 Audit & Compliance"])
    app.include_router(hsm.router, prefix="/api/v1/hsm", tags=["🔒 HSM & Digital Signatures"])
    
    logger.info("All routes registered successfully")
    
except ImportError as e:
    logger.error(f"Error importing routes: {e}")

# Health check endpoint mejorado
@app.get("/health", tags=["🏥 Health"])
async def health_check():
    """
    Health check completo del sistema
    Incluye verificación de todos los componentes críticos
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "system": "Sistema Judicial Digital - Marruecos",
        "components": {}
    }
    
    # Check database
    try:
        if check_db_health():
            health_status["components"]["database"] = "connected"
        else:
            health_status["components"]["database"] = "disconnected"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        import redis
        redis_client = redis.from_url(settings.redis_url)
        redis_client.ping()
        health_status["components"]["cache"] = "connected"
    except Exception as e:
        health_status["components"]["cache"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Elasticsearch
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch([settings.elasticsearch_url])
        if es.ping():
            health_status["components"]["search"] = "connected"
        else:
            health_status["components"]["search"] = "disconnected"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["search"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check HSM
    try:
        from .hsm.hsm_manager_production_ready import get_hsm_manager
        hsm_manager = get_hsm_manager()
        hsm_health = hsm_manager.health_check()
        health_status["components"]["hsm"] = hsm_health.get("status", "unknown")
    except Exception as e:
        health_status["components"]["hsm"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Return appropriate HTTP status
    status_code = 200
    if health_status["status"] == "unhealthy":
        status_code = 503
    elif health_status["status"] == "degraded":
        status_code = 200  # Still functional
    
    return JSONResponse(content=health_status, status_code=status_code)

# Root endpoint con información del sistema
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
            "Escalabilidad Gubernamental"
        ],
        "api_docs": "/docs" if settings.debug else "Disponible en entorno desarrollo",
        "health": "/health",
        "contact": "Sistema listo para deployment gubernamental"
    }

# Endpoint de métricas para monitoreo
@app.get("/metrics", tags=["📊 Metrics"])
async def get_metrics():
    """
    Métricas del sistema para monitoreo
    """
    import psutil
    import time
    
    # Métricas del sistema
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": time.time() - psutil.boot_time()
        },
        "application": {
            "environment": settings.environment,
            "debug": settings.debug,
            "version": "1.0.0"
        }
    }
    
    # Métricas de cache si está disponible
    try:
        import redis
        redis_client = redis.from_url(settings.redis_url)
        info = redis_client.info()
        metrics["cache"] = {
            "used_memory_human": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0)
        }
        
        # Calcular hit rate
        hits = metrics["cache"]["keyspace_hits"]
        misses = metrics["cache"]["keyspace_misses"]
        total = hits + misses
        metrics["cache"]["hit_rate"] = (hits / total * 100) if total > 0 else 0
        
    except Exception:
        metrics["cache"] = {"status": "unavailable"}
    
    return metrics

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Manejador global de excepciones
    """
    logger.error(f"Global exception on {request.url}: {exc}", exc_info=True)
    
    # No exponer detalles en producción
    if settings.debug:
        detail = str(exc)
    else:
        detail = "Error interno del servidor"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": detail,
            "path": str(request.url.path),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Custom 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """
    Manejador personalizado para 404
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint no encontrado",
            "path": str(request.url.path),
            "message": "El recurso solicitado no existe",
            "suggestion": "Consulte /docs para ver endpoints disponibles"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Configuración optimizada para producción
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.environment == "development",
        workers=1 if settings.environment == "development" else 4,
        log_level="info",
        access_log=settings.debug
    )