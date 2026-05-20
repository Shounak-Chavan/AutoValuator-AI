"""
test_health.py - Health Check Endpoint Tests

Tests for the root/health endpoints of the API.
These tests are great for beginners because they:
1. Test simple endpoints with no complex logic
2. Don't require authentication
3. Show how to use TestClient to make requests
4. Demonstrate basic assertion patterns

Why test health endpoints?
- Verify the API is running and responding
- Quick smoke test before more complex tests
- Good entry point to learn testing
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """
    Group related tests in a class for organization.
    This makes it easier to run all health-related tests together.
    """
    
    @pytest.mark.unit
    def test_root_endpoint_exists(self, client: TestClient):
        """
        Test: Does the root endpoint (/) respond?
        
        This is a smoke test to verify the API is running.
        
        How it works:
        1. client.get("/") - Makes a GET request to root
        2. response.status_code == 200 - Check for success status
        3. assert - Fail test if condition is false
        """
        response = client.get("/")
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_root_endpoint_response_format(self, client: TestClient):
        """
        Test: Does the root endpoint return expected data?
        """
        response = client.get("/")
        # response.json() converts JSON response to Python dict
        data = response.json()
        
        # Verify response contains expected keys
        assert "message" in data or "title" in data or len(data) > 0
    
    @pytest.mark.unit
    def test_invalid_endpoint_404(self, client: TestClient):
        """
        Test: Non-existent endpoints return 404?
        
        This verifies the API properly handles invalid routes.
        404 = Not Found (HTTP standard)
        """
        response = client.get("/this-endpoint-does-not-exist")
        assert response.status_code == 404
    
    @pytest.mark.unit
    def test_metrics_endpoint_exists(self, client: TestClient):
        """
        Test: Prometheus metrics endpoint is available?
        
        Your app exposes Prometheus metrics at /metrics
        This is important for monitoring and observability.
        """
        response = client.get("/metrics")
        # Metrics endpoint should exist (200) or be protected (401/403)
        assert response.status_code in [200, 401, 403]
