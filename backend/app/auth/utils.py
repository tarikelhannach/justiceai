# backend/app/auth/utils.py - Utilidades de Autenticación

import secrets
import string
import logging
from typing import Optional
from datetime import datetime, timedelta
import redis
import json

from ..config import settings

logger = logging.getLogger(__name__)

def generate_verification_code(length: int = 6) -> str:
    """Generar código de verificación alfanumérico"""
    try:
        characters = string.ascii_uppercase + string.digits
        code = ''.join(secrets.choice(characters) for _ in range(length))
        return code
    except Exception as e:
        logger.error(f"Error generating verification code: {e}")
        return ""

def generate_numeric_code(length: int = 6) -> str:
    """Generar código numérico"""
    try:
        return ''.join(secrets.choice(string.digits) for _ in range(length))
    except Exception as e:
        logger.error(f"Error generating numeric code: {e}")
        return ""

def send_verification_code(
    email: str, 
    code: str, 
    code_type: str = "email_verification"
) -> bool:
    """Enviar código de verificación por email"""
    try:
        # Aquí se integraría con el servicio de notificaciones
        # Por ahora solo log
        logger.info(f"Verification code {code} sent to {email} for {code_type}")
        return True
    except Exception as e:
        logger.error(f"Error sending verification code: {e}")
        return False

def verify_verification_code(
    email: str, 
    code: str, 
    code_type: str = "email_verification"
) -> bool:
    """Verificar código de verificación"""
    try:
        redis_client = redis.from_url(settings.redis_url)
        
        # Obtener código guardado
        stored_data = redis_client.get(f"verification:{code_type}:{email}")
        if not stored_data:
            return False
        
        data = json.loads(stored_data)
        stored_code = data.get("code")
        expires_at = datetime.fromisoformat(data.get("expires_at"))
        
        # Verificar expiración
        if datetime.utcnow() > expires_at:
            redis_client.delete(f"verification:{code_type}:{email}")
            return False
        
        # Verificar código
        is_valid = code == stored_code
        
        if is_valid:
            # Eliminar código usado
            redis_client.delete(f"verification:{code_type}:{email}")
            logger.info(f"Verification code verified for {email}")
        else:
            logger.warning(f"Invalid verification code for {email}")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error verifying code: {e}")
        return False

def store_verification_code(
    email: str, 
    code: str, 
    code_type: str = "email_verification",
    expiry_minutes: int = 15
) -> bool:
    """Guardar código de verificación con expiración"""
    try:
        redis_client = redis.from_url(settings.redis_url)
        
        data = {
            "code": code,
            "email": email,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=expiry_minutes)).isoformat()
        }
        
        # Guardar con expiración
        redis_client.setex(
            f"verification:{code_type}:{email}",
            expiry_minutes * 60,
            json.dumps(data)
        )
        
        logger.info(f"Verification code stored for {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error storing verification code: {e}")
        return False

def generate_password_reset_token(email: str) -> str:
    """Generar token para reset de contraseña"""
    try:
        token = secrets.token_urlsafe(32)
        
        # Guardar token con expiración
        redis_client = redis.from_url(settings.redis_url)
        data = {
            "email": email,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        redis_client.setex(
            f"password_reset:{token}",
            3600,  # 1 hora
            json.dumps(data)
        )
        
        logger.info(f"Password reset token generated for {email}")
        return token
        
    except Exception as e:
        logger.error(f"Error generating password reset token: {e}")
        return ""

def verify_password_reset_token(token: str) -> Optional[str]:
    """Verificar token de reset de contraseña"""
    try:
        redis_client = redis.from_url(settings.redis_url)
        
        stored_data = redis_client.get(f"password_reset:{token}")
        if not stored_data:
            return None
        
        data = json.loads(stored_data)
        email = data.get("email")
        expires_at = datetime.fromisoformat(data.get("expires_at"))
        
        # Verificar expiración
        if datetime.utcnow() > expires_at:
            redis_client.delete(f"password_reset:{token}")
            return None
        
        return email
        
    except Exception as e:
        logger.error(f"Error verifying password reset token: {e}")
        return None

def invalidate_password_reset_token(token: str) -> bool:
    """Invalidar token de reset de contraseña"""
    try:
        redis_client = redis.from_url(settings.redis_url)
        redis_client.delete(f"password_reset:{token}")
        logger.info(f"Password reset token invalidated: {token}")
        return True
    except Exception as e:
        logger.error(f"Error invalidating password reset token: {e}")
        return False

def generate_session_id() -> str:
    """Generar ID de sesión único"""
    try:
        return secrets.token_urlsafe(32)
    except Exception as e:
        logger.error(f"Error generating session ID: {e}")
        return ""

def store_user_session(
    user_id: int, 
    session_id: str, 
    ip_address: str = None,
    user_agent: str = None,
    expires_hours: int = 24
) -> bool:
    """Guardar sesión de usuario"""
    try:
        redis_client = redis.from_url(settings.redis_url)
        
        session_data = {
            "user_id": user_id,
            "session_id": session_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=expires_hours)).isoformat()
        }
        
        redis_client.setex(
            f"user_session:{session_id}",
            expires_hours * 3600,
            json.dumps(session_data)
        )
        
        logger.info(f"User session stored: {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error storing user session: {e}")
        return False

def get_user_session(session_id: str) -> Optional[dict]:
    """Obtener sesión de usuario"""
    try:
        redis_client = redis.from_url(settings.redis_url)
        
        stored_data = redis_client.get(f"user_session:{session_id}")
        if not stored_data:
            return None
        
        data = json.loads(stored_data)
        expires_at = datetime.fromisoformat(data.get("expires_at"))
        
        # Verificar expiración
        if datetime.utcnow() > expires_at:
            redis_client.delete(f"user_session:{session_id}")
            return None
        
        return data
        
    except Exception as e:
        logger.error(f"Error getting user session: {e}")
        return None

def invalidate_user_session(session_id: str) -> bool:
    """Invalidar sesión de usuario"""
    try:
        redis_client = redis.from_url(settings.redis_url)
        redis_client.delete(f"user_session:{session_id}")
        logger.info(f"User session invalidated: {session_id}")
        return True
    except Exception as e:
        logger.error(f"Error invalidating user session: {e}")
        return False

def cleanup_expired_sessions() -> int:
    """Limpiar sesiones expiradas"""
    try:
        redis_client = redis.from_url(settings.redis_url)
        
        # Obtener todas las claves de sesión
        session_keys = redis_client.keys("user_session:*")
        expired_count = 0
        
        for key in session_keys:
            stored_data = redis_client.get(key)
            if stored_data:
                data = json.loads(stored_data)
                expires_at = datetime.fromisoformat(data.get("expires_at"))
                
                if datetime.utcnow() > expires_at:
                    redis_client.delete(key)
                    expired_count += 1
        
        logger.info(f"Cleaned up {expired_count} expired sessions")
        return expired_count
        
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {e}")
        return 0
