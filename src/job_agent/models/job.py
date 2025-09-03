"""Job data models."""

from datetime import datetime

from pydantic import BaseModel, Field


class Job(BaseModel):
    """Job posting model."""

    id: str = Field(..., description="Unique job identifier derived from filename")
    client: str = Field(..., description="Client name (Klant)")
    client_reference: str = Field(..., description="Client reference (Klantreferentie)")
    location: str = Field(..., description="Job location (Locatie)")
    percentage: str = Field(..., description="Work percentage (Inzetspercentage)")
    function: str = Field(..., description="Job function (Gevraagde functie)")
    industry: str = Field(..., description="Industry sector (Branche)")
    sales_responsible: str = Field(
        ..., description="Sales contact (Verantwoordelijke sales)"
    )
    grade: str = Field(..., description="Grade indication (Grade indicatie)")
    period: str = Field(..., description="Expected period (Verwachte periode)")
    role: str = Field(..., description="Role description (Rol)")
    created_at: datetime = Field(..., description="File creation/modification time")
    updated_at: datetime = Field(..., description="Last processed time")


class JobSummary(BaseModel):
    """Lightweight job summary for listing."""

    id: str
    function: str
    client: str
    location: str
    period: str
    updated_at: datetime


class JobsResponse(BaseModel):
    """Response model for job listings."""

    jobs: list[JobSummary]
    total: int
    page: int = 1
    page_size: int = 50


class JobResponse(BaseModel):
    """Response model for single job details."""

    job: Job


class JobRefreshResponse(BaseModel):
    """Response model for job data refresh."""

    success: bool
    message: str
    jobs_processed: int
    errors: list[str] = []
