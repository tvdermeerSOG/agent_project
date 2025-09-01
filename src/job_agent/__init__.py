"""Job Agent - Automated Job Board Polling and Application System.

This package provides automated job board polling, job matching based on user
preferences, and AI-powered motivation letter generation using Azure OpenAI.
"""

__version__ = "0.1.0"
__author__ = "Job Agent Team"
__email__ = "team@jobagent.com"

from .core.config import settings

__all__ = ["settings"]
