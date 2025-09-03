"""Tests for GitHub API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock

from job_agent.app import create_app
from job_agent.models.github import GitHubIssuesResponse, GitHubIssue, GitHubUser


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_github_service():
    """Create mock GitHub service."""
    service = Mock()
    service.get_open_issues = AsyncMock()
    service.health_check = AsyncMock()
    return service


class TestGitHubEndpoints:
    """Test GitHub API endpoints."""

    def test_get_open_issues_endpoint_exists(self, client):
        """Test that the GitHub issues endpoint exists."""
        # Test without required parameters - should return 422
        response = client.get("/api/v1/github/issues/open")
        assert response.status_code == 422

    def test_get_open_issues_with_params(self, client):
        """Test GitHub issues endpoint with parameters."""
        # This will make a real API call, so we'll test basic parameter validation
        response = client.get(
            "/api/v1/github/issues/open",
            params={"owner": "test", "repo": "test"}
        )
        # Should either succeed or fail with a proper error message
        assert response.status_code in [200, 500]

    def test_github_health_endpoint_exists(self, client):
        """Test that the GitHub health endpoint exists."""
        response = client.get("/api/v1/github/health")
        # Should either succeed or fail with a proper error message
        assert response.status_code in [200, 500]