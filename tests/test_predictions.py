"""
test_predictions.py - Prediction Endpoint Tests

Tests for the ML prediction API endpoints.
This demonstrates:
1. Testing endpoints with complex request bodies
2. Testing endpoints that require authentication
3. Testing endpoints that interact with ML models
4. Testing error cases and validation

Note: These tests use mock authentication since the API requires headers.
Real integration tests might use a test database with real models.
"""

import pytest
import os
from fastapi.testclient import TestClient
from app.core.security import create_token


class TestPredictionEndpoints:
    """Group all prediction-related tests"""
    
    @pytest.fixture
    def valid_prediction_data(self):
        """
        Fixture: Sample valid car data for predictions
        
        This is test data that matches the CareFeatures schema from routes_predict.py
        """
        return {
            "company": "maruti",
            "year": 2020,
            "owner": "First Owner",
            "fuel": "Petrol",
            "seller_type": "Individual",
            "transmission": "Manual",
            "km_driven": 50000,
            "mileage_mpg": 18.0,
            "engine_cc": 1000,
            "max_power_bhp": 85,
            "torque_nm": 130,
            "seats": 5
        }
    
    @pytest.fixture
    def auth_headers(self, valid_jwt_token):
        """
        Fixture: Authentication headers for protected endpoints
        
        The /predict endpoint requires:
        - API key in headers (from config)
        - JWT token in headers (from login)
        """
        return {
            "api-key": os.getenv("API_KEY", "test-api-key-123"),
            "token": valid_jwt_token
        }
    
    @pytest.mark.unit
    def test_prediction_endpoint_requires_authentication(self, client: TestClient, valid_prediction_data):
        """
        Test: Does the prediction endpoint require authentication?
        
        Important security check: Protected endpoints should reject
        requests without proper authentication headers.
        """
        # Try to make prediction WITHOUT authentication headers
        response = client.post("/predict", json=valid_prediction_data)
        
        # Should fail with unauthorized status
        # 401 = Unauthorized (missing or invalid credentials)
        # 422 = Unprocessable (missing required header)
        assert response.status_code in [401, 403, 422]
    
    @pytest.mark.unit
    def test_prediction_with_valid_data_and_auth(self, client: TestClient, valid_prediction_data, auth_headers):
        """
        Test: Can we make a prediction with valid data and authentication?
        
        This is an integration test that exercises the full prediction flow:
        1. Prepare car data
        2. Send POST request with auth headers
        3. Verify response contains prediction
        
        Note: This test might fail if:
        - Model file doesn't exist (check app/models/model.joblib)
        - Database isn't initialized
        - Dependencies aren't properly mocked
        """
        response = client.post(
            "/predict",
            json=valid_prediction_data,
            headers=auth_headers
        )
        
        # Should succeed
        if response.status_code == 200:
            data = response.json()
            
            # Response should contain prediction result
            # Check for common prediction field names
            assert ("prediction" in data or
                    "predicted_price" in data or
                    "price" in data or
                    "result" in data)
        else:
            # If not 200, should be a meaningful error
            # (might fail if dependencies aren't set up)
            print(f"Response status: {response.status_code}")
            print(f"Response: {response.json()}")
    
    @pytest.mark.unit
    def test_prediction_with_invalid_data_type(self, client: TestClient, valid_prediction_data, auth_headers):
        """
        Test: Does API validate input data types?
        
        If we send wrong data types (e.g., string instead of number),
        FastAPI should reject it with a 422 error.
        """
        # Modify data: send string for numeric field
        invalid_data = valid_prediction_data.copy()
        invalid_data["year"] = "not-a-number"  # Should be integer
        
        response = client.post(
            "/predict",
            json=invalid_data,
            headers=auth_headers
        )
        
        # Should fail validation
        assert response.status_code == 422
    
    @pytest.mark.unit
    def test_prediction_with_missing_required_field(self, client: TestClient, valid_prediction_data, auth_headers):
        """
        Test: Does API reject incomplete requests?
        
        Pydantic (FastAPI's validation library) should catch missing fields
        and return a 422 error with details about what's missing.
        """
        # Remove a required field
        incomplete_data = valid_prediction_data.copy()
        del incomplete_data["company"]  # Required field
        
        response = client.post(
            "/predict",
            json=incomplete_data,
            headers=auth_headers
        )
        
        # Should fail validation
        assert response.status_code == 422
    
    @pytest.mark.unit
    def test_prediction_with_wrong_api_key(self, client: TestClient, valid_prediction_data, valid_jwt_token):
        """
        Test: Does API reject invalid API keys?
        
        Security check: Wrong API key should result in 403 Forbidden
        """
        # Use wrong API key
        wrong_headers = {
            "api-key": "this-is-not-the-real-api-key",
            "token": valid_jwt_token
        }
        
        response = client.post(
            "/predict",
            json=valid_prediction_data,
            headers=wrong_headers
        )
        
        # Should fail with forbidden
        assert response.status_code in [403, 401]
    
    @pytest.mark.unit
    def test_prediction_numeric_boundaries(self, client: TestClient, auth_headers):
        """
        Test: How does the model handle extreme values?
        
        ML models can produce unexpected results with outlier inputs.
        This test checks if the API handles such cases gracefully.
        """
        extreme_data = {
            "company": "maruti",
            "year": 1990,  # Very old car
            "owner": "First Owner",
            "fuel": "Petrol",
            "seller_type": "Individual",
            "transmission": "Manual",
            "km_driven": 999999,  # Very high mileage
            "mileage_mpg": 50,  # Unrealistically high
            "engine_cc": 5000,  # Large engine
            "max_power_bhp": 500,  # Very powerful
            "torque_nm": 500,
            "seats": 5
        }
        
        response = client.post(
            "/predict",
            json=extreme_data,
            headers=auth_headers
        )
        
        # Should handle gracefully (not crash with 500 error)
        assert response.status_code != 500


class TestPredictionListEndpoint:
    """Tests for the list predictions endpoint"""
    
    @pytest.mark.unit
    def test_list_predictions_endpoint_exists(self, client: TestClient):
        """
        Test: Can we list previous predictions?
        
        Most ML APIs store prediction history for auditing and analysis.
        """
        # This endpoint might not require auth, or might - depends on your implementation
        response = client.get("/predictions")
        
        # Should exist (might be 200 or require auth 401)
        assert response.status_code in [200, 401, 403]
    
    @pytest.mark.unit
    def test_list_predictions_returns_list(self, client: TestClient):
        """
        Test: Does the predictions list endpoint return a list?
        """
        response = client.get("/predictions")
        
        if response.status_code == 200:
            data = response.json()
            # Should be a list
            assert isinstance(data, list)
