import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.core.database import Base, get_db
from app.models.models import Usuario, Materia, Evaluacion, DatoHabitual, RegistroDiario
import bcrypt

def create_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    hashed = create_hash("testpass123")
    user = Usuario(
        email="test@example.com",
        nombre="Test User",
        hashed_password=hashed,
        objetivo_promedio=7.0
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_token(client, test_user):
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def test_materia(db_session, test_user):
    materia = Materia(
        usuario_id=test_user.id,
        nombre="Matemáticas I",
        objetivo_nota=7.5
    )
    db_session.add(materia)
    db_session.commit()
    db_session.refresh(materia)
    return materia


@pytest.fixture(scope="function")
def test_evaluacion(db_session, test_user, test_materia):
    evaluacion = Evaluacion(
        usuario_id=test_user.id,
        materia_id=test_materia.id,
        tipo="examen",
        nota=7.5,
        ponderacion=1.0
    )
    db_session.add(evaluacion)
    db_session.commit()
    db_session.refresh(evaluacion)
    return evaluacion


@pytest.fixture(scope="function")
def test_habito(db_session, test_user):
    habito = DatoHabitual(
        usuario_id=test_user.id,
        tipo="descanso",
        duracion_minutos=30,
        notas="Descanso entre sesiones"
    )
    db_session.add(habito)
    db_session.commit()
    db_session.refresh(habito)
    return habito
