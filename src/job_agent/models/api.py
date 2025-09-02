"""API request and response models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """Base API response model."""

    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )


class ErrorResponse(APIResponse):
    """Error response model."""

    success: bool = Field(default=False, description="Request success status")
    error_code: str | None = Field(None, description="Error code")
    details: dict[str, Any] | None = Field(None, description="Error details")


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=50, ge=1, le=100, description="Items per page")


class SortParams(BaseModel):
    """Sorting parameters."""

    sort_by: str = Field(default="updated_at", description="Field to sort by")
    sort_order: str = Field(
        default="desc", pattern="^(asc|desc)$", description="Sort order"
    )


class FilterParams(BaseModel):
    """Job filtering parameters."""

    client: str | None = Field(None, description="Filter by client")
    location: str | None = Field(None, description="Filter by location")
    industry: str | None = Field(None, description="Filter by industry")
    function: str | None = Field(None, description="Filter by function")
    search: str | None = Field(None, description="Search term")


class JobListRequest(BaseModel):
    """Job list request parameters."""

    pagination: PaginationParams = Field(default_factory=PaginationParams)
    sorting: SortParams = Field(default_factory=SortParams)
    filters: FilterParams = Field(default_factory=FilterParams)  # type: ignore
