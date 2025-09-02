"""Unit tests for Azure OpenAI service."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from azure.core.credentials import AccessToken, TokenCredential

from job_agent.core.config import AzureOpenAISettings
from job_agent.services.openai_service import AzureOpenAIService, get_openai_service


@pytest.fixture()
def mock_credential():
    """Mock Azure credential."""
    credential = Mock(spec=TokenCredential)
    credential.get_token.return_value = AccessToken(
        token="mock_token",
        expires_on=9999999999,  # Far future
    )
    return credential


@pytest.fixture()
def openai_settings():
    """Mock Azure OpenAI settings."""
    return AzureOpenAISettings(
        endpoint="https://test.openai.azure.com/",
        api_version="2024-02-15-preview",
        deployment_name="gpt-4-test",
        model="gpt-4-test",
        max_tokens=1000,
        temperature=0.5,
    )


@pytest.fixture()
def mock_openai_client():
    """Mock Azure OpenAI client."""
    with patch("job_agent.services.openai_service.AzureOpenAI") as mock_client:
        yield mock_client


class TestAzureOpenAIService:
    """Test Azure OpenAI service."""

    def test_initialization_with_settings(self, openai_settings, mock_credential):
        """Test service initialization with provided settings."""
        service = AzureOpenAIService(openai_settings, mock_credential)

        assert service.settings == openai_settings
        assert service.credential == mock_credential

    def test_initialization_without_settings_raises_error(self, mock_credential):
        """Test service initialization without settings raises error."""
        with patch("job_agent.services.openai_service.settings") as mock_settings:
            mock_settings.azure_openai = None

            with pytest.raises(ValueError, match="Azure OpenAI settings are required"):
                AzureOpenAIService(credential=mock_credential)

    def test_client_property_creates_client(
        self, openai_settings, mock_credential, mock_openai_client
    ):
        """Test client property creates Azure OpenAI client."""
        service = AzureOpenAIService(openai_settings, mock_credential)

        # Access client property
        client = service.client

        # Verify credential.get_token was called with correct scope
        mock_credential.get_token.assert_called_once_with(
            "https://cognitiveservices.azure.com/.default"
        )

        # Verify AzureOpenAI was initialized with correct parameters
        mock_openai_client.assert_called_once_with(
            azure_endpoint="https://test.openai.azure.com/",
            api_version="2024-02-15-preview",
            azure_ad_token="mock_token",
        )

    def test_client_property_reuses_existing_client(
        self, openai_settings, mock_credential, mock_openai_client
    ):
        """Test client property reuses existing client instance."""
        service = AzureOpenAIService(openai_settings, mock_credential)

        # Access client property twice
        client1 = service.client
        client2 = service.client

        # Should only create client once
        assert mock_openai_client.call_count == 1
        assert client1 == client2

    @pytest.mark.asyncio()
    async def test_chat_completion_success(
        self, openai_settings, mock_credential, mock_openai_client
    ):
        """Test successful chat completion."""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage.total_tokens = 50

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client_instance

        service = AzureOpenAIService(openai_settings, mock_credential)

        messages = [{"role": "user", "content": "Hello"}]
        result = await service.chat_completion(messages)

        assert result == "Test response"

        # Verify the completion was called with correct parameters
        mock_client_instance.chat.completions.create.assert_called_once_with(
            model="gpt-4-test", messages=messages, max_tokens=1000, temperature=0.5
        )

    @pytest.mark.asyncio()
    async def test_chat_completion_with_custom_parameters(
        self, openai_settings, mock_credential, mock_openai_client
    ):
        """Test chat completion with custom parameters."""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage.total_tokens = 75

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client_instance

        service = AzureOpenAIService(openai_settings, mock_credential)

        messages = [{"role": "user", "content": "Hello"}]
        result = await service.chat_completion(
            messages, max_tokens=2000, temperature=0.9, top_p=0.95
        )

        assert result == "Test response"

        # Verify custom parameters were used
        mock_client_instance.chat.completions.create.assert_called_once_with(
            model="gpt-4-test",
            messages=messages,
            max_tokens=2000,
            temperature=0.9,
            top_p=0.95,
        )

    @pytest.mark.asyncio()
    async def test_chat_completion_empty_response_raises_error(
        self, openai_settings, mock_credential, mock_openai_client
    ):
        """Test chat completion with empty response raises error."""
        # Setup mock response with empty content
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = None

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client_instance

        service = AzureOpenAIService(openai_settings, mock_credential)

        messages = [{"role": "user", "content": "Hello"}]

        with pytest.raises(ValueError, match="Empty response from Azure OpenAI"):
            await service.chat_completion(messages)

    @pytest.mark.asyncio()
    async def test_generate_motivation_letter(self, openai_settings, mock_credential):
        """Test motivation letter generation."""
        service = AzureOpenAIService(openai_settings, mock_credential)

        # Mock the chat_completion method
        with patch.object(
            service, "chat_completion", new_callable=AsyncMock
        ) as mock_chat:
            mock_chat.return_value = "Generated motivation letter"

            result = await service.generate_motivation_letter(
                job_description="Software Engineer position",
                user_profile="Experienced developer",
                company_info="Tech startup",
            )

            assert result == "Generated motivation letter"

            # Verify chat_completion was called with correct message structure
            mock_chat.assert_called_once()
            messages = mock_chat.call_args[0][0]

            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"
            assert "Software Engineer position" in messages[1]["content"]
            assert "Experienced developer" in messages[1]["content"]
            assert "Tech startup" in messages[1]["content"]

    def test_test_connection_success(
        self, openai_settings, mock_credential, mock_openai_client
    ):
        """Test successful connection test."""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client_instance

        service = AzureOpenAIService(openai_settings, mock_credential)

        result = service.test_connection()

        assert result is True

        # Verify test completion was called
        mock_client_instance.chat.completions.create.assert_called_once_with(
            model="gpt-4-test",
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=10,
        )

    def test_test_connection_failure(
        self, openai_settings, mock_credential, mock_openai_client
    ):
        """Test connection test failure."""
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = Exception(
            "Connection failed"
        )
        mock_openai_client.return_value = mock_client_instance

        service = AzureOpenAIService(openai_settings, mock_credential)

        result = service.test_connection()

        assert result is False


class TestGetOpenAIService:
    """Test global service instance function."""

    def test_get_openai_service_creates_instance(self):
        """Test get_openai_service creates service instance."""
        with patch("job_agent.services.openai_service._openai_service", None):
            with patch(
                "job_agent.services.openai_service.AzureOpenAIService"
            ) as mock_service:
                result = get_openai_service()

                mock_service.assert_called_once()
                assert result == mock_service.return_value

    def test_get_openai_service_reuses_instance(self):
        """Test get_openai_service reuses existing instance."""
        mock_instance = Mock()

        with patch("job_agent.services.openai_service._openai_service", mock_instance):
            result = get_openai_service()

            assert result == mock_instance
