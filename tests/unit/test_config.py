"""Unit tests for configuration management."""

import os
from unittest.mock import mock_open, patch

from pydantic_settings import SettingsConfigDict

from job_agent.core.config import AzureOpenAISettings, AzureSettings, Settings


class TestAzureOpenAISettings:
    """Test Azure OpenAI settings."""

    def test_azure_openai_settings_initialization(self):
        """Test Azure OpenAI settings can be initialized with required fields."""
        settings = AzureOpenAISettings(
            endpoint="https://test.openai.azure.com/",
            api_version="2024-02-15-preview",
            deployment_name="gpt-4",
            model="gpt-4",
        )

        assert settings.endpoint == "https://test.openai.azure.com/"
        assert settings.api_version == "2024-02-15-preview"
        assert settings.deployment_name == "gpt-4"
        assert settings.model == "gpt-4"
        assert settings.max_tokens == 4096  # default value
        assert settings.temperature == 0.7  # default value

    def test_azure_openai_settings_custom_defaults(self):
        """Test Azure OpenAI settings with custom values."""
        settings = AzureOpenAISettings(
            endpoint="https://test.openai.azure.com/",
            api_version="2024-02-15-preview",
            deployment_name="gpt-35-turbo",
            model="gpt-35-turbo",
            max_tokens=2048,
            temperature=0.5,
        )

        assert settings.max_tokens == 2048
        assert settings.temperature == 0.5

    def test_azure_openai_settings_env_prefix(self):
        """Test Azure OpenAI settings can be loaded from environment variables."""
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_ENDPOINT": "https://env.openai.azure.com/",
                "AZURE_OPENAI_API_VERSION": "2024-03-01",
                "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4-env",
                "AZURE_OPENAI_MODEL": "gpt-4-env",
                "AZURE_OPENAI_MAX_TOKENS": "8192",
                "AZURE_OPENAI_TEMPERATURE": "0.9",
            },
        ):
            settings = AzureOpenAISettings()  # type: ignore[call-arg]

            assert settings.endpoint == "https://env.openai.azure.com/"
            assert settings.api_version == "2024-03-01"
            assert settings.deployment_name == "gpt-4-env"
            assert settings.model == "gpt-4-env"
            assert settings.max_tokens == 8192
            assert settings.temperature == 0.9


class TestAzureSettings:
    """Test Azure settings."""

    def test_azure_settings_initialization(self):
        """Test Azure settings can be initialized with required fields."""
        settings = AzureSettings(
            resource_group="test-rg", subscription="test-subscription"
        )

        assert settings.resource_group == "test-rg"
        assert settings.subscription == "test-subscription"

    def test_azure_settings_env_prefix(self):
        """Test Azure settings can be loaded from environment variables."""
        with patch.dict(
            os.environ,
            {
                "AZURE_RESOURCE_GROUP": "env-rg",
                "AZURE_SUBSCRIPTION": "env-subscription",
            },
        ):
            settings = AzureSettings()  # type: ignore[call-arg]

            assert settings.resource_group == "env-rg"
            assert settings.subscription == "env-subscription"


class TestSettings:
    """Test main application settings."""

    def test_settings_default_values(self):
        """Test settings default values."""
        # Mock the YAML loading to avoid file dependency
        with patch.object(Settings, "_load_yaml_config"):
            # Clear environment variables that might affect the test
            env_vars_to_clear = [
                "DEBUG",
                "APP_NAME",
                "APP_VERSION",
                "API_V1_PREFIX",
                "ALLOWED_HOSTS",
                "LOG_LEVEL",
                "LOG_FORMAT",
            ]
            with patch.dict(os.environ, {}, clear=False):
                # Remove specific environment variables
                for var in env_vars_to_clear:
                    os.environ.pop(var, None)

                # Create a clean config without env_file
                original_config = Settings.model_config
                Settings.model_config = SettingsConfigDict(
                    case_sensitive=False, extra="ignore"
                )

                try:
                    settings = Settings()

                    assert settings.app_name == "Job Agent"
                    assert settings.app_version == "0.1.0"
                    assert settings.debug is False
                    assert settings.api_v1_prefix == "/api/v1"
                    assert settings.allowed_hosts == ["*"]
                    assert settings.log_level == "INFO"
                    assert settings.log_format == "json"
                finally:
                    # Restore original config
                    Settings.model_config = original_config

    def test_settings_yaml_loading_success(self):
        """Test successful YAML configuration loading."""
        yaml_content = """
azure_openai:
  endpoint: "https://yaml.openai.azure.com/"
  api_version: "2024-02-15-preview"
  deployment_name: "gpt-4-yaml"
  model: "gpt-4-yaml"
  max_tokens: 3000
  temperature: 0.8

azure:
  resource_group: "yaml-rg"
  subscription: "yaml-subscription"
"""

        with (
            patch("pathlib.Path.open", mock_open(read_data=yaml_content)),
            patch("pathlib.Path.exists", return_value=True),
        ):
            settings = Settings()

            assert settings.azure_openai is not None
            assert settings.azure_openai.endpoint == "https://yaml.openai.azure.com/"
            assert settings.azure_openai.deployment_name == "gpt-4-yaml"
            assert settings.azure_openai.max_tokens == 3000
            assert settings.azure_openai.temperature == 0.8

            assert settings.azure is not None
            assert settings.azure.resource_group == "yaml-rg"
            assert settings.azure.subscription == "yaml-subscription"

    def test_settings_yaml_loading_file_not_found(self):
        """Test YAML configuration when file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            settings = Settings()

            assert settings.azure_openai is None
            assert settings.azure is None

    def test_settings_yaml_loading_invalid_yaml(self):
        """Test YAML configuration with invalid YAML content."""
        invalid_yaml = "invalid: yaml: content: ["

        with (
            patch("pathlib.Path.open", mock_open(read_data=invalid_yaml)),
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.print") as mock_print,
        ):
            settings = Settings()

            # Should handle the error gracefully
            assert settings.azure_openai is None
            assert settings.azure is None
            mock_print.assert_called_once()
            assert "Warning: Could not load config.yaml" in str(mock_print.call_args)

    def test_settings_yaml_loading_missing_sections(self):
        """Test YAML configuration with missing sections."""
        yaml_content = """
some_other_config:
  value: "test"
"""

        with (
            patch("pathlib.Path.open", mock_open(read_data=yaml_content)),
            patch("pathlib.Path.exists", return_value=True),
        ):
            settings = Settings()

            assert settings.azure_openai is None
            assert settings.azure is None
