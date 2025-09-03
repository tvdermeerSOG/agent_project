"""Dependency injection for FastAPI."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from job_agent.core.config import Settings, settings
from job_agent.core.health import HealthCheckService, get_health_service
from job_agent.services.github_service import GitHubService, get_github_service
from job_agent.services.job_service import JobService, get_job_service
from job_agent.services.openai_service import AzureOpenAIService, get_openai_service


@lru_cache
def get_settings() -> Settings:
    """Get application settings.

    Returns:
        Application settings instance
    """
    return settings


def get_job_data_service() -> JobService:
    """Get job data service dependency.

    Returns:
        JobService instance
    """
    return get_job_service()


def get_health_check_service() -> HealthCheckService:
    """Get health check service dependency.

    Returns:
        HealthCheckService instance
    """
    return get_health_service()


def get_azure_openai_service() -> AzureOpenAIService:
    """Get Azure OpenAI service dependency.

    Returns:
        AzureOpenAIService instance
    """
    return get_openai_service()


def get_github_data_service() -> GitHubService:
    """Get GitHub service dependency.

    Returns:
        GitHubService instance
    """
    return get_github_service()


# Type aliases for dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
JobServiceDep = Annotated[JobService, Depends(get_job_data_service)]
HealthServiceDep = Annotated[HealthCheckService, Depends(get_health_check_service)]
OpenAIServiceDep = Annotated[AzureOpenAIService, Depends(get_azure_openai_service)]
GitHubServiceDep = Annotated[GitHubService, Depends(get_github_data_service)]
