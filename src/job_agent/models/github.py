"""GitHub-related models."""

from datetime import datetime

from pydantic import BaseModel, Field


class GitHubUser(BaseModel):
    """GitHub user model."""

    login: str = Field(..., description="User login name")
    id: int = Field(..., description="User ID")
    avatar_url: str | None = Field(None, description="User avatar URL")


class GitHubLabel(BaseModel):
    """GitHub label model."""

    name: str = Field(..., description="Label name")
    description: str | None = Field(None, description="Label description")
    color: str = Field(..., description="Label color")


class GitHubIssue(BaseModel):
    """GitHub issue model."""

    id: int = Field(..., description="Issue ID")
    number: int = Field(..., description="Issue number")
    title: str = Field(..., description="Issue title")
    body: str | None = Field(None, description="Issue body")
    state: str = Field(..., description="Issue state (open/closed)")
    user: GitHubUser = Field(..., description="Issue creator")
    labels: list[GitHubLabel] = Field(default_factory=list, description="Issue labels")
    comments: int = Field(..., description="Number of comments")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    html_url: str | None = Field(None, description="Issue URL")


class GitHubIssuesResponse(BaseModel):
    """Response model for GitHub issues listing."""

    issues: list[GitHubIssue] = Field(..., description="List of issues")
    total_count: int = Field(..., description="Total number of issues")
    repository: str = Field(..., description="Repository name")
    owner: str = Field(..., description="Repository owner")
