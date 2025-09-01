"""Pytest configuration and shared fixtures."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()  # type: ignore[misc]
def _client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application."""
    # This will be implemented in Task 1.3 when we create the FastAPI app
    # For now, we'll raise NotImplementedError to satisfy mypy
    raise NotImplementedError("FastAPI app not yet implemented - see Task 1.3")
