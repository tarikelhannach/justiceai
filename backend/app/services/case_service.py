# backend/app/services/case_service.py - Servicio de Gestión de Casos

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..models import CaseFile, CaseStatus, CaseType, User, AuditLog, Document
from ..config import settings

logger = logging.getLogger(__name__)

class CaseService:
    """
    Servicio de gestión de casos judiciales
    Proporciona lógica de negocio para operaciones de casos
    """
    
    def __init__(self):
        self.default_priority = CaseStatus.DRAFT
        self.auto_assign_enabled = True
    
    async def create_case(
        self,
        case_data: Dict[str, Any],
        creator_id: int,
        db: Session
    ) -> CaseFile:
        """Crear nuevo caso con validaciones de negocio"""
        try:
            # Generar número de caso único
            case_number = await self._generate_case_number(db)
            
            # Validar datos específicos del caso
            await self._validate_case_data(case_data)
            
            # Crear caso
            case = CaseFile(
                case_number=case_number,
                title=case_data['title'],
                description=case_data.get('description'),
                case_type=case_data['case_type'],
                priority=case_data.get('priority', CaseStatus.DRAFT),
                court_name=case_data.get('court_name'),
                judge_name=case_data.get('judge_name'),
                court_session_date=case_data.get('court_session_date'),
                created_by=creator_id,
                assigned_to=case_data.get('assigned_to'),
                metadata=case_data.get('metadata', {})
            )
            
            db.add(case)
            db.commit()
            db.refresh(case)
            
            # Auto-asignar si está habilitado
            if self.auto_assign_enabled and not case.assigned_to:
                await self._auto_assign_case(case, db)
            
            logger.info(f"Case created: {case.case_number}")
            return case
            
        except Exception as e:
            logger.error(f"Error creating case: {e}")
            db.rollback()
            raise
    
    async def update_case_status(
        self,
        case_id: int,
        new_status: CaseStatus,
        user_id: int,
        db: Session,
        reason: Optional[str] = None
    ) -> bool:
        """Actualizar estado del caso con validaciones"""
        try:
            case = db.query(CaseFile).filter(CaseFile.id == case_id).first()
            if not case:
                return False
            
            # Validar transición de estado
            if not await self._validate_status_transition(case.status, new_status):
                raise ValueError(f"Invalid status transition: {case.status} -> {new_status}")
            
            old_status = case.status
            case.status = new_status
            
            # Actualizar timestamps según estado
            if new_status == CaseStatus.CLOSED:
                case.closed_at = datetime.utcnow()
            elif new_status == CaseStatus.OPEN and old_status == CaseStatus.DRAFT:
                case.updated_at = datetime.utcnow()
            
            db.commit()
            
            # Log de auditoría
            audit_log = AuditLog(
                action="CASE_STATUS_UPDATE",
                resource_type="case",
                resource_id=case_id,
                user_id=user_id,
                description=f"Estado cambiado de {old_status.value} a {new_status.value}",
                old_values={"status": old_status.value},
                new_values={"status": new_status.value, "reason": reason}
            )
            db.add(audit_log)
            db.commit()
            
            logger.info(f"Case {case.case_number} status updated: {old_status} -> {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating case status: {e}")
            db.rollback()
            return False
    
    async def assign_case(
        self,
        case_id: int,
        assignee_id: int,
        user_id: int,
        db: Session
    ) -> bool:
        """Asignar caso a usuario específico"""
        try:
            case = db.query(CaseFile).filter(CaseFile.id == case_id).first()
            if not case:
                return False
            
            # Verificar que el asignado existe y tiene permisos
            assignee = db.query(User).filter(User.id == assignee_id).first()
            if not assignee or not assignee.is_active:
                raise ValueError("Invalid assignee")
            
            old_assignee = case.assigned_to
            case.assigned_to = assignee_id
            case.updated_at = datetime.utcnow()
            
            db.commit()
            
            # Log de auditoría
            audit_log = AuditLog(
                action="CASE_ASSIGN",
                resource_type="case",
                resource_id=case_id,
                user_id=user_id,
                description=f"Caso asignado a {assignee.name}",
                old_values={"assigned_to": old_assignee},
                new_values={"assigned_to": assignee_id}
            )
            db.add(audit_log)
            db.commit()
            
            logger.info(f"Case {case.case_number} assigned to {assignee.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning case: {e}")
            db.rollback()
            return False
    
    async def get_case_statistics(
        self,
        user_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Obtener estadísticas de casos"""
        try:
            query = db.query(CaseFile)
            
            # Filtrar por usuario si se especifica
            if user_id:
                query = query.filter(
                    or_(
                        CaseFile.created_by == user_id,
                        CaseFile.assigned_to == user_id
                    )
                )
            
            # Filtrar por fechas
            if date_from:
                query = query.filter(CaseFile.created_at >= date_from)
            if date_to:
                query = query.filter(CaseFile.created_at <= date_to)
            
            # Estadísticas básicas
            total_cases = query.count()
            
            # Casos por estado
            cases_by_status = {}
            for status in CaseStatus:
                count = query.filter(CaseFile.status == status).count()
                cases_by_status[status.value] = count
            
            # Casos por tipo
            cases_by_type = {}
            for case_type in CaseType:
                count = query.filter(CaseFile.case_type == case_type).count()
                cases_by_type[case_type.value] = count
            
            # Casos por prioridad
            cases_by_priority = {}
            for priority in ["low", "medium", "high", "urgent"]:
                count = query.filter(CaseFile.priority == priority).count()
                cases_by_priority[priority] = count
            
            # Casos por mes (últimos 12 meses)
            cases_by_month = {}
            for i in range(12):
                month_start = datetime.utcnow() - timedelta(days=30*i)
                month_end = month_start + timedelta(days=30)
                count = query.filter(
                    and_(
                        CaseFile.created_at >= month_start,
                        CaseFile.created_at < month_end
                    )
                ).count()
                cases_by_month[month_start.strftime("%Y-%m")] = count
            
            # Tiempo promedio de procesamiento
            closed_cases = query.filter(CaseFile.status == CaseStatus.CLOSED).all()
            avg_processing_time = 0
            if closed_cases:
                total_days = sum([
                    (case.closed_at - case.created_at).days 
                    for case in closed_cases 
                    if case.closed_at
                ])
                avg_processing_time = total_days / len(closed_cases)
            
            return {
                "total_cases": total_cases,
                "cases_by_status": cases_by_status,
                "cases_by_type": cases_by_type,
                "cases_by_priority": cases_by_priority,
                "cases_by_month": cases_by_month,
                "average_processing_time_days": round(avg_processing_time, 2),
                "period": {
                    "from": date_from.isoformat() if date_from else None,
                    "to": date_to.isoformat() if date_to else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting case statistics: {e}")
            return {}
    
    async def search_cases(
        self,
        search_query: str,
        filters: Dict[str, Any],
        user_id: Optional[int] = None,
        db: Session = None
    ) -> List[CaseFile]:
        """Búsqueda avanzada de casos"""
        try:
            query = db.query(CaseFile)
            
            # Búsqueda de texto
            if search_query:
                search_filter = or_(
                    CaseFile.title.ilike(f"%{search_query}%"),
                    CaseFile.description.ilike(f"%{search_query}%"),
                    CaseFile.case_number.ilike(f"%{search_query}%")
                )
                query = query.filter(search_filter)
            
            # Aplicar filtros
            if filters.get('status'):
                query = query.filter(CaseFile.status == filters['status'])
            if filters.get('case_type'):
                query = query.filter(CaseFile.case_type == filters['case_type'])
            if filters.get('priority'):
                query = query.filter(CaseFile.priority == filters['priority'])
            if filters.get('court_name'):
                query = query.filter(CaseFile.court_name.ilike(f"%{filters['court_name']}%"))
            if filters.get('date_from'):
                query = query.filter(CaseFile.created_at >= filters['date_from'])
            if filters.get('date_to'):
                query = query.filter(CaseFile.created_at <= filters['date_to'])
            
            # Filtrar por usuario si se especifica
            if user_id:
                query = query.filter(
                    or_(
                        CaseFile.created_by == user_id,
                        CaseFile.assigned_to == user_id
                    )
                )
            
            # Ordenar por fecha de creación descendente
            query = query.order_by(CaseFile.created_at.desc())
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error searching cases: {e}")
            return []
    
    async def _generate_case_number(self, db: Session) -> str:
        """Generar número de caso único"""
        try:
            # Obtener el último número de caso del día
            today = datetime.utcnow().strftime('%Y%m%d')
            prefix = f"CAS-{today}"
            
            last_case = db.query(CaseFile).filter(
                CaseFile.case_number.like(f"{prefix}%")
            ).order_by(CaseFile.id.desc()).first()
            
            if last_case:
                # Extraer número secuencial y incrementar
                last_number = int(last_case.case_number.split('-')[-1])
                next_number = last_number + 1
            else:
                next_number = 1
            
            return f"{prefix}-{next_number:04d}"
            
        except Exception as e:
            logger.error(f"Error generating case number: {e}")
            # Fallback con timestamp
            return f"CAS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    async def _validate_case_data(self, case_data: Dict[str, Any]) -> None:
        """Validar datos del caso"""
        required_fields = ['title', 'case_type']
        for field in required_fields:
            if field not in case_data or not case_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Validar longitud del título
        if len(case_data['title']) < 5:
            raise ValueError("Case title too short")
        
        # Validar fecha de sesión si se proporciona
        if case_data.get('court_session_date'):
            session_date = case_data['court_session_date']
            if isinstance(session_date, str):
                session_date = datetime.fromisoformat(session_date)
            if session_date < datetime.utcnow():
                raise ValueError("Court session date cannot be in the past")
    
    async def _validate_status_transition(
        self, 
        current_status: CaseStatus, 
        new_status: CaseStatus
    ) -> bool:
        """Validar transición de estado del caso"""
        valid_transitions = {
            CaseStatus.DRAFT: [CaseStatus.OPEN, CaseStatus.CANCELLED],
            CaseStatus.OPEN: [CaseStatus.IN_PROGRESS, CaseStatus.CLOSED, CaseStatus.CANCELLED],
            CaseStatus.IN_PROGRESS: [CaseStatus.UNDER_REVIEW, CaseStatus.CLOSED, CaseStatus.CANCELLED],
            CaseStatus.UNDER_REVIEW: [CaseStatus.CLOSED, CaseStatus.IN_PROGRESS],
            CaseStatus.CLOSED: [CaseStatus.ARCHIVED],
            CaseStatus.ARCHIVED: [CaseStatus.OPEN],  # Reabrir caso archivado
            CaseStatus.CANCELLED: []  # No se puede cambiar desde cancelado
        }
        
        return new_status in valid_transitions.get(current_status, [])
    
    async def _auto_assign_case(self, case: CaseFile, db: Session) -> None:
        """Auto-asignar caso basado en reglas de negocio"""
        try:
            # Buscar usuarios disponibles según el tipo de caso
            available_users = db.query(User).filter(
                and_(
                    User.is_active == True,
                    User.role.in_([UserRole.JUDGE, UserRole.CLERK])
                )
            ).all()
            
            if available_users:
                # Asignar al usuario con menos casos pendientes
                user_case_counts = {}
                for user in available_users:
                    pending_cases = db.query(CaseFile).filter(
                        and_(
                            CaseFile.assigned_to == user.id,
                            CaseFile.status.in_([
                                CaseStatus.OPEN, 
                                CaseStatus.IN_PROGRESS, 
                                CaseStatus.UNDER_REVIEW
                            ])
                        )
                    ).count()
                    user_case_counts[user.id] = pending_cases
                
                # Asignar al usuario con menos casos
                best_user_id = min(user_case_counts, key=user_case_counts.get)
                case.assigned_to = best_user_id
                db.commit()
                
                logger.info(f"Case {case.case_number} auto-assigned to user {best_user_id}")
                
        except Exception as e:
            logger.error(f"Error in auto-assignment: {e}")
