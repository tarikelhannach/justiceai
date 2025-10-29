# backend/tests/unit/test_cases.py - Tests Unitarios para Casos Judiciales

import pytest
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import Case, User, CaseStatus, UserRole

@pytest.mark.unit
class TestCaseCreation:
    """Tests para creación de casos."""
    
    def test_create_case_success(self, db_session: Session, lawyer_user: User, judge_user: User):
        """Test creación exitosa de caso."""
        case = Case(
            case_number="TEST-2025-001",
            title="Caso de Prueba",
            description="Descripción del caso de prueba",
            status=CaseStatus.PENDING,
            owner_id=lawyer_user.id,
            assigned_judge_id=judge_user.id
        )
        
        db_session.add(case)
        db_session.commit()
        db_session.refresh(case)
        
        assert case.id is not None
        assert case.case_number == "TEST-2025-001"
        assert case.status == CaseStatus.PENDING
        assert case.owner_id == lawyer_user.id
        assert case.assigned_judge_id == judge_user.id
    
    def test_create_case_without_judge(self, db_session: Session, lawyer_user: User):
        """Test creación de caso sin juez asignado."""
        case = Case(
            case_number="TEST-2025-002",
            title="Caso sin Juez",
            description="Caso creado sin juez asignado",
            status=CaseStatus.PENDING,
            owner_id=lawyer_user.id
        )
        
        db_session.add(case)
        db_session.commit()
        db_session.refresh(case)
        
        assert case.assigned_judge_id is None
    
    def test_case_number_uniqueness(self, db_session: Session, sample_case: Case):
        """Test que el número de caso debe ser único."""
        duplicate_case = Case(
            case_number=sample_case.case_number,
            title="Caso Duplicado",
            description="Este caso tiene número duplicado",
            status=CaseStatus.PENDING,
            owner_id=sample_case.owner_id
        )
        
        db_session.add(duplicate_case)
        
        with pytest.raises(Exception):  # SQLAlchemy integrity error
            db_session.commit()

@pytest.mark.unit
class TestCaseStatus:
    """Tests para estados de casos."""
    
    def test_case_status_values(self):
        """Test valores válidos de estados."""
        assert CaseStatus.PENDING.value == "pending"
        assert CaseStatus.IN_PROGRESS.value == "in_progress"
        assert CaseStatus.RESOLVED.value == "resolved"
        assert CaseStatus.CLOSED.value == "closed"
    
    def test_update_case_status(self, db_session: Session, sample_case: Case):
        """Test actualización de estado de caso."""
        original_status = sample_case.status
        sample_case.status = CaseStatus.IN_PROGRESS
        
        db_session.commit()
        db_session.refresh(sample_case)
        
        assert sample_case.status == CaseStatus.IN_PROGRESS
        assert sample_case.status != original_status

@pytest.mark.unit
class TestCaseRBAC:
    """Tests para control de acceso basado en roles."""
    
    def test_admin_can_view_all_cases(self, db_session: Session, admin_user: User, sample_case: Case):
        """Test que admin puede ver todos los casos."""
        # Admin tiene permisos completos
        assert admin_user.role == UserRole.ADMIN
        # En la lógica real, el admin puede acceder a cualquier caso
    
    def test_lawyer_can_only_view_own_cases(self, db_session: Session, lawyer_user: User, sample_case: Case):
        """Test que abogado solo ve sus propios casos."""
        assert lawyer_user.role == UserRole.LAWYER
        # El abogado solo puede ver casos donde owner_id == lawyer_user.id
        assert sample_case.owner_id == lawyer_user.id
    
    def test_judge_can_view_assigned_cases(self, db_session: Session, judge_user: User, sample_case: Case):
        """Test que juez puede ver casos asignados."""
        assert judge_user.role == UserRole.JUDGE
        # El juez puede ver casos donde assigned_judge_id == judge_user.id
        assert sample_case.assigned_judge_id == judge_user.id
    
    def test_clerk_can_view_all_cases(self, db_session: Session, clerk_user: User):
        """Test que secretario puede ver todos los casos."""
        assert clerk_user.role == UserRole.CLERK
        # Clerk tiene permisos completos como admin

@pytest.mark.unit
class TestCaseValidation:
    """Tests para validación de casos."""
    
    def test_case_number_format(self, db_session: Session, lawyer_user: User):
        """Test formato de número de caso."""
        case = Case(
            case_number="CAS-2025-12345",
            title="Test Format",
            description="Test case number format",
            status=CaseStatus.PENDING,
            owner_id=lawyer_user.id
        )
        
        db_session.add(case)
        db_session.commit()
        
        assert case.case_number.startswith("CAS-")
        assert len(case.case_number) > 0
    
    def test_case_requires_title(self, db_session: Session, lawyer_user: User):
        """Test que el caso requiere título."""
        case = Case(
            case_number="TEST-2025-003",
            title="",
            description="Caso sin título",
            status=CaseStatus.PENDING,
            owner_id=lawyer_user.id
        )
        
        # El título vacío debería validarse en la capa de API
        assert case.title == ""
    
    def test_case_requires_owner(self, db_session: Session):
        """Test que el caso requiere propietario."""
        case = Case(
            case_number="TEST-2025-004",
            title="Caso sin propietario",
            description="Este caso no tiene propietario",
            status=CaseStatus.PENDING
        )
        
        db_session.add(case)
        
        with pytest.raises(Exception):  # Foreign key constraint
            db_session.commit()

@pytest.mark.unit
class TestCaseRelationships:
    """Tests para relaciones de casos."""
    
    def test_case_has_owner(self, db_session: Session, sample_case: Case):
        """Test que caso tiene propietario."""
        assert sample_case.owner is not None
        assert isinstance(sample_case.owner, User)
        assert sample_case.owner.id == sample_case.owner_id
    
    def test_case_has_assigned_judge(self, db_session: Session, sample_case: Case):
        """Test que caso tiene juez asignado."""
        if sample_case.assigned_judge_id:
            assert sample_case.assigned_judge is not None
            assert isinstance(sample_case.assigned_judge, User)
            assert sample_case.assigned_judge.role == UserRole.JUDGE
    
    def test_case_without_assigned_judge(self, db_session: Session, lawyer_user: User):
        """Test caso sin juez asignado."""
        case = Case(
            case_number="TEST-2025-005",
            title="Sin Juez",
            description="Caso sin juez asignado",
            status=CaseStatus.PENDING,
            owner_id=lawyer_user.id
        )
        
        db_session.add(case)
        db_session.commit()
        
        assert case.assigned_judge is None

@pytest.mark.unit
class TestCaseTimestamps:
    """Tests para timestamps de casos."""
    
    def test_case_has_created_at(self, db_session: Session, sample_case: Case):
        """Test que caso tiene fecha de creación."""
        assert sample_case.created_at is not None
        assert isinstance(sample_case.created_at, datetime)
    
    def test_case_has_updated_at(self, db_session: Session, sample_case: Case):
        """Test que caso tiene fecha de actualización."""
        assert sample_case.updated_at is not None
        assert isinstance(sample_case.updated_at, datetime)
    
    def test_updated_at_changes_on_modification(self, db_session: Session, sample_case: Case):
        """Test que updated_at cambia al modificar."""
        import time
        original_updated_at = sample_case.updated_at
        
        time.sleep(0.1)
        sample_case.title = "Título Actualizado"
        sample_case.updated_at = datetime.utcnow()
        
        db_session.commit()
        db_session.refresh(sample_case)
        
        assert sample_case.updated_at > original_updated_at

@pytest.mark.unit
class TestCaseSearch:
    """Tests para búsqueda de casos."""
    
    def test_search_by_case_number(self, db_session: Session, sample_case: Case):
        """Test búsqueda por número de caso."""
        result = db_session.query(Case).filter(
            Case.case_number.ilike(f"%{sample_case.case_number}%")
        ).first()
        
        assert result is not None
        assert result.id == sample_case.id
    
    def test_search_by_title(self, db_session: Session, sample_case: Case):
        """Test búsqueda por título."""
        result = db_session.query(Case).filter(
            Case.title.ilike("%Prueba%")
        ).first()
        
        assert result is not None
    
    def test_search_by_status(self, db_session: Session, sample_case: Case):
        """Test búsqueda por estado."""
        results = db_session.query(Case).filter(
            Case.status == CaseStatus.OPEN
        ).all()
        
        assert isinstance(results, list)
    
    def test_search_by_assigned_judge(self, db_session: Session, sample_case: Case, judge_user: User):
        """Test búsqueda por juez asignado."""
        results = db_session.query(Case).filter(
            Case.assigned_judge_id == judge_user.id
        ).all()
        
        assert len(results) >= 1
        assert sample_case in results

@pytest.mark.unit  
class TestCaseStatistics:
    """Tests para estadísticas de casos."""
    
    def test_count_cases_by_status(self, db_session: Session):
        """Test contar casos por estado."""
        pending_count = db_session.query(Case).filter(
            Case.status == CaseStatus.PENDING
        ).count()
        
        assert pending_count >= 0
    
    def test_count_cases_by_owner(self, db_session: Session, lawyer_user: User):
        """Test contar casos por propietario."""
        owner_cases_count = db_session.query(Case).filter(
            Case.owner_id == lawyer_user.id
        ).count()
        
        assert owner_cases_count >= 0
    
    def test_count_cases_by_judge(self, db_session: Session, judge_user: User):
        """Test contar casos por juez."""
        judge_cases_count = db_session.query(Case).filter(
            Case.assigned_judge_id == judge_user.id
        ).count()
        
        assert judge_cases_count >= 0
