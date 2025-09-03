"""Application workflow API endpoints (future implementation)."""

from fastapi import APIRouter

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/")
async def list_applications() -> dict[str, list[str] | str]:
    """List application workflows (placeholder for future implementation).

    Returns:
        Placeholder response
    """
    return {
        "message": "Application workflow endpoints will be implemented in future tasks",
        "available_endpoints": [
            "GET /applications/ - List applications",
            "POST /applications/ - Create new application",
            "GET /applications/{app_id} - Get application details",
            "PUT /applications/{app_id}/status - Update application status",
        ],
    }


@router.post("/")
async def create_application() -> dict[str, list[str] | str]:
    """Create a new job application (placeholder for future implementation).

    Returns:
        Placeholder response
    """
    return {
        "message": "Application creation will be implemented in future tasks",
        "features": [
            "AI-powered motivation letter generation",
            "User preference matching",
            "Application tracking",
            "Notification system",
        ],
    }
