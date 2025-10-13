# backend/app/config.py - Configuración del Sistema

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Configuración centralizada del Sistema Judicial Digital
    Optimizada para deployment en Marruecos
    """
    
    # Información del sistema
    app_name: str = Field(default="Sistema Judicial Digital - Marruecos", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Base de datos
    database_url: str = Field(
        default="postgresql://justicia:password@localhost:5432/justicia_db",
        env="DATABASE_URL"
    )
    
    # Redis para cache y sessions
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Elasticsearch para búsqueda
    elasticsearch_url: str = Field(
        default="http://localhost:9200", 
        env="ELASTICSEARCH_URL"
    )
    elasticsearch_index: str = Field(default="justicia_cases", env="ELASTICSEARCH_INDEX")
    
    # Seguridad y JWT
    secret_key: str = Field(..., env="SECRET_KEY")  # Requerido
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # OCR Configuration
    tesseract_cmd: Optional[str] = Field(default=None, env="TESSERACT_CMD")
    ocr_languages: str = Field(default="ara+fra+spa", env="OCR_LANGUAGES")
    ocr_timeout: int = Field(default=30, env="OCR_TIMEOUT")
    
    # HSM Configuration
    hsm_type: str = Field(default="software_fallback", env="HSM_TYPE")
    hsm_library_path: Optional[str] = Field(default=None, env="HSM_LIBRARY_PATH")
    hsm_pin: Optional[str] = Field(default=None, env="HSM_PIN")
    hsm_slot_id: int = Field(default=0, env="HSM_SLOT_ID")
    
    # Azure Key Vault (para HSM en la nube)
    azure_key_vault_url: Optional[str] = Field(default=None, env="AZURE_KEY_VAULT_URL")
    azure_client_id: Optional[str] = Field(default=None, env="AZURE_CLIENT_ID")
    azure_client_secret: Optional[str] = Field(default=None, env="AZURE_CLIENT_SECRET")
    azure_tenant_id: Optional[str] = Field(default=None, env="AZURE_TENANT_ID")
    
    # File Storage
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    allowed_file_types: str = Field(
        default="pdf,jpg,jpeg,png,tiff,doc,docx", 
        env="ALLOWED_FILE_TYPES"
    )
    
    # CORS y Security
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080", 
        env="ALLOWED_ORIGINS"
    )
    allowed_hosts: str = Field(
        default="localhost,127.0.0.1,*.justicia.ma", 
        env="ALLOWED_HOSTS"
    )
    
    # Celery Configuration
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    celery_task_serializer: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    celery_accept_content: str = Field(default="json", env="CELERY_ACCEPT_CONTENT")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # Monitoring y Alertas
    enable_monitoring: bool = Field(default=True, env="ENABLE_MONITORING")
    slack_webhook_url: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    alert_email: Optional[str] = Field(default=None, env="ALERT_EMAIL")
    
    # Configuración específica para Marruecos
    morocco_timezone: str = Field(default="Africa/Casablanca", env="MOROCCO_TIMEZONE")
    morocco_currency: str = Field(default="MAD", env="MOROCCO_CURRENCY")
    default_language: str = Field(default="ar", env="DEFAULT_LANGUAGE")  # árabe por defecto
    
    # Compliance y Auditoría
    enable_audit_logging: bool = Field(default=True, env="ENABLE_AUDIT_LOGGING")
    audit_retention_days: int = Field(default=2555, env="AUDIT_RETENTION_DAYS")  # 7 años
    enable_gdpr_compliance: bool = Field(default=True, env="ENABLE_GDPR_COMPLIANCE")
    
    # Performance Settings
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    cache_default_ttl: int = Field(default=3600, env="CACHE_DEFAULT_TTL")  # 1 hora
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        allowed_environments = ['development', 'testing', 'staging', 'production']
        if v not in allowed_environments:
            raise ValueError(f'Environment must be one of: {allowed_environments}')
        return v
    
    @validator('hsm_type')
    def validate_hsm_type(cls, v):
        allowed_types = ['software_fallback', 'pkcs11', 'azure_keyvault']
        if v not in allowed_types:
            raise ValueError(f'HSM type must be one of: {allowed_types}')
        return v
    
    @validator('upload_dir')
    def validate_upload_dir(cls, v):
        # Crear directorio si no existe
        os.makedirs(v, exist_ok=True)
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for alembic"""
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    @property
    def allowed_file_extensions(self) -> list:
        """Get list of allowed file extensions"""
        return [ext.strip().lower() for ext in self.allowed_file_types.split(",")]
    
    @property
    def cors_origins(self) -> list:
        """Get list of allowed CORS origins"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def trusted_hosts(self) -> list:
        """Get list of trusted hosts"""
        return [host.strip() for host in self.allowed_hosts.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton pattern para settings
_settings = None

def get_settings() -> Settings:
    """Get settings instance (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Export settings instance
settings = get_settings()

# Configuraciones específicas por entorno
def get_database_config():
    """Get database configuration optimized for environment"""
    base_config = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "echo": settings.debug,
    }
    
    if settings.is_production:
        base_config.update({
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow,
            "pool_timeout": 30,
        })
    else:
        base_config.update({
            "pool_size": 5,
            "max_overflow": 10,
        })
    
    return base_config

def get_redis_config():
    """Get Redis configuration"""
    return {
        "decode_responses": True,
        "socket_connect_timeout": 5,
        "socket_timeout": 5,
        "retry_on_timeout": True,
        "health_check_interval": 30,
    }

def get_elasticsearch_config():
    """Get Elasticsearch configuration"""
    return {
        "timeout": 30,
        "max_retries": 3,
        "retry_on_timeout": True,
    }

def get_celery_config():
    """Get Celery configuration"""
    return {
        "broker_url": settings.celery_broker_url,
        "result_backend": settings.celery_result_backend,
        "task_serializer": settings.celery_task_serializer,
        "accept_content": [settings.celery_accept_content],
        "result_serializer": "json",
        "timezone": settings.morocco_timezone,
        "enable_utc": True,
        "task_track_started": True,
        "task_time_limit": 300,  # 5 minutos
        "task_soft_time_limit": 240,  # 4 minutos
        "worker_max_tasks_per_child": 1000,
        "worker_max_memory_per_child": 200000,  # 200MB
    }

# Validación de configuración crítica
def validate_critical_config():
    """Validate critical configuration on startup"""
    errors = []
    
    # Check required environment variables
    if not settings.secret_key:
        errors.append("SECRET_KEY is required")
    
    # Check database connection format
    if not settings.database_url.startswith(("postgresql://", "postgresql+psycopg2://", "sqlite://")):
        errors.append("DATABASE_URL must be a valid database connection string")
    
    # Check HSM configuration
    if settings.hsm_type == "pkcs11" and not settings.hsm_library_path:
        errors.append("HSM_LIBRARY_PATH is required for PKCS#11 HSM")
    
    if settings.hsm_type == "azure_keyvault":
        required_azure_vars = [
            settings.azure_key_vault_url,
            settings.azure_client_id,
            settings.azure_client_secret,
            settings.azure_tenant_id
        ]
        if not all(required_azure_vars):
            errors.append("Azure Key Vault configuration is incomplete")
    
    # Check file upload directory
    if not os.path.exists(settings.upload_dir):
        try:
            os.makedirs(settings.upload_dir, exist_ok=True)
        except Exception:
            errors.append(f"Cannot create upload directory: {settings.upload_dir}")
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")

# Configuración específica para Marruecos
MOROCCO_SPECIFIC_CONFIG = {
    "languages": {
        "ar": {"name": "العربية", "rtl": True, "tesseract_code": "ara"},
        "fr": {"name": "Français", "rtl": False, "tesseract_code": "fra"},
        "es": {"name": "Español", "rtl": False, "tesseract_code": "spa"},
    },
    "legal_system": {
        "court_types": ["محكمة_ابتدائية", "cour_d_appel", "tribunal_administratif"],
        "case_types": ["مدني", "جنائي", "إداري", "تجاري"],
        "document_types": ["حكم", "قرار", "أمر", "مذكرة"],
    },
    "compliance": {
        "data_retention_years": 7,
        "audit_requirements": ["user_actions", "document_access", "signature_events"],
        "encryption_standard": "AES-256-GCM",
    }
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "detailed",
            "class": "logging.FileHandler",
            "filename": "justicia_digital.log",
        },
    },
    "root": {
        "level": "INFO" if not settings.debug else "DEBUG",
        "handlers": ["default", "file"],
    },
}