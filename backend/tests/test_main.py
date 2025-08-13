"""
Test main application endpoints.
"""
import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "MyChordHub API"


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "mychordhub-backend"


def test_openapi_docs(client: TestClient):
    """Test OpenAPI documentation is accessible."""
    response = client.get("/api/v1/docs")
    assert response.status_code == 200


def test_openapi_json(client: TestClient):
    """Test OpenAPI JSON schema is accessible."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data