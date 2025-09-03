"""GitHub API endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from job_agent.api.deps import GitHubServiceDep
from job_agent.models.github import GitHubIssuesResponse

router = APIRouter(prefix="/github", tags=["github"])


@router.get("/issues/open", response_model=GitHubIssuesResponse)
async def get_open_issues(
    github_service: GitHubServiceDep,
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(30, ge=1, le=100, description="Number of issues per page")
) -> GitHubIssuesResponse:
    """Get open issues from a GitHub repository.

    Args:
        github_service: GitHub service dependency
        owner: Repository owner (e.g., 'tvdermeerSOG')
        repo: Repository name (e.g., 'agent_project')
        page: Page number for pagination (default: 1)
        per_page: Number of issues per page (default: 30, max: 100)

    Returns:
        List of open issues with metadata

    Raises:
        HTTPException: If the GitHub API request fails
    """
    try:
        issues_response = await github_service.get_open_issues(
            owner=owner,
            repo=repo,
            page=page,
            per_page=per_page
        )
        return issues_response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch GitHub issues: {str(e)}"
        )


@router.get("/health")
async def github_health_check(github_service: GitHubServiceDep) -> dict[str, Any]:
    """Check GitHub API connectivity and rate limits.

    Args:
        github_service: GitHub service dependency

    Returns:
        GitHub API health status
    """
    try:
        health_status = await github_service.health_check()
        return health_status

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"GitHub health check failed: {str(e)}"
        )
