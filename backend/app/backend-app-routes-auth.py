# backend/app/routes/auth.py - Endpoints de Autenticación

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging

from ..database import get_db
from ..models import User, UserRole, AuditLog
from ..config import settings
from ..auth.auth import (
    authenticate_user, 
    create_access_token, 
    create_refresh_token, 
    get_current_user,
    get_password_hash,
    verify_token
)
from ..security.input_validator import ComprehensiveInputValidator
from ..services.notification_service import NotificationService
from .schemas import (
    UserCreate, 
    UserResponse, 
    Token, 
    TokenRefresh,
    UserLogin,
    PasswordChange,
    PasswordReset,
    UserUpdate
)

logger = logging.getLogger(__name__)
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize services
notification_service = NotificationService()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Registrar nuevo usuario en el sistema judicial
    Específicamente diseñado para el sistema marroquí
    """
    try:
        # Validación de entrada
        ComprehensiveInputValidator.rate_limit_check(
            request.client.host, 
            "register"
        )
        
        # Sanitizar inputs
        email = ComprehensiveInputValidator.sanitize_sql_input(user_data.email.lower())
        name = ComprehensiveInputValidator.sanitize_sql_input(user_data.name)
        
        # Verificar si usuario ya existe
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya existe en el sistema"
            )
        
        # Verificar CIN marroquí si se proporciona
        if user_data.national_id:
            national_id = ComprehensiveInputValidator.sanitize_sql_input(user_data.national_id)
            existing_cin = db.query(User).filter(User.national_id == national_id).first()
            if existing_cin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Este número de identificación nacional ya está registrado"
                )
        
        # Validar rol - algunos roles requieren aprobación
        restricted_roles = [UserRole.JUDGE, UserRole.ADMIN]
        if user_data.role in restricted_roles:
            user_data.role = UserRole.CITIZEN  # Asignar rol básico temporalmente
            requires_approval = True
        else:
            requires_approval = False
        
        # Crear usuario
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,
            role=user_data.role,
            national_id=user_data.national_id,
            phone=user_data.phone,
            address=user_data.address,
            city=user_data.city,
            preferred_language=user_data.preferred_language or "ar",
            is_active=True,
            is_verified=False  # Requiere verificación por email
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Log de auditoría
        audit_log = AuditLog(
            action="USER_REGISTER",
            resource_type="user",
            resource_id=db_user.id,
            user_id=db_user.id,
            user_email=db_user.email,
            user_ip=request.client.host,
            user_agent=request.headers.get("User-Agent"),
            description=f"Usuario registrado: {db_user.email}",
            new_values={"email": db_user.email, "role": db_user.role.value}
        )
        db.add(audit_log)
        db.commit()
        
        # Enviar notificación de bienvenida
        if requires_approval:
            await notification_service.send_approval_required_notification(
                db_user.email, 
                db_user.name
            )
        else:
            await notification_service.send_welcome_notification(
                db_user.email, 
                db_user.name,
                db_user.preferred_language
            )
        
        logger.info(f"New user registered: {db_user.email}")
        
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            role=db_user.role,
            is_active=db_user.is_active,
            is_verified=db_user.is_verified,
            preferred_language=db_user.preferred_language,
            created_at=db_user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante el registro"
        )

@router.post("/token", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autenticación de usuario y generación de tokens JWT
    Optimizado para el sistema judicial marroquí
    """
    try:
        # Rate limiting para autenticación
        ComprehensiveInputValidator.rate_limit_check(
            request.client.host,
            "login"
        )
        
        # Sanitizar inputs
        email = ComprehensiveInputValidator.sanitize_sql_input(form_data.username.lower())
        
        # Autenticar usuario
        user = authenticate_user(db, email, form_data.password)
        if not user:
            # Log intento de login fallido
            audit_log = AuditLog(
                action="LOGIN_FAILED",
                resource_type="user",
                user_email=email,
                user_ip=request.client.host,
                user_agent=request.headers.get("User-Agent"),
                description=f"Intento de login fallido para: {email}"
            )
            db.add(audit_log)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar si usuario está activo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cuenta desactivada. Contacte al administrador.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=refresh_token_expires
        )
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Log de auditoría exitoso
        audit_log = AuditLog(
            action="LOGIN_SUCCESS",
            resource_type="user",
            resource_id=user.id,
            user_id=user.id,
            user_email=user.email,
            user_ip=request.client.host,
            user_agent=request.headers.get("User-Agent"),
            description=f"Login exitoso: {user.email}"
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"User logged in: {user.email}")
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                preferred_language=user.preferred_language,
                created_at=user.created_at
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno durante la autenticación"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Renovar token de acceso usando refresh token
    """
    try:
        # Verificar refresh token
        payload = verify_token(token_data.refresh_token)
        email = payload.get("sub")
        user_id = payload.get("user_id")
        
        if not email or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de renovación inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Obtener usuario
        user = db.query(User).filter(User.id == user_id, User.email == email).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear nuevos tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
        new_refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=refresh_token_expires
        )
        
        # Log de auditoría
        audit_log = AuditLog(
            action="TOKEN_REFRESH",
            resource_type="user",
            resource_id=user.id,
            user_id=user.id,
            user_email=user.email,
            user_ip=request.client.host,
            user_agent=request.headers.get("User-Agent"),
            description="Token renovado exitosamente"
        )
        db.add(audit_log)
        db.commit()
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                preferred_language=user.preferred_language,
                created_at=user.created_at
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error al renovar token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Obtener información del usuario actual
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        national_id=current_user.national_id,
        phone=current_user.phone,
        address=current_user.address,
        city=current_user.city,
        preferred_language=current_user.preferred_language,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar información del usuario actual
    """
    try:
        # Preparar datos para actualizar
        update_data = user_update.dict(exclude_unset=True)
        old_values = {
            "name": current_user.name,
            "phone": current_user.phone,
            "address": current_user.address,
            "city": current_user.city,
            "preferred_language": current_user.preferred_language
        }
        
        # Actualizar campos
        for field, value in update_data.items():
            if hasattr(current_user, field):
                sanitized_value = ComprehensiveInputValidator.sanitize_sql_input(str(value))
                setattr(current_user, field, sanitized_value)
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        # Log de auditoría
        audit_log = AuditLog(
            action="USER_UPDATE",
            resource_type="user",
            resource_id=current_user.id,
            user_id=current_user.id,
            user_email=current_user.email,
            user_ip=request.client.host,
            user_agent=request.headers.get("User-Agent"),
            description="Información de usuario actualizada",
            old_values=old_values,
            new_values=update_data
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"User updated their profile: {current_user.email}")
        
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            role=current_user.role,
            is_active=current_user.is_active,
            is_verified=current_user.is_verified,
            national_id=current_user.national_id,
            phone=current_user.phone,
            address=current_user.address,
            city=current_user.city,
            preferred_language=current_user.preferred_language,
            created_at=current_user.created_at,
            last_login=current_user.last_login
        )
        
    except Exception as e:
        logger.error(f"User update error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar información del usuario"
        )

@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar contraseña del usuario actual
    """
    try:
        # Verificar contraseña actual
        from ..auth.utils import verify_password
        if not verify_password(password_change.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )
        
        # Actualizar contraseña
        current_user.hashed_password = get_password_hash(password_change.new_password)
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        # Log de auditoría
        audit_log = AuditLog(
            action="PASSWORD_CHANGE",
            resource_type="user",
            resource_id=current_user.id,
            user_id=current_user.id,
            user_email=current_user.email,
            user_ip=request.client.host,
            user_agent=request.headers.get("User-Agent"),
            description="Contraseña cambiada exitosamente"
        )
        db.add(audit_log)
        db.commit()
        
        # Enviar notificación de seguridad
        await notification_service.send_password_change_notification(
            current_user.email,
            current_user.name,
            current_user.preferred_language
        )
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return {"message": "Contraseña cambiada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cambiar contraseña"
        )

@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout del usuario (invalidar sesión)
    """
    try:
        # Log de auditoría
        audit_log = AuditLog(
            action="LOGOUT",
            resource_type="user",
            resource_id=current_user.id,
            user_id=current_user.id,
            user_email=current_user.email,
            user_ip=request.client.host,
            user_agent=request.headers.get("User-Agent"),
            description="Usuario cerró sesión"
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"User logged out: {current_user.email}")
        
        return {"message": "Logout exitoso"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error durante el logout"
        )