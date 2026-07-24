"""
Configuration pytest partagee : base SQLite en memoire, TestClient FastAPI,
et fixtures pour creer des utilisateurs de chaque role avec leur token.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.role import RoleName

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _register_and_login(client: TestClient, email: str, role: str) -> str:
    client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Test User",
            "password": "test1234",
            "role": role,
        },
    )
    response = client.post(
        "/auth/login",
        data={"username": email, "password": "test1234"},
    )
    return response.json()["access_token"]


@pytest.fixture()
def student_token(client):
    return _register_and_login(client, "student@test.com", RoleName.STUDENT.value)


@pytest.fixture()
def company_token(client):
    return _register_and_login(client, "company@test.com", RoleName.COMPANY.value)


@pytest.fixture()
def manager_token(client):
    return _register_and_login(client, "manager@test.com", RoleName.PROGRAM_MANAGER.value)


@pytest.fixture()
def admin_token(client):
    return _register_and_login(client, "admin@test.com", RoleName.ADMIN.value)


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
