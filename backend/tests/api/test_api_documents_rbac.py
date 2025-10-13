# backend/tests/api/test_api_documents_rbac.py - Tests de API de Documentos con RBAC

import pytest
from fastapi.testclient import TestClient
from io import BytesIO

@pytest.mark.api
@pytest.mark.rbac
class TestDocumentsAPIAdmin:
    """Tests de API de documentos con rol Admin."""
    
    def test_admin_can_list_all_documents(self, client: TestClient, admin_headers):
        """Test que admin puede listar todos los documentos."""
        response = client.get("/api/documents/", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_admin_can_upload_document(self, client: TestClient, admin_headers, sample_case):
        """Test que admin puede subir documentos."""
        file_content = b"PDF content here"
        files = {
            "file": ("test_admin.pdf", BytesIO(file_content), "application/pdf")
        }
        data = {"case_id": sample_case.id}
        
        response = client.post(
            "/api/documents/upload",
            files=files,
            data=data,
            headers=admin_headers
        )
        
        assert response.status_code == 201
    
    def test_admin_can_delete_any_document(self, client: TestClient, admin_headers, sample_document):
        """Test que admin puede eliminar cualquier documento."""
        response = client.delete(
            f"/api/documents/{sample_document.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200

@pytest.mark.api
@pytest.mark.rbac
class TestDocumentsAPIJudge:
    """Tests de API de documentos con rol Judge."""
    
    def test_judge_can_access_assigned_case_documents(self, client: TestClient, judge_headers, sample_case):
        """Test que juez puede acceder a documentos de casos asignados."""
        response = client.get(
            f"/api/documents/?case_id={sample_case.id}",
            headers=judge_headers
        )
        
        assert response.status_code == 200
    
    def test_judge_can_upload_to_assigned_case(self, client: TestClient, judge_headers, sample_case):
        """Test que juez puede subir documentos a casos asignados."""
        file_content = b"PDF content"
        files = {
            "file": ("judge_doc.pdf", BytesIO(file_content), "application/pdf")
        }
        data = {"case_id": sample_case.id}
        
        response = client.post(
            "/api/documents/upload",
            files=files,
            data=data,
            headers=judge_headers
        )
        
        assert response.status_code == 201
    
    def test_judge_cannot_access_unassigned_case_documents(self, client: TestClient, judge_headers, db_session, lawyer_user):
        """Test que juez NO puede acceder a documentos de casos no asignados."""
        from app.models import Case, CaseStatus
        from datetime import datetime
        
        unassigned_case = Case(
            case_number="UNASSIGNED-DOC-001",
            title="Caso No Asignado",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=lawyer_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(unassigned_case)
        db_session.commit()
        
        response = client.get(
            f"/api/documents/?case_id={unassigned_case.id}",
            headers=judge_headers
        )
        
        assert response.status_code == 403

@pytest.mark.api
@pytest.mark.rbac
class TestDocumentsAPILawyer:
    """Tests de API de documentos con rol Lawyer."""
    
    def test_lawyer_can_access_own_case_documents(self, client: TestClient, lawyer_headers, sample_case):
        """Test que abogado puede acceder a documentos de sus casos."""
        response = client.get(
            f"/api/documents/?case_id={sample_case.id}",
            headers=lawyer_headers
        )
        
        assert response.status_code == 200
    
    def test_lawyer_can_upload_to_own_case(self, client: TestClient, lawyer_headers, sample_case):
        """Test que abogado puede subir documentos a sus casos."""
        file_content = b"PDF content"
        files = {
            "file": ("lawyer_doc.pdf", BytesIO(file_content), "application/pdf")
        }
        data = {"case_id": sample_case.id}
        
        response = client.post(
            "/api/documents/upload",
            files=files,
            data=data,
            headers=lawyer_headers
        )
        
        assert response.status_code == 201
    
    def test_lawyer_cannot_access_other_case_documents(self, client: TestClient, lawyer_headers, db_session, citizen_user):
        """Test que abogado NO puede acceder a documentos de otros casos."""
        from app.models import Case, CaseStatus
        from datetime import datetime
        
        other_case = Case(
            case_number="OTHER-DOC-001",
            title="Caso de Otro",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=citizen_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(other_case)
        db_session.commit()
        
        response = client.get(
            f"/api/documents/?case_id={other_case.id}",
            headers=lawyer_headers
        )
        
        assert response.status_code == 403
    
    def test_lawyer_cannot_delete_document(self, client: TestClient, lawyer_headers, sample_document):
        """Test que abogado NO puede eliminar documentos."""
        response = client.delete(
            f"/api/documents/{sample_document.id}",
            headers=lawyer_headers
        )
        
        assert response.status_code == 403

@pytest.mark.api
@pytest.mark.rbac
class TestDocumentsAPIClerk:
    """Tests de API de documentos con rol Clerk."""
    
    def test_clerk_can_access_all_documents(self, client: TestClient, clerk_headers):
        """Test que secretario puede acceder a todos los documentos."""
        response = client.get("/api/documents/", headers=clerk_headers)
        
        assert response.status_code == 200
    
    def test_clerk_can_delete_any_document(self, client: TestClient, clerk_headers, sample_document):
        """Test que secretario puede eliminar cualquier documento."""
        response = client.delete(
            f"/api/documents/{sample_document.id}",
            headers=clerk_headers
        )
        
        assert response.status_code == 200

@pytest.mark.api
@pytest.mark.rbac
class TestDocumentsAPICitizen:
    """Tests de API de documentos con rol Citizen."""
    
    def test_citizen_can_access_own_case_documents(self, client: TestClient, citizen_headers, db_session, citizen_user):
        """Test que ciudadano puede acceder a documentos de sus casos."""
        from app.models import Case, CaseStatus
        from datetime import datetime
        
        citizen_case = Case(
            case_number="CIT-DOC-001",
            title="Caso Ciudadano",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=citizen_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(citizen_case)
        db_session.commit()
        
        response = client.get(
            f"/api/documents/?case_id={citizen_case.id}",
            headers=citizen_headers
        )
        
        assert response.status_code == 200
    
    def test_citizen_can_upload_to_own_case(self, client: TestClient, citizen_headers, db_session, citizen_user):
        """Test que ciudadano puede subir documentos a sus casos."""
        from app.models import Case, CaseStatus
        from datetime import datetime
        
        citizen_case = Case(
            case_number="CIT-DOC-002",
            title="Caso Ciudadano",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=citizen_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(citizen_case)
        db_session.commit()
        
        file_content = b"PDF content"
        files = {
            "file": ("citizen_doc.pdf", BytesIO(file_content), "application/pdf")
        }
        data = {"case_id": citizen_case.id}
        
        response = client.post(
            "/api/documents/upload",
            files=files,
            data=data,
            headers=citizen_headers
        )
        
        assert response.status_code == 201
    
    def test_citizen_cannot_delete_document(self, client: TestClient, citizen_headers, db_session, citizen_user):
        """Test que ciudadano NO puede eliminar documentos."""
        from app.models import Document, Case, CaseStatus
        from datetime import datetime
        
        citizen_case = Case(
            case_number="CIT-DOC-003",
            title="Caso Ciudadano",
            description="Test",
            status=CaseStatus.PENDING,
            owner_id=citizen_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(citizen_case)
        db_session.commit()
        
        doc = Document(
            filename="test.pdf",
            file_path="/test.pdf",
            file_type="application/pdf",
            file_size=1024,
            case_id=citizen_case.id,
            uploaded_by=citizen_user.id,
            created_at=datetime.utcnow()
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.delete(
            f"/api/documents/{doc.id}",
            headers=citizen_headers
        )
        
        assert response.status_code == 403

@pytest.mark.api
@pytest.mark.rbac
class TestDocumentsAPIFileValidation:
    """Tests de validación de archivos."""
    
    def test_reject_invalid_file_type(self, client: TestClient, admin_headers):
        """Test rechazo de tipo de archivo no permitido."""
        file_content = b"Executable content"
        files = {
            "file": ("malicious.exe", BytesIO(file_content), "application/x-msdownload")
        }
        
        response = client.post(
            "/api/documents/upload",
            files=files,
            headers=admin_headers
        )
        
        assert response.status_code == 400
    
    def test_reject_oversized_file(self, client: TestClient, admin_headers):
        """Test rechazo de archivo demasiado grande."""
        # Simular archivo de 100MB (excede límite de 50MB)
        large_content = b"X" * (100 * 1024 * 1024)
        files = {
            "file": ("large.pdf", BytesIO(large_content), "application/pdf")
        }
        
        response = client.post(
            "/api/documents/upload",
            files=files,
            headers=admin_headers
        )
        
        assert response.status_code == 400
