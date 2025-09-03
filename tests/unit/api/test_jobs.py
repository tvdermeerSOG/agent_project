"""Test FastAPI job endpoints."""

import pytest
from fastapi.testclient import TestClient

from job_agent.app import create_app


@pytest.fixture()
def client():
    """Create a test client."""
    app = create_app()
    return TestClient(app)


def test_list_jobs_endpoint(client):
    """Test the job listing endpoint."""
    response = client.get("/api/v1/jobs/")
    assert response.status_code == 200

    data = response.json()
    assert "jobs" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data

    assert isinstance(data["jobs"], list)
    assert data["total"] >= 0
    assert data["page"] == 1
    assert data["page_size"] == 50


def test_list_jobs_with_pagination(client):
    """Test job listing with pagination parameters."""
    response = client.get("/api/v1/jobs/?page=1&page_size=2")
    assert response.status_code == 200

    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["jobs"]) <= 2


def test_list_jobs_with_filters(client):
    """Test job listing with filters."""
    response = client.get("/api/v1/jobs/?client=Amsterdam")
    assert response.status_code == 200

    data = response.json()
    # If there are results, they should match the filter
    for job in data["jobs"]:
        assert "amsterdam" in job["client"].lower()


def test_get_specific_job(client):
    """Test getting a specific job by ID."""
    # First get list of jobs to find a valid ID
    list_response = client.get("/api/v1/jobs/")
    assert list_response.status_code == 200

    jobs_data = list_response.json()
    if jobs_data["total"] > 0:
        first_job_id = jobs_data["jobs"][0]["id"]

        # Get the specific job
        response = client.get(f"/api/v1/jobs/{first_job_id}")
        assert response.status_code == 200

        data = response.json()
        assert "job" in data
        assert data["job"]["id"] == first_job_id


def test_get_nonexistent_job(client):
    """Test getting a non-existent job."""
    response = client.get("/api/v1/jobs/nonexistent_job")
    assert response.status_code == 404


def test_refresh_jobs_endpoint(client):
    """Test the job refresh endpoint."""
    response = client.post("/api/v1/jobs/refresh")
    assert response.status_code == 200

    data = response.json()
    assert "success" in data
    assert "message" in data
    assert "jobs_processed" in data
    assert "errors" in data

    assert isinstance(data["success"], bool)
    assert isinstance(data["jobs_processed"], int)
    assert isinstance(data["errors"], list)
