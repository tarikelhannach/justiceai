# backend/app/auth/two_factor.py - 2FA Simplificado

import pyotp
import qrcode
import io
import base64
import logging
from typing import Optional
from datetime import datetime, timedelta
import redis
import json

from ..config import settings

logger = logging.getLogger(__name__)

class TwoFactorAuth:
    """Sistema de autenticación de dos factores simplificado"""
    # Atributo de clase para facilitar el patch en tests
    redis_client = None
    
    def __init__(self):
        # Inicializa redis una sola vez a nivel de clase si está disponible
        if self.__class__.redis_client is None:
            try:
                self.__class__.redis_client = redis.from_url(settings.redis_url)
            except Exception as e:
                logger.warning(f"Redis not available: {e}")
        self.totp_issuer = "Sistema Judicial Digital - Marruecos"
        self.code_expiry = 300  # 5 minutos
        self.max_attempts = 3
    
    def generate_secret_key(self, user_email: str) -> str:
        """Generar clave secreta para TOTP"""
        secret = pyotp.random_base32()
        # Guardar clave secreta temporalmente si Redis está disponible
        try:
            if self.__class__.redis_client:
                self.__class__.redis_client.setex(
                    f"2fa_secret:{user_email}",
                    self.code_expiry,
                    secret
                )
        except Exception as e:
            # No bloquear generación de secret si Redis falla
            logger.warning(f"Skipping Redis cache for 2FA secret due to error: {e}")
        
        logger.info(f"2FA secret generated for {user_email}")
        return secret
    
    def generate_qr_code(self, user_email: str, secret: str) -> str:
        """Generar código QR para configuración de 2FA"""
        try:
            # Crear URI para TOTP
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user_email,
                issuer_name=self.totp_issuer
            )
            
            # Generar QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # Convertir a imagen base64
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            logger.info(f"QR code generated for {user_email}")
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            raise
    
    def verify_totp_code(self, secret: str, code: str, user_email: str) -> bool:
        """Verificar código TOTP"""
        try:
            # Verificar intentos si Redis está disponible
            if self.__class__.redis_client:
                attempts_key = f"2fa_attempts:{user_email}"
                attempts = self.__class__.redis_client.get(attempts_key)
                
                if attempts and int(attempts) >= self.max_attempts:
                    logger.warning(f"2FA max attempts exceeded for {user_email}")
                    return False
            
            # Verificar código
            totp = pyotp.TOTP(secret)
            is_valid = totp.verify(code, valid_window=1)  # Ventana de 1 período
            
            if is_valid:
                # Limpiar intentos en caso de éxito
                if self.__class__.redis_client:
                    self.__class__.redis_client.delete(attempts_key)
                logger.info(f"2FA TOTP verified for {user_email}")
            else:
                # Incrementar intentos fallidos
                if self.__class__.redis_client:
                    self.__class__.redis_client.incr(attempts_key)
                    self.__class__.redis_client.expire(attempts_key, 900)  # 15 minutos
                logger.warning(f"2FA TOTP verification failed for {user_email}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying TOTP code: {e}")
            return False
    
    def is_2fa_enabled(self, user_email: str) -> bool:
        """Verificar si 2FA está habilitado para usuario"""
        try:
            if not self.__class__.redis_client:
                return False
            return self.__class__.redis_client.exists(f"user_2fa:{user_email}")
        except Exception as e:
            logger.error(f"Error checking 2FA status: {e}")
            return False

    def verify_sms_code(self, user_email: str, code: str) -> bool:
        """Verificar código enviado por SMS almacenado temporalmente en Redis.
        Espera un JSON con el formato: {"code": str, "phone": str, "created_at": iso}.
        """
        try:
            if not self.__class__.redis_client:
                logger.warning("Redis not available for SMS verification")
                return False
            key = f"sms_code:{user_email}"
            data = self.__class__.redis_client.get(key)
            if not data:
                return False
            try:
                payload = json.loads(data)
            except Exception:
                return False
            stored_code = payload.get("code")
            if not stored_code:
                return False
            is_valid = stored_code == code
            if is_valid:
                # Código verificado, limpiar
                self.__class__.redis_client.delete(key)
            return is_valid
        except Exception as e:
            logger.error(f"Error verifying SMS code: {e}")
            return False
