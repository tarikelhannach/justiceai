# backend/tests/api/test_api_users_rbac.py - Tests de API de Usuarios con RBAC

import pytest
from fastapi.testclient import TestClient

@pytest.mark.api
@pytest.mark.rbac
class TestUsersAPIAdmin:
    """Tests de API de usuarios con rol Admin."""
    
    def test_admin_can_list_all_users(self, client: TestClient, admin_headers):
        """Test que admin puede listar todos los usuarios."""
        response = client.get("/api/users/", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_admin_can_create_user(self, client: TestClient, admin_headers):
        """Test que admin puede crear usuarios."""
        user_data = {
            "email": "nuevo.admin@justicia.ma",
            "name": "Nuevo Usuario Admin",
            "password": "SecurePass123!",
            "role": "citizen"
        }
        
        response = client.post("/api/users/", json=user_data, headers=admin_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "nuevo.admin@justicia.ma"
        assert data["role"] == "citizen"
    
    def test_admin_can_update_user(self, client: TestClient, admin_headers, citizen_user):
        """Test que admin puede actualizar usuarios."""
        update_data = {
            "name": "Nombre Actualizado",
            "role": "lawyer"
        }
        
        response = client.put(
            f"/api/users/{citizen_user.id}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nombre Actualizado"
        assert data["role"] == "lawyer"
    
    def test_admin_can_delete_user(self, client: TestClient, admin_headers, db_session):
        """Test que admin puede eliminar usuarios."""
        from app.models import User, UserRole
        from datetime import datetime
        from app.auth.auth import get_password_hash
        
        user = User(
            email="delete@justicia.ma",
            name="To Delete",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.CITIZEN,
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.delete(f"/api/users/{user.id}", headers=admin_headers)
        
        assert response.status_code == 204
    
    def test_admin_cannot_delete_self(self, client: TestClient, admin_headers, admin_user):
        """Test que admin NO puede eliminarse a sí mismo."""
        response = client.delete(f"/api/users/{admin_user.id}", headers=admin_headers)
        
        assert response.status_code == 400

@pytest.mark.api
@pytest.mark.rbac
class TestUsersAPIClerk:
    """Tests de API de usuarios con rol Clerk."""
    
    def test_clerk_can_list_all_users(self, client: TestClient, clerk_headers):
        """Test que secretario puede listar todos los usuarios."""
        response = client.get("/api/users/", headers=clerk_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_clerk_can_create_user(self, client: TestClient, clerk_headers):
        """Test que secretario puede crear usuarios."""
        user_data = {
            "email": "nuevo.clerk@justicia.ma",
            "name": "Nuevo Usuario Clerk",
            "password": "SecurePass123!",
            "role": "citizen"
        }
        
        response = client.post("/api/users/", json=user_data, headers=clerk_headers)
        
        assert response.status_code == 201
    
    def test_clerk_can_update_user(self, client: TestClient, clerk_headers, citizen_user):
        """Test que secretario puede actualizar usuarios."""
        update_data = {
            "name": "Actualizado por Clerk"
        }
        
        response = client.put(
            f"/api/users/{citizen_user.id}",
            json=update_data,
            headers=clerk_headers
        )
        
        assert response.status_code == 200

@pytest.mark.api
@pytest.mark.rbac
class TestUsersAPIJudge:
    """Tests de API de usuarios con rol Judge."""
    
    def test_judge_cannot_list_users(self, client: TestClient, judge_headers):
        """Test que juez NO puede listar usuarios."""
        response = client.get("/api/users/", headers=judge_headers)
        
        assert response.status_code == 403
    
    def test_judge_cannot_create_user(self, client: TestClient, judge_headers):
        """Test que juez NO puede crear usuarios."""
        user_data = {
            "email": "intento.judge@justicia.ma",
            "name": "Intento",
            "password": "Pass123!",
            "role": "citizen"
        }
        
        response = client.post("/api/users/", json=user_data, headers=judge_headers)
        
        assert response.status_code == 403
    
    def test_judge_can_access_own_profile(self, client: TestClient, judge_headers):
        """Test que juez puede acceder a su propio perfil."""
        response = client.get("/api/users/me", headers=judge_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "judge"
    
    def test_judge_can_update_own_profile(self, client: TestClient, judge_headers):
        """Test que juez puede actualizar su propio perfil."""
        update_data = {
            "name": "Juez Actualizado"
        }
        
        response = client.put("/api/users/me", json=update_data, headers=judge_headers)
        
        assert response.status_code == 200

@pytest.mark.api
@pytest.mark.rbac
class TestUsersAPILawyer:
    """Tests de API de usuarios con rol Lawyer."""
    
    def test_lawyer_cannot_list_users(self, client: TestClient, lawyer_headers):
        """Test que abogado NO puede listar usuarios."""
        response = client.get("/api/users/", headers=lawyer_headers)
        
        assert response.status_code == 403
    
    def test_lawyer_cannot_create_user(self, client: TestClient, lawyer_headers):
        """Test que abogado NO puede crear usuarios."""
        user_data = {
            "email": "intento.lawyer@justicia.ma",
            "name": "Intento",
            "password": "Pass123!",
            "role": "citizen"
        }
        
        response = client.post("/api/users/", json=user_data, headers=lawyer_headers)
        
        assert response.status_code == 403
    
    def test_lawyer_can_access_own_profile(self, client: TestClient, lawyer_headers):
        """Test que abogado puede acceder a su propio perfil."""
        response = client.get("/api/users/me", headers=lawyer_headers)
        
        assert response.status_code == 200
    
    def test_lawyer_can_update_own_profile(self, client: TestClient, lawyer_headers):
        """Test que abogado puede actualizar su propio perfil."""
        update_data = {
            "name": "Abogado Actualizado"
        }
        
        response = client.put("/api/users/me", json=update_data, headers=lawyer_headers)
        
        assert response.status_code == 200
    
    def test_lawyer_cannot_change_own_role(self, client: TestClient, lawyer_headers):
        """Test que abogado NO puede cambiar su propio rol."""
        update_data = {
            "role": "admin"
        }
        
        response = client.put("/api/users/me", json=update_data, headers=lawyer_headers)
        
        # El rol no debería cambiar
        if response.status_code == 200:
            data = response.json()
            assert data["role"] == "lawyer"

@pytest.mark.api
@pytest.mark.rbac
class TestUsersAPICitizen:
    """Tests de API de usuarios con rol Citizen."""
    
    def test_citizen_cannot_list_users(self, client: TestClient, citizen_headers):
        """Test que ciudadano NO puede listar usuarios."""
        response = client.get("/api/users/", headers=citizen_headers)
        
        assert response.status_code == 403
    
    def test_citizen_cannot_create_user(self, client: TestClient, citizen_headers):
        """Test que ciudadano NO puede crear usuarios."""
        user_data = {
            "email": "intento.citizen@justicia.ma",
            "name": "Intento",
            "password": "Pass123!",
            "role": "lawyer"
        }
        
        response = client.post("/api/users/", json=user_data, headers=citizen_headers)
        
        assert response.status_code == 403
    
    def test_citizen_can_access_own_profile(self, client: TestClient, citizen_headers):
        """Test que ciudadano puede acceder a su propio perfil."""
        response = client.get("/api/users/me", headers=citizen_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "citizen"
    
    def test_citizen_can_update_own_profile(self, client: TestClient, citizen_headers):
        """Test que ciudadano puede actualizar su propio perfil."""
        update_data = {
            "name": "Ciudadano Actualizado",
            "email": "nuevo.email@justicia.ma"
        }
        
        response = client.put("/api/users/me", json=update_data, headers=citizen_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Ciudadano Actualizado"

@pytest.mark.api
@pytest.mark.rbac
class TestUsersAPIJudgeList:
    """Tests de listado de jueces."""
    
    def test_all_roles_can_list_judges(self, client: TestClient, admin_headers, judge_headers, lawyer_headers, clerk_headers, citizen_headers):
        """Test que todos los roles pueden listar jueces (para asignación)."""
        # Admin
        response = client.get("/api/users/judges", headers=admin_headers)
        assert response.status_code == 200
        
        # Judge
        response = client.get("/api/users/judges", headers=judge_headers)
        assert response.status_code == 200
        
        # Lawyer
        response = client.get("/api/users/judges", headers=lawyer_headers)
        assert response.status_code == 200
        
        # Clerk
        response = client.get("/api/users/judges", headers=clerk_headers)
        assert response.status_code == 200
        
        # Citizen
        response = client.get("/api/users/judges", headers=citizen_headers)
        assert response.status_code == 200
    
    def test_judges_list_only_contains_judges(self, client: TestClient, admin_headers, judge_user):
        """Test que listado de jueces solo contiene usuarios con rol judge."""
        response = client.get("/api/users/judges", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        for user in data:
            assert user["role"] == "judge"
