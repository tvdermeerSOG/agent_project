#!/usr/bin/env python3
"""
Test script for the chat_completion() function in Azure OpenAI service.

This script tests the chat_completion functionality with various scenarios
to ensure proper integration with Azure OpenAI service.
"""

import asyncio
import logging
import sys

from src.job_agent.services.openai_service import get_openai_service

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_basic_chat_completion() -> bool:
    """Test basic chat completion functionality."""
    logger.info("Testing basic chat completion...")

    try:
        service = get_openai_service()

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! Can you tell me a short joke?"},
        ]

        response = await service.chat_completion(messages, max_tokens=100)

        logger.info("✅ Basic chat completion successful!")
        logger.info(f"Response: {response}")
        return True

    except Exception as e:
        logger.error(f"❌ Basic chat completion failed: {e}")
        return False


async def test_chat_completion_with_parameters() -> bool:
    """Test chat completion with custom parameters."""
    logger.info("Testing chat completion with custom parameters...")

    try:
        service = get_openai_service()

        messages = [
            {"role": "system", "content": "You are a creative writer."},
            {
                "role": "user",
                "content": "Write a very short poem about Python programming.",
            },
        ]

        response = await service.chat_completion(
            messages, max_tokens=150, temperature=0.9
        )

        logger.info("✅ Chat completion with parameters successful!")
        logger.info(f"Response: {response}")
        return True

    except Exception as e:
        logger.error(f"❌ Chat completion with parameters failed: {e}")
        return False


async def test_motivation_letter_generation() -> bool:
    """Test the motivation letter generation functionality."""
    logger.info("Testing motivation letter generation...")

    try:
        service = get_openai_service()

        job_description = """
        Senior Python Developer
        We are looking for an experienced Python developer to join our team.
        Requirements: 5+ years Python experience, FastAPI, Azure cloud experience.
        """

        user_profile = """
        John Doe - Senior Software Engineer with 6 years of Python development experience.
        Skilled in FastAPI, Azure services, and microservices architecture.
        Previously worked on large-scale web applications and cloud deployments.
        """

        company_info = (
            "TechCorp - A leading technology company specializing in cloud solutions."
        )

        response = await service.generate_motivation_letter(
            job_description, user_profile, company_info
        )

        logger.info("✅ Motivation letter generation successful!")
        logger.info(f"Generated letter preview: {response[:200]}...")
        return True

    except Exception as e:
        logger.error(f"❌ Motivation letter generation failed: {e}")
        return False


def test_connection() -> bool:
    """Test the connection to Azure OpenAI service."""
    logger.info("Testing Azure OpenAI connection...")

    try:
        service = get_openai_service()

        if service.test_connection():
            logger.info("✅ Azure OpenAI connection test successful!")
            return True
        else:
            logger.error("❌ Azure OpenAI connection test failed!")
            return False

    except Exception as e:
        logger.error(f"❌ Azure OpenAI connection test failed with exception: {e}")
        return False


async def test_error_handling() -> bool:
    """Test error handling with invalid inputs."""
    logger.info("Testing error handling...")

    try:
        service = get_openai_service()

        # Test with empty messages
        try:
            await service.chat_completion([])
            logger.error("❌ Should have failed with empty messages")
            return False
        except Exception:
            logger.info("✅ Correctly handled empty messages")

        # Test with invalid message format
        try:
            await service.chat_completion([{"invalid": "format"}])
            logger.error("❌ Should have failed with invalid message format")
            return False
        except Exception:
            logger.info("✅ Correctly handled invalid message format")

        logger.info("✅ Error handling tests passed!")
        return True

    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
        return False


async def run_all_tests() -> bool:
    """Run all test scenarios."""
    logger.info("🚀 Starting Azure OpenAI chat_completion() tests...")
    logger.info("=" * 60)

    tests = [
        ("Connection Test", test_connection),
        ("Basic Chat Completion", test_basic_chat_completion),
        ("Chat Completion with Parameters", test_chat_completion_with_parameters),
        ("Motivation Letter Generation", test_motivation_letter_generation),
        ("Error Handling", test_error_handling),
    ]

    results = []

    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        logger.info("-" * 40)

        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()

        results.append((test_name, result))

        if result:
            logger.info(f"✅ {test_name} PASSED")
        else:
            logger.info(f"❌ {test_name} FAILED")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:<30} {status}")

    logger.info("-" * 60)
    logger.info(f"Total: {passed}/{total} tests passed")

    if passed == total:
        logger.info(
            "🎉 All tests passed! Azure OpenAI integration is working correctly."
        )
        return True
    else:
        logger.info(f"⚠️  {total - passed} tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    try:
        # Check if we're authenticated with Azure
        logger.info("🔐 Checking Azure authentication...")

        import subprocess

        result = subprocess.run(
            ["az", "account", "show"], capture_output=True, text=True, check=False
        )

        if result.returncode != 0:
            logger.error(
                "❌ Not authenticated with Azure CLI. Please run 'az login' first."
            )
            sys.exit(1)
        else:
            logger.info("✅ Azure CLI authentication confirmed")

        # Run the tests
        success = asyncio.run(run_all_tests())

        if success:
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)
