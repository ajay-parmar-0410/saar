"""Tests for the onboarding API endpoint."""

import os
import sys
import time

import jwt
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


@pytest.fixture(scope="module")
def client():
    from main import app
    return TestClient(app)


@pytest.fixture(scope="module")
def auth_header(test_user_id: str):
    """Create a valid JWT auth header for the test user."""
    secret = os.environ.get("SUPABASE_JWT_SECRET", "")
    if not secret:
        pytest.skip("SUPABASE_JWT_SECRET not set")

    token = jwt.encode(
        {
            "sub": test_user_id,
            "email": "test@saar.local",
            "role": "authenticated",
            "aud": "authenticated",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        },
        secret,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


class TestStarterPackEndpoint:
    def test_get_starter_pack(self, client: TestClient, auth_header: dict):
        response = client.get(
            "/api/v1/onboarding/starter-pack?user_types=ai_tech",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert "github" in data["sources"]
        assert "artificial_intelligence" in data["topics"]

    def test_combined_starter_pack(self, client: TestClient, auth_header: dict):
        response = client.get(
            "/api/v1/onboarding/starter-pack?user_types=ai_tech,trader",
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert "github" in data["sources"]
        assert "yahoo_finance" in data["sources"]

    def test_invalid_user_type(self, client: TestClient, auth_header: dict):
        response = client.get(
            "/api/v1/onboarding/starter-pack?user_types=invalid",
            headers=auth_header,
        )
        assert response.status_code == 400

    def test_requires_auth(self, client: TestClient):
        response = client.get("/api/v1/onboarding/starter-pack?user_types=ai_tech")
        assert response.status_code in (401, 403)


class TestCompleteOnboarding:
    def test_full_onboarding(self, client: TestClient, auth_header: dict):
        response = client.post(
            "/api/v1/onboarding/complete",
            headers=auth_header,
            json={
                "user_types": ["ai_tech", "general"],
                "topics": ["ai", "weather"],
                "sources": ["github", "newsapi"],
                "briefing_depth": "detailed",
                "location": "Mumbai",
                "interests": [
                    {"type": "stock", "value": "RELIANCE"},
                    {"type": "repo", "value": "langchain-ai/langchain"},
                ],
                "schedule": {
                    "times": ["07:00", "18:00"],
                    "timezone": "Asia/Kolkata",
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Onboarding complete"
        assert data["interests_count"] == 2
        assert set(data["user_types"]) == {"ai_tech", "general"}

    def test_minimal_onboarding(self, client: TestClient, auth_header: dict):
        """Only required fields — defaults should fill the rest."""
        response = client.post(
            "/api/v1/onboarding/complete",
            headers=auth_header,
            json={"user_types": ["general"]},
        )
        assert response.status_code == 200
        data = response.json()
        # Should have gotten default topics/sources from starter pack
        assert len(data["topics"]) > 0
        assert len(data["sources"]) > 0

    def test_invalid_user_type_rejected(self, client: TestClient, auth_header: dict):
        response = client.post(
            "/api/v1/onboarding/complete",
            headers=auth_header,
            json={"user_types": ["invalid_type"]},
        )
        assert response.status_code == 422

    def test_empty_user_types_rejected(self, client: TestClient, auth_header: dict):
        response = client.post(
            "/api/v1/onboarding/complete",
            headers=auth_header,
            json={"user_types": []},
        )
        assert response.status_code == 422

    def test_invalid_interest_type_rejected(self, client: TestClient, auth_header: dict):
        response = client.post(
            "/api/v1/onboarding/complete",
            headers=auth_header,
            json={
                "user_types": ["general"],
                "interests": [{"type": "invalid", "value": "test"}],
            },
        )
        assert response.status_code == 422

    def test_requires_auth(self, client: TestClient):
        response = client.post(
            "/api/v1/onboarding/complete",
            json={"user_types": ["general"]},
        )
        assert response.status_code in (401, 403)
