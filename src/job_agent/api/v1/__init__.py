"""API version 1 router."""

from fastapi import APIRouter

from job_agent.api.v1 import applications, github, health, jobs

api_router = APIRouter()

# Include all v1 routers
api_router.include_router(health.router)
api_router.include_router(jobs.router)
api_router.include_router(applications.router)
api_router.include_router(github.router)
