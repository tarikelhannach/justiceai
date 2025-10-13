from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..database import get_db
from ..models import User, UserRole, AuditLog
from ..auth.jwt import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from ..config import settings
from ..middleware.rate_limit import ip_limiter

router = APIRouter(prefix="/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: UserRole = UserRole.CITIZEN

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True

@router.post("/login", response_model=TokenResponse)
@ip_limiter.limit("5/minute")  # Max 5 login attempts per minute per IP
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """Iniciar sesión con rate limiting (5 intentos/minuto por IP)"""
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        # Log failed login attempt
        audit_log = AuditLog(
            action="login_failed",
            resource_type="auth",
            details=f"Failed login attempt for {login_data.email}",
            status="failed"
        )
        db.add(audit_log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    # Log successful login
    audit_log = AuditLog(
        user_id=user.id,
        action="login",
        resource_type="auth",
        status="success"
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_verified": user.is_verified
        }
    }

@router.post("/register", response_model=TokenResponse)
@ip_limiter.limit("3/hour")  # Max 3 registrations per hour per IP
async def register(request: Request, register_data: RegisterRequest, db: Session = Depends(get_db)):
    """Registrar nuevo usuario con rate limiting (3 registros/hora por IP)"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == register_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Create new user
    new_user = User(
        email=register_data.email,
        name=register_data.name,
        hashed_password=get_password_hash(register_data.password[:72]),
        role=register_data.role,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": new_user.email},
        expires_delta=access_token_expires
    )
    
    # Log registration
    audit_log = AuditLog(
        user_id=new_user.id,
        action="user_registered",
        resource_type="user",
        resource_id=new_user.id,
        status="success"
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name,
            "role": new_user.role.value,
            "is_active": new_user.is_active,
            "is_verified": new_user.is_verified
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Cerrar sesión (registrar en audit log)"""
    audit_log = AuditLog(
        user_id=current_user.id,
        action="logout",
        resource_type="auth",
        status="success"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Sesión cerrada exitosamente"}
