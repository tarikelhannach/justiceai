# backend/app/routes/audit.py - Rutas de Auditoría

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_, func
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.database import get_db
from app.models import AuditLog, User, UserRole
from app.auth.auth import get_current_user
from app.auth.jwt import require_role
from app.routes.schemas import AuditLogResponse, AuditLogCreate, AuditLogStats

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin', 'clerk']))
):
    """
    Obtener logs de auditoría con filtros.
    Solo admin y clerk pueden acceder.
    """
    query = db.query(AuditLog)
    
    # Aplicar filtros
    if action:
        query = query.filter(AuditLog.action == action)
    
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if status:
        query = query.filter(AuditLog.status == status)
    
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    if search:
        query = query.filter(
            or_(
                AuditLog.action.ilike(f"%{search}%"),
                AuditLog.details.ilike(f"%{search}%"),
                AuditLog.ip_address.ilike(f"%{search}%")
            )
        )
    
    # Obtener total count ANTES de paginar
    total_count = query.count()
    
    # Ordenar por fecha descendente
    query = query.order_by(desc(AuditLog.created_at))
    
    # Paginación
    logs = query.offset(skip).limit(limit).all()
    
    # Retornar con metadata de paginación
    return {
        "logs": logs,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }

@router.get("/logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin', 'clerk']))
):
    """Obtener un log específico por ID."""
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Log no encontrado")
    
    return log

@router.get("/stats", response_model=AuditLogStats)
async def get_audit_stats(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin', 'clerk']))
):
    """
    Obtener estadísticas de auditoría.
    Solo admin puede acceder.
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total de logs
    total_logs = db.query(func.count(AuditLog.id)).filter(
        AuditLog.created_at >= start_date
    ).scalar()
    
    # Logs por acción
    logs_by_action = db.query(
        AuditLog.action,
        func.count(AuditLog.id).label('count')
    ).filter(
        AuditLog.created_at >= start_date
    ).group_by(AuditLog.action).all()
    
    # Logs por usuario (top 10)
    logs_by_user = db.query(
        AuditLog.user_id,
        User.name,
        User.email,
        func.count(AuditLog.id).label('count')
    ).join(User).filter(
        AuditLog.created_at >= start_date
    ).group_by(AuditLog.user_id, User.name, User.email).order_by(
        desc('count')
    ).limit(10).all()
    
    # Logs por estado
    logs_by_status = db.query(
        AuditLog.status,
        func.count(AuditLog.id).label('count')
    ).filter(
        AuditLog.created_at >= start_date
    ).group_by(AuditLog.status).all()
    
    # Logs por tipo de recurso
    logs_by_resource = db.query(
        AuditLog.resource_type,
        func.count(AuditLog.id).label('count')
    ).filter(
        AuditLog.created_at >= start_date
    ).group_by(AuditLog.resource_type).all()
    
    # Logs por día (últimos N días)
    logs_by_day = db.query(
        func.date(AuditLog.created_at).label('date'),
        func.count(AuditLog.id).label('count')
    ).filter(
        AuditLog.created_at >= start_date
    ).group_by(func.date(AuditLog.created_at)).order_by('date').all()
    
    return {
        "total_logs": total_logs,
        "days": days,
        "start_date": start_date,
        "by_action": [{"action": a, "count": c} for a, c in logs_by_action],
        "by_user": [
            {"user_id": uid, "name": name, "email": email, "count": c}
            for uid, name, email, c in logs_by_user
        ],
        "by_status": [{"status": s, "count": c} for s, c in logs_by_status],
        "by_resource": [{"resource_type": r, "count": c} for r, c in logs_by_resource],
        "by_day": [{"date": d, "count": c} for d, c in logs_by_day]
    }

@router.get("/export")
async def export_audit_logs(
    format: str = Query(default="json", regex="^(json|csv)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin']))
):
    """
    Exportar logs de auditoría en formato JSON o CSV.
    Solo admin puede exportar.
    """
    query = db.query(AuditLog)
    
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    logs = query.order_by(desc(AuditLog.created_at)).all()
    
    if format == "json":
        # Exportar como JSON estructurado
        export_data = []
        for log in logs:
            export_data.append({
                "id": log.id,
                "timestamp": log.created_at.isoformat(),
                "user_id": log.user_id,
                "user_email": log.user.email if log.user else None,
                "user_name": log.user.name if log.user else None,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "status": log.status,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "details": log.details
            })
        
        return {
            "format": "json",
            "count": len(export_data),
            "exported_at": datetime.utcnow().isoformat(),
            "data": export_data
        }
    
    elif format == "csv":
        # Exportar como CSV
        import io
        import csv
        from fastapi.responses import StreamingResponse
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'ID', 'Timestamp', 'User ID', 'User Email', 'User Name',
            'Action', 'Resource Type', 'Resource ID', 'Status',
            'IP Address', 'User Agent', 'Details'
        ])
        
        # Rows
        for log in logs:
            writer.writerow([
                log.id,
                log.created_at.isoformat(),
                log.user_id,
                log.user.email if log.user else '',
                log.user.name if log.user else '',
                log.action,
                log.resource_type or '',
                log.resource_id or '',
                log.status,
                log.ip_address or '',
                log.user_agent or '',
                log.details or ''
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=audit_logs.csv"}
        )

@router.post("/logs", response_model=AuditLogResponse)
async def create_audit_log(
    log_data: AuditLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crear un log de auditoría manualmente.
    Normalmente los logs se crean automáticamente.
    """
    audit_log = AuditLog(
        user_id=current_user.id,
        action=log_data.action,
        resource_type=log_data.resource_type,
        resource_id=log_data.resource_id,
        ip_address=log_data.ip_address,
        user_agent=log_data.user_agent,
        details=log_data.details,
        status=log_data.status
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log

@router.get("/actions")
async def get_available_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin', 'clerk']))
):
    """Obtener lista de acciones disponibles para filtrar."""
    actions = db.query(AuditLog.action).distinct().all()
    return [a[0] for a in actions]

@router.get("/resource-types")
async def get_resource_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin', 'clerk']))
):
    """Obtener lista de tipos de recursos para filtrar."""
    resource_types = db.query(AuditLog.resource_type).distinct().all()
    return [r[0] for r in resource_types if r[0]]

@router.delete("/logs/{log_id}")
async def delete_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin']))
):
    """
    Eliminar un log de auditoría.
    Solo admin puede eliminar logs (con precaución).
    """
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Log no encontrado")
    
    # Crear log de eliminación antes de eliminar
    delete_log = AuditLog(
        user_id=current_user.id,
        action="delete_audit_log",
        resource_type="audit_log",
        resource_id=log_id,
        details=f"Deleted audit log {log_id}: {log.action}",
        status="success"
    )
    db.add(delete_log)
    
    db.delete(log)
    db.commit()
    
    return {"message": "Log eliminado exitosamente"}
