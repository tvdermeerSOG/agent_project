"""Job data service for managing job information."""

import asyncio
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from job_agent.core.config import settings
from job_agent.models.job import Job, JobSummary

logger = structlog.get_logger(__name__)


class JobService:
    """Service for managing job data from local markdown files."""

    def __init__(self) -> None:
        """Initialize the job data service."""
        self.data_directory = Path(settings.jobs_data_directory)
        self._job_cache: dict[str, Job] = {}
        self._last_refresh: datetime | None = None
        self._refresh_interval = settings.jobs_refresh_interval

    async def get_all_jobs(self, refresh: bool = False) -> list[Job]:
        """Get all jobs from cache or refresh from files.

        Args:
            refresh: Force refresh from files

        Returns:
            List of all jobs
        """
        if refresh or self._should_refresh():
            await self._refresh_jobs()

        return list(self._job_cache.values())

    async def get_job_summaries(self, refresh: bool = False) -> list[JobSummary]:
        """Get job summaries for listing.

        Args:
            refresh: Force refresh from files

        Returns:
            List of job summaries
        """
        jobs = await self.get_all_jobs(refresh=refresh)
        return [
            JobSummary(
                id=job.id,
                function=job.function,
                client=job.client,
                location=job.location,
                period=job.period,
                updated_at=job.updated_at,
            )
            for job in jobs
        ]

    async def get_job_by_id(self, job_id: str, refresh: bool = False) -> Job | None:
        """Get a specific job by ID.

        Args:
            job_id: Job identifier
            refresh: Force refresh from files

        Returns:
            Job if found, None otherwise
        """
        if refresh or self._should_refresh():
            await self._refresh_jobs()

        return self._job_cache.get(job_id)

    async def refresh_jobs(self) -> dict[str, Any]:
        """Refresh job data from files and return refresh statistics.

        Returns:
            Dict with refresh statistics
        """
        start_time = datetime.now(UTC)
        errors: list[str] = []
        processed_count = 0

        try:
            await self._refresh_jobs()
            processed_count = len(self._job_cache)

            logger.info(
                "Job data refreshed successfully",
                jobs_count=processed_count,
                duration=(datetime.now(UTC) - start_time).total_seconds(),
            )

            return {
                "success": True,
                "message": f"Successfully refreshed {processed_count} jobs",
                "jobs_processed": processed_count,
                "errors": errors,
            }

        except Exception as e:
            error_msg = f"Failed to refresh job data: {str(e)}"
            logger.error("Job data refresh failed", error=str(e))
            errors.append(error_msg)

            return {
                "success": False,
                "message": error_msg,
                "jobs_processed": processed_count,
                "errors": errors,
            }

    async def validate_data_access(self) -> bool:
        """Validate that job data directory is accessible.

        Returns:
            True if directory is accessible, False otherwise
        """
        try:
            if not self.data_directory.exists():
                logger.warning(
                    "Job data directory does not exist", path=str(self.data_directory)
                )
                return False

            if not self.data_directory.is_dir():
                logger.warning(
                    "Job data path is not a directory", path=str(self.data_directory)
                )
                return False

            # Try to list directory contents
            list(self.data_directory.glob("*.md"))
            return True

        except Exception as e:
            logger.error(
                "Failed to access job data directory",
                error=str(e),
                path=str(self.data_directory),
            )
            return False

    def _should_refresh(self) -> bool:
        """Check if job data should be refreshed.

        Returns:
            True if refresh is needed
        """
        if self._last_refresh is None:
            return True

        time_since_refresh = (datetime.now(UTC) - self._last_refresh).total_seconds()
        if time_since_refresh > self._refresh_interval:
            return True
        return False

    async def _refresh_jobs(self) -> None:
        """Refresh job data from markdown files."""
        if not await self.validate_data_access():
            raise ValueError(f"Cannot access job data directory: {self.data_directory}")

        job_files = list(self.data_directory.glob("*.md"))
        logger.info("Starting job data refresh", file_count=len(job_files))

        new_cache = {}

        for file_path in job_files:
            try:
                job = await self._parse_job_file(file_path)
                new_cache[job.id] = job

            except Exception as e:
                logger.warning(
                    "Failed to parse job file", file=str(file_path), error=str(e)
                )

        self._job_cache = new_cache
        self._last_refresh = datetime.now(UTC)

        logger.info("Job data refresh completed", jobs_loaded=len(self._job_cache))

    async def _parse_job_file(self, file_path: Path) -> Job:
        """Parse a single job markdown file.

        Args:
            file_path: Path to the job file

        Returns:
            Parsed Job object

        Raises:
            ValueError: If file parsing fails
        """
        try:
            # Read file content
            content = await asyncio.to_thread(file_path.read_text, encoding="utf-8")

            # Get file stats
            stat = await asyncio.to_thread(os.stat, file_path)
            file_modified = datetime.fromtimestamp(stat.st_mtime)

            # Parse job data from content
            job_data = await self._parse_job_content(content)

            # Create job ID from filename
            job_id = file_path.stem

            # Create Job object
            job = Job(
                id=job_id,
                created_at=file_modified,
                updated_at=datetime.now(UTC),
                **job_data,
            )

            return job

        except Exception as e:
            raise ValueError(f"Failed to parse job file {file_path.name}: {str(e)}")

    async def _parse_job_content(self, content: str) -> dict[str, str]:
        """Parse job data from markdown content.

        Args:
            content: Raw markdown content

        Returns:
            Dict with parsed job fields

        Raises:
            ValueError: If required fields are missing
        """
        lines = content.strip().split("\n")

        # Field mapping from Dutch to English
        field_mapping = {
            "Klant": "client",
            "Klantreferentie": "client_reference",
            "Locatie": "location",
            "Inzetspercentage": "percentage",
            "Gevraagde functie": "function",
            "Branche": "industry",
            "Verantwoordelijke sales": "sales_responsible",
            "Grade indicatie": "grade",
            "Verwachte periode": "period",
            "Rol": "role",
        }

        parsed_data = {}
        current_field = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this line is a field name
            if line in field_mapping:
                current_field = field_mapping[line]
            elif current_field:
                # This line contains the value for the current field
                parsed_data[current_field] = line
                current_field = None

        # Validate required fields
        required_fields = set(field_mapping.values())
        missing_fields = required_fields - set(parsed_data.keys())

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        return parsed_data


# Global service instance - will be initialized when first accessed
_job_service: JobService | None = None


def get_job_service() -> JobService:
    """Get the global job service instance.

    Returns:
        JobService: Configured service instance
    """
    global _job_service
    if _job_service is None:
        _job_service = JobService()
    return _job_service
