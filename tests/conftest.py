# tests/conftest.py
"""
Fixtures globales para la suite de pruebas de MediBook.

Provee:
  - Motor de BD en SQLite (aislado de producción)
  - Sesión de BD por cada test (con rollback automático)
  - Cliente HTTP de prueba para FastAPI (TestClient)
  - Fixtures de autenticación para tests con RBAC
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from medibook.infra.db import Base
from medibook.api.dependencies import get_db
from medibook.main import app

from medibook.domain.specialty import Specialty
from medibook.domain.doctor import Doctor
from medibook.domain.patient import Patient
from medibook.domain.user import User
from medibook.api.auth.password import password_hasher
from medibook.api.auth.token import token_service

from fastapi.testclient import TestClient


# ---------- Engine y Session de Prueba (SQLite) ----------

TEST_DATABASE_URL = "sqlite:///./test_medibook.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = sessionmaker(
    bind=test_engine, autoflush=False, autocommit=False
)


# ---------- Fixtures ----------

@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """Crea todas las tablas al inicio de la sesión de tests."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Provee una sesión de BD limpia para cada test.
    Hace rollback al final para aislar los tests entre sí.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """
    Cliente HTTP de prueba que inyecta la sesión de test
    en lugar de la sesión de producción.
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ---------- Fixtures de Datos ----------

@pytest.fixture
def sample_specialty(db_session: Session) -> Specialty:
    """Crea una especialidad de prueba."""
    specialty = Specialty(name="Cardiología", description="Especialidad del corazón")
    db_session.add(specialty)
    db_session.commit()
    db_session.refresh(specialty)
    return specialty


@pytest.fixture
def sample_doctor(db_session: Session, sample_specialty: Specialty) -> Doctor:
    """Crea un doctor de prueba asociado a una especialidad."""
    doctor = Doctor(
        name="Dr. Test",
        email="test@medibook.com",
        phone="+52 55 0000 0000",
        specialty_id=sample_specialty.id,
        active=True,
    )
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)
    return doctor


@pytest.fixture
def sample_patient(db_session: Session) -> Patient:
    """Crea un paciente de prueba."""
    patient = Patient(
        full_name="Paciente Test",
        email="paciente@test.com",
        phone="+52 55 1111 1111",
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


# ---------- Fixtures de Autenticación ----------

def _create_user_and_token(
    db_session: Session,
    username: str,
    role: str,
) -> dict:
    """Helper: crea un usuario y retorna sus headers con token JWT."""
    user = User(
        username=username,
        email=f"{username}@test.com",
        hashed_password=password_hasher.hash("TestPass123"),
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = token_service.create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(db_session: Session) -> dict:
    """Headers con token JWT de un usuario ADMIN."""
    return _create_user_and_token(db_session, "admin_test", "ADMIN")


@pytest.fixture
def doctor_headers(db_session: Session) -> dict:
    """Headers con token JWT de un usuario DOCTOR."""
    return _create_user_and_token(db_session, "doctor_test", "DOCTOR")


@pytest.fixture
def receptionist_headers(db_session: Session) -> dict:
    """Headers con token JWT de un usuario RECEPTIONIST."""
    return _create_user_and_token(db_session, "receptionist_test", "RECEPTIONIST")


@pytest.fixture
def patient_headers(db_session: Session) -> dict:
    """Headers con token JWT de un usuario PATIENT."""
    return _create_user_and_token(db_session, "patient_test", "PATIENT")
