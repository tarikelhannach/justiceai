# backend/app/config_production.py - Configuración de Producción

import os
from typing import List, Optional
from pydantic import BaseSettings, Field, validator
import logging

logger = logging.getLogger(__name__)

class ProductionSettings(BaseSettings):
    """Configuración optimizada para producción en Marruecos"""
    
    # Información del sistema
    app_name: str = Field(default="Sistema Judicial Digital - Marruecos", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="production", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Base de datos PostgreSQL
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    database_pool_recycle: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")
    
    # Redis
    redis_url: str = Field(..., env="REDIS_URL")
    redis_max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    redis_socket_timeout: int = Field(default=5, env="REDIS_SOCKET_TIMEOUT")
    redis_socket_connect_timeout: int = Field(default=5, env="REDIS_SOCKET_CONNECT_TIMEOUT")
    
    # Elasticsearch
    elasticsearch_url: str = Field(..., env="ELASTICSEARCH_URL")
    elasticsearch_username: Optional[str] = Field(default=None, env="ELASTICSEARCH_USERNAME")
    elasticsearch_password: Optional[str] = Field(default=None, env="ELASTICSEARCH_PASSWORD")
    elasticsearch_verify_certs: bool = Field(default=True, env="ELASTICSEARCH_VERIFY_CERTS")
    elasticsearch_ca_certs: Optional[str] = Field(default=None, env="ELASTICSEARCH_CA_CERTS")
    
    # Seguridad
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["https://justicia.ma", "https://www.justicia.ma"],
        env="ALLOWED_ORIGINS"
    )
    allowed_hosts: List[str] = Field(
        default=["justicia.ma", "www.justicia.ma", "api.justicia.ma"],
        env="ALLOWED_HOSTS"
    )
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    rate_limit_burst: int = Field(default=10, env="RATE_LIMIT_BURST")
    
    # Configuración específica para Marruecos
    morocco_timezone: str = Field(default="Africa/Casablanca", env="MOROCCO_TIMEZONE")
    default_language: str = Field(default="ar", env="DEFAULT_LANGUAGE")
    supported_languages: List[str] = Field(
        default=["ar", "fr", "es"],
        env="SUPPORTED_LANGUAGES"
    )
    
    # OCR
    ocr_languages: str = Field(default="ara+fra+spa", env="OCR_LANGUAGES")
    ocr_engine: str = Field(default="tesseract", env="OCR_ENGINE")
    ocr_psm: int = Field(default=6, env="OCR_PSM")
    ocr_oem: int = Field(default=3, env="OCR_OEM")
    
    # HSM
    hsm_type: str = Field(default="software_fallback", env="HSM_TYPE")
    hsm_pkcs11_library: Optional[str] = Field(default=None, env="HSM_PKCS11_LIBRARY")
    hsm_slot_id: Optional[int] = Field(default=None, env="HSM_SLOT_ID")
    hsm_pin: Optional[str] = Field(default=None, env="HSM_PIN")
    hsm_azure_vault_url: Optional[str] = Field(default=None, env="HSM_AZURE_VAULT_URL")
    hsm_azure_client_id: Optional[str] = Field(default=None, env="HSM_AZURE_CLIENT_ID")
    hsm_azure_client_secret: Optional[str] = Field(default=None, env="HSM_AZURE_CLIENT_SECRET")
    hsm_azure_tenant_id: Optional[str] = Field(default=None, env="HSM_AZURE_TENANT_ID")
    
    # File storage
    upload_path: str = Field(default="/app/uploads", env="UPLOAD_PATH")
    max_file_size: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    allowed_file_types: List[str] = Field(
        default=["pdf", "doc", "docx", "jpg", "jpeg", "png", "tiff"],
        env="ALLOWED_FILE_TYPES"
    )
    
    # Celery
    celery_broker_url: str = Field(..., env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., env="CELERY_RESULT_BACKEND")
    celery_task_serializer: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    celery_result_serializer: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    celery_accept_content: List[str] = Field(default=["json"], env="CELERY_ACCEPT_CONTENT")
    celery_timezone: str = Field(default="Africa/Casablanca", env="CELERY_TIMEZONE")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    enable_health_checks: bool = Field(default=True, env="ENABLE_HEALTH_CHECKS")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Auditoría
    enable_audit_logging: bool = Field(default=True, env="ENABLE_AUDIT_LOGGING")
    audit_log_level: str = Field(default="INFO", env="AUDIT_LOG_LEVEL")
    audit_retention_days: int = Field(default=2555, env="AUDIT_RETENTION_DAYS")  # 7 años
    
    # Notificaciones
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_tls: bool = Field(default=True, env="SMTP_TLS")
    smtp_ssl: bool = Field(default=False, env="SMTP_SSL")
    
    # SMS
    sms_provider: Optional[str] = Field(default=None, env="SMS_PROVIDER")
    sms_api_key: Optional[str] = Field(default=None, env="SMS_API_KEY")
    sms_api_secret: Optional[str] = Field(default=None, env="SMS_API_SECRET")
    sms_from_number: Optional[str] = Field(default=None, env="SMS_FROM_NUMBER")
    
    # Backup
    backup_enabled: bool = Field(default=True, env="BACKUP_ENABLED")
    backup_schedule: str = Field(default="0 2 * * *", env="BACKUP_SCHEDULE")  # Daily at 2 AM
    backup_retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    backup_s3_bucket: Optional[str] = Field(default=None, env="BACKUP_S3_BUCKET")
    backup_s3_region: Optional[str] = Field(default=None, env="BACKUP_S3_REGION")
    
    # Compliance
    gdpr_enabled: bool = Field(default=True, env="GDPR_ENABLED")
    data_retention_years: int = Field(default=7, env="DATA_RETENTION_YEARS")
    encryption_at_rest: bool = Field(default=True, env="ENCRYPTION_AT_REST")
    encryption_key: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    
    @validator('allowed_origins', pre=True)
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('allowed_hosts', pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v
    
    @validator('supported_languages', pre=True)
    def parse_supported_languages(cls, v):
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(',')]
        return v
    
    @validator('allowed_file_types', pre=True)
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(',')]
        return v
    
    @validator('celery_accept_content', pre=True)
    def parse_celery_accept_content(cls, v):
        if isinstance(v, str):
            return [content.strip() for content in v.split(',')]
        return v
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"
    
    @property
    def database_url_sync(self) -> str:
        """URL de base de datos síncrona para SQLAlchemy"""
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    @property
    def trusted_hosts(self) -> List[str]:
        """Hosts confiables para TrustedHostMiddleware"""
        return self.allowed_hosts
    
    @property
    def cors_origins(self) -> List[str]:
        """Orígenes CORS"""
        return self.allowed_origins
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Singleton para producción
production_settings = ProductionSettings()

# Configuración específica para Marruecos
MOROCCO_SPECIFIC_CONFIG = {
    "country": "Morocco",
    "country_code": "MA",
    "timezone": "Africa/Casablanca",
    "languages": {
        "primary": "ar",
        "secondary": "fr",
        "tertiary": "es"
    },
    "legal_system": {
        "type": "Civil Law",
        "based_on": "French Civil Code",
        "sharia_applicable": True
    },
    "government_integration": {
        "ministry_of_justice": "https://justice.gov.ma",
        "national_id_system": "CIN",
        "court_system": "Hierarchical"
    },
    "compliance": {
        "data_protection_law": "Morocco Data Protection Law",
        "digital_signature_law": "Morocco Digital Signature Law",
        "audit_requirements": "Annual Government Audit"
    },
    "infrastructure": {
        "cloud_provider": "Morocco Cloud",
        "data_sovereignty": True,
        "backup_location": "Morocco"
    }
}
