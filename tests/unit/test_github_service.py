"""Tests for GitHub service."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from job_agent.services.github_service import GitHubService
from job_agent.models.github import GitHubIssuesResponse


class TestGitHubService:
    """Test GitHub service functionality."""

    def test_github_service_initialization(self):
        """Test GitHub service can be initialized."""
        service = GitHubService()
        assert service.base_url == "https://api.github.com"
        assert service.github_token is None
        assert "Accept" in service.headers

    def test_github_service_with_token(self):
        """Test GitHub service initialization with token."""
        token = "test-token"
        service = GitHubService(github_token=token)
        assert service.github_token == token
        assert f"token {token}" in service.headers.get("Authorization", "")

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        service = GitHubService()
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "rate": {
                "limit": 60,
                "remaining": 59,
                "reset": 1234567890
            }
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await service.health_check()
            
            assert result["status"] == "healthy"
            assert "rate_limit" in result
            assert result["authenticated"] is False

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check failure."""
        service = GitHubService()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.HTTPError("Connection failed")
            )
            
            result = await service.health_check()
            
            assert result["status"] == "unhealthy"
            assert "error" in result

    @pytest.mark.asyncio
    async def test_get_open_issues_basic(self):
        """Test basic get_open_issues functionality."""
        service = GitHubService()
        
        # Mock response data
        mock_issues_data = [
            {
                "id": 1,
                "number": 1,
                "title": "Test Issue",
                "body": "Test body",
                "state": "open",
                "user": {
                    "login": "testuser",
                    "id": 123,
                    "avatar_url": "https://example.com/avatar.jpg"
                },
                "labels": [
                    {
                        "name": "bug",
                        "description": "Something isn't working",
                        "color": "d73a4a"
                    }
                ],
                "comments": 5,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z",
                "html_url": "https://github.com/test/test/issues/1"
            }
        ]
        
        mock_response = Mock()
        mock_response.json.return_value = mock_issues_data
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await service.get_open_issues("testowner", "testrepo")
            
            assert isinstance(result, GitHubIssuesResponse)
            assert len(result.issues) == 1
            assert result.issues[0].title == "Test Issue"
            assert result.owner == "testowner"
            assert result.repository == "testrepo"