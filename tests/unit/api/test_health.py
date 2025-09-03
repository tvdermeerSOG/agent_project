"""Test FastAPI health endpoints."""

import pytest
from fastapi.testclient import TestClient

from job_agent.app import create_app


@pytest.fixture()
def client():
    """Create a test client."""
    app = create_app()
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert data["api"] == "/api/v1"


def test_health_endpoint(client):
    """Test the basic health endpoint."""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200

    data = response.json()
    assert "health" in data

    health = data["health"]
    assert "status" in health
    assert "timestamp" in health
    assert "version" in health
    assert "checks" in health


def test_detailed_health_endpoint(client):
    """Test the detailed health endpoint."""
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200

    data = response.json()
    assert "health" in data

    health = data["health"]
    assert "status" in health
    assert "checks" in health

    checks = health["checks"]
    assert "azure_openai" in checks
    assert "configuration" in checks
    assert "job_data_access" in checks
    assert "job_data_validation" in checks
    assert "system_resources" in checks


def test_readiness_endpoint(client):
    """Test the readiness probe endpoint."""
    response = client.get("/api/v1/health/ready")
    # Should be either 200 (ready) or 503 (not ready)
    assert response.status_code in [200, 503]

    data = response.json()
    if response.status_code == 200:
        assert data["status"] == "ready"


def test_liveness_endpoint(client):
    """Test the liveness probe endpoint."""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "alive"
