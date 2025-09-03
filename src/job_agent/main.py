"""Main entry point for the Job Agent application."""

import uvicorn

from job_agent.app import create_app
from job_agent.core.config import settings


def main() -> None:
    """Main entry point for the application."""
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📝 Debug mode: {settings.debug}")
    print(f"📊 Log level: {settings.log_level}")
    print(f"🌐 Server: {settings.host}:{settings.port}")
    print(f"� Job data directory: {settings.jobs_data_directory}")
    print("✅ FastAPI application ready!")

    # Create and run the FastAPI application
    app = create_app()

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
