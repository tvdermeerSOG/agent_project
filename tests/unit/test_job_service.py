"""Test the job service functionality."""

import pytest

from job_agent.services.job_service import get_job_service


@pytest.mark.asyncio()
async def test_job_service_singleton():
    """Test that get_job_service returns the same instance."""
    service1 = get_job_service()
    service2 = get_job_service()
    assert service1 is service2


@pytest.mark.asyncio()
async def test_validate_data_access():
    """Test job data directory access validation."""
    service = get_job_service()
    access_ok = await service.validate_data_access()
    assert access_ok is True


@pytest.mark.asyncio()
async def test_get_job_summaries():
    """Test getting job summaries."""
    service = get_job_service()
    summaries = await service.get_job_summaries(refresh=True)

    assert len(summaries) >= 3  # We have at least 3 job files

    # Check structure of first summary
    first_summary = summaries[0]
    assert hasattr(first_summary, "id")
    assert hasattr(first_summary, "function")
    assert hasattr(first_summary, "client")
    assert hasattr(first_summary, "location")
    assert hasattr(first_summary, "period")
    assert hasattr(first_summary, "updated_at")


@pytest.mark.asyncio()
async def test_get_all_jobs():
    """Test getting all job details."""
    service = get_job_service()
    jobs = await service.get_all_jobs(refresh=True)

    assert len(jobs) >= 3  # We have at least 3 job files

    # Check structure of first job
    first_job = jobs[0]
    assert hasattr(first_job, "id")
    assert hasattr(first_job, "client")
    assert hasattr(first_job, "client_reference")
    assert hasattr(first_job, "location")
    assert hasattr(first_job, "percentage")
    assert hasattr(first_job, "function")
    assert hasattr(first_job, "industry")
    assert hasattr(first_job, "sales_responsible")
    assert hasattr(first_job, "grade")
    assert hasattr(first_job, "period")
    assert hasattr(first_job, "role")


@pytest.mark.asyncio()
async def test_get_job_by_id():
    """Test getting a specific job by ID."""
    service = get_job_service()

    # First get all jobs to find a valid ID
    jobs = await service.get_all_jobs(refresh=True)
    assert len(jobs) > 0

    first_job_id = jobs[0].id

    # Get the specific job
    job = await service.get_job_by_id(first_job_id)
    assert job is not None
    assert job.id == first_job_id

    # Test with non-existent ID
    non_existent_job = await service.get_job_by_id("non_existent_id")
    assert non_existent_job is None


@pytest.mark.asyncio()
async def test_refresh_jobs():
    """Test job refresh functionality."""
    service = get_job_service()
    result = await service.refresh_jobs()

    assert result["success"] is True
    assert result["jobs_processed"] >= 3
    assert isinstance(result["errors"], list)
    assert "message" in result
