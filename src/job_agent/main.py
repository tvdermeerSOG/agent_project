"""Main entry point for the Job Agent application."""

from job_agent.core.config import settings


def main() -> None:
    """Main entry point for the application."""
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📝 Debug mode: {settings.debug}")
    print(f"📊 Log level: {settings.log_level}")
    print("✅ Project setup complete!")
    print("\n🔄 Next steps:")
    print("  1. Complete Task 1.2: Azure Integration Setup")
    print("  2. Complete Task 1.3: Core FastAPI Application")
    print("  3. Continue with job board integration...")


if __name__ == "__main__":
    main()
