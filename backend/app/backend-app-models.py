# backend/app/models.py - Modelos de Base de Datos

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from typing import Optional

Base = declarative_base()

# Enums para tipos específicos
class UserRole(enum.Enum):
    ADMIN = "admin"
    JUDGE = "judge"
    LAWYER = "lawyer"
    CLERK = "clerk"
    CITIZEN = "citizen"

class CaseStatus(enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    CLOSED = "closed"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"

class CaseType(enum.Enum):
    CIVIL = "civil"
    CRIMINAL = "criminal"
    ADMINISTRATIVE = "administrative"
    COMMERCIAL = "commercial"
    FAMILY = "family"
    LABOR = "labor"

class Priority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class DocumentType(enum.Enum):
    COMPLAINT = "complaint"      # شكوى
    JUDGMENT = "judgment"        # حكم
    ORDER = "order"             # أمر
    MOTION = "motion"           # مذكرة
    EVIDENCE = "evidence"       # دليل
    CERTIFICATE = "certificate" # شهادة
    OTHER = "other"

class SignatureStatus(enum.Enum):
    PENDING = "pending"
    SIGNED = "signed"
    VERIFIED = "verified"
    INVALID = "invalid"
    EXPIRED = "expired"

# Modelo de Usuario
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Información adicional específica para Marruecos
    national_id = Column(String(50), unique=True, nullable=True)  # CIN marroquí
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    preferred_language = Column(String(5), default="ar")  # ar, fr, es
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    created_cases = relationship("CaseFile", back_populates="creator", foreign_keys="CaseFile.created_by")
    assigned_cases = relationship("CaseFile", back_populates="assignee", foreign_keys="CaseFile.assigned_to")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

# Modelo de Caso Judicial
class CaseFile(Base):
    __tablename__ = "case_files"
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Clasificación
    case_type = Column(Enum(CaseType), nullable=False)
    status = Column(Enum(CaseStatus), default=CaseStatus.DRAFT)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    
    # Información judicial específica para Marruecos
    court_name = Column(String(255), nullable=True)  # اسم المحكمة
    judge_name = Column(String(255), nullable=True)   # اسم القاضي
    court_session_date = Column(DateTime(timezone=True), nullable=True)
    
    # Usuarios relacionados
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadatos JSON para flexibilidad
    metadata = Column(JSON, default=dict)
    
    # Campos de auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    creator = relationship("User", back_populates="created_cases", foreign_keys=[created_by])
    assignee = relationship("User", back_populates="assigned_cases", foreign_keys=[assigned_to])
    documents = relationship("Document", back_populates="case_file")
    case_participants = relationship("CaseParticipant", back_populates="case_file")
    audit_logs = relationship("AuditLog", back_populates="case_file")
    
    def __repr__(self):
        return f"<CaseFile(id={self.id}, case_number='{self.case_number}', status='{self.status}')>"

# Modelo de Documento
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Clasificación del documento
    document_type = Column(Enum(DocumentType), default=DocumentType.OTHER)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    # OCR y contenido
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Integer, nullable=True)  # 0-100
    ocr_language = Column(String(10), nullable=True)
    is_searchable = Column(Boolean, default=False)
    
    # Firma digital
    digital_signature = Column(LargeBinary, nullable=True)
    signature_certificate = Column(LargeBinary, nullable=True)
    signature_timestamp = Column(DateTime(timezone=True), nullable=True)
    signature_status = Column(Enum(SignatureStatus), default=SignatureStatus.PENDING)
    signed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relación con caso
    case_id = Column(Integer, ForeignKey("case_files.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    case_file = relationship("CaseFile", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    signer = relationship("User", foreign_keys=[signed_by])
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', case_id={self.case_id})>"

# Modelo de Participantes en el Caso
class CaseParticipant(Base):
    __tablename__ = "case_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("case_files.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Información del participante (si no es usuario registrado)
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)  # plaintiff, defendant, witness, lawyer, etc.
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    
    # Información específica para Marruecos
    national_id = Column(String(50), nullable=True)
    lawyer_bar_number = Column(String(50), nullable=True)  # رقم المحامي في النقابة
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    case_file = relationship("CaseFile", back_populates="case_participants")
    user = relationship("User")
    
    def __repr__(self):
        return f"<CaseParticipant(id={self.id}, name='{self.name}', role='{self.role}')>"

# Modelo de Log de Auditoría
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Información de la acción
    action = Column(String(100), nullable=False)  # CREATE, UPDATE, DELETE, VIEW, SIGN, etc.
    resource_type = Column(String(50), nullable=False)  # case, document, user, etc.
    resource_id = Column(Integer, nullable=True)
    
    # Usuario que realizó la acción
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)  # Backup si user es eliminado
    user_ip = Column(String(45), nullable=True)  # IPv4 o IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Detalles de la acción
    description = Column(Text, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    # Información del sistema
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    session_id = Column(String(255), nullable=True)
    request_id = Column(String(255), nullable=True)
    
    # Caso relacionado (si aplica)
    case_id = Column(Integer, ForeignKey("case_files.id"), nullable=True)
    
    # Relaciones
    user = relationship("User", back_populates="audit_logs")
    case_file = relationship("CaseFile", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', resource_type='{self.resource_type}')>"

# Modelo para Configuración del Sistema
class SystemConfiguration(Base):
    __tablename__ = "system_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    value_type = Column(String(20), default="string")  # string, int, bool, json
    description = Column(Text, nullable=True)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    updater = relationship("User")
    
    def __repr__(self):
        return f"<SystemConfiguration(key='{self.key}', value='{self.value}')>"

# Modelo para Sesiones de Usuario (Redis backup)
class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Información de la sesión
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Metadatos de sesión
    session_data = Column(JSON, default=dict)
    
    user = relationship("User")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, session_id='{self.session_id}')>"

# Modelo para Notificaciones
class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Contenido de la notificación
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="info")  # info, warning, error, success
    
    # Estado
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    
    # Relación con recursos
    related_resource_type = Column(String(50), nullable=True)  # case, document, etc.
    related_resource_id = Column(Integer, nullable=True)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    recipient = relationship("User")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, recipient_id={self.recipient_id}, title='{self.title}')>"

# Modelo para Templates de Documentos
class DocumentTemplate(Base):
    __tablename__ = "document_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(String(50), nullable=False)  # judgment, order, motion, etc.
    
    # Contenido del template
    content = Column(Text, nullable=False)  # HTML o Markdown
    variables = Column(JSON, default=list)  # Lista de variables disponibles
    
    # Configuración
    is_active = Column(Boolean, default=True)
    language = Column(String(5), default="ar")
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    creator = relationship("User")
    
    def __repr__(self):
        return f"<DocumentTemplate(id={self.id}, name='{self.name}', type='{self.template_type}')>"

# Índices adicionales para optimización
from sqlalchemy import Index

# Índices compuestos para queries comunes
Index('idx_case_status_created', CaseFile.status, CaseFile.created_at)
Index('idx_case_assigned_status', CaseFile.assigned_to, CaseFile.status)
Index('idx_document_case_type', Document.case_id, Document.document_type)
Index('idx_audit_user_timestamp', AuditLog.user_id, AuditLog.timestamp.desc())
Index('idx_audit_resource', AuditLog.resource_type, AuditLog.resource_id)
Index('idx_notification_recipient_read', Notification.recipient_id, Notification.is_read)

# Función helper para crear todas las tablas
def create_tables(engine):
    """Crear todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)

# Función helper para obtener modelo por nombre
def get_model_by_name(model_name: str):
    """Obtener clase de modelo por nombre"""
    models = {
        'user': User,
        'case_file': CaseFile,
        'document': Document,
        'case_participant': CaseParticipant,
        'audit_log': AuditLog,
        'system_configuration': SystemConfiguration,
        'user_session': UserSession,
        'notification': Notification,
        'document_template': DocumentTemplate,
    }
    return models.get(model_name.lower())