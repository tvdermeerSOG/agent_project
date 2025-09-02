"""Application configuration settings."""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class AzureOpenAISettings(BaseSettings):
    """Azure OpenAI service configuration."""

    endpoint: str
    api_version: str
    deployment_name: str
    model: str
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0.7

    model_config = ConfigDict(env_prefix="AZURE_OPENAI_")


class AzureSettings(BaseSettings):
    """Azure service configuration."""

    resource_group: str
    subscription: str

    model_config = ConfigDict(env_prefix="AZURE_")


class Settings(BaseSettings):
    """Application settings."""

    model_config = ConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

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

    # Azure configurations
    azure_openai: Optional[AzureOpenAISettings] = None
    azure: Optional[AzureSettings] = None

    def __init__(self, **kwargs):
        """Initialize settings with YAML configuration."""
        super().__init__(**kwargs)
        self._load_yaml_config()

    def _load_yaml_config(self) -> None:
        """Load configuration from config.yaml file."""
        config_path = Path(__file__).parent.parent.parent.parent / "config.yaml"

        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as file:
                    config_data = yaml.safe_load(file)

                if "azure_openai" in config_data:
                    self.azure_openai = AzureOpenAISettings(
                        **config_data["azure_openai"]
                    )

                if "azure" in config_data:
                    self.azure = AzureSettings(**config_data["azure"])

            except Exception as e:
                # Log error but don't fail - allow environment variables to override
                print(f"Warning: Could not load config.yaml: {e}")


# Global settings instance
settings = Settings()
