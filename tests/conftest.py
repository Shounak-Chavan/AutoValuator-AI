"""
conftest.py - Pytest Configuration & Fixtures

This file is automatically discovered and loaded by pytest before running tests.
It contains shared fixtures that multiple test files can use to avoid code duplication.

What are fixtures?
- Fixtures are functions that set up test data or dependencies
- Use the @pytest.fixture decorator
- Tests receive fixtures as function parameters
- Fixtures can be reused across multiple tests
"""

import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.db.base import Base
from app.core.dependencies import  get_api_key, get_current_user
from app.db.session import get_db


# Test Database Setup
# Using SQLite in-memory database for tests (fast and isolated)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create all tables in test database
Base.metadata.create_all(bind=engine)

# Session factory for tests
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Database fixture that provides a clean database for each test.
    
    Scope "function" means a fresh database is created for each test,
    ensuring tests don't interfere with each other.
    
    Usage in tests:
        def test_something(db):
            # db is an active database session
    """
    # Create fresh tables for this test
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    yield db  # Give database to test
    
    db.close()
    # Clean up after test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session):
    """
    TestClient fixture that provides a test client for making HTTP requests.
    
    TestClient simulates HTTP requests without actually starting a server.
    This makes tests fast and safe for development.
    
    It also injects the test database into the app so tests use test data,
    not production data.
    
    Usage in tests:
        def test_api_endpoint(client):
            response = client.get("/api/endpoint")
    """
    # Override get_db dependency to use test database
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    # Inject test database into FastAPI app
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    test_client = TestClient(app)
    
    yield test_client
    
    # Clean up: remove overrides after test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_with_auth(client: TestClient) -> TestClient:
    """
    Test client fixture that includes authentication headers.
    
    For testing protected endpoints that require API key and JWT token.
    
    Usage in tests:
        def test_protected_endpoint(client_with_auth):
            response = client_with_auth.get("/protected")
    """
    # Set default test API key
    client.headers.update({
        "api-key": os.getenv("API_KEY", "test-api-key-123"),
        "token": "test-jwt-token"  # Will be generated in actual tests
    })
    
    return client


@pytest.fixture(scope="function")
def valid_jwt_token():
    """
    Fixture that generates a valid JWT token for testing authentication.
    
    Usage in tests:
        def test_with_token(valid_jwt_token):
            headers = {"token": valid_jwt_token}
    """
    from app.core.security import create_token
    token = create_token({"sub": "testuser"})
    return token
