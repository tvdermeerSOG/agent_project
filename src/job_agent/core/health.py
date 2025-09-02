"""Health check logic and utilities."""

import asyncio
from datetime import UTC, datetime
from typing import Any

import psutil
import structlog

from job_agent.core.config import settings
from job_agent.models.health import DetailedHealthCheck, HealthCheck
from job_agent.services.job_service import get_job_service
from job_agent.services.openai_service import get_openai_service

logger = structlog.get_logger()


class HealthCheckService:
    """Service for performing application health checks."""

    def __init__(self) -> None:
        """Initialize the health check service."""
        self._cache: dict[str, Any] = {}
        self._cache_ttl = (
            settings.health_checks.cache_ttl if settings.health_checks else 30
        )
        self._timeout = settings.health_checks.timeout if settings.health_checks else 5

    async def get_basic_health(self) -> HealthCheck:
        """Get basic health status.

        Returns:
            Basic health check result
        """
        checks = {"status": "healthy", "timestamp": datetime.now(UTC).isoformat()}

        return HealthCheck(
            status="healthy",
            timestamp=datetime.now(UTC),
            version=settings.app_version,
            checks=checks,
        )

    async def get_detailed_health(self) -> DetailedHealthCheck:
        """Get detailed health status with component checks.

        Returns:
            Detailed health check result
        """
        # Perform individual health checks
        checks = await asyncio.gather(
            self._check_azure_openai(),
            self._check_configuration(),
            self._check_job_data_access(),
            self._check_job_data_validation(),
            self._check_system_resources(),
            return_exceptions=True,
        )

        (
            azure_openai,
            configuration,
            job_data_access,
            job_data_validation,
            system_resources,
        ) = checks

        # Handle exceptions
        azure_openai = (
            azure_openai if not isinstance(azure_openai, Exception) else False
        )
        configuration = (
            configuration if not isinstance(configuration, Exception) else False
        )
        job_data_access = (
            job_data_access if not isinstance(job_data_access, Exception) else False
        )
        job_data_validation = (
            job_data_validation
            if not isinstance(job_data_validation, Exception)
            else False
        )
        system_resources = (
            system_resources if not isinstance(system_resources, Exception) else {}
        )

        # Determine overall status
        all_checks_passed = all(
            [azure_openai, configuration, job_data_access, job_data_validation]
        )

        overall_status = "healthy" if all_checks_passed else "unhealthy"

        # Build detailed checks
        detailed_checks = {
            "azure_openai": azure_openai,
            "configuration": configuration,
            "job_data_access": job_data_access,
            "job_data_validation": job_data_validation,
            "system_resources": system_resources,
            "overall": overall_status,
        }

        return DetailedHealthCheck(
            status=overall_status,
            timestamp=datetime.now(UTC),
            version=settings.app_version,
            checks=detailed_checks,
            azure_openai=azure_openai,
            configuration=configuration,
            job_data_access=job_data_access,
            job_data_validation=job_data_validation,
            system_resources=system_resources,
        )

    async def _check_azure_openai(self) -> bool:
        """Check Azure OpenAI service connectivity.

        Returns:
            True if service is accessible
        """
        try:
            openai_service = get_openai_service()
            # Perform a simple test (if test_connection method exists)
            if hasattr(openai_service, "test_connection"):
                # Run the synchronous test_connection in a thread
                return await asyncio.wait_for(
                    asyncio.to_thread(openai_service.test_connection),
                    timeout=self._timeout,
                )

            # Otherwise just check if service is configured
            return openai_service is not None

        except Exception as e:
            logger.warning("Azure OpenAI health check failed", error=str(e))
            return False

    async def _check_configuration(self) -> bool:
        """Check configuration validity.

        Returns:
            True if configuration is valid
        """
        try:
            # Check if settings are properly loaded
            if not settings.app_name or not settings.app_version:
                return False

            # Check Azure OpenAI configuration
            if not settings.azure_openai:
                logger.warning("Azure OpenAI configuration missing")
                return False

            # Check job data configuration
            if not settings.jobs_data_directory:
                logger.warning("Job data directory not configured")
                return False

            return True

        except Exception as e:
            logger.warning("Configuration health check failed", error=str(e))
            return False

    async def _check_job_data_access(self) -> bool:
        """Check job data directory access.

        Returns:
            True if job data directory is accessible
        """
        try:
            job_service = get_job_service()
            return await asyncio.wait_for(
                job_service.validate_data_access(), timeout=self._timeout
            )

        except Exception as e:
            logger.warning("Job data access health check failed", error=str(e))
            return False

    async def _check_job_data_validation(self) -> bool:
        """Check job data parsing and validation.

        Returns:
            True if job data can be parsed successfully
        """
        try:
            job_service = get_job_service()
            jobs = await asyncio.wait_for(
                job_service.get_all_jobs(refresh=True), timeout=self._timeout
            )

            # Check if we have at least one valid job
            return len(jobs) > 0

        except Exception as e:
            logger.warning("Job data validation health check failed", error=str(e))
            return False

    async def _check_system_resources(self) -> dict[str, Any]:
        """Check system resource usage.

        Returns:
            Dict with system resource information
        """
        try:
            # Get system information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "healthy": cpu_percent < 90
                and memory.percent < 90
                and disk.percent < 90,
            }

        except Exception as e:
            logger.warning("System resources health check failed", error=str(e))
            return {"healthy": False, "error": str(e)}


# Global health check service instance
_health_service: HealthCheckService | None = None


def get_health_service() -> HealthCheckService:
    """Get the global health check service instance.

    Returns:
        HealthCheckService instance
    """
    global _health_service
    if _health_service is None:
        _health_service = HealthCheckService()
    return _health_service
