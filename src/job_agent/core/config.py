"""Application configuration settings."""

from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class AzureOpenAISettings(BaseSettings):
    """Azure OpenAI service configuration."""

    endpoint: str
    api_version: str
    deployment_name: str
    model: str
    max_tokens: int | None = 4096
    temperature: float | None = 0.7

    model_config = SettingsConfigDict(env_prefix="AZURE_OPENAI_")


class AzureSettings(BaseSettings):
    """Azure service configuration."""

    resource_group: str
    subscription: str

    model_config = SettingsConfigDict(env_prefix="AZURE_")


class APISettings(BaseSettings):
    """API configuration."""

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["*"]
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"

    model_config = SettingsConfigDict(env_prefix="API_")


class JobsSettings(BaseSettings):
    """Jobs configuration."""

    data_directory: str = "data/jobs"
    file_format: str = "markdown"
    refresh_interval: int = 300

    model_config = SettingsConfigDict(env_prefix="JOBS_")


class JobBoardSettings(BaseSettings):
    """Job board integration configuration."""

    endpoint: str | None = None
    api_key: str | None = None
    poll_interval: int = 3600

    model_config = SettingsConfigDict(env_prefix="JOB_BOARD_")


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "json"
    file: str | None = None

    model_config = SettingsConfigDict(env_prefix="LOGGING_")


class HealthChecksSettings(BaseSettings):
    """Health checks configuration."""

    cache_ttl: int = 30
    timeout: int = 5

    model_config = SettingsConfigDict(env_prefix="HEALTH_CHECKS_")


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )

    # Application
    app_name: str = "Job Agent"
    app_version: str = "0.1.0"
    debug: bool = False
    reload: bool = False

    # API
    api_v1_prefix: str = "/api/v1"
    allowed_hosts: list[str] = ["*"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Azure configurations
    azure_openai: AzureOpenAISettings | None = None
    azure: AzureSettings | None = None

    # Configuration sections
    api: APISettings | None = None
    jobs: JobsSettings | None = None
    job_board: JobBoardSettings | None = None
    logging: LoggingSettings | None = None
    health_checks: HealthChecksSettings | None = None

    def __init__(self, **kwargs: Any) -> None:
        """Initialize settings with YAML configuration."""
        super().__init__(**kwargs)
        self._load_yaml_config()

    def _load_yaml_config(self) -> None:
        """Load configuration from config.yaml file."""
        config_path = Path(__file__).parent.parent.parent.parent / "config.yaml"

        if config_path.exists():
            try:
                with config_path.open(encoding="utf-8") as file:
                    config_data = yaml.safe_load(file)

                if "azure_openai" in config_data:
                    self.azure_openai = AzureOpenAISettings(
                        **config_data["azure_openai"]
                    )

                if "azure" in config_data:
                    self.azure = AzureSettings(**config_data["azure"])

                if "api" in config_data:
                    self.api = APISettings(**config_data["api"])

                if "jobs" in config_data:
                    self.jobs = JobsSettings(**config_data["jobs"])

                if "job_board" in config_data:
                    self.job_board = JobBoardSettings(**config_data["job_board"])

                if "logging" in config_data:
                    self.logging = LoggingSettings(**config_data["logging"])

                if "health_checks" in config_data:
                    self.health_checks = HealthChecksSettings(
                        **config_data["health_checks"]
                    )

            except Exception as e:
                # Log error but don't fail - allow environment variables to override
                print(f"Warning: Could not load config.yaml: {e}")

    # Convenience properties for backward compatibility
    @property
    def host(self) -> str:
        """Get API host."""
        return self.api.host if self.api else "0.0.0.0"

    @property
    def port(self) -> int:
        """Get API port."""
        return self.api.port if self.api else 8000

    @property
    def docs_url(self) -> str:
        """Get API docs URL."""
        return self.api.docs_url if self.api else "/docs"

    @property
    def redoc_url(self) -> str:
        """Get API redoc URL."""
        return self.api.redoc_url if self.api else "/redoc"

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS origins."""
        return self.api.cors_origins if self.api else ["*"]

    @property
    def jobs_data_directory(self) -> str:
        """Get jobs data directory."""
        return self.jobs.data_directory if self.jobs else "data/jobs"

    @property
    def jobs_file_format(self) -> str:
        """Get jobs file format."""
        return self.jobs.file_format if self.jobs else "markdown"

    @property
    def jobs_refresh_interval(self) -> int:
        """Get jobs refresh interval."""
        return self.jobs.refresh_interval if self.jobs else 300


# Global settings instance
settings = Settings()
