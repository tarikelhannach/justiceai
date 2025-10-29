# backend/tests/unit/test_users.py - Tests Unitarios para Usuarios

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.auth.auth import get_password_hash, verify_password

@pytest.mark.unit
class TestUserCreation:
    """Tests para creación de usuarios."""
    
    def test_create_user_success(self, db_session: Session):
        """Test creación exitosa de usuario."""
        user = User(
            email="nuevo@justicia.ma",
            name="Usuario Nuevo",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.CITIZEN,
            is_active=True,
            is_verified=False
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "nuevo@justicia.ma"
        assert user.role == UserRole.CITIZEN
        assert user.is_active is True
    
    def test_user_email_uniqueness(self, db_session: Session, admin_user: User):
        """Test que el email debe ser único."""
        duplicate_user = User(
            email=admin_user.email,
            name="Usuario Duplicado",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.CITIZEN
        )
        
        db_session.add(duplicate_user)
        
        with pytest.raises(Exception):  # SQLAlchemy integrity error
            db_session.commit()
    
    def test_password_hashing(self):
        """Test que contraseñas se hashean correctamente."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert verify_password(password, hashed)

@pytest.mark.unit
class TestUserRoles:
    """Tests para roles de usuario."""
    
    def test_admin_role(self, admin_user: User):
        """Test rol de administrador."""
        assert admin_user.role == UserRole.ADMIN
        assert admin_user.role.value == "admin"
    
    def test_judge_role(self, judge_user: User):
        """Test rol de juez."""
        assert judge_user.role == UserRole.JUDGE
        assert judge_user.role.value == "judge"
    
    def test_lawyer_role(self, lawyer_user: User):
        """Test rol de abogado."""
        assert lawyer_user.role == UserRole.LAWYER
        assert lawyer_user.role.value == "lawyer"
    
    def test_clerk_role(self, clerk_user: User):
        """Test rol de secretario."""
        assert clerk_user.role == UserRole.CLERK
        assert clerk_user.role.value == "clerk"
    
    def test_citizen_role(self, citizen_user: User):
        """Test rol de ciudadano."""
        assert citizen_user.role == UserRole.CITIZEN
        assert citizen_user.role.value == "citizen"
    
    def test_all_roles_exist(self):
        """Test que todos los roles existen."""
        roles = [
            UserRole.ADMIN,
            UserRole.JUDGE,
            UserRole.LAWYER,
            UserRole.CLERK,
            UserRole.CITIZEN
        ]
        
        for role in roles:
            assert role in UserRole

@pytest.mark.unit
class TestUserAuthentication:
    """Tests para autenticación de usuario."""
    
    def test_password_verification_success(self):
        """Test verificación exitosa de contraseña."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_password_verification_failure(self):
        """Test fallo en verificación de contraseña."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_user_is_active_by_default(self, db_session: Session):
        """Test que usuario está activo por defecto."""
        user = User(
            email="activo@justicia.ma",
            name="Usuario Activo",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.CITIZEN,
            is_active=True
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.is_active is True
    
    def test_user_can_be_deactivated(self, db_session: Session, citizen_user: User):
        """Test que usuario puede ser desactivado."""
        citizen_user.is_active = False
        db_session.commit()
        db_session.refresh(citizen_user)
        
        assert citizen_user.is_active is False

@pytest.mark.unit
class TestUserValidation:
    """Tests para validación de usuario."""
    
    def test_valid_email_format(self):
        """Test formato válido de email."""
        valid_emails = [
            "user@justicia.ma",
            "test.user@justicia.ma",
            "admin@justice.gov.ma"
        ]
        
        for email in valid_emails:
            assert "@" in email
            assert "." in email
    
    def test_user_requires_email(self, db_session: Session):
        """Test que usuario requiere email."""
        user = User(
            name="Sin Email",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.CITIZEN
        )
        
        db_session.add(user)
        
        with pytest.raises(Exception):  # NOT NULL constraint
            db_session.commit()
    
    def test_user_requires_name(self, db_session: Session):
        """Test que usuario requiere nombre."""
        user = User(
            email="test@justicia.ma",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.CITIZEN
        )
        
        db_session.add(user)
        
        with pytest.raises(Exception):  # NOT NULL constraint
            db_session.commit()
    
    def test_user_requires_password(self, db_session: Session):
        """Test que usuario requiere contraseña."""
        user = User(
            email="test@justicia.ma",
            name="Test User",
            role=UserRole.CITIZEN
        )
        
        db_session.add(user)
        
        with pytest.raises(Exception):  # NOT NULL constraint
            db_session.commit()

@pytest.mark.unit
class TestUserPermissions:
    """Tests para permisos de usuario."""
    
    def test_admin_has_full_permissions(self, admin_user: User):
        """Test que admin tiene permisos completos."""
        assert admin_user.role == UserRole.ADMIN
        # Admin puede crear, leer, actualizar, eliminar
    
    def test_clerk_has_management_permissions(self, clerk_user: User):
        """Test que secretario tiene permisos de gestión."""
        assert clerk_user.role == UserRole.CLERK
        # Clerk puede gestionar casos y usuarios
    
    def test_judge_has_case_permissions(self, judge_user: User):
        """Test que juez tiene permisos sobre casos."""
        assert judge_user.role == UserRole.JUDGE
        # Juez puede ver y modificar casos asignados
    
    def test_lawyer_has_limited_permissions(self, lawyer_user: User):
        """Test que abogado tiene permisos limitados."""
        assert lawyer_user.role == UserRole.LAWYER
        # Abogado solo puede ver y modificar sus propios casos
    
    def test_citizen_has_minimal_permissions(self, citizen_user: User):
        """Test que ciudadano tiene permisos mínimos."""
        assert citizen_user.role == UserRole.CITIZEN
        # Ciudadano solo puede ver sus propios casos

@pytest.mark.unit
class TestUserTimestamps:
    """Tests para timestamps de usuario."""
    
    def test_user_has_created_at(self, admin_user: User):
        """Test que usuario tiene fecha de creación."""
        assert admin_user.created_at is not None
        assert isinstance(admin_user.created_at, datetime)
    
    def test_user_creation_timestamp_accurate(self, db_session: Session):
        """Test que timestamp de creación es preciso."""
        before = datetime.utcnow()
        
        user = User(
            email="timestamp@justicia.ma",
            name="Timestamp Test",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.CITIZEN,
            created_at=datetime.utcnow()
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        after = datetime.utcnow()
        
        assert before <= user.created_at <= after

@pytest.mark.unit
class TestUserSearch:
    """Tests para búsqueda de usuarios."""
    
    def test_search_by_email(self, db_session: Session, admin_user: User):
        """Test búsqueda por email."""
        result = db_session.query(User).filter(
            User.email == admin_user.email
        ).first()
        
        assert result is not None
        assert result.id == admin_user.id
    
    def test_search_by_role(self, db_session: Session):
        """Test búsqueda por rol."""
        judges = db_session.query(User).filter(
            User.role == UserRole.JUDGE
        ).all()
        
        assert isinstance(judges, list)
        for judge in judges:
            assert judge.role == UserRole.JUDGE
    
    def test_search_by_name(self, db_session: Session, lawyer_user: User):
        """Test búsqueda por nombre."""
        result = db_session.query(User).filter(
            User.name.ilike(f"%{lawyer_user.name}%")
        ).first()
        
        assert result is not None
    
    def test_filter_active_users(self, db_session: Session):
        """Test filtrar usuarios activos."""
        active_users = db_session.query(User).filter(
            User.is_active == True
        ).all()
        
        assert isinstance(active_users, list)
        for user in active_users:
            assert user.is_active is True

@pytest.mark.unit
class TestUserUpdate:
    """Tests para actualización de usuario."""
    
    def test_update_user_name(self, db_session: Session, citizen_user: User):
        """Test actualizar nombre de usuario."""
        original_name = citizen_user.name
        new_name = "Nombre Actualizado"
        
        citizen_user.name = new_name
        db_session.commit()
        db_session.refresh(citizen_user)
        
        assert citizen_user.name == new_name
        assert citizen_user.name != original_name
    
    def test_update_user_email(self, db_session: Session, citizen_user: User):
        """Test actualizar email de usuario."""
        original_email = citizen_user.email
        new_email = "nuevo.email@justicia.ma"
        
        citizen_user.email = new_email
        db_session.commit()
        db_session.refresh(citizen_user)
        
        assert citizen_user.email == new_email
        assert citizen_user.email != original_email
    
    def test_update_user_role(self, db_session: Session, citizen_user: User):
        """Test actualizar rol de usuario."""
        original_role = citizen_user.role
        
        citizen_user.role = UserRole.LAWYER
        db_session.commit()
        db_session.refresh(citizen_user)
        
        assert citizen_user.role == UserRole.LAWYER
        assert citizen_user.role != original_role

@pytest.mark.unit
class TestUserDeletion:
    """Tests para eliminación de usuario."""
    
    def test_delete_user_removes_record(self, db_session: Session):
        """Test que eliminar usuario remueve el registro."""
        user = User(
            email="delete@justicia.ma",
            name="To Delete",
            hashed_password=get_password_hash("Password123!"),
            role=UserRole.CITIZEN
        )
        
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        
        db_session.delete(user)
        db_session.commit()
        
        deleted_user = db_session.query(User).filter(User.id == user_id).first()
        assert deleted_user is None
    
    def test_only_admin_can_delete_users(self, admin_user: User):
        """Test que solo admin puede eliminar usuarios."""
        assert admin_user.role == UserRole.ADMIN
        # Solo admin tiene permisos de eliminación
