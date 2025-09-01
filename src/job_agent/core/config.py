"""Application configuration settings."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):  # type: ignore[misc]
    """Application settings."""

    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    # Application
    app_name: str = "Job Agent"
    app_version: str = "0.1.0"
    debug: bool = False

    # API
    api_v1_prefix: str = "/api/v1"
    allowed_hosts: list[str] = ["*"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Azure (will be properly configured in Task 1.2)
    azure_openai_endpoint: str | None = None
    azure_openai_api_version: str = "2024-02-15-preview"


# Global settings instance
settings = Settings()
