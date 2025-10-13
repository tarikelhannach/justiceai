# backend/app/routes/schemas.py - Esquemas Pydantic para API

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from ..models import UserRole, CaseStatus, CaseType, Priority, DocumentType, SignatureStatus

# ========================================
# SCHEMAS DE USUARIO
# ========================================

class UserBase(BaseModel):
    email: str = Field(..., description="Email del usuario")
    name: str = Field(..., min_length=2, max_length=255, description="Nombre completo")
    national_id: Optional[str] = Field(None, description="CIN marroquí")
    phone: Optional[str] = Field(None, description="Teléfono")
    address: Optional[str] = Field(None, description="Dirección")
    city: Optional[str] = Field(None, description="Ciudad")
    preferred_language: str = Field("ar", description="Idioma preferido")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Contraseña")
    role: UserRole = Field(UserRole.CITIZEN, description="Rol del usuario")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None)
    address: Optional[str] = Field(None)
    city: Optional[str] = Field(None)
    preferred_language: Optional[str] = Field(None)

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ========================================
# SCHEMAS DE AUTENTICACIÓN
# ========================================

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class TokenRefresh(BaseModel):
    refresh_token: str

class UserLogin(BaseModel):
    email: str = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña")

class PasswordChange(BaseModel):
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class PasswordReset(BaseModel):
    email: str = Field(..., description="Email del usuario")

# ========================================
# SCHEMAS DE CASOS
# ========================================

class CaseBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500, description="Título del caso")
    description: Optional[str] = Field(None, description="Descripción del caso")
    case_type: CaseType = Field(..., description="Tipo de caso")
    priority: Priority = Field(Priority.MEDIUM, description="Prioridad del caso")
    court_name: Optional[str] = Field(None, description="Nombre de la corte")
    judge_name: Optional[str] = Field(None, description="Nombre del juez")
    court_session_date: Optional[datetime] = Field(None, description="Fecha de sesión")
    assigned_to: Optional[int] = Field(None, description="ID del usuario asignado")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = Field(None)
    case_type: Optional[CaseType] = Field(None)
    priority: Optional[Priority] = Field(None)
    status: Optional[CaseStatus] = Field(None)
    court_name: Optional[str] = Field(None)
    judge_name: Optional[str] = Field(None)
    court_session_date: Optional[datetime] = Field(None)
    assigned_to: Optional[int] = Field(None)
    metadata: Optional[Dict[str, Any]] = Field(None)

class CaseResponse(CaseBase):
    id: int
    case_number: str
    status: CaseStatus
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CaseListResponse(BaseModel):
    cases: List[CaseResponse]
    total: int
    page: int
    size: int

# ========================================
# SCHEMAS DE PARTICIPANTES
# ========================================

class CaseParticipantBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Nombre del participante")
    role: str = Field(..., description="Rol del participante")
    contact_email: Optional[str] = Field(None, description="Email de contacto")
    contact_phone: Optional[str] = Field(None, description="Teléfono de contacto")
    address: Optional[str] = Field(None, description="Dirección")
    national_id: Optional[str] = Field(None, description="CIN marroquí")
    lawyer_bar_number: Optional[str] = Field(None, description="Número de colegiación")

class CaseParticipantCreate(CaseParticipantBase):
    case_id: int = Field(..., description="ID del caso")

class CaseParticipantResponse(CaseParticipantBase):
    id: int
    case_id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ========================================
# SCHEMAS DE DOCUMENTOS
# ========================================

class DocumentBase(BaseModel):
    title: Optional[str] = Field(None, description="Título del documento")
    description: Optional[str] = Field(None, description="Descripción del documento")
    document_type: DocumentType = Field(DocumentType.OTHER, description="Tipo de documento")

class DocumentCreate(DocumentBase):
    case_id: int = Field(..., description="ID del caso")

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    document_type: Optional[DocumentType] = Field(None)

class DocumentResponse(DocumentBase):
    id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[int] = None
    ocr_language: Optional[str] = None
    is_searchable: bool
    signature_status: SignatureStatus
    case_id: int
    uploaded_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ========================================
# SCHEMAS DE BÚSQUEDA
# ========================================

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Consulta de búsqueda")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros adicionales")
    page: int = Field(1, ge=1, description="Página")
    size: int = Field(20, ge=1, le=100, description="Tamaño de página")
    language: Optional[str] = Field("ar", description="Idioma de búsqueda")

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    page: int
    size: int
    query: str
    took: float

# ========================================
# SCHEMAS DE AUDITORÍA
# ========================================

class AuditLogResponse(BaseModel):
    id: int
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    user_ip: Optional[str] = None
    description: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    timestamp: datetime
    case_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# ========================================
# SCHEMAS DE HSM
# ========================================

class SignatureRequest(BaseModel):
    document_id: int = Field(..., description="ID del documento")
    certificate_id: str = Field(..., description="ID del certificado")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos de la firma")

class SignatureResponse(BaseModel):
    signature_id: str
    signature: str  # Base64 encoded
    certificate: str  # Base64 encoded
    timestamp: datetime
    status: str
    metadata: Optional[Dict[str, Any]] = None

class CertificateInfo(BaseModel):
    certificate_id: str
    subject: str
    issuer: str
    valid_from: datetime
    valid_to: datetime
    status: str
    key_usage: List[str]

# ========================================
# SCHEMAS DE NOTIFICACIONES
# ========================================

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    is_sent: bool
    related_resource_type: Optional[str] = None
    related_resource_id: Optional[int] = None
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ========================================
# SCHEMAS DE ESTADÍSTICAS
# ========================================

class SystemStats(BaseModel):
    total_cases: int
    total_documents: int
    total_users: int
    active_cases: int
    pending_documents: int
    signatures_today: int
    system_health: str
    last_updated: datetime

class CaseStats(BaseModel):
    cases_by_type: Dict[str, int]
    cases_by_status: Dict[str, int]
    cases_by_priority: Dict[str, int]
    cases_by_month: Dict[str, int]
    average_processing_time: float
    total_documents: int
    signed_documents: int
