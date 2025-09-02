"""Azure OpenAI service integration."""

import logging
from typing import Any, Optional

from azure.core.credentials import TokenCredential
from openai import AzureOpenAI

from ..core.config import AzureOpenAISettings, settings
from ..utils.azure_utils import azure_credential_manager

logger = logging.getLogger(__name__)


class AzureOpenAIService:
    """Service for interacting with Azure OpenAI."""

    def __init__(
        self,
        openai_settings: Optional[AzureOpenAISettings] = None,
        credential: Optional[TokenCredential] = None,
    ) -> None:
        """Initialize the Azure OpenAI service.

        Args:
            openai_settings: Azure OpenAI configuration settings
            credential: Azure credential for authentication
        """
        self.settings = openai_settings or settings.azure_openai
        if not self.settings:
            raise ValueError("Azure OpenAI settings are required")

        self.credential = credential or azure_credential_manager.get_credential()
        self._client: Optional[AzureOpenAI] = None

    @property
    def client(self) -> AzureOpenAI:
        """Get or create the Azure OpenAI client.

        Returns:
            AzureOpenAI: Configured Azure OpenAI client
        """
        if self._client is None:
            try:
                # Get token for Azure OpenAI scope
                token = self.credential.get_token(
                    "https://cognitiveservices.azure.com/.default"
                )

                self._client = AzureOpenAI(
                    azure_endpoint=self.settings.endpoint,
                    api_version=self.settings.api_version,
                    azure_ad_token=token.token,
                )
                logger.info("Azure OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI client: {e}")
                raise

        return self._client

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate a chat completion using Azure OpenAI.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens in response (uses setting default if None)
            temperature: Sampling temperature (uses setting default if None)
            **kwargs: Additional parameters for the completion

        Returns:
            str: Generated response content

        Raises:
            Exception: If completion fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.settings.deployment_name,
                messages=messages,
                max_tokens=max_tokens or self.settings.max_tokens,
                temperature=temperature or self.settings.temperature,
                **kwargs,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from Azure OpenAI")

            logger.info(
                f"Chat completion successful, tokens used: {response.usage.total_tokens if response.usage else 'unknown'}"
            )
            return content

        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise

    async def generate_motivation_letter(
        self,
        job_description: str,
        user_profile: str,
        company_info: Optional[str] = None,
    ) -> str:
        """Generate a motivation letter for a job application.

        Args:
            job_description: Description of the job position
            user_profile: User's profile and experience
            company_info: Additional company information (optional)

        Returns:
            str: Generated motivation letter
        """
        system_prompt = """You are an expert job application writer. Create a compelling,
        professional motivation letter that highlights the candidate's relevant experience
        and demonstrates enthusiasm for the role. The letter should be concise, engaging,
        and tailored to the specific job and company."""

        user_message = f"""
        Please write a motivation letter for the following job application:

        Job Description:
        {job_description}

        Candidate Profile:
        {user_profile}
        """

        if company_info:
            user_message += f"\n\nCompany Information:\n{company_info}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            return await self.chat_completion(messages)
        except Exception as e:
            logger.error(f"Failed to generate motivation letter: {e}")
            raise

    def test_connection(self) -> bool:
        """Test the connection to Azure OpenAI service.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Simple test completion
            response = self.client.chat.completions.create(
                model=self.settings.deployment_name,
                messages=[{"role": "user", "content": "Hello, this is a test."}],
                max_tokens=10,
            )

            if response.choices and response.choices[0].message.content:
                logger.info("Azure OpenAI connection test successful")
                return True
            else:
                logger.warning("Azure OpenAI test returned empty response")
                return False

        except Exception as e:
            logger.error(f"Azure OpenAI connection test failed: {e}")
            return False


# Global service instance - will be initialized when first accessed
_openai_service: Optional[AzureOpenAIService] = None


def get_openai_service() -> AzureOpenAIService:
    """Get the global Azure OpenAI service instance.

    Returns:
        AzureOpenAIService: Configured service instance
    """
    global _openai_service
    if _openai_service is None:
        _openai_service = AzureOpenAIService()
    return _openai_service
