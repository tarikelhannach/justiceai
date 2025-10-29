# backend/tests/integration/test_database.py - Tests de Integración con Base de Datos

import pytest
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import User, Case, Document, AuditLog, UserRole, CaseStatus

@pytest.mark.integration
class TestDatabaseIntegration:
    """Tests de integración con PostgreSQL."""
    
    def test_database_connection(self, db_session: Session):
        """Test conexión exitosa a la base de datos."""
        from sqlalchemy import text
        result = db_session.execute(text("SELECT 1")).scalar()
        assert result == 1
    
    def test_create_and_retrieve_user(self, db_session: Session):
        """Test crear y recuperar usuario de BD."""
        user = User(
            email="integration@justicia.ma",
            name="Integration Test User",
            hashed_password="hashed_password_test",
            role=UserRole.CITIZEN,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db_session.add(user)
        db_session.commit()
        
        retrieved_user = db_session.query(User).filter(
            User.email == "integration@justicia.ma"
        ).first()
        
        assert retrieved_user is not None
        assert retrieved_user.name == "Integration Test User"
        assert retrieved_user.role == UserRole.CITIZEN
    
    def test_foreign_key_relationships(self, db_session: Session, lawyer_user: User, judge_user: User):
        """Test relaciones de claves foráneas."""
        case = Case(
            case_number="INT-2025-001",
            title="Integration Test Case",
            description="Testing foreign key relationships",
            status=CaseStatus.PENDING,
            owner_id=lawyer_user.id,
            assigned_judge_id=judge_user.id,
            created_at=datetime.utcnow()
        )
        
        db_session.add(case)
        db_session.commit()
        db_session.refresh(case)
        
        # Verificar relaciones
        assert case.owner.id == lawyer_user.id
        assert case.assigned_judge.id == judge_user.id
        assert case.owner.role == UserRole.LAWYER
        assert case.assigned_judge.role == UserRole.JUDGE
    
    def test_cascade_delete(self, db_session: Session, sample_case: Case, sample_document: Document):
        """Test eliminación en cascada."""
        case_id = sample_case.id
        
        # Verificar que existe documento asociado
        doc_count_before = db_session.query(Document).filter(
            Document.case_id == case_id
        ).count()
        
        assert doc_count_before >= 1
        
        # Eliminar caso (debería eliminar documentos asociados si hay CASCADE)
        db_session.delete(sample_case)
        db_session.commit()
        
        # Verificar que el caso fue eliminado
        deleted_case = db_session.query(Case).filter(Case.id == case_id).first()
        assert deleted_case is None
    
    def test_transaction_rollback(self, db_session: Session, lawyer_user: User):
        """Test rollback de transacción."""
        try:
            user = User(
                email=lawyer_user.email,  # Email duplicado, causará error
                name="Duplicate User",
                hashed_password="test",
                role=UserRole.CITIZEN
            )
            
            db_session.add(user)
            db_session.commit()
        except Exception:
            db_session.rollback()
        
        # Verificar que no se creó el usuario duplicado
        duplicate_count = db_session.query(User).filter(
            User.email == lawyer_user.email
        ).count()
        
        assert duplicate_count == 1  # Solo el original
    
    def test_bulk_insert(self, db_session: Session):
        """Test inserción masiva."""
        users = [
            User(
                email=f"bulk{i}@justicia.ma",
                name=f"Bulk User {i}",
                hashed_password="test",
                role=UserRole.CITIZEN,
                is_active=True,
                created_at=datetime.utcnow()
            )
            for i in range(100)
        ]
        
        db_session.bulk_save_objects(users)
        db_session.commit()
        
        count = db_session.query(User).filter(
            User.email.like("bulk%@justicia.ma")
        ).count()
        
        assert count == 100
    
    def test_complex_query(self, db_session: Session, admin_user: User, lawyer_user: User, judge_user: User):
        """Test consulta compleja con joins."""
        # Crear varios casos
        for i in range(5):
            case = Case(
                case_number=f"COMPLEX-{i}",
                title=f"Complex Query Test {i}",
                description="Test",
                status=CaseStatus.PENDING if i % 2 == 0 else CaseStatus.IN_PROGRESS,
                owner_id=lawyer_user.id,
                assigned_judge_id=judge_user.id if i % 2 == 0 else None,
                created_at=datetime.utcnow()
            )
            db_session.add(case)
        
        db_session.commit()
        
        # Query compleja: casos pendientes con juez asignado
        result = db_session.query(Case).join(
            User, Case.owner_id == User.id
        ).filter(
            Case.status == CaseStatus.PENDING,
            Case.assigned_judge_id.isnot(None),
            User.role == UserRole.LAWYER
        ).count()
        
        assert result >= 3

@pytest.mark.integration
class TestAuditLogIntegration:
    """Tests de integración con logs de auditoría."""
    
    def test_audit_log_creation(self, db_session: Session, admin_user: User):
        """Test creación de log de auditoría."""
        audit = AuditLog(
            user_id=admin_user.id,
            action="test_action",
            resource_type="user",
            resource_id=admin_user.id,
            details="Test audit log entry",
            status="success",
            timestamp=datetime.utcnow()
        )
        
        db_session.add(audit)
        db_session.commit()
        
        retrieved = db_session.query(AuditLog).filter(
            AuditLog.action == "test_action"
        ).first()
        
        assert retrieved is not None
        assert retrieved.user_id == admin_user.id
        assert retrieved.status == "success"
    
    def test_audit_log_query_by_user(self, db_session: Session, admin_user: User):
        """Test consultar logs por usuario."""
        # Crear varios logs
        for i in range(3):
            audit = AuditLog(
                user_id=admin_user.id,
                action=f"action_{i}",
                resource_type="case",
                resource_id=i,
                details=f"Test {i}",
                status="success",
                timestamp=datetime.utcnow()
            )
            db_session.add(audit)
        
        db_session.commit()
        
        logs = db_session.query(AuditLog).filter(
            AuditLog.user_id == admin_user.id
        ).all()
        
        assert len(logs) >= 3
    
    def test_audit_log_query_by_action(self, db_session: Session, lawyer_user: User):
        """Test consultar logs por acción."""
        audit = AuditLog(
            user_id=lawyer_user.id,
            action="create_case",
            resource_type="case",
            resource_id=1,
            details="Created new case",
            status="success",
            timestamp=datetime.utcnow()
        )
        
        db_session.add(audit)
        db_session.commit()
        
        logs = db_session.query(AuditLog).filter(
            AuditLog.action == "create_case"
        ).all()
        
        assert len(logs) >= 1

@pytest.mark.integration
class TestDatabasePerformance:
    """Tests de performance de base de datos."""
    
    @pytest.mark.slow
    def test_large_query_performance(self, db_session: Session):
        """Test performance de consulta grande."""
        import time
        
        # Crear muchos registros
        users = [
            User(
                email=f"perf{i}@justicia.ma",
                name=f"Performance User {i}",
                hashed_password="test",
                role=UserRole.CITIZEN,
                is_active=True,
                created_at=datetime.utcnow()
            )
            for i in range(1000)
        ]
        
        db_session.bulk_save_objects(users)
        db_session.commit()
        
        # Medir tiempo de consulta
        start = time.time()
        result = db_session.query(User).filter(
            User.email.like("perf%@justicia.ma")
        ).all()
        end = time.time()
        
        assert len(result) == 1000
        assert (end - start) < 1.0  # Debe completarse en menos de 1 segundo
    
    @pytest.mark.slow
    def test_index_performance(self, db_session: Session):
        """Test performance con índices."""
        import time
        
        # La búsqueda por email debería ser rápida gracias al índice UNIQUE
        start = time.time()
        user = db_session.query(User).filter(
            User.email == "admin@justicia.ma"
        ).first()
        end = time.time()
        
        assert (end - start) < 0.1  # Debe ser muy rápido con índice
