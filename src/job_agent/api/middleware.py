"""Custom middleware for the FastAPI application."""

import time
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger("middleware")


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request timing."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request with timing.

        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint

        Returns:
            Response with timing headers
        """
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate timing
        process_time = time.time() - start_time

        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)

        # Log request
        logger.info(
            "Request processed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=process_time,
        )

        return response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation IDs to requests."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request with correlation ID.

        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint

        Returns:
            Response with correlation ID header
        """
        # Get correlation ID from header or generate one
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            import uuid

            correlation_id = str(uuid.uuid4())

        # Store in request state
        request.state.correlation_id = correlation_id

        # Process request
        response = await call_next(request)

        # Add correlation ID to response
        response.headers["X-Correlation-ID"] = correlation_id

        return response
