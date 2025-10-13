# backend/tests/unit/test_auth.py - Tests Unitarios de Autenticación

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

from app.auth.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.auth.two_factor import TwoFactorAuth
from app.auth.utils import (
    generate_verification_code,
    store_verification_code,
    verify_verification_code
)

class TestPasswordHashing:
    """Tests para hash de contraseñas."""
    
    def test_password_hashing(self):
        """Test hashing de contraseña."""
        password = "TestPassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
    
    def test_password_verification(self):
        """Test verificación de contraseña."""
        password = "TestPassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False
        assert verify_password("", hashed) is False

class TestTokenGeneration:
    """Tests para generación de tokens."""
    
    def test_create_access_token(self):
        """Test creación de token de acceso."""
        data = {"sub": "test@justicia.ma", "user_id": 1}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """Test creación de token de renovación."""
        data = {"sub": "test@justicia.ma", "user_id": 1}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token(self):
        """Test verificación de token."""
        data = {"sub": "test@justicia.ma", "user_id": 1}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload["sub"] == "test@justicia.ma"
        assert payload["user_id"] == 1
    
    def test_verify_invalid_token(self):
        """Test verificación de token inválido."""
        with pytest.raises(Exception):
            verify_token("invalid_token")

class TestTwoFactorAuth:
    """Tests para autenticación de dos factores."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.two_factor = TwoFactorAuth()
    
    def test_generate_secret_key(self):
        """Test generación de clave secreta."""
        email = "test@justicia.ma"
        secret = self.two_factor.generate_secret_key(email)
        
        assert isinstance(secret, str)
        assert len(secret) > 0
    
    def test_generate_qr_code(self):
        """Test generación de código QR."""
        email = "test@justicia.ma"
        secret = self.two_factor.generate_secret_key(email)
        qr_code = self.two_factor.generate_qr_code(email, secret)
        
        assert isinstance(qr_code, str)
        assert qr_code.startswith("data:image/png;base64,")
    
    @patch('app.auth.two_factor.TwoFactorAuth.redis_client')
    def test_verify_totp_code(self, mock_redis):
        """Test verificación de código TOTP."""
        mock_redis.get.return_value = None
        
        email = "test@justicia.ma"
        secret = "JBSWY3DPEHPK3PXP"
        code = "123456"
        
        # Mock de verificación exitosa
        with patch('pyotp.TOTP.verify') as mock_verify:
            mock_verify.return_value = True
            
            result = self.two_factor.verify_totp_code(secret, code, email)
            assert result is True
    
    @patch('app.auth.two_factor.TwoFactorAuth.redis_client')
    def test_verify_sms_code(self, mock_redis):
        """Test verificación de código SMS."""
        import json
        
        email = "test@justicia.ma"
        code = "123456"
        
        # Mock de datos guardados
        stored_data = json.dumps({
            "code": code,
            "phone": "+212600000000",
            "created_at": datetime.utcnow().isoformat()
        })
        mock_redis.get.return_value = stored_data
        
        result = self.two_factor.verify_sms_code(email, code)
        assert result is True

class TestVerificationUtils:
    """Tests para utilidades de verificación."""
    
    def test_generate_verification_code(self):
        """Test generación de código de verificación."""
        code = generate_verification_code()
        
        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isalnum()
    
    def test_generate_numeric_code(self):
        """Test generación de código numérico."""
        from app.auth.utils import generate_numeric_code
        
        code = generate_numeric_code()
        
        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()
    
    @patch('app.auth.utils.redis.from_url')
    def test_store_verification_code(self, mock_redis_class):
        """Test almacenamiento de código de verificación."""
        mock_redis = Mock()
        mock_redis_class.return_value = mock_redis
        
        email = "test@justicia.ma"
        code = "ABC123"
        
        result = store_verification_code(email, code)
        assert result is True
        mock_redis.setex.assert_called_once()
    
    @patch('app.auth.utils.redis.from_url')
    def test_verify_verification_code(self, mock_redis_class):
        """Test verificación de código de verificación."""
        import json
        
        mock_redis = Mock()
        mock_redis_class.return_value = mock_redis
        
        email = "test@justicia.ma"
        code = "ABC123"
        
        # Mock de datos guardados
        stored_data = json.dumps({
            "code": code,
            "email": email,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=15)).isoformat()
        })
        mock_redis.get.return_value = stored_data
        
        result = verify_verification_code(email, code)
        assert result is True

class TestSecurityFeatures:
    """Tests para características de seguridad."""
    
    def test_password_strength_validation(self):
        """Test validación de fortaleza de contraseña."""
        from app.routes.schemas import UserCreate
        
        # Contraseña válida
        valid_data = {
            "email": "test@justicia.ma",
            "name": "Test User",
            "password": "StrongPassword123",
            "role": "citizen"
        }
        
        user = UserCreate(**valid_data)
        assert user.password == "StrongPassword123"
        
        # Contraseña débil
        weak_data = {
            "email": "test@justicia.ma",
            "name": "Test User",
            "password": "weak",
            "role": "citizen"
        }
        
        with pytest.raises(ValueError):
            UserCreate(**weak_data)
    
    def test_email_validation(self):
        """Test validación de email."""
        from app.routes.schemas import UserCreate
        
        # Email válido
        valid_data = {
            "email": "test@justicia.ma",
            "name": "Test User",
            "password": "StrongPassword123",
            "role": "citizen"
        }
        
        user = UserCreate(**valid_data)
        assert user.email == "test@justicia.ma"
        
        # Email inválido
        invalid_data = {
            "email": "invalid-email",
            "name": "Test User",
            "password": "StrongPassword123",
            "role": "citizen"
        }
        
        with pytest.raises(ValueError):
            UserCreate(**invalid_data)

@pytest.mark.slow
class TestPerformance:
    """Tests de performance para autenticación."""
    
    def test_password_hashing_performance(self):
        """Test performance de hash de contraseñas."""
        import time
        
        password = "TestPassword123"
        
        start_time = time.time()
        for _ in range(100):
            get_password_hash(password)
        end_time = time.time()
        
        # Debe completarse en menos de 5 segundos
        assert (end_time - start_time) < 5.0
    
    def test_token_generation_performance(self):
        """Test performance de generación de tokens."""
        import time
        
        data = {"sub": "test@justicia.ma", "user_id": 1}
        
        start_time = time.time()
        for _ in range(1000):
            create_access_token(data)
        end_time = time.time()
        
        # Debe completarse en menos de 1 segundo
        assert (end_time - start_time) < 1.0
