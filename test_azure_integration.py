#!/usr/bin/env python3
"""
Manual test script for Azure OpenAI integration.
Run this script to test the Azure OpenAI connection and functionality.
"""

import asyncio
import sys

from job_agent.core.config import settings
from job_agent.services.openai_service import get_openai_service
from job_agent.utils.azure_utils import azure_credential_manager


async def main() -> bool:
    """Test Azure OpenAI integration."""
    print("🔧 Azure OpenAI Integration Test")
    print("=" * 40)

    # Test 1: Configuration loading
    print("\n1. Testing configuration loading...")
    if settings.azure_openai:
        print(f"   ✓ Azure OpenAI endpoint: {settings.azure_openai.endpoint}")
        print(f"   ✓ Deployment name: {settings.azure_openai.deployment_name}")
        print(f"   ✓ API version: {settings.azure_openai.api_version}")
        print(f"   ✓ Model: {settings.azure_openai.model}")
    else:
        print("   ✗ Azure OpenAI configuration not loaded")
        return False

    # Test 2: Azure credential
    print("\n2. Testing Azure credential...")
    try:
        azure_credential_manager.get_credential()
        print("   ✓ Azure credential acquired")
    except Exception as e:
        print(f"   ✗ Azure credential failed: {e}")
        return False

    # Test 3: OpenAI service initialization
    print("\n3. Testing OpenAI service initialization...")
    try:
        service = get_openai_service()
        print("   ✓ OpenAI service created")
    except Exception as e:
        print(f"   ✗ OpenAI service creation failed: {e}")
        return False

    # Test 4: Simple chat completion
    print("\n4. Testing chat completion...")
    try:
        messages = [
            {
                "role": "user",
                "content": "Say 'Hello from Azure OpenAI!' and nothing else.",
            }
        ]

        response = await service.chat_completion(messages, max_tokens=20)
        print(f"   ✓ Chat completion successful: {response.strip()}")
    except Exception as e:
        print(f"   ✗ Chat completion failed: {e}")
        return False

    # Test 5: Motivation letter generation (brief version)
    print("\n5. Testing motivation letter generation...")
    try:
        job_description = (
            "Python Developer position requiring FastAPI and Azure experience."
        )
        user_profile = "Senior developer with 3 years Python and cloud experience."

        letter = await service.generate_motivation_letter(
            job_description=job_description,
            user_profile=user_profile,
            company_info="Tech startup",
        )

        print(f"   ✓ Motivation letter generated ({len(letter)} characters)")
        print(f"   Preview: {letter[:100]}...")
    except Exception as e:
        print(f"   ✗ Motivation letter generation failed: {e}")
        return False

    print("\n🎉 All tests passed! Azure OpenAI integration is working correctly.")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)
