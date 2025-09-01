"""Test for basic project setup and configuration."""

from job_agent.core.config import settings


def test_settings_exist():
    """Test that settings can be imported and have expected values."""
    assert settings.app_name == "Job Agent"
    assert settings.app_version == "0.1.0"
    assert settings.api_v1_prefix == "/api/v1"


def test_python_version():
    """Test that we're running on Python 3.11+."""
    import sys

    assert sys.version_info >= (3, 11), f"Python version {sys.version_info} is too old"


class TestProjectStructure:
    """Test that the project structure is set up correctly."""

    def test_package_imports(self):
        """Test that all main packages can be imported."""
        import job_agent
        import job_agent.api
        import job_agent.core
        import job_agent.models
        import job_agent.services
        import job_agent.utils

        assert job_agent.__version__ == "0.1.0"
