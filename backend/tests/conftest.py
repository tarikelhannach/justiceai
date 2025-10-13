# backend/tests/conftest.py - Configuración Completa de Tests para Sistema Judicial

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta
from typing import Generator, Dict
import tempfile
import os

from app.main import app
from app.database import get_db
from app.models import Base, User, Case, Document
from app.auth.auth import get_password_hash, create_access_token

# Base de datos de testing en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Limpiar tablas
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

# ============================================================================
# FIXTURES DE USUARIOS POR ROL - Sistema Gubernamental Marroquí
# ============================================================================

@pytest.fixture(scope="function")
def admin_user(db_session: Session) -> User:
    """Usuario con rol de Administrador."""
    user = User(
        email="admin@justicia.ma",
        name="Administrador Sistema",
        hashed_password=get_password_hash("Admin123!"),
        role="admin",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def judge_user(db_session: Session) -> User:
    """Usuario con rol de Juez."""
    user = User(
        email="juez@justicia.ma",
        name="Juez Mohamed El Fassi",
        hashed_password=get_password_hash("Judge123!"),
        role="judge",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def lawyer_user(db_session: Session) -> User:
    """Usuario con rol de Abogado."""
    user = User(
        email="abogado@justicia.ma",
        name="Abogado Fatima Zahra",
        hashed_password=get_password_hash("Lawyer123!"),
        role="lawyer",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def clerk_user(db_session: Session) -> User:
    """Usuario con rol de Secretario Judicial."""
    user = User(
        email="secretario@justicia.ma",
        name="Secretario Ahmed Benani",
        hashed_password=get_password_hash("Clerk123!"),
        role="clerk",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def citizen_user(db_session: Session) -> User:
    """Usuario con rol de Ciudadano."""
    user = User(
        email="ciudadano@justicia.ma",
        name="Ciudadano Hassan Ibrahim",
        hashed_password=get_password_hash("Citizen123!"),
        role="citizen",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

# ============================================================================
# FIXTURES DE TOKENS DE AUTENTICACIÓN
# ============================================================================

@pytest.fixture(scope="function")
def admin_token(admin_user: User) -> str:
    """Token de autenticación para administrador."""
    return create_access_token({"sub": admin_user.email, "user_id": admin_user.id})

@pytest.fixture(scope="function")
def judge_token(judge_user: User) -> str:
    """Token de autenticación para juez."""
    return create_access_token({"sub": judge_user.email, "user_id": judge_user.id})

@pytest.fixture(scope="function")
def lawyer_token(lawyer_user: User) -> str:
    """Token de autenticación para abogado."""
    return create_access_token({"sub": lawyer_user.email, "user_id": lawyer_user.id})

@pytest.fixture(scope="function")
def clerk_token(clerk_user: User) -> str:
    """Token de autenticación para secretario."""
    return create_access_token({"sub": clerk_user.email, "user_id": clerk_user.id})

@pytest.fixture(scope="function")
def citizen_token(citizen_user: User) -> str:
    """Token de autenticación para ciudadano."""
    return create_access_token({"sub": citizen_user.email, "user_id": citizen_user.id})

# ============================================================================
# FIXTURES DE HEADERS DE AUTENTICACIÓN
# ============================================================================

@pytest.fixture(scope="function")
def admin_headers(admin_token: str) -> Dict[str, str]:
    """Headers de autenticación para administrador."""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture(scope="function")
def judge_headers(judge_token: str) -> Dict[str, str]:
    """Headers de autenticación para juez."""
    return {"Authorization": f"Bearer {judge_token}"}

@pytest.fixture(scope="function")
def lawyer_headers(lawyer_token: str) -> Dict[str, str]:
    """Headers de autenticación para abogado."""
    return {"Authorization": f"Bearer {lawyer_token}"}

@pytest.fixture(scope="function")
def clerk_headers(clerk_token: str) -> Dict[str, str]:
    """Headers de autenticación para secretario."""
    return {"Authorization": f"Bearer {clerk_token}"}

@pytest.fixture(scope="function")
def citizen_headers(citizen_token: str) -> Dict[str, str]:
    """Headers de autenticación para ciudadano."""
    return {"Authorization": f"Bearer {citizen_token}"}

# ============================================================================
# FIXTURES DE DATOS DE PRUEBA - Sistema Judicial
# ============================================================================

@pytest.fixture(scope="function")
def sample_case(db_session: Session, lawyer_user: User, judge_user: User) -> Case:
    """Caso judicial de muestra."""
    case = Case(
        case_number="CAS-2025-001",
        title="Caso de Prueba - Demanda Civil",
        description="Caso de prueba para testing del sistema",
        case_type="civil",
        status="open",
        owner_id=lawyer_user.id,
        assigned_judge_id=judge_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)
    return case

@pytest.fixture(scope="function")
def sample_document(db_session: Session, sample_case: Case, lawyer_user: User) -> Document:
    """Documento judicial de muestra."""
    doc = Document(
        filename="demanda_inicial.pdf",
        file_path="/uploads/demanda_inicial.pdf",
        file_type="application/pdf",
        file_size=1024000,
        case_id=sample_case.id,
        uploaded_by=lawyer_user.id,
        created_at=datetime.utcnow()
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)
    return doc

# ============================================================================
# FIXTURES DE MOCKS - Servicios Externos
# ============================================================================

@pytest.fixture(scope="function")
def mock_redis():
    """Mock de Redis para testing."""
    import redis
    from unittest.mock import Mock
    
    mock_redis = Mock(spec=redis.Redis)
    mock_redis.ping.return_value = True
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.exists.return_value = False
    mock_redis.keys.return_value = []
    mock_redis.lpush.return_value = 1
    
    return mock_redis

@pytest.fixture(scope="function")
def mock_elasticsearch():
    """Mock de Elasticsearch para testing."""
    from unittest.mock import Mock
    
    mock_es = Mock()
    mock_es.ping.return_value = True
    mock_es.search.return_value = {
        "hits": {
            "total": {"value": 0},
            "hits": []
        }
    }
    mock_es.index.return_value = {"result": "created"}
    mock_es.delete.return_value = {"result": "deleted"}
    
    return mock_es

@pytest.fixture(scope="function")
def mock_hsm():
    """Mock de HSM para testing de firmas digitales."""
    from unittest.mock import Mock
    
    mock_hsm = Mock()
    mock_hsm.sign.return_value = b"mock_signature_bytes"
    mock_hsm.verify.return_value = True
    
    return mock_hsm

# ============================================================================
# CONFIGURACIÓN DE PYTEST
# ============================================================================

def pytest_configure(config):
    """Configuración de pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "rbac: marks tests for role-based access control"
    )
