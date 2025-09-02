"""Logging infrastructure and configuration."""

import logging
import sys
from typing import Any

import structlog
from structlog.stdlib import LoggerFactory

from job_agent.core.config import settings


def configure_logging() -> None:
    """Configure structured logging for the application."""

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            _get_processor(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


def _get_processor() -> (
    structlog.processors.JSONRenderer | structlog.dev.ConsoleRenderer
):
    """Get the appropriate log processor based on configuration."""
    if settings.log_format.lower() == "json":
        return structlog.processors.JSONRenderer()
    else:
        return structlog.dev.ConsoleRenderer(
            colors=True, exception_formatter=structlog.dev.better_traceback
        )


def get_logger(name: str | None = None) -> Any:
    """Get a configured logger instance.

    Args:
        name: Logger name (optional)

    Returns:
        Configured logger
    """
    return structlog.get_logger(name)


class LoggingMiddleware:
    """FastAPI middleware for request/response logging."""

    def __init__(self, app: Any) -> None:
        self.app = app
        self.logger = get_logger("http")

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_info = {
            "method": scope["method"],
            "path": scope["path"],
            "query_string": scope.get("query_string", b"").decode(),
            "client": scope.get("client"),
        }

        self.logger.info("Request started", **request_info)

        async def send_wrapper(message: dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                self.logger.info(
                    "Request completed", status_code=message["status"], **request_info
                )
            await send(message)

        await self.app(scope, receive, send_wrapper)


def add_correlation_id_processor(
    logger: Any, _method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add correlation ID to log events."""
    # This would be enhanced with actual correlation ID from request context
    # For now, we'll add a placeholder
    event_dict["correlation_id"] = getattr(logger, "_correlation_id", None)
    return event_dict


def configure_uvicorn_logging() -> None:
    """Configure uvicorn logging to use our structured logging."""

    # Configure uvicorn loggers to use our format
    uvicorn_loggers = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
    ]

    for logger_name in uvicorn_loggers:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True
