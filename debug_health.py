"""Simple test to check health endpoint response structure."""

from fastapi.testclient import TestClient

from job_agent.app import create_app


def test_debug_health_response() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health/detailed")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    data = response.json()
    health = data["health"]
    print(f"Health keys: {list(health.keys())}")


if __name__ == "__main__":
    test_debug_health_response()
