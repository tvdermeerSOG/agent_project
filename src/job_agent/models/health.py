"""Health check models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    """Basic health check model."""

    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")
    checks: dict[str, Any] = Field(..., description="Individual check results")


class DetailedHealthCheck(HealthCheck):
    """Detailed health check with component-specific checks."""

    azure_openai: bool = Field(..., description="Azure OpenAI service status")
    configuration: bool = Field(..., description="Configuration validation status")
    job_data_access: bool = Field(..., description="Job data directory access")
    job_data_validation: bool = Field(..., description="Job data parsing validation")
    system_resources: dict[str, Any] = Field(..., description="System resource status")


class HealthCheckResponse(BaseModel):
    """Health check endpoint response."""

    health: HealthCheck
