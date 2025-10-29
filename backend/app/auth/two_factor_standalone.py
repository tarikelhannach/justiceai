# backend/app/auth/two_factor_standalone.py - 2FA Standalone (Sin Redis)

import pyotp
import qrcode
import io
import base64
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class TwoFactorAuthStandalone:
    """
    Sistema de autenticación de dos factores standalone
    Funciona sin Redis para testing y desarrollo
    """
    
    def __init__(self, storage_file: str = "2fa_storage.json"):
        self.storage_file = storage_file
        self.totp_issuer = "Sistema Judicial Digital - Marruecos"
        self.code_expiry = 300  # 5 minutos
        self.max_attempts = 3
        self._load_storage()
    
    def _load_storage(self):
        """Cargar datos de almacenamiento"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    self.storage = json.load(f)
            else:
                self.storage = {}
        except Exception as e:
            logger.error(f"Error loading storage: {e}")
            self.storage = {}
    
    def _save_storage(self):
        """Guardar datos de almacenamiento"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.storage, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving storage: {e}")
    
    def generate_secret_key(self, user_email: str) -> str:
        """Generar clave secreta para TOTP"""
        try:
            secret = pyotp.random_base32()
            
            # Guardar clave secreta temporalmente
            self.storage[f"2fa_secret:{user_email}"] = {
                "secret": secret,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(seconds=self.code_expiry)).isoformat()
            }
            self._save_storage()
            
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
            # Verificar intentos
            attempts_key = f"2fa_attempts:{user_email}"
            attempts = self.storage.get(attempts_key, 0)
            
            if attempts >= self.max_attempts:
                logger.warning(f"2FA max attempts exceeded for {user_email}")
                return False
            
            # Verificar código
            totp = pyotp.TOTP(secret)
            is_valid = totp.verify(code, valid_window=1)  # Ventana de 1 período
            
            if is_valid:
                # Limpiar intentos en caso de éxito
                if attempts_key in self.storage:
                    del self.storage[attempts_key]
                self._save_storage()
                logger.info(f"2FA TOTP verified for {user_email}")
            else:
                # Incrementar intentos fallidos
                self.storage[attempts_key] = attempts + 1
                self._save_storage()
                logger.warning(f"2FA TOTP verification failed for {user_email}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying TOTP code: {e}")
            return False
    
    def generate_sms_code(self, user_email: str, phone: str) -> str:
        """Generar código SMS de 6 dígitos"""
        try:
            import random
            code = str(random.randint(100000, 999999))
            
            # Guardar código con expiración
            self.storage[f"2fa_sms:{user_email}"] = {
                "code": code,
                "phone": phone,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(seconds=self.code_expiry)).isoformat()
            }
            self._save_storage()
            
            # Simular envío SMS
            logger.info(f"SMS code {code} would be sent to {phone}")
            
            return code
            
        except Exception as e:
            logger.error(f"Error generating SMS code: {e}")
            raise
    
    def verify_sms_code(self, user_email: str, code: str) -> bool:
        """Verificar código SMS"""
        try:
            # Verificar intentos
            attempts_key = f"2fa_sms_attempts:{user_email}"
            attempts = self.storage.get(attempts_key, 0)
            
            if attempts >= self.max_attempts:
                logger.warning(f"2FA SMS max attempts exceeded for {user_email}")
                return False
            
            # Obtener código guardado
            stored_data = self.storage.get(f"2fa_sms:{user_email}")
            if not stored_data:
                logger.warning(f"No SMS code found for {user_email}")
                return False
            
            # Verificar expiración
            expires_at = datetime.fromisoformat(stored_data["expires_at"])
            if datetime.utcnow() > expires_at:
                del self.storage[f"2fa_sms:{user_email}"]
                self._save_storage()
                return False
            
            stored_code = stored_data["code"]
            
            # Verificar código
            is_valid = code == stored_code
            
            if is_valid:
                # Limpiar datos
                if f"2fa_sms:{user_email}" in self.storage:
                    del self.storage[f"2fa_sms:{user_email}"]
                if attempts_key in self.storage:
                    del self.storage[attempts_key]
                self._save_storage()
                logger.info(f"2FA SMS verified for {user_email}")
            else:
                # Incrementar intentos fallidos
                self.storage[attempts_key] = attempts + 1
                self._save_storage()
                logger.warning(f"2FA SMS verification failed for {user_email}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying SMS code: {e}")
            return False
    
    def enable_2fa_for_user(self, user_email: str, secret: str, verification_code: str) -> bool:
        """Habilitar 2FA para usuario después de verificación"""
        try:
            # Verificar código antes de habilitar
            if not self.verify_totp_code(secret, verification_code, user_email):
                return False
            
            # Guardar configuración 2FA del usuario
            user_2fa_data = {
                "secret": secret,
                "enabled_at": datetime.utcnow().isoformat(),
                "method": "totp"
            }
            
            self.storage[f"user_2fa:{user_email}"] = user_2fa_data
            self._save_storage()
            
            # Limpiar clave temporal
            if f"2fa_secret:{user_email}" in self.storage:
                del self.storage[f"2fa_secret:{user_email}"]
                self._save_storage()
            
            logger.info(f"2FA enabled for {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enabling 2FA: {e}")
            return False
    
    def disable_2fa_for_user(self, user_email: str) -> bool:
        """Deshabilitar 2FA para usuario"""
        try:
            # Eliminar configuración 2FA
            if f"user_2fa:{user_email}" in self.storage:
                del self.storage[f"user_2fa:{user_email}"]
            
            # Limpiar datos relacionados
            for key in list(self.storage.keys()):
                if key.startswith(f"2fa_") and user_email in key:
                    del self.storage[key]
            
            self._save_storage()
            
            logger.info(f"2FA disabled for {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error disabling 2FA: {e}")
            return False
    
    def is_2fa_enabled(self, user_email: str) -> bool:
        """Verificar si 2FA está habilitado para usuario"""
        return f"user_2fa:{user_email}" in self.storage
    
    def get_user_2fa_method(self, user_email: str) -> Optional[str]:
        """Obtener método 2FA del usuario"""
        user_data = self.storage.get(f"user_2fa:{user_email}")
        if user_data:
            return user_data.get("method")
        return None
    
    def generate_backup_codes(self, user_email: str, count: int = 10) -> list:
        """Generar códigos de respaldo para 2FA"""
        try:
            import secrets
            backup_codes = []
            
            for _ in range(count):
                code = secrets.token_hex(4).upper()
                backup_codes.append(code)
            
            # Guardar códigos de respaldo
            self.storage[f"2fa_backup_codes:{user_email}"] = {
                "codes": backup_codes,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            self._save_storage()
            
            logger.info(f"Backup codes generated for {user_email}")
            return backup_codes
            
        except Exception as e:
            logger.error(f"Error generating backup codes: {e}")
            return []
    
    def verify_backup_code(self, user_email: str, code: str) -> bool:
        """Verificar código de respaldo"""
        try:
            stored_data = self.storage.get(f"2fa_backup_codes:{user_email}")
            if not stored_data:
                return False
            
            # Verificar expiración
            expires_at = datetime.fromisoformat(stored_data["expires_at"])
            if datetime.utcnow() > expires_at:
                del self.storage[f"2fa_backup_codes:{user_email}"]
                self._save_storage()
                return False
            
            backup_codes = stored_data["codes"]
            
            if code in backup_codes:
                # Eliminar código usado
                backup_codes.remove(code)
                if backup_codes:
                    self.storage[f"2fa_backup_codes:{user_email}"] = {
                        "codes": backup_codes,
                        "created_at": stored_data["created_at"],
                        "expires_at": stored_data["expires_at"]
                    }
                else:
                    del self.storage[f"2fa_backup_codes:{user_email}"]
                
                self._save_storage()
                logger.info(f"Backup code used for {user_email}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying backup code: {e}")
            return False
