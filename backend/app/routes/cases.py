# backend/app/routes/cases.py - Gestión de Casos Judiciales

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..database import get_db
from ..models import CaseFile, CaseStatus, CaseType, Priority, User, AuditLog
from ..auth.auth import get_current_user
from ..security.input_validator import ComprehensiveInputValidator
from .schemas import (
    CaseCreate, CaseUpdate, CaseResponse, CaseListResponse,
    CaseParticipantCreate, CaseParticipantResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_data: CaseCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo caso judicial"""
    try:
        # Validación de entrada
        ComprehensiveInputValidator.rate_limit_check(
            request.client.host, 
            "create_case"
        )
        
        # Generar número de caso único
        case_number = f"CAS-{datetime.now().strftime('%Y%m%d')}-{db.query(CaseFile).count() + 1:04d}"
        
        # Crear caso
        db_case = CaseFile(
            case_number=case_number,
            title=ComprehensiveInputValidator.sanitize_sql_input(case_data.title),
            description=ComprehensiveInputValidator.sanitize_sql_input(case_data.description),
            case_type=case_data.case_type,
            priority=case_data.priority,
            court_name=ComprehensiveInputValidator.sanitize_sql_input(case_data.court_name),
            judge_name=ComprehensiveInputValidator.sanitize_sql_input(case_data.judge_name),
            court_session_date=case_data.court_session_date,
            created_by=current_user.id,
            assigned_to=case_data.assigned_to,
            metadata=case_data.metadata or {}
        )
        
        db.add(db_case)
        db.commit()
        db.refresh(db_case)
        
        # Log de auditoría
        audit_log = AuditLog(
            action="CASE_CREATE",
            resource_type="case",
            resource_id=db_case.id,
            user_id=current_user.id,
            user_email=current_user.email,
            user_ip=request.client.host,
            user_agent=request.headers.get("User-Agent"),
            description=f"Caso creado: {db_case.case_number}",
            new_values={"case_number": db_case.case_number, "title": db_case.title}
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"Case created: {db_case.case_number} by {current_user.email}")
        
        return CaseResponse(
            id=db_case.id,
            case_number=db_case.case_number,
            title=db_case.title,
            description=db_case.description,
            case_type=db_case.case_type,
            status=db_case.status,
            priority=db_case.priority,
            court_name=db_case.court_name,
            judge_name=db_case.judge_name,
            court_session_date=db_case.court_session_date,
            created_by=db_case.created_by,
            assigned_to=db_case.assigned_to,
            created_at=db_case.created_at,
            updated_at=db_case.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error creating case: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear el caso"
        )

@router.get("/", response_model=List[CaseResponse])
async def list_cases(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[CaseStatus] = None,
    case_type_filter: Optional[CaseType] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar casos con filtros"""
    try:
        query = db.query(CaseFile)
        
        # Aplicar filtros
        if status_filter:
            query = query.filter(CaseFile.status == status_filter)
        if case_type_filter:
            query = query.filter(CaseFile.case_type == case_type_filter)
        
        # Solo casos del usuario o asignados al usuario
        if current_user.role.value in ["citizen", "lawyer"]:
            query = query.filter(
                (CaseFile.created_by == current_user.id) | 
                (CaseFile.assigned_to == current_user.id)
            )
        
        cases = query.offset(skip).limit(limit).all()
        
        return [
            CaseResponse(
                id=case.id,
                case_number=case.case_number,
                title=case.title,
                description=case.description,
                case_type=case.case_type,
                status=case.status,
                priority=case.priority,
                court_name=case.court_name,
                judge_name=case.judge_name,
                court_session_date=case.court_session_date,
                created_by=case.created_by,
                assigned_to=case.assigned_to,
                created_at=case.created_at,
                updated_at=case.updated_at
            )
            for case in cases
        ]
        
    except Exception as e:
        logger.error(f"Error listing cases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al listar casos"
        )

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener caso específico"""
    try:
        case = db.query(CaseFile).filter(CaseFile.id == case_id).first()
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caso no encontrado"
            )
        
        # Verificar permisos
        if (current_user.role.value in ["citizen", "lawyer"] and 
            case.created_by != current_user.id and 
            case.assigned_to != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ver este caso"
            )
        
        return CaseResponse(
            id=case.id,
            case_number=case.case_number,
            title=case.title,
            description=case.description,
            case_type=case.case_type,
            status=case.status,
            priority=case.priority,
            court_name=case.court_name,
            judge_name=case.judge_name,
            court_session_date=case.court_session_date,
            created_by=case.created_by,
            assigned_to=case.assigned_to,
            created_at=case.created_at,
            updated_at=case.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting case {case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener el caso"
        )

@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: int,
    case_update: CaseUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar caso"""
    try:
        case = db.query(CaseFile).filter(CaseFile.id == case_id).first()
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caso no encontrado"
            )
        
        # Verificar permisos
        if (current_user.role.value in ["citizen", "lawyer"] and 
            case.created_by != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para modificar este caso"
            )
        
        # Guardar valores antiguos para auditoría
        old_values = {
            "title": case.title,
            "description": case.description,
            "status": case.status.value,
            "priority": case.priority.value
        }
        
        # Actualizar campos
        update_data = case_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(case, field):
                sanitized_value = ComprehensiveInputValidator.sanitize_sql_input(str(value))
                setattr(case, field, sanitized_value)
        
        case.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(case)
        
        # Log de auditoría
        audit_log = AuditLog(
            action="CASE_UPDATE",
            resource_type="case",
            resource_id=case.id,
            user_id=current_user.id,
            user_email=current_user.email,
            user_ip=request.client.host,
            user_agent=request.headers.get("User-Agent"),
            description=f"Caso actualizado: {case.case_number}",
            old_values=old_values,
            new_values=update_data
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"Case updated: {case.case_number} by {current_user.email}")
        
        return CaseResponse(
            id=case.id,
            case_number=case.case_number,
            title=case.title,
            description=case.description,
            case_type=case.case_type,
            status=case.status,
            priority=case.priority,
            court_name=case.court_name,
            judge_name=case.judge_name,
            court_session_date=case.court_session_date,
            created_by=case.created_by,
            assigned_to=case.assigned_to,
            created_at=case.created_at,
            updated_at=case.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating case {case_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar el caso"
        )
