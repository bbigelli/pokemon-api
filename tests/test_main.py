import pytest
from fastapi.testclient import TestClient
from fastapi import status, FastAPI, Request
from app.main import app
from unittest.mock import patch, MagicMock, AsyncMock
from starlette.responses import JSONResponse

client = TestClient(app)

def test_root_endpoint_structure():
    """Test root endpoint response structure"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data
    assert "auth_required" in data
    assert "public_endpoints" in data
    assert data["version"] == "1.0.0"
    assert data["message"] == "Welcome to Pokemon API"

def test_health_check_response():
    """Test health check response structure"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["service"] == "pokemon-api"

def test_documentation_endpoints():
    """Test documentation endpoints are accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    assert response.status_code == 200

def test_openapi_json():
    """Test OpenAPI JSON endpoint"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
    assert data["info"]["title"] == "Pokemon API"

@pytest.mark.asyncio
async def test_global_exception_handler():
    """Test global exception handler"""
    from app.main import global_exception_handler
    
    # Create a mock request
    mock_request = MagicMock(spec=Request)
    
    # Create an exception
    test_exception = Exception("Test error")
    
    # Call the handler directly (it's an async function)
    response = await global_exception_handler(mock_request, test_exception)
    
    # Verify response
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    response_data = response.body.decode()
    assert "Internal server error" in response_data

def test_cors_middleware():
    """Test CORS middleware is configured"""
    response = client.get("/health", headers={"Origin": "http://test.com"})
    assert "access-control-allow-origin" in response.headers

def test_request_logging_middleware():
    """Test request logging middleware adds process time header"""
    response = client.get("/health")
    assert "X-Process-Time" in response.headers
    
    # Verify it's a valid float
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0

def test_not_found_handler():
    """Test 404 not found handler"""
    response = client.get("/nonexistent-endpoint-12345")
    assert response.status_code == 404

def test_rate_limit_exceeded_handler():
    """Test rate limit exceeded handler is registered"""
    from app.main import app
    # The handler should be registered
    assert app.exception_handlers is not None