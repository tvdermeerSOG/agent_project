"""Health check API endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException

from job_agent.api.deps import HealthServiceDep
from job_agent.models.health import HealthCheckResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthCheckResponse)
async def get_health(health_service: HealthServiceDep) -> HealthCheckResponse:
    """Get basic application health status.

    Returns:
        Basic health check information
    """
    try:
        health = await health_service.get_basic_health()
        return HealthCheckResponse(health=health)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/detailed", response_model=HealthCheckResponse)
async def get_detailed_health(health_service: HealthServiceDep) -> HealthCheckResponse:
    """Get detailed application health status with component checks.

    Returns:
        Detailed health check information including:
        - Azure OpenAI service status
        - Job data access and validation
        - System resource usage
        - Configuration validation
    """
    try:
        health = await health_service.get_detailed_health()
        return HealthCheckResponse(health=health)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Detailed health check failed: {str(e)}"
        )


@router.get("/ready")
async def readiness_check(health_service: HealthServiceDep) -> dict[str, Any]:
    """Kubernetes-style readiness probe.

    Returns:
        Simple ready/not ready status
    """
    try:
        health = await health_service.get_detailed_health()

        if health.status == "healthy":
            return {"status": "ready"}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Readiness check failed: {str(e)}")


@router.get("/live")
async def liveness_check() -> dict[str, Any]:
    """Kubernetes-style liveness probe.

    Returns:
        Simple alive status
    """
    return {"status": "alive"}
