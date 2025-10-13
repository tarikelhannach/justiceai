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
    
    def __init__(self):
        self.redis_client = None
        try:
            self.redis_client = redis.from_url(settings.redis_url)
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
        self.totp_issuer = "Sistema Judicial Digital - Marruecos"
        self.code_expiry = 300  # 5 minutos
        self.max_attempts = 3
    
    def generate_secret_key(self, user_email: str) -> str:
        """Generar clave secreta para TOTP"""
        try:
            secret = pyotp.random_base32()
            
            # Guardar clave secreta temporalmente si Redis está disponible
            if self.redis_client:
                self.redis_client.setex(
                    f"2fa_secret:{user_email}",
                    self.code_expiry,
                    secret
                )
            
            logger.info(f"2FA secret generated for {user_email}")
            return secret
            
        except Exception as e:
            logger.error(f"Error generating 2FA secret: {e}")
            raise
    
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
            if self.redis_client:
                attempts_key = f"2fa_attempts:{user_email}"
                attempts = self.redis_client.get(attempts_key)
                
                if attempts and int(attempts) >= self.max_attempts:
                    logger.warning(f"2FA max attempts exceeded for {user_email}")
                    return False
            
            # Verificar código
            totp = pyotp.TOTP(secret)
            is_valid = totp.verify(code, valid_window=1)  # Ventana de 1 período
            
            if is_valid:
                # Limpiar intentos en caso de éxito
                if self.redis_client:
                    self.redis_client.delete(attempts_key)
                logger.info(f"2FA TOTP verified for {user_email}")
            else:
                # Incrementar intentos fallidos
                if self.redis_client:
                    self.redis_client.incr(attempts_key)
                    self.redis_client.expire(attempts_key, 900)  # 15 minutos
                logger.warning(f"2FA TOTP verification failed for {user_email}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying TOTP code: {e}")
            return False
    
    def is_2fa_enabled(self, user_email: str) -> bool:
        """Verificar si 2FA está habilitado para usuario"""
        try:
            if not self.redis_client:
                return False
            return self.redis_client.exists(f"user_2fa:{user_email}")
        except Exception as e:
            logger.error(f"Error checking 2FA status: {e}")
            return False
