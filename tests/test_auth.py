"""
test_auth.py - Authentication Tests

Tests for the login endpoint and JWT token generation.
This demonstrates:
1. Testing POST endpoints with request bodies
2. Testing error cases (invalid credentials)
3. Testing successful authentication flows
4. Using fixtures for token generation

Key concepts:
- POST: Send data to create/modify resources
- Headers: Additional metadata sent with requests
- Status codes: 200=success, 401=unauthorized, 403=forbidden
"""

import pytest
from fastapi.testclient import TestClient
from app.core.security import create_token, verify_token


class TestAuthentication:
    """Group all authentication-related tests"""
    
    @pytest.mark.unit
    def test_login_success_with_valid_credentials(self, client: TestClient):
        """
        Test: Can user login with correct username and password?
        
        How it works:
        1. Prepare login data as JSON
        2. POST to /login endpoint
        3. Check response status is 200 (success)
        4. Verify response contains access token
        """
        # Prepare login data
        login_data = {
            "username": "admin",
            "password": "admin"
        }
        
        # Make POST request with JSON body
        # json= parameter automatically converts dict to JSON
        response = client.post("/login", json=login_data)
        
        # Verify successful response
        assert response.status_code == 200
        
        # Get response data
        data = response.json()
        
        # Verify token exists in response
        assert "access_token" in data
        assert data["access_token"] is not None
        assert len(data["access_token"]) > 0
    
    @pytest.mark.unit
    def test_login_failure_with_wrong_password(self, client: TestClient):
        """
        Test: Does login fail with incorrect password?
        
        Security is important! Wrong credentials should be rejected.
        Status code 200 here might seem odd - some APIs return 200 with error
        in body. We check both the status and response content.
        """
        login_data = {
            "username": "admin",
            "password": "wrong-password"
        }
        
        response = client.post("/login", json=login_data)
        data = response.json()
        
        # Should either fail with non-200 status or have error in response
        if response.status_code == 200:
            # If status is 200, check if error field exists
            assert "error" in data
        else:
            # Or fail with proper error status
            assert response.status_code in [401, 403]
    
    @pytest.mark.unit
    def test_login_failure_with_wrong_username(self, client: TestClient):
        """
        Test: Does login fail with incorrect username?
        """
        login_data = {
            "username": "wrong-user",
            "password": "admin"
        }
        
        response = client.post("/login", json=login_data)
        data = response.json()
        
        if response.status_code == 200:
            assert "error" in data
        else:
            assert response.status_code in [401, 403]
    
    @pytest.mark.unit
    def test_login_with_missing_fields(self, client: TestClient):
        """
        Test: Does API properly validate request body?
        
        If required fields are missing, FastAPI should reject the request
        with a 422 status code (Unprocessable Entity).
        """
        # Missing password field
        incomplete_data = {
            "username": "admin"
        }
        
        response = client.post("/login", json=incomplete_data)
        
        # Should fail validation
        assert response.status_code == 422
    
    @pytest.mark.unit
    def test_jwt_token_creation(self, valid_jwt_token):
        """
        Test: Can JWT tokens be created and verified?
        
        This tests the token utility functions directly.
        Notice we're NOT testing an endpoint, but testing a utility function.
        
        This demonstrates:
        - Testing non-endpoint code
        - Using the valid_jwt_token fixture
        """
        token = valid_jwt_token
        
        # Token should be a non-empty string
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    @pytest.mark.unit
    def test_jwt_token_verification(self, valid_jwt_token):
        """
        Test: Can JWT tokens be verified after creation?
        """
        token = valid_jwt_token
        
        # Verify the token
        payload = verify_token(token)
        
        # Should return a payload with user data
        assert payload is not None
        assert "sub" in payload
        assert payload["sub"] == "testuser"
    
    @pytest.mark.unit
    def test_jwt_invalid_token_returns_none(self):
        """
        Test: Invalid tokens fail gracefully?
        
        When an invalid token is provided, verify_token should return None.
        """
        invalid_token = "this-is-not-a-valid-jwt-token"
        
        payload = verify_token(invalid_token)
        
        # Should return None for invalid tokens
        assert payload is None


class TestTokenUtilities:
    """Group token utility function tests"""
    
    @pytest.mark.unit
    def test_token_contains_expiration(self, valid_jwt_token):
        """
        Test: Do generated tokens have expiration times?
        
        Security: Tokens should expire to limit damage if stolen.
        """
        token = valid_jwt_token
        payload = verify_token(token)
        
        # Token should contain expiration time
        assert "exp" in payload
        
        # Expiration should be a timestamp (integer)
        assert isinstance(payload["exp"], int)
        assert payload["exp"] > 0
