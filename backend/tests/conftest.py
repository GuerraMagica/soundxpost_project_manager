"""Pytest fixtures: isolated in-memory SQLite DB per test."""
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    session = TestingSessionLocal()
    yield session
    session.close()
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    return TestClient(app)


def _create_user(db_session, email: str, role: str, password: str = "TestPass123!"):
    from app import models
    from app.auth import hash_password

    user = models.User(
        name=f"Test {role}",
        email=email,
        role=role,
        hashed_password=hash_password(password),
        is_active=True,
        is_demo=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user, password


@pytest.fixture()
def admin_client(client, db_session):
    """A TestClient authenticated as an ADMIN user (bearer token attached)."""
    user, password = _create_user(db_session, "admin@test.local", "ADMIN")
    resp = client.post("/api/auth/login", json={"email": user.email, "password": password})
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture()
def make_user(db_session):
    """Factory fixture: create additional users with arbitrary roles for a test."""

    def _make(email: str, role: str, password: str = "TestPass123!"):
        return _create_user(db_session, email, role, password)

    return _make


def login_as(client, email: str, password: str) -> TestClient:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
