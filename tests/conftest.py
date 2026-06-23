import os
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.db.models import Prediction
from app.main import app
from app.db.base import Base
from app.core.dependencies import get_api_key, get_current_user
from app.db.session import get_db


# Shared in-memory SQLite database
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db: Session):

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_with_auth(client: TestClient):

    client.headers.update(
        {
            "api-key": os.getenv("API_KEY", "test-api-key"),
            "token": "test-jwt-token",
        }
    )

    return client


@pytest.fixture(scope="function")
def valid_jwt_token():
    from app.core.security import create_token

    return create_token({"sub": "testuser"})