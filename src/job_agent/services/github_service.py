"""GitHub API service for repository operations."""

from functools import lru_cache
from typing import Any

import httpx
import structlog
from pydantic import ValidationError

from job_agent.core.config import settings
from job_agent.models.github import (
    GitHubIssue,
    GitHubIssuesResponse,
    GitHubLabel,
    GitHubUser,
)

logger = structlog.get_logger(__name__)


class GitHubService:
    """Service for interacting with GitHub API."""

    def __init__(self, github_token: str | None = None) -> None:
        """Initialize GitHub service.

        Args:
            github_token: Optional GitHub token for authenticated requests
        """
        self.base_url = "https://api.github.com"
        self.github_token = github_token
        self.timeout = 30.0

        # Headers for GitHub API
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"{settings.app_name}/{settings.app_version}",
        }

        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"

    async def get_open_issues(
        self,
        owner: str,
        repo: str,
        page: int = 1,
        per_page: int = 30
    ) -> GitHubIssuesResponse:
        """Get open issues from a GitHub repository.

        Args:
            owner: Repository owner
            repo: Repository name
            page: Page number for pagination
            per_page: Number of issues per page (max 100)

        Returns:
            GitHubIssuesResponse with list of open issues

        Raises:
            httpx.HTTPError: If the GitHub API request fails
            ValidationError: If the response data is invalid
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {
            "state": "open",
            "page": page,
            "per_page": min(per_page, 100),  # GitHub API limit
            "sort": "created",
            "direction": "desc"
        }

        logger.info(
            "Fetching open issues",
            owner=owner,
            repo=repo,
            page=page,
            per_page=per_page
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()

                issues_data = response.json()

                # Convert raw GitHub API response to our models
                issues = []
                for issue_data in issues_data:
                    try:
                        # Parse user
                        user_data = issue_data.get("user", {})
                        user = GitHubUser(
                            login=user_data.get("login", "unknown"),
                            id=user_data.get("id", 0),
                            avatar_url=user_data.get("avatar_url")
                        )

                        # Parse labels
                        labels = []
                        for label_data in issue_data.get("labels", []):
                            label = GitHubLabel(
                                name=label_data.get("name", ""),
                                description=label_data.get("description"),
                                color=label_data.get("color", "")
                            )
                            labels.append(label)

                        # Parse issue
                        issue = GitHubIssue(
                            id=issue_data.get("id", 0),
                            number=issue_data.get("number", 0),
                            title=issue_data.get("title", ""),
                            body=issue_data.get("body"),
                            state=issue_data.get("state", "open"),
                            user=user,
                            labels=labels,
                            comments=issue_data.get("comments", 0),
                            created_at=issue_data.get("created_at"),
                            updated_at=issue_data.get("updated_at"),
                            html_url=issue_data.get("html_url")
                        )
                        issues.append(issue)

                    except ValidationError as e:
                        logger.warning(
                            "Failed to parse issue data",
                            issue_id=issue_data.get("id"),
                            error=str(e)
                        )
                        continue

                # Get total count from headers if available
                total_count = len(issues)
                if "Link" in response.headers:
                    # Parse pagination info if needed
                    # For now, just use the current page count
                    pass

                result = GitHubIssuesResponse(
                    issues=issues,
                    total_count=total_count,
                    repository=repo,
                    owner=owner
                )

                logger.info(
                    "Successfully fetched issues",
                    owner=owner,
                    repo=repo,
                    count=len(issues)
                )

                return result

        except httpx.HTTPError as e:
            logger.error(
                "GitHub API request failed",
                owner=owner,
                repo=repo,
                error=str(e)
            )
            raise
        except Exception as e:
            logger.error(
                "Unexpected error fetching issues",
                owner=owner,
                repo=repo,
                error=str(e)
            )
            raise

    async def health_check(self) -> dict[str, Any]:
        """Check if GitHub API is accessible.

        Returns:
            Health check result
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/rate_limit",
                    headers=self.headers
                )
                response.raise_for_status()

                rate_limit_data = response.json()

                return {
                    "status": "healthy",
                    "rate_limit": rate_limit_data.get("rate", {}),
                    "authenticated": self.github_token is not None
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "authenticated": self.github_token is not None
            }


@lru_cache
def get_github_service() -> GitHubService:
    """Get a cached GitHub service instance.

    Returns:
        GitHubService instance
    """
    # For now, we'll use no token (public API access)
    # In production, this would come from environment variables
    github_token = getattr(settings, "github_token", None)
    return GitHubService(github_token=github_token)
