# backend/tests/api/test_api_auth.py - Tests de API de Autenticación

import pytest
from fastapi.testclient import TestClient

@pytest.mark.api
class TestAuthAPI:
    """Tests de API de autenticación."""
    
    def test_login_success(self, client: TestClient, admin_user):
        """Test login exitoso."""
        response = client.post("/api/auth/login", json={
            "email": admin_user.email,
            "password": "Admin123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_email(self, client: TestClient):
        """Test login con email inválido."""
        response = client.post("/api/auth/login", json={
            "email": "noexiste@justicia.ma",
            "password": "Password123!"
        })
        
        assert response.status_code in [401, 400]
    
    def test_login_invalid_password(self, client: TestClient, admin_user):
        """Test login con contraseña incorrecta."""
        response = client.post("/api/auth/login", json={
            "email": admin_user.email,
            "password": "WrongPassword"
        })
        
        assert response.status_code == 401
    
    def test_login_missing_fields(self, client: TestClient):
        """Test login con campos faltantes."""
        response = client.post("/api/auth/login", json={
            "email": "test@justicia.ma"
        })
        
        assert response.status_code == 422
    
    def test_protected_endpoint_without_auth(self, client: TestClient):
        """Test acceso a endpoint protegido sin autenticación."""
        response = client.get("/api/cases/")
        
        assert response.status_code == 401
    
    def test_protected_endpoint_with_auth(self, client: TestClient, admin_headers):
        """Test acceso a endpoint protegido con autenticación."""
        response = client.get("/api/cases/", headers=admin_headers)
        
        assert response.status_code == 200
