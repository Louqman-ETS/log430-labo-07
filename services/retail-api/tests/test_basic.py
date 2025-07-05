import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test de l'endpoint de santé."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
    assert "timestamp" in data


def test_root_endpoint(client: TestClient):
    """Test de l'endpoint racine."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_docs_endpoint(client: TestClient):
    """Test de l'endpoint de documentation."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_endpoint(client: TestClient):
    """Test de l'endpoint OpenAPI."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
