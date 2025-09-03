"""Job management API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from job_agent.api.deps import JobServiceDep
from job_agent.models.api import FilterParams, SortParams
from job_agent.models.job import (
    JobRefreshResponse,
    JobResponse,
    JobsResponse,
    JobSummary,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=JobsResponse)
async def list_jobs(
    job_service: JobServiceDep,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    client: str = Query(None, description="Filter by client"),
    location: str = Query(None, description="Filter by location"),
    industry: str = Query(None, description="Filter by industry"),
    function: str = Query(None, description="Filter by function"),
    search: str = Query(None, description="Search term"),
    sort_by: str = Query("updated_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    refresh: bool = Query(False, description="Force refresh from files"),
) -> JobsResponse:
    """List all available jobs with optional filtering and pagination.

    Returns:
        Paginated list of job summaries
    """
    try:
        # Get all jobs
        jobs = await job_service.get_job_summaries(refresh=refresh)

        # Apply filters
        filtered_jobs = _apply_filters(
            jobs,
            FilterParams(
                client=client,
                location=location,
                industry=industry,
                function=function,
                search=search,
            ),
        )

        # Apply sorting
        sorted_jobs = _apply_sorting(
            filtered_jobs, SortParams(sort_by=sort_by, sort_order=sort_order)
        )

        # Apply pagination
        total = len(sorted_jobs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_jobs = sorted_jobs[start_idx:end_idx]

        return JobsResponse(
            jobs=paginated_jobs, total=total, page=page, page_size=page_size
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    job_service: JobServiceDep,
    refresh: bool = Query(False, description="Force refresh from files"),
) -> JobResponse:
    """Get details for a specific job.

    Args:
        job_id: Job identifier
        refresh: Force refresh from files

    Returns:
        Job details
    """
    try:
        job = await job_service.get_job_by_id(job_id, refresh=refresh)

        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        return JobResponse(job=job)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")


@router.post("/refresh", response_model=JobRefreshResponse)
async def refresh_jobs(job_service: JobServiceDep) -> JobRefreshResponse:
    """Refresh job data from local files.

    This endpoint forces a refresh of all job data from the markdown files
    in the configured data directory.

    Returns:
        Refresh operation results
    """
    try:
        result = await job_service.refresh_jobs()

        return JobRefreshResponse(
            success=result["success"],
            message=result["message"],
            jobs_processed=result["jobs_processed"],
            errors=result["errors"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh jobs: {str(e)}")


def _apply_filters(jobs: list[JobSummary], filters: FilterParams) -> list[JobSummary]:
    """Apply filters to job list.

    Args:
        jobs: List of job summaries
        filters: Filter parameters

    Returns:
        Filtered job list
    """
    filtered_jobs = jobs

    if filters.client:
        filtered_jobs = [
            j for j in filtered_jobs if filters.client.lower() in j.client.lower()
        ]

    if filters.location:
        filtered_jobs = [
            j for j in filtered_jobs if filters.location.lower() in j.location.lower()
        ]

    if filters.function:
        filtered_jobs = [
            j for j in filtered_jobs if filters.function.lower() in j.function.lower()
        ]

    if filters.search:
        search_term = filters.search.lower()
        filtered_jobs = [
            j
            for j in filtered_jobs
            if (
                search_term in j.client.lower()
                or search_term in j.function.lower()
                or search_term in j.location.lower()
            )
        ]

    return filtered_jobs


def _apply_sorting(jobs: list[JobSummary], sorting: SortParams) -> list[JobSummary]:
    """Apply sorting to job list.

    Args:
        jobs: List of job summaries
        sorting: Sort parameters

    Returns:
        Sorted job list
    """
    reverse = sorting.sort_order == "desc"

    if sorting.sort_by == "client":
        return sorted(jobs, key=lambda j: j.client, reverse=reverse)
    elif sorting.sort_by == "function":
        return sorted(jobs, key=lambda j: j.function, reverse=reverse)
    elif sorting.sort_by == "location":
        return sorted(jobs, key=lambda j: j.location, reverse=reverse)
    elif sorting.sort_by == "updated_at":
        return sorted(jobs, key=lambda j: j.updated_at, reverse=reverse)
    else:
        # Default to updated_at
        return sorted(jobs, key=lambda j: j.updated_at, reverse=reverse)
