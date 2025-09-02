"""Azure utilities for authentication and credential management."""

import logging

from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)


class AzureCredentialManager:
    """Manages Azure credentials using DefaultAzureCredential."""

    def __init__(self) -> None:
        """Initialize the credential manager."""
        self._credential: TokenCredential | None = None

    def get_credential(self) -> TokenCredential:
        """Get Azure credential using DefaultAzureCredential.

        Returns:
            TokenCredential: Azure credential for authentication

        Raises:
            Exception: If credential acquisition fails
        """
        if self._credential is None:
            try:
                # DefaultAzureCredential automatically tries multiple authentication methods:
                # 1. Environment variables (Azure CLI, Service Principal)
                # 2. Managed Identity (if running on Azure)
                # 3. Azure CLI (if logged in)
                # 4. Azure PowerShell
                # 5. Interactive browser (as fallback)
                self._credential = DefaultAzureCredential()
                logger.info("Azure credential initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Azure credential: {e}")
                raise

        return self._credential

    def test_credential(self) -> bool:
        """Test if the credential can acquire a token.

        Returns:
            bool: True if credential is working, False otherwise
        """
        try:
            credential = self.get_credential()
            # Test token acquisition with Azure Resource Manager scope
            credential.get_token("https://management.azure.com/.default")
            logger.info("Azure credential test successful")
            return True
        except Exception as e:
            logger.error(f"Azure credential test failed: {e}")
            return False


# Global instance
azure_credential_manager = AzureCredentialManager()
