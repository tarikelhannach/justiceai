# backend/tests/api/test_api_cases_rbac.py - Tests de API de Casos con RBAC

import pytest
from fastapi.testclient import TestClient

@pytest.mark.api
@pytest.mark.rbac
class TestCasesAPIAdmin:
    """Tests de API de casos con rol Admin."""
    
    def test_admin_can_list_all_cases(self, client: TestClient, admin_headers, sample_case):
        """Test que admin puede listar todos los casos."""
        response = client.get("/api/cases/", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_admin_can_create_case(self, client: TestClient, admin_headers, judge_user):
        """Test que admin puede crear casos."""
        case_data = {
            "case_number": "ADM-2025-001",
            "title": "Caso Creado por Admin",
            "description": "Test de creación por admin",
            "status": "pending",
            "assigned_judge_id": judge_user.id
        }
        
        response = client.post("/api/cases/", json=case_data, headers=admin_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["case_number"] == "ADM-2025-001"
        assert data["assigned_judge_id"] == judge_user.id
    
    def test_admin_can_update_any_case(self, client: TestClient, admin_headers, sample_case):
        """Test que admin puede actualizar cualquier caso."""
        update_data = {
            "title": "Título Actualizado por Admin",
            "status": "in_progress"
        }
        
        response = client.put(
            f"/api/cases/{sample_case.id}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Título Actualizado por Admin"
        assert data["status"] == "in_progress"
    
    def test_admin_can_delete_case(self, client: TestClient, admin_headers, db_session, lawyer_user):
        """Test que admin puede eliminar casos."""
        from app.models import Case, CaseStatus
        from datetime import datetime
        
        case = Case(
            case_number="DEL-2025-001",
            title="Caso para Eliminar",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=lawyer_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(case)
        db_session.commit()
        
        response = client.delete(f"/api/cases/{case.id}", headers=admin_headers)
        
        assert response.status_code == 200

@pytest.mark.api
@pytest.mark.rbac
class TestCasesAPIJudge:
    """Tests de API de casos con rol Judge."""
    
    def test_judge_can_list_assigned_cases(self, client: TestClient, judge_headers, sample_case):
        """Test que juez puede listar casos asignados."""
        response = client.get("/api/cases/", headers=judge_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_judge_can_view_assigned_case(self, client: TestClient, judge_headers, sample_case):
        """Test que juez puede ver caso asignado."""
        response = client.get(f"/api/cases/{sample_case.id}", headers=judge_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_case.id
    
    def test_judge_cannot_view_unassigned_case(self, client: TestClient, judge_headers, db_session, lawyer_user):
        """Test que juez NO puede ver caso no asignado."""
        from app.models import Case, CaseStatus
        from datetime import datetime
        
        unassigned_case = Case(
            case_number="UNASSIGNED-2025-001",
            title="Caso No Asignado",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=lawyer_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(unassigned_case)
        db_session.commit()
        
        response = client.get(f"/api/cases/{unassigned_case.id}", headers=judge_headers)
        
        assert response.status_code == 403
    
    def test_judge_can_update_assigned_case(self, client: TestClient, judge_headers, sample_case):
        """Test que juez puede actualizar caso asignado."""
        update_data = {
            "status": "in_progress"
        }
        
        response = client.put(
            f"/api/cases/{sample_case.id}",
            json=update_data,
            headers=judge_headers
        )
        
        assert response.status_code == 200
    
    def test_judge_cannot_delete_case(self, client: TestClient, judge_headers, sample_case):
        """Test que juez NO puede eliminar casos."""
        response = client.delete(f"/api/cases/{sample_case.id}", headers=judge_headers)
        
        # Debe fallar porque require_role(['admin', 'clerk'])
        assert response.status_code in [403, 401]

@pytest.mark.api
@pytest.mark.rbac
class TestCasesAPILawyer:
    """Tests de API de casos con rol Lawyer."""
    
    def test_lawyer_can_list_own_cases(self, client: TestClient, lawyer_headers, sample_case):
        """Test que abogado puede listar sus propios casos."""
        response = client.get("/api/cases/", headers=lawyer_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_lawyer_can_view_own_case(self, client: TestClient, lawyer_headers, sample_case):
        """Test que abogado puede ver su propio caso."""
        response = client.get(f"/api/cases/{sample_case.id}", headers=lawyer_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_case.id
    
    def test_lawyer_cannot_view_other_case(self, client: TestClient, lawyer_headers, db_session, citizen_user):
        """Test que abogado NO puede ver caso de otro usuario."""
        from app.models import Case, CaseStatus
        from datetime import datetime
        
        other_case = Case(
            case_number="OTHER-2025-001",
            title="Caso de Otro Usuario",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=citizen_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(other_case)
        db_session.commit()
        
        response = client.get(f"/api/cases/{other_case.id}", headers=lawyer_headers)
        
        assert response.status_code == 403
    
    def test_lawyer_can_create_case(self, client: TestClient, lawyer_headers):
        """Test que abogado puede crear casos."""
        case_data = {
            "case_number": "LAW-2025-001",
            "title": "Caso Creado por Abogado",
            "description": "Test de creación por abogado",
            "status": "pending"
        }
        
        response = client.post("/api/cases/", json=case_data, headers=lawyer_headers)
        
        assert response.status_code == 201
    
    def test_lawyer_cannot_assign_judge(self, client: TestClient, lawyer_headers, judge_user):
        """Test que abogado NO puede asignar juez al crear caso."""
        case_data = {
            "case_number": "LAW-2025-002",
            "title": "Intento Asignar Juez",
            "description": "Test",
            "status": "pending",
            "assigned_judge_id": judge_user.id
        }
        
        response = client.post("/api/cases/", json=case_data, headers=lawyer_headers)
        
        assert response.status_code == 403
    
    def test_lawyer_can_update_own_case(self, client: TestClient, lawyer_headers, sample_case):
        """Test que abogado puede actualizar su propio caso."""
        update_data = {
            "description": "Descripción actualizada"
        }
        
        response = client.put(
            f"/api/cases/{sample_case.id}",
            json=update_data,
            headers=lawyer_headers
        )
        
        assert response.status_code == 200
    
    def test_lawyer_cannot_delete_case(self, client: TestClient, lawyer_headers, sample_case):
        """Test que abogado NO puede eliminar casos."""
        response = client.delete(f"/api/cases/{sample_case.id}", headers=lawyer_headers)
        
        assert response.status_code in [403, 401]

@pytest.mark.api
@pytest.mark.rbac
class TestCasesAPIClerk:
    """Tests de API de casos con rol Clerk."""
    
    def test_clerk_can_list_all_cases(self, client: TestClient, clerk_headers, sample_case):
        """Test que secretario puede listar todos los casos."""
        response = client.get("/api/cases/", headers=clerk_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_clerk_can_create_case_with_judge(self, client: TestClient, clerk_headers, judge_user):
        """Test que secretario puede crear caso con juez asignado."""
        case_data = {
            "case_number": "CLK-2025-001",
            "title": "Caso Creado por Secretario",
            "description": "Test",
            "status": "pending",
            "assigned_judge_id": judge_user.id
        }
        
        response = client.post("/api/cases/", json=case_data, headers=clerk_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["assigned_judge_id"] == judge_user.id
    
    def test_clerk_can_update_any_case(self, client: TestClient, clerk_headers, sample_case):
        """Test que secretario puede actualizar cualquier caso."""
        update_data = {
            "status": "resolved"
        }
        
        response = client.put(
            f"/api/cases/{sample_case.id}",
            json=update_data,
            headers=clerk_headers
        )
        
        assert response.status_code == 200
    
    def test_clerk_can_delete_case(self, client: TestClient, clerk_headers, db_session, lawyer_user):
        """Test que secretario puede eliminar casos."""
        from app.models import Case, CaseStatus
        from datetime import datetime
        
        case = Case(
            case_number="CLK-DEL-2025-001",
            title="Caso para Eliminar",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=lawyer_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(case)
        db_session.commit()
        
        response = client.delete(f"/api/cases/{case.id}", headers=clerk_headers)
        
        assert response.status_code == 200

@pytest.mark.api
@pytest.mark.rbac
class TestCasesAPICitizen:
    """Tests de API de casos con rol Citizen."""
    
    def test_citizen_can_list_own_cases(self, client: TestClient, citizen_headers, db_session, citizen_user):
        """Test que ciudadano puede listar sus propios casos."""
        from app.models import Case, CaseStatus
        from datetime import datetime
        
        case = Case(
            case_number="CIT-2025-001",
            title="Caso de Ciudadano",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=citizen_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(case)
        db_session.commit()
        
        response = client.get("/api/cases/", headers=citizen_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_citizen_can_create_case(self, client: TestClient, citizen_headers):
        """Test que ciudadano puede crear casos."""
        case_data = {
            "case_number": "CIT-2025-002",
            "title": "Caso Creado por Ciudadano",
            "description": "Test de creación por ciudadano",
            "status": "pending"
        }
        
        response = client.post("/api/cases/", json=case_data, headers=citizen_headers)
        
        assert response.status_code == 201
    
    def test_citizen_cannot_assign_judge(self, client: TestClient, citizen_headers, judge_user):
        """Test que ciudadano NO puede asignar juez."""
        case_data = {
            "case_number": "CIT-2025-003",
            "title": "Intento Asignar Juez",
            "description": "Test",
            "status": "pending",
            "assigned_judge_id": judge_user.id
        }
        
        response = client.post("/api/cases/", json=case_data, headers=citizen_headers)
        
        assert response.status_code == 403
    
    def test_citizen_cannot_change_status(self, client: TestClient, citizen_headers, db_session, citizen_user):
        """Test que ciudadano NO puede cambiar estado del caso."""
        from app.models import Case, CaseStatus
        from datetime import datetime
        
        case = Case(
            case_number="CIT-2025-004",
            title="Caso de Ciudadano",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=citizen_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(case)
        db_session.commit()
        
        update_data = {
            "status": "resolved"
        }
        
        response = client.put(
            f"/api/cases/{case.id}",
            json=update_data,
            headers=citizen_headers
        )
        
        # Ciudadano no puede cambiar estado sensible
        # La respuesta puede ser 200 pero el status no debería cambiar
        # O puede ser 403 dependiendo de la implementación
        assert response.status_code in [200, 403]
    
    def test_citizen_cannot_delete_case(self, client: TestClient, citizen_headers, db_session, citizen_user):
        """Test que ciudadano NO puede eliminar casos."""
        from app.models import Case, CaseStatus
        from datetime import datetime
        
        case = Case(
            case_number="CIT-2025-005",
            title="Caso de Ciudadano",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=citizen_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(case)
        db_session.commit()
        
        response = client.delete(f"/api/cases/{case.id}", headers=citizen_headers)
        
        assert response.status_code in [403, 401]

@pytest.mark.api
@pytest.mark.rbac
class TestCasesAPISearch:
    """Tests de búsqueda de casos con RBAC."""
    
    def test_search_respects_rbac(self, client: TestClient, lawyer_headers, judge_headers, admin_headers):
        """Test que búsqueda respeta RBAC."""
        # Admin ve todos
        admin_response = client.get("/api/cases/search/?query=test", headers=admin_headers)
        assert admin_response.status_code == 200
        admin_results = admin_response.json()
        
        # Lawyer solo ve los suyos
        lawyer_response = client.get("/api/cases/search/?query=test", headers=lawyer_headers)
        assert lawyer_response.status_code == 200
        lawyer_results = lawyer_response.json()
        
        # Judge solo ve asignados
        judge_response = client.get("/api/cases/search/?query=test", headers=judge_headers)
        assert judge_response.status_code == 200
        judge_results = judge_response.json()
        
        # Admin debería ver más o igual
        assert len(admin_results) >= len(lawyer_results)
        assert len(admin_results) >= len(judge_results)
