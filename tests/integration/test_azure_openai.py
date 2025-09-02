"""Integration tests for Azure OpenAI connectivity."""

import os
from unittest.mock import patch

import pytest

from job_agent.core.config import settings
from job_agent.services.openai_service import get_openai_service
from job_agent.utils.azure_utils import azure_credential_manager


class TestAzureOpenAIIntegration:
    """Integration tests for Azure OpenAI service."""

    @pytest.mark.integration()
    def test_azure_credential_acquisition(self):
        """Test Azure credential can be acquired."""
        # This test requires actual Azure CLI authentication
        try:
            credential = azure_credential_manager.get_credential()
            assert credential is not None

            # Test credential functionality
            success = azure_credential_manager.test_credential()
            assert success is True

        except Exception as e:
            pytest.skip(f"Azure authentication not available: {e}")

    @pytest.mark.integration()
    def test_config_loading_from_yaml(self):
        """Test configuration loading from YAML file."""
        # Ensure config is loaded
        assert (
            settings.azure_openai is not None
        ), "Azure OpenAI configuration not loaded from config.yaml"
        assert (
            settings.azure is not None
        ), "Azure configuration not loaded from config.yaml"

        # Verify required fields
        assert settings.azure_openai.endpoint
        assert settings.azure_openai.api_version
        assert settings.azure_openai.deployment_name
        assert settings.azure_openai.model

    @pytest.mark.integration()
    @pytest.mark.skipif(
        not os.getenv("RUN_AZURE_INTEGRATION_TESTS"),
        reason="Azure integration tests require RUN_AZURE_INTEGRATION_TESTS=1",
    )
    def test_azure_openai_connection(self):
        """Test actual Azure OpenAI service connection.

        This test requires:
        1. Azure CLI authentication (az login)
        2. Access to the 'rag-cog' OpenAI service
        3. Environment variable RUN_AZURE_INTEGRATION_TESTS=1
        """
        try:
            service = get_openai_service()

            # Test connection
            success = service.test_connection()
            assert success is True, "Failed to connect to Azure OpenAI service"

        except Exception as e:
            pytest.fail(f"Azure OpenAI integration test failed: {e}")

    @pytest.mark.integration()
    @pytest.mark.skipif(
        not os.getenv("RUN_AZURE_INTEGRATION_TESTS"),
        reason="Azure integration tests require RUN_AZURE_INTEGRATION_TESTS=1",
    )
    @pytest.mark.asyncio()
    async def test_chat_completion_end_to_end(self):
        """Test end-to-end chat completion.

        This test requires:
        1. Azure CLI authentication (az login)
        2. Access to the 'rag-cog' OpenAI service
        3. Environment variable RUN_AZURE_INTEGRATION_TESTS=1
        """
        try:
            service = get_openai_service()

            messages = [
                {
                    "role": "user",
                    "content": "Hello! Please respond with 'Integration test successful'.",
                }
            ]

            response = await service.chat_completion(messages, max_tokens=50)

            assert response is not None
            assert len(response) > 0
            assert isinstance(response, str)

        except Exception as e:
            pytest.fail(f"End-to-end chat completion test failed: {e}")

    @pytest.mark.integration()
    @pytest.mark.skipif(
        not os.getenv("RUN_AZURE_INTEGRATION_TESTS"),
        reason="Azure integration tests require RUN_AZURE_INTEGRATION_TESTS=1",
    )
    @pytest.mark.asyncio()
    async def test_motivation_letter_generation_end_to_end(self):
        """Test end-to-end motivation letter generation.

        This test requires:
        1. Azure CLI authentication (az login)
        2. Access to the 'rag-cog' OpenAI service
        3. Environment variable RUN_AZURE_INTEGRATION_TESTS=1
        """
        try:
            service = get_openai_service()

            job_description = """
            Software Engineer position at a tech startup.
            Requirements: Python, FastAPI, Azure cloud experience.
            """

            user_profile = """
            Senior software engineer with 5 years of experience in Python development.
            Experienced with FastAPI, Azure services, and cloud architectures.
            """

            motivation_letter = await service.generate_motivation_letter(
                job_description=job_description,
                user_profile=user_profile,
                company_info="Innovative tech startup focused on AI solutions",
            )

            assert motivation_letter is not None
            assert len(motivation_letter) > 100  # Should be a substantial response
            assert isinstance(motivation_letter, str)

            # Basic content checks
            assert any(
                keyword in motivation_letter.lower()
                for keyword in ["engineer", "python", "experience"]
            )

        except Exception as e:
            pytest.fail(f"End-to-end motivation letter generation test failed: {e}")


@pytest.mark.integration()
class TestConfigurationValidation:
    """Test configuration validation and environment handling."""

    def test_config_yaml_exists(self):
        """Test that config.yaml file exists."""
        from pathlib import Path

        config_path = Path(__file__).parent.parent.parent / "config.yaml"
        assert config_path.exists(), "config.yaml file not found"

    def test_environment_variable_override(self):
        """Test that environment variables can override config.yaml settings."""

        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_ENDPOINT": "https://test-override.openai.azure.com/",
                "AZURE_OPENAI_API_VERSION": "2024-03-01-preview",
                "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4-override",
                "AZURE_OPENAI_MODEL": "gpt-4-override",
            },
        ):
            # Create new settings instance to pick up environment variables
            from job_agent.core.config import AzureOpenAISettings

            env_settings = AzureOpenAISettings()  # type: ignore[call-arg]

            assert env_settings.endpoint == "https://test-override.openai.azure.com/"
            assert env_settings.api_version == "2024-03-01-preview"
            assert env_settings.deployment_name == "gpt-4-override"
            assert env_settings.model == "gpt-4-override"
