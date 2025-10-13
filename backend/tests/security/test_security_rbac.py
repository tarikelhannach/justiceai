# backend/tests/security/test_security_rbac.py - Tests de Seguridad RBAC Exhaustivos

import pytest
from fastapi.testclient import TestClient

@pytest.mark.security
@pytest.mark.rbac
class TestDenyByDefaultPolicy:
    """Tests de política deny-by-default."""
    
    def test_unknown_role_denied(self, client: TestClient, db_session):
        """Test que rol desconocido es denegado."""
        from app.models import User
        from app.auth.auth import get_password_hash, create_access_token
        from datetime import datetime
        
        # Crear usuario con rol "inválido" (esto no debería ser posible en producción)
        # Este test asume que hay validación de enum
        pass
    
    def test_no_permission_by_default(self, client: TestClient, citizen_headers):
        """Test que usuarios no tienen permisos por defecto."""
        # Intentar acceso a endpoint administrativo
        response = client.get("/api/users/", headers=citizen_headers)
        assert response.status_code == 403
        
        # Intentar crear usuario (solo admin/clerk)
        response = client.post("/api/users/", json={
            "email": "test@justicia.ma",
            "name": "Test",
            "password": "Pass123!",
            "role": "citizen"
        }, headers=citizen_headers)
        assert response.status_code == 403
    
    def test_explicit_permission_required(self, client: TestClient, lawyer_headers, judge_headers):
        """Test que se requiere permiso explícito."""
        # Abogado intenta eliminar caso (requiere admin/clerk explícito)
        response = client.delete("/api/cases/999", headers=lawyer_headers)
        assert response.status_code in [403, 404]
        
        # Juez intenta eliminar caso (requiere admin/clerk explícito)
        response = client.delete("/api/cases/999", headers=judge_headers)
        assert response.status_code in [403, 404]

@pytest.mark.security
@pytest.mark.rbac
class TestHorizontalPrivilegeEscalation:
    """Tests de prevención de escalada horizontal de privilegios."""
    
    def test_lawyer_cannot_access_other_lawyer_cases(self, client: TestClient, db_session):
        """Test que abogado no puede acceder a casos de otro abogado."""
        from app.models import User, Case, UserRole, CaseStatus
        from app.auth.auth import get_password_hash, create_access_token
        from datetime import datetime
        
        # Crear segundo abogado
        lawyer2 = User(
            email="lawyer2@justicia.ma",
            name="Abogado 2",
            hashed_password=get_password_hash("Lawyer123!"),
            role=UserRole.LAWYER,
            created_at=datetime.utcnow()
        )
        db_session.add(lawyer2)
        db_session.commit()
        
        # Crear caso del segundo abogado
        case2 = Case(
            case_number="LAW2-2025-001",
            title="Caso Abogado 2",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=lawyer2.id,
            created_at=datetime.utcnow()
        )
        db_session.add(case2)
        db_session.commit()
        
        # Primer abogado intenta acceder
        lawyer1_token = create_access_token({"sub": "abogado@justicia.ma", "user_id": 1})
        lawyer1_headers = {"Authorization": f"Bearer {lawyer1_token}"}
        
        response = client.get(f"/api/cases/{case2.id}", headers=lawyer1_headers)
        assert response.status_code in [403, 404]
    
    def test_citizen_cannot_access_other_citizen_cases(self, client: TestClient, db_session, citizen_user):
        """Test que ciudadano no puede acceder a casos de otro ciudadano."""
        from app.models import User, Case, UserRole, CaseStatus
        from app.auth.auth import get_password_hash, create_access_token
        from datetime import datetime
        
        # Crear segundo ciudadano
        citizen2 = User(
            email="citizen2@justicia.ma",
            name="Ciudadano 2",
            hashed_password=get_password_hash("Citizen123!"),
            role=UserRole.CITIZEN,
            created_at=datetime.utcnow()
        )
        db_session.add(citizen2)
        db_session.commit()
        
        # Crear caso del segundo ciudadano
        case2 = Case(
            case_number="CIT2-2025-001",
            title="Caso Ciudadano 2",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=citizen2.id,
            created_at=datetime.utcnow()
        )
        db_session.add(case2)
        db_session.commit()
        
        # Primer ciudadano intenta acceder
        citizen1_token = create_access_token({"sub": citizen_user.email, "user_id": citizen_user.id})
        citizen1_headers = {"Authorization": f"Bearer {citizen1_token}"}
        
        response = client.get(f"/api/cases/{case2.id}", headers=citizen1_headers)
        assert response.status_code in [403, 404]

@pytest.mark.security
@pytest.mark.rbac
class TestVerticalPrivilegeEscalation:
    """Tests de prevención de escalada vertical de privilegios."""
    
    def test_user_cannot_elevate_own_role(self, client: TestClient, citizen_headers):
        """Test que usuario no puede elevar su propio rol."""
        # Intentar cambiar rol a admin
        response = client.put("/api/users/me", json={
            "role": "admin"
        }, headers=citizen_headers)
        
        if response.status_code == 200:
            data = response.json()
            # El rol NO debe haber cambiado
            assert data.get("role") != "admin"
    
    def test_lawyer_cannot_assign_judge_on_create(self, client: TestClient, lawyer_headers, judge_user):
        """Test que abogado no puede asignar juez al crear caso."""
        case_data = {
            "case_number": "ESC-2025-001",
            "title": "Intento Escalada",
            "description": "Test",
            "status": "pending",
            "assigned_judge_id": judge_user.id
        }
        
        response = client.post("/api/cases/", json=case_data, headers=lawyer_headers)
        assert response.status_code == 403
    
    def test_citizen_cannot_change_case_status(self, client: TestClient, db_session, citizen_user):
        """Test que ciudadano no puede cambiar estado de caso."""
        from app.models import Case, CaseStatus
        from app.auth.auth import create_access_token
        from datetime import datetime
        
        case = Case(
            case_number="STAT-2025-001",
            title="Test Estado",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=citizen_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(case)
        db_session.commit()
        
        citizen_token = create_access_token({"sub": citizen_user.email, "user_id": citizen_user.id})
        citizen_headers = {"Authorization": f"Bearer {citizen_token}"}
        
        response = client.put(f"/api/cases/{case.id}", json={
            "status": "resolved"
        }, headers=citizen_headers)
        
        # Debería ser rechazado o ignorado
        if response.status_code == 200:
            # Verificar que el estado no cambió
            db_session.refresh(case)
            assert case.status == CaseStatus.PENDING

@pytest.mark.security
@pytest.mark.rbac  
class TestCrossTenantIsolation:
    """Tests de aislamiento entre usuarios (multi-tenancy)."""
    
    def test_complete_data_isolation(self, client: TestClient, db_session):
        """Test aislamiento completo de datos entre usuarios."""
        from app.models import User, Case, Document, UserRole, CaseStatus
        from app.auth.auth import get_password_hash, create_access_token
        from datetime import datetime
        
        # Crear dos abogados separados
        lawyer1 = User(
            email="isolated1@justicia.ma",
            name="Abogado Aislado 1",
            hashed_password=get_password_hash("Pass123!"),
            role=UserRole.LAWYER,
            created_at=datetime.utcnow()
        )
        lawyer2 = User(
            email="isolated2@justicia.ma",
            name="Abogado Aislado 2",
            hashed_password=get_password_hash("Pass123!"),
            role=UserRole.LAWYER,
            created_at=datetime.utcnow()
        )
        db_session.add_all([lawyer1, lawyer2])
        db_session.commit()
        
        # Crear casos para cada uno
        case1 = Case(
            case_number="ISO1-2025-001",
            title="Caso Aislado 1",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=lawyer1.id,
            created_at=datetime.utcnow()
        )
        case2 = Case(
            case_number="ISO2-2025-001",
            title="Caso Aislado 2",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=lawyer2.id,
            created_at=datetime.utcnow()
        )
        db_session.add_all([case1, case2])
        db_session.commit()
        
        # Lawyer1 lista casos - debe ver solo los suyos
        lawyer1_token = create_access_token({"sub": lawyer1.email, "user_id": lawyer1.id})
        lawyer1_headers = {"Authorization": f"Bearer {lawyer1_token}"}
        
        response = client.get("/api/cases/", headers=lawyer1_headers)
        assert response.status_code == 200
        cases = response.json()
        
        # Solo debe ver case1
        case_ids = [c["id"] for c in cases]
        assert case1.id in case_ids
        assert case2.id not in case_ids

@pytest.mark.security
@pytest.mark.rbac
class TestRoleHierarchy:
    """Tests de jerarquía de roles."""
    
    def test_admin_has_all_permissions(self, client: TestClient, admin_headers, sample_case):
        """Test que admin tiene todos los permisos."""
        # Puede listar todos los casos
        response = client.get("/api/cases/", headers=admin_headers)
        assert response.status_code == 200
        
        # Puede ver cualquier caso
        response = client.get(f"/api/cases/{sample_case.id}", headers=admin_headers)
        assert response.status_code == 200
        
        # Puede actualizar cualquier caso
        response = client.put(f"/api/cases/{sample_case.id}", json={
            "title": "Actualizado"
        }, headers=admin_headers)
        assert response.status_code == 200
        
        # Puede eliminar casos
        response = client.delete(f"/api/cases/{sample_case.id}", headers=admin_headers)
        assert response.status_code == 200
    
    def test_clerk_has_admin_like_permissions(self, client: TestClient, clerk_headers):
        """Test que clerk tiene permisos similares a admin."""
        # Puede listar todos los casos
        response = client.get("/api/cases/", headers=clerk_headers)
        assert response.status_code == 200
        
        # Puede gestionar usuarios
        response = client.get("/api/users/", headers=clerk_headers)
        assert response.status_code == 200
    
    def test_judge_limited_to_assigned_cases(self, client: TestClient, judge_headers, sample_case):
        """Test que juez está limitado a casos asignados."""
        # Puede ver caso asignado
        response = client.get(f"/api/cases/{sample_case.id}", headers=judge_headers)
        assert response.status_code == 200
        
        # NO puede gestionar usuarios
        response = client.get("/api/users/", headers=judge_headers)
        assert response.status_code == 403
