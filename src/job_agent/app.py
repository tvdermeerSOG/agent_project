"""FastAPI application factory."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from job_agent.api.middleware import CorrelationIdMiddleware, TimingMiddleware
from job_agent.api.v1 import api_router
from job_agent.core.config import settings
from job_agent.core.logging import configure_logging, configure_uvicorn_logging


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management.

    Args:
        app: FastAPI application instance
    """
    # Startup
    configure_logging()
    configure_uvicorn_logging()

    # Log startup
    import structlog

    logger = structlog.get_logger("app")
    logger.info(
        "Application starting",
        app_name=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    yield

    # Shutdown
    logger.info("Application shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Automated job board polling and application system with AI-powered motivation letters",
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware
    app.add_middleware(TimingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)

    # Include API routers
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Root endpoint
    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": settings.docs_url,
            "redoc": settings.redoc_url,
            "api": settings.api_v1_prefix,
        }

    return app
