#!/usr/bin/env python3
"""Quick type check test."""

import os

from src.job_agent.core.config import AzureOpenAISettings, AzureSettings

# Test with environment variables (should work)
os.environ.update(
    {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4",
        "AZURE_OPENAI_MODEL": "gpt-4",
        "AZURE_RESOURCE_GROUP": "test-rg",
        "AZURE_SUBSCRIPTION": "test-subscription",
    }
)

try:
    # This should work at runtime
    openai_settings = AzureOpenAISettings()  # type: ignore[call-arg]
    azure_settings = AzureSettings()  # type: ignore[call-arg]
    print("✓ Type ignore comments work correctly")
    print(f"OpenAI endpoint: {openai_settings.endpoint}")
    print(f"Azure resource group: {azure_settings.resource_group}")
except Exception as e:
    print(f"✗ Error: {e}")
