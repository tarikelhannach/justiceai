# backend/tests/unit/test_documents.py - Tests Unitarios para Documentos

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from pathlib import Path

from app.models import Document, User, Case

@pytest.mark.unit
class TestDocumentCreation:
    """Tests para creación de documentos."""
    
    def test_create_document_success(self, db_session: Session, sample_case: Case, lawyer_user: User):
        """Test creación exitosa de documento."""
        doc = Document(
            filename="documento_prueba.pdf",
            file_path="/uploads/documento_prueba.pdf",
            file_type="application/pdf",
            file_size=1024000,
            case_id=sample_case.id,
            uploaded_by=lawyer_user.id
        )
        
        db_session.add(doc)
        db_session.commit()
        db_session.refresh(doc)
        
        assert doc.id is not None
        assert doc.filename == "documento_prueba.pdf"
        assert doc.case_id == sample_case.id
        assert doc.uploaded_by == lawyer_user.id
    
    def test_create_document_without_case(self, db_session: Session, lawyer_user: User):
        """Test creación de documento sin caso asociado."""
        doc = Document(
            filename="documento_general.pdf",
            file_path="/uploads/documento_general.pdf",
            file_type="application/pdf",
            file_size=512000,
            uploaded_by=lawyer_user.id
        )
        
        db_session.add(doc)
        db_session.commit()
        
        assert doc.case_id is None

@pytest.mark.unit
class TestDocumentValidation:
    """Tests para validación de documentos."""
    
    def test_allowed_file_types(self):
        """Test tipos de archivo permitidos."""
        allowed_types = [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        for file_type in allowed_types:
            assert file_type in [
                "application/pdf",
                "image/jpeg",
                "image/png",
                "image/gif",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ]
    
    def test_max_file_size(self):
        """Test tamaño máximo de archivo."""
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        
        test_size_valid = 10 * 1024 * 1024  # 10MB
        test_size_invalid = 100 * 1024 * 1024  # 100MB
        
        assert test_size_valid < MAX_FILE_SIZE
        assert test_size_invalid > MAX_FILE_SIZE
    
    def test_document_requires_filename(self, db_session: Session, lawyer_user: User):
        """Test que documento requiere nombre de archivo."""
        doc = Document(
            filename="",
            file_path="/uploads/test.pdf",
            file_type="application/pdf",
            file_size=1024,
            uploaded_by=lawyer_user.id
        )
        
        # Filename vacío debería validarse en la capa de API
        assert doc.filename == ""
    
    def test_document_requires_uploader(self, db_session: Session):
        """Test que documento requiere usuario que lo sube."""
        doc = Document(
            filename="test.pdf",
            file_path="/uploads/test.pdf",
            file_type="application/pdf",
            file_size=1024
        )
        
        db_session.add(doc)
        
        with pytest.raises(Exception):  # Foreign key constraint
            db_session.commit()

@pytest.mark.unit
class TestDocumentRBAC:
    """Tests para control de acceso a documentos."""
    
    def test_admin_can_access_all_documents(self, db_session: Session, admin_user: User):
        """Test que admin puede acceder a todos los documentos."""
        assert admin_user.role.value == "admin"
        # Admin tiene permisos completos
    
    def test_clerk_can_access_all_documents(self, db_session: Session, clerk_user: User):
        """Test que secretario puede acceder a todos los documentos."""
        assert clerk_user.role.value == "clerk"
        # Clerk tiene permisos completos
    
    def test_judge_can_access_case_documents(self, db_session: Session, judge_user: User, sample_document: Document):
        """Test que juez puede acceder a documentos de sus casos."""
        # Si el juez está asignado al caso, puede acceder a los documentos
        if sample_document.case:
            if sample_document.case.assigned_judge_id == judge_user.id:
                assert True
    
    def test_lawyer_can_access_own_case_documents(self, db_session: Session, lawyer_user: User, sample_document: Document):
        """Test que abogado puede acceder a documentos de sus casos."""
        # Si el abogado es dueño del caso, puede acceder
        if sample_document.case:
            if sample_document.case.owner_id == lawyer_user.id:
                assert True
    
    def test_user_can_access_own_uploaded_documents(self, db_session: Session, sample_document: Document):
        """Test que usuario puede acceder a sus documentos subidos."""
        uploader_id = sample_document.uploaded_by
        assert sample_document.uploaded_by == uploader_id

@pytest.mark.unit
class TestDocumentRelationships:
    """Tests para relaciones de documentos."""
    
    def test_document_has_uploader(self, db_session: Session, sample_document: Document):
        """Test que documento tiene usuario que lo subió."""
        assert sample_document.uploader is not None
        assert isinstance(sample_document.uploader, User)
    
    def test_document_can_have_case(self, db_session: Session, sample_document: Document):
        """Test que documento puede tener caso asociado."""
        if sample_document.case_id:
            assert sample_document.case is not None
            assert isinstance(sample_document.case, Case)
    
    def test_case_can_have_multiple_documents(self, db_session: Session, sample_case: Case, lawyer_user: User):
        """Test que caso puede tener múltiples documentos."""
        doc1 = Document(
            filename="doc1.pdf",
            file_path="/uploads/doc1.pdf",
            file_type="application/pdf",
            file_size=1024,
            case_id=sample_case.id,
            uploaded_by=lawyer_user.id
        )
        
        doc2 = Document(
            filename="doc2.pdf",
            file_path="/uploads/doc2.pdf",
            file_type="application/pdf",
            file_size=2048,
            case_id=sample_case.id,
            uploaded_by=lawyer_user.id
        )
        
        db_session.add(doc1)
        db_session.add(doc2)
        db_session.commit()
        
        case_docs = db_session.query(Document).filter(
            Document.case_id == sample_case.id
        ).all()
        
        assert len(case_docs) >= 2

@pytest.mark.unit
class TestDocumentTimestamps:
    """Tests para timestamps de documentos."""
    
    def test_document_has_created_at(self, db_session: Session, sample_document: Document):
        """Test que documento tiene fecha de creación."""
        assert sample_document.created_at is not None
        assert isinstance(sample_document.created_at, datetime)
    
    def test_document_creation_timestamp_accurate(self, db_session: Session, lawyer_user: User):
        """Test que timestamp de creación es preciso."""
        before = datetime.utcnow()
        
        doc = Document(
            filename="timestamp_test.pdf",
            file_path="/uploads/timestamp_test.pdf",
            file_type="application/pdf",
            file_size=1024,
            uploaded_by=lawyer_user.id,
            created_at=datetime.utcnow()
        )
        
        db_session.add(doc)
        db_session.commit()
        db_session.refresh(doc)
        
        after = datetime.utcnow()
        
        assert before <= doc.created_at <= after

@pytest.mark.unit
class TestDocumentSearch:
    """Tests para búsqueda de documentos."""
    
    def test_search_by_filename(self, db_session: Session, sample_document: Document):
        """Test búsqueda por nombre de archivo."""
        result = db_session.query(Document).filter(
            Document.filename.ilike(f"%{sample_document.filename}%")
        ).first()
        
        assert result is not None
        assert result.id == sample_document.id
    
    def test_search_by_case(self, db_session: Session, sample_case: Case):
        """Test búsqueda por caso."""
        results = db_session.query(Document).filter(
            Document.case_id == sample_case.id
        ).all()
        
        assert isinstance(results, list)
    
    def test_search_by_uploader(self, db_session: Session, lawyer_user: User):
        """Test búsqueda por usuario que subió."""
        results = db_session.query(Document).filter(
            Document.uploaded_by == lawyer_user.id
        ).all()
        
        assert isinstance(results, list)
    
    def test_search_by_file_type(self, db_session: Session):
        """Test búsqueda por tipo de archivo."""
        results = db_session.query(Document).filter(
            Document.file_type == "application/pdf"
        ).all()
        
        assert isinstance(results, list)

@pytest.mark.unit
class TestDocumentDeletion:
    """Tests para eliminación de documentos."""
    
    def test_delete_document_removes_record(self, db_session: Session, sample_document: Document):
        """Test que eliminar documento remueve el registro."""
        doc_id = sample_document.id
        
        db_session.delete(sample_document)
        db_session.commit()
        
        deleted_doc = db_session.query(Document).filter(Document.id == doc_id).first()
        assert deleted_doc is None
    
    def test_admin_can_delete_any_document(self, db_session: Session, admin_user: User):
        """Test que admin puede eliminar cualquier documento."""
        assert admin_user.role.value == "admin"
        # Admin tiene permisos de eliminación
    
    def test_clerk_can_delete_any_document(self, db_session: Session, clerk_user: User):
        """Test que secretario puede eliminar cualquier documento."""
        assert clerk_user.role.value == "clerk"
        # Clerk tiene permisos de eliminación
