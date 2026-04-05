"""Integration tests for the full API flow against real Supabase.

Tests onboarding → preferences → interests → briefing creation → chat history
using a real test user. Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.
"""

import os
import sys
import time

import jwt
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


@pytest.fixture(scope="module")
def client():
    import briefing.scheduler

    with patch.object(briefing.scheduler, "get_scheduler") as mock_sched, \
         patch.object(briefing.scheduler, "load_all_schedules", new=_mock_load):
        mock_sched.return_value = MagicMock()
        from main import app
        yield TestClient(app, raise_server_exceptions=False)


async def _mock_load(*args, **kwargs):
    return 0


def _auth_headers(user_id: str) -> dict[str, str]:
    secret = os.environ.get("SUPABASE_JWT_SECRET", "")
    if not secret:
        pytest.skip("SUPABASE_JWT_SECRET not set")
    token = jwt.encode(
        {
            "sub": user_id,
            "email": "integration@saar-test.local",
            "role": "authenticated",
            "aud": "authenticated",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        },
        secret,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


class TestOnboardingFlow:
    """Full onboarding → profile → preferences flow."""

    def test_complete_onboarding(self, client: TestClient, test_user_id: str):
        headers = _auth_headers(test_user_id)

        # Step 1: Get starter pack
        resp = client.get(
            "/api/v1/onboarding/starter-pack?user_types=ai_tech",
            headers=headers,
        )
        assert resp.status_code == 200
        pack = resp.json()
        assert "github" in pack["sources"]

        # Step 2: Complete onboarding
        resp = client.post(
            "/api/v1/onboarding/complete",
            headers=headers,
            json={
                "user_types": ["ai_tech"],
                "topics": pack["topics"],
                "sources": pack["sources"],
                "briefing_depth": "detailed",
                "location": "Mumbai",
                "schedule": {"times": ["07:00"], "timezone": "Asia/Kolkata"},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "Onboarding complete"

    def test_profile_after_onboarding(self, client: TestClient, test_user_id: str):
        headers = _auth_headers(test_user_id)
        resp = client.get("/api/v1/user/profile", headers=headers)
        assert resp.status_code == 200
        profile = resp.json()
        assert profile["id"] == test_user_id


class TestPreferencesFlow:
    """Read and update preferences."""

    def test_get_preferences(self, client: TestClient, test_user_id: str):
        headers = _auth_headers(test_user_id)
        resp = client.get("/api/v1/preferences", headers=headers)
        assert resp.status_code == 200
        prefs = resp.json()
        assert prefs["user_id"] == test_user_id
        assert len(prefs["topics"]) > 0

    def test_update_preferences(self, client: TestClient, test_user_id: str):
        headers = _auth_headers(test_user_id)
        resp = client.put(
            "/api/v1/preferences",
            headers=headers,
            json={"topics": ["ai", "weather"], "briefing_depth": "headlines"},
        )
        assert resp.status_code == 200
        assert resp.json()["briefing_depth"] == "headlines"

        # Restore
        client.put(
            "/api/v1/preferences",
            headers=headers,
            json={"briefing_depth": "detailed"},
        )


class TestInterestsFlow:
    """Add, list, and remove interests."""

    def test_add_list_remove(self, client: TestClient, test_user_id: str):
        headers = _auth_headers(test_user_id)

        # Add
        resp = client.post(
            "/api/v1/interests",
            headers=headers,
            json={"type": "stock", "value": "INFY"},
        )
        assert resp.status_code == 201
        item_id = resp.json()["id"]

        # List
        resp = client.get("/api/v1/interests", headers=headers)
        assert resp.status_code == 200
        values = [i["value"] for i in resp.json()]
        assert "INFY" in values

        # Remove
        resp = client.delete(f"/api/v1/interests/{item_id}", headers=headers)
        assert resp.status_code == 204


class TestScheduleFlow:
    """Read and update schedule."""

    def test_get_and_update_schedule(self, client: TestClient, test_user_id: str):
        headers = _auth_headers(test_user_id)

        resp = client.get("/api/v1/schedule", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["timezone"] == "Asia/Kolkata"

        resp = client.put(
            "/api/v1/schedule",
            headers=headers,
            json={"times": ["08:00", "20:00"]},
        )
        assert resp.status_code == 200
        assert set(resp.json()["times"]) == {"08:00", "20:00"}


class TestBriefingsFlow:
    """List and read briefings."""

    def test_list_briefings(self, client: TestClient, test_user_id: str):
        headers = _auth_headers(test_user_id)
        resp = client.get("/api/v1/briefings", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "briefings" in data
        assert "total" in data

    def test_get_briefing_not_found(self, client: TestClient, test_user_id: str):
        headers = _auth_headers(test_user_id)
        # Use a valid UUID format that doesn't exist
        resp = client.get(
            "/api/v1/briefings/00000000-0000-0000-0000-000000000000",
            headers=headers,
        )
        assert resp.status_code == 404


class TestChatFlow:
    """Chat history endpoint."""

    def test_get_history(self, client: TestClient, test_user_id: str):
        headers = _auth_headers(test_user_id)
        resp = client.get("/api/v1/chat/history", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "messages" in data
