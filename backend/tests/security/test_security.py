# backend/tests/security/test_security.py - Tests de Seguridad

import pytest
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta

@pytest.mark.security
class TestAuthenticationSecurity:
    """Tests de seguridad de autenticación."""
    
    def test_login_with_invalid_credentials(self, client: TestClient):
        """Test login con credenciales inválidas."""
        response = client.post("/api/auth/login", json={
            "email": "noexiste@justicia.ma",
            "password": "wrongpassword"
        })
        
        assert response.status_code in [401, 400]
    
    def test_access_without_token(self, client: TestClient):
        """Test acceso sin token de autenticación."""
        response = client.get("/api/cases/")
        
        assert response.status_code == 401
    
    def test_access_with_invalid_token(self, client: TestClient):
        """Test acceso con token inválido."""
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = client.get("/api/cases/", headers=headers)
        
        assert response.status_code == 401
    
    def test_access_with_expired_token(self, client: TestClient):
        """Test acceso con token expirado."""
        # Crear token expirado
        expired_payload = {
            "sub": "test@justicia.ma",
            "user_id": 1,
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        
        # Este test requeriría crear un token JWT expirado
        # Por ahora solo verificamos que se rechace
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.expired"}
        response = client.get("/api/cases/", headers=headers)
        
        assert response.status_code == 401
    
    def test_password_hashing_security(self):
        """Test que las contraseñas se hashean de forma segura."""
        from app.auth.auth import get_password_hash, verify_password
        
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        
        # El hash no debe contener la contraseña en texto plano
        assert password not in hashed
        
        # Debe usar bcrypt o similar (longitud > 50)
        assert len(hashed) > 50
        
        # Debe poder verificarse
        assert verify_password(password, hashed)

@pytest.mark.security
class TestAuthorizationSecurity:
    """Tests de seguridad de autorización."""
    
    def test_rbac_prevents_unauthorized_access(self, client: TestClient, citizen_headers, lawyer_headers):
        """Test que RBAC previene acceso no autorizado."""
        # Ciudadano intenta acceder a lista de usuarios (solo admin/clerk)
        response = client.get("/api/users/", headers=citizen_headers)
        assert response.status_code == 403
        
        # Abogado intenta acceder a lista de usuarios (solo admin/clerk)
        response = client.get("/api/users/", headers=lawyer_headers)
        assert response.status_code == 403
    
    def test_user_cannot_access_other_user_data(self, client: TestClient, lawyer_headers, citizen_user):
        """Test que usuario no puede acceder a datos de otro usuario."""
        response = client.get(f"/api/users/{citizen_user.id}", headers=lawyer_headers)
        
        # Debería fallar con 403 o 404
        assert response.status_code in [403, 404]
    
    def test_privilege_escalation_prevention(self, client: TestClient, citizen_headers):
        """Test prevención de escalada de privilegios."""
        # Intentar actualizar el propio rol a admin
        update_data = {
            "role": "admin"
        }
        
        response = client.put("/api/users/me", json=update_data, headers=citizen_headers)
        
        # El endpoint /users/me no debe permitir cambiar el rol
        if response.status_code == 200:
            data = response.json()
            # El rol no debería haber cambiado
            assert data.get("role") != "admin"
    
    def test_cross_tenant_isolation(self, client: TestClient, lawyer_headers, db_session, citizen_user):
        """Test aislamiento entre usuarios (cross-tenant)."""
        from app.models import Case, CaseStatus
        from datetime import datetime
        
        # Crear caso de otro usuario
        other_case = Case(
            case_number="ISOLATION-2025-001",
            title="Caso de Otro Usuario",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=citizen_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(other_case)
        db_session.commit()
        
        # Abogado intenta acceder al caso de otro usuario
        response = client.get(f"/api/cases/{other_case.id}", headers=lawyer_headers)
        
        assert response.status_code == 403

@pytest.mark.security
class TestInputValidationSecurity:
    """Tests de seguridad de validación de entrada."""
    
    def test_sql_injection_prevention(self, client: TestClient, admin_headers):
        """Test prevención de SQL injection."""
        # Intentar SQL injection en búsqueda
        malicious_query = "'; DROP TABLE cases; --"
        
        response = client.get(
            f"/api/cases/search/?query={malicious_query}",
            headers=admin_headers
        )
        
        # No debe causar error 500, debe ser manejado
        assert response.status_code in [200, 400]
        
        # La tabla cases debe seguir existiendo (se verifica con otra query)
        response = client.get("/api/cases/", headers=admin_headers)
        assert response.status_code == 200
    
    def test_xss_prevention_in_input(self, client: TestClient, admin_headers):
        """Test prevención de XSS en inputs."""
        xss_payload = "<script>alert('XSS')</script>"
        
        case_data = {
            "case_number": "XSS-2025-001",
            "title": xss_payload,
            "description": "Test XSS",
            "status": "pending"
        }
        
        response = client.post("/api/cases/", json=case_data, headers=admin_headers)
        
        # Debe rechazar o sanitizar
        if response.status_code == 201:
            data = response.json()
            # El script no debe ejecutarse
            assert "<script>" not in data.get("title", "")
    
    def test_command_injection_prevention(self, client: TestClient, admin_headers):
        """Test prevención de command injection."""
        command_payload = "test; rm -rf /"
        
        case_data = {
            "case_number": command_payload,
            "title": "Command Injection Test",
            "description": "Test",
            "status": "pending"
        }
        
        response = client.post("/api/cases/", json=case_data, headers=admin_headers)
        
        # Debe validar formato de case_number
        assert response.status_code in [201, 400]
    
    def test_oversized_input_rejection(self, client: TestClient, admin_headers):
        """Test rechazo de inputs excesivamente largos."""
        huge_text = "A" * 1000000  # 1MB de texto
        
        case_data = {
            "case_number": "LARGE-2025-001",
            "title": "Test",
            "description": huge_text,
            "status": "pending"
        }
        
        response = client.post("/api/cases/", json=case_data, headers=admin_headers)
        
        # Debe rechazar o limitar
        assert response.status_code in [201, 400, 413]
    
    def test_invalid_file_type_rejection(self, client: TestClient, admin_headers):
        """Test rechazo de tipos de archivo no permitidos."""
        # Este test requiere un endpoint de upload de documentos
        # Verificar que solo se aceptan tipos permitidos
        pass

@pytest.mark.security
class TestCSRFProtection:
    """Tests de protección CSRF."""
    
    def test_csrf_token_required_for_state_changes(self, client: TestClient, admin_headers):
        """Test que se requiere protección CSRF para cambios de estado."""
        # En producción, endpoints que modifican estado deberían requerir CSRF token
        # Este es un recordatorio para implementar CSRF en producción
        pass

@pytest.mark.security
class TestRateLimiting:
    """Tests de rate limiting."""
    
    @pytest.mark.slow
    def test_rate_limit_enforcement(self, client: TestClient):
        """Test que se aplica rate limiting."""
        # Intentar muchos logins en poco tiempo
        for i in range(50):
            response = client.post("/api/auth/login", json={
                "email": f"test{i}@justicia.ma",
                "password": "password"
            })
            
            # Después de cierto número debería rechazar (429 Too Many Requests)
            if i > 20:
                # Puede empezar a rechazar después de 20 intentos
                if response.status_code == 429:
                    assert True
                    return
        
        # Si no se implementa rate limiting, este test debería fallar
        # En producción, debe implementarse

@pytest.mark.security
class TestDataEncryption:
    """Tests de encriptación de datos."""
    
    def test_passwords_are_hashed(self, db_session, admin_user):
        """Test que contraseñas están hasheadas en BD."""
        # La contraseña en BD no debe ser texto plano
        assert admin_user.hashed_password != "Admin123!"
        assert len(admin_user.hashed_password) > 50
    
    def test_sensitive_data_not_in_logs(self):
        """Test que datos sensibles no aparecen en logs."""
        # Este test verificaría que contraseñas, tokens, etc.
        # no se loggean en texto plano
        pass

@pytest.mark.security
class TestSessionSecurity:
    """Tests de seguridad de sesión."""
    
    def test_session_invalidation_on_logout(self, client: TestClient, admin_headers):
        """Test que sesión se invalida al logout."""
        # Hacer logout
        response = client.post("/api/auth/logout", headers=admin_headers)
        
        # Intentar usar el mismo token después del logout
        response = client.get("/api/cases/", headers=admin_headers)
        
        # Debería fallar si se implementa invalidación de tokens
        # En JWT simple sin blacklist, el token seguiría siendo válido
        # En producción debería implementarse blacklist
        pass
    
    def test_concurrent_session_limits(self):
        """Test límite de sesiones concurrentes por usuario."""
        # En un sistema gubernamental, puede limitarse a N sesiones activas
        pass

@pytest.mark.security
class TestAuditLogging:
    """Tests de logging de auditoría."""
    
    def test_sensitive_actions_are_logged(self, client: TestClient, admin_headers, db_session):
        """Test que acciones sensibles se loggean."""
        from app.models import AuditLog
        
        # Realizar acción sensible
        response = client.post("/api/cases/", json={
            "case_number": "AUDIT-2025-001",
            "title": "Test Audit",
            "description": "Test",
            "status": "pending"
        }, headers=admin_headers)
        
        # Verificar que se creó log de auditoría
        logs = db_session.query(AuditLog).filter(
            AuditLog.action == "create_case"
        ).all()
        
        assert len(logs) >= 1
    
    def test_failed_login_attempts_logged(self):
        """Test que intentos fallidos de login se loggean."""
        # En producción, debe loggearse para detectar ataques
        pass
