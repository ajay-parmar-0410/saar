"""Tests for Phase 7 API routes — all endpoints."""

import os
import sys
import time
from unittest.mock import MagicMock, patch

import jwt
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Set a test JWT secret before importing app
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-secret-key-for-unit-tests")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-key")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key")
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")

JWT_SECRET = os.environ["SUPABASE_JWT_SECRET"]
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"
TEST_EMAIL = "test@saar.local"


def _make_token(
    user_id: str = TEST_USER_ID,
    email: str = TEST_EMAIL,
) -> str:
    """Create a valid test JWT."""
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def _auth_headers(user_id: str = TEST_USER_ID) -> dict[str, str]:
    """Authorization headers with valid JWT."""
    return {"Authorization": f"Bearer {_make_token(user_id)}"}


# --- Fixtures ---


@pytest.fixture(scope="module")
def client():
    """TestClient with scheduler startup mocked out."""
    # Pre-import the module so patch can find the attribute
    import briefing.scheduler

    with patch.object(briefing.scheduler, "get_scheduler") as mock_sched, \
         patch.object(briefing.scheduler, "load_all_schedules", new=_mock_load_all):
        mock_sched.return_value = MagicMock()
        from main import app
        yield TestClient(app, raise_server_exceptions=False)


async def _mock_load_all(*args, **kwargs):
    return 0


# --- Health ---


class TestHealth:
    def test_health_returns_ok(self, client: TestClient):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# --- User Profile ---


class TestUserProfile:
    def test_profile_requires_auth(self, client: TestClient):
        resp = client.get("/api/v1/user/profile")
        assert resp.status_code in (401, 403)

    @patch("api.v1.user.get_user")
    def test_get_profile(self, mock_get_user, client: TestClient):
        mock_get_user.return_value = {
            "id": TEST_USER_ID,
            "email": TEST_EMAIL,
            "name": "Test User",
            "user_type": ["ai_tech"],
            "onboarded": True,
            "last_active_at": "2026-04-04T00:00:00Z",
            "created_at": "2026-04-01T00:00:00Z",
        }
        resp = client.get("/api/v1/user/profile", headers=_auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == TEST_USER_ID
        assert data["email"] == TEST_EMAIL
        assert data["onboarded"] is True

    @patch("api.v1.user.get_user")
    def test_get_profile_not_found(self, mock_get_user, client: TestClient):
        mock_get_user.return_value = None
        resp = client.get("/api/v1/user/profile", headers=_auth_headers())
        assert resp.status_code == 404


class TestDeleteAccount:
    @patch("api.v1.user.delete_user")
    @patch("api.v1.user.get_user")
    def test_delete_account(self, mock_get_user, mock_delete, client: TestClient):
        mock_get_user.return_value = {"id": TEST_USER_ID}
        resp = client.delete("/api/v1/user", headers=_auth_headers())
        assert resp.status_code == 200
        assert resp.json()["message"] == "Account deleted successfully"
        mock_delete.assert_called_once_with(TEST_USER_ID)

    @patch("api.v1.user.get_user")
    def test_delete_account_not_found(self, mock_get_user, client: TestClient):
        mock_get_user.return_value = None
        resp = client.delete("/api/v1/user", headers=_auth_headers())
        assert resp.status_code == 404


# --- Preferences ---


class TestPreferences:
    @patch("api.v1.preferences.get_preferences")
    def test_get_preferences(self, mock_get, client: TestClient):
        mock_get.return_value = {
            "user_id": TEST_USER_ID,
            "topics": ["ai", "tech"],
            "sources": ["github", "hackernews"],
            "briefing_depth": "detailed",
            "location": "Mumbai",
            "updated_at": "2026-04-04T00:00:00Z",
        }
        resp = client.get("/api/v1/preferences", headers=_auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["topics"] == ["ai", "tech"]
        assert data["briefing_depth"] == "detailed"

    @patch("api.v1.preferences.get_preferences")
    def test_get_preferences_not_found(self, mock_get, client: TestClient):
        mock_get.return_value = None
        resp = client.get("/api/v1/preferences", headers=_auth_headers())
        assert resp.status_code == 404

    @patch("api.v1.preferences.update_preferences")
    @patch("api.v1.preferences.get_preferences")
    def test_update_preferences(self, mock_get, mock_update, client: TestClient):
        mock_get.return_value = {
            "user_id": TEST_USER_ID,
            "topics": ["ai"],
            "sources": ["github"],
            "briefing_depth": "detailed",
            "location": "Mumbai",
        }
        mock_update.return_value = {
            "user_id": TEST_USER_ID,
            "topics": ["ai", "finance"],
            "sources": ["github"],
            "briefing_depth": "headlines",
            "location": "Mumbai",
            "updated_at": "2026-04-04T00:00:00Z",
        }
        resp = client.put(
            "/api/v1/preferences",
            json={"topics": ["ai", "finance"], "briefing_depth": "headlines"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 200
        assert resp.json()["topics"] == ["ai", "finance"]
        assert resp.json()["briefing_depth"] == "headlines"

    @patch("api.v1.preferences.get_preferences")
    def test_update_preferences_invalid_depth(self, mock_get, client: TestClient):
        mock_get.return_value = {"user_id": TEST_USER_ID}
        resp = client.put(
            "/api/v1/preferences",
            json={"briefing_depth": "ultra"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 422

    @patch("api.v1.preferences.get_preferences")
    def test_update_preferences_empty_body(self, mock_get, client: TestClient):
        mock_get.return_value = {"user_id": TEST_USER_ID}
        resp = client.put(
            "/api/v1/preferences",
            json={},
            headers=_auth_headers(),
        )
        assert resp.status_code == 400


# --- Interests ---


class TestInterests:
    @patch("api.v1.interests.get_interests")
    def test_list_interests(self, mock_get, client: TestClient):
        mock_get.return_value = [
            {
                "id": "int-1",
                "user_id": TEST_USER_ID,
                "type": "stock",
                "value": "AAPL",
                "added_at": "2026-04-04T00:00:00Z",
            },
        ]
        resp = client.get("/api/v1/interests", headers=_auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["value"] == "AAPL"

    @patch("api.v1.interests.add_interest")
    def test_add_interest(self, mock_add, client: TestClient):
        mock_add.return_value = {
            "id": "int-2",
            "user_id": TEST_USER_ID,
            "type": "repo",
            "value": "anthropics/claude-code",
            "added_at": "2026-04-04T00:00:00Z",
        }
        resp = client.post(
            "/api/v1/interests",
            json={"type": "repo", "value": "anthropics/claude-code"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 201
        assert resp.json()["type"] == "repo"

    def test_add_interest_invalid_type(self, client: TestClient):
        resp = client.post(
            "/api/v1/interests",
            json={"type": "invalid_type", "value": "test"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 422

    def test_add_interest_empty_value(self, client: TestClient):
        resp = client.post(
            "/api/v1/interests",
            json={"type": "stock", "value": "   "},
            headers=_auth_headers(),
        )
        assert resp.status_code == 422

    @patch("api.v1.interests.remove_interest")
    @patch("api.v1.interests.get_interests")
    def test_delete_interest(self, mock_get, mock_remove, client: TestClient):
        mock_get.return_value = [
            {"id": "int-1", "user_id": TEST_USER_ID, "type": "stock", "value": "AAPL"},
        ]
        resp = client.delete(
            "/api/v1/interests/int-1",
            headers=_auth_headers(),
        )
        assert resp.status_code == 204

    @patch("api.v1.interests.get_interests")
    def test_delete_interest_not_found(self, mock_get, client: TestClient):
        mock_get.return_value = []
        resp = client.delete(
            "/api/v1/interests/nonexistent",
            headers=_auth_headers(),
        )
        assert resp.status_code == 404


# --- Schedule ---


class TestSchedule:
    @patch("api.v1.schedule.get_schedule")
    def test_get_schedule(self, mock_get, client: TestClient):
        mock_get.return_value = {
            "user_id": TEST_USER_ID,
            "times": ["07:00", "19:00"],
            "timezone": "Asia/Kolkata",
            "enabled": True,
        }
        resp = client.get("/api/v1/schedule", headers=_auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["times"] == ["07:00", "19:00"]
        assert data["enabled"] is True

    @patch("api.v1.schedule._reschedule_jobs")
    @patch("api.v1.schedule.update_schedule")
    @patch("api.v1.schedule.get_schedule")
    def test_update_schedule(self, mock_get, mock_update, mock_resched, client: TestClient):
        mock_get.return_value = {
            "user_id": TEST_USER_ID,
            "times": ["07:00"],
            "timezone": "Asia/Kolkata",
            "enabled": True,
        }
        mock_update.return_value = {
            "user_id": TEST_USER_ID,
            "times": ["08:00"],
            "timezone": "Asia/Kolkata",
            "enabled": True,
        }
        resp = client.put(
            "/api/v1/schedule",
            json={"times": ["08:00"]},
            headers=_auth_headers(),
        )
        assert resp.status_code == 200
        assert resp.json()["times"] == ["08:00"]
        mock_resched.assert_called_once()

    def test_update_schedule_invalid_time(self, client: TestClient):
        resp = client.put(
            "/api/v1/schedule",
            json={"times": ["25:00"]},
            headers=_auth_headers(),
        )
        assert resp.status_code == 422

    def test_update_schedule_invalid_timezone(self, client: TestClient):
        resp = client.put(
            "/api/v1/schedule",
            json={"timezone": "Fake/Zone"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 422


# --- Briefings ---


class TestBriefings:
    @patch("api.v1.briefings.get_user_briefings")
    def test_list_briefings(self, mock_get, client: TestClient):
        mock_get.return_value = [
            {
                "id": "br-1",
                "user_id": TEST_USER_ID,
                "top_story": "AI breakthrough",
                "item_count": 12,
                "alert_count": 2,
                "read": False,
                "generated_at": "2026-04-04T07:00:00Z",
            },
        ]
        resp = client.get("/api/v1/briefings", headers=_auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["briefings"]) == 1
        assert data["briefings"][0]["top_story"] == "AI breakthrough"

    @patch("api.v1.briefings.get_user_briefings")
    def test_list_briefings_pagination(self, mock_get, client: TestClient):
        mock_get.return_value = []
        resp = client.get(
            "/api/v1/briefings?limit=5&offset=10",
            headers=_auth_headers(),
        )
        assert resp.status_code == 200
        mock_get.assert_called_once_with(TEST_USER_ID, limit=5, offset=10)

    @patch("api.v1.briefings.get_briefing")
    def test_get_briefing_detail(self, mock_get, client: TestClient):
        mock_get.return_value = {
            "id": "br-1",
            "user_id": TEST_USER_ID,
            "content": "# Daily Briefing",
            "sections": [],
            "top_story": "AI breakthrough",
            "item_count": 12,
            "alert_count": 2,
            "read": False,
            "read_at": None,
            "generated_at": "2026-04-04T07:00:00Z",
        }
        resp = client.get("/api/v1/briefings/br-1", headers=_auth_headers())
        assert resp.status_code == 200
        assert resp.json()["content"] == "# Daily Briefing"

    @patch("api.v1.briefings.get_briefing")
    def test_get_briefing_not_found(self, mock_get, client: TestClient):
        mock_get.return_value = None
        resp = client.get("/api/v1/briefings/nonexistent", headers=_auth_headers())
        assert resp.status_code == 404

    @patch("api.v1.briefings.get_briefing")
    def test_get_briefing_wrong_user(self, mock_get, client: TestClient):
        mock_get.return_value = {
            "id": "br-1",
            "user_id": "other-user-id",
            "content": "",
            "sections": [],
        }
        resp = client.get("/api/v1/briefings/br-1", headers=_auth_headers())
        assert resp.status_code == 404  # Not 403 — don't leak existence

    @patch("api.v1.briefings.mark_as_read")
    @patch("api.v1.briefings.get_briefing")
    def test_mark_read(self, mock_get, mock_mark, client: TestClient):
        mock_get.return_value = {
            "id": "br-1",
            "user_id": TEST_USER_ID,
        }
        mock_mark.return_value = {
            "id": "br-1",
            "read": True,
            "read_at": "2026-04-04T12:00:00Z",
        }
        resp = client.put("/api/v1/briefings/br-1/read", headers=_auth_headers())
        assert resp.status_code == 200
        assert resp.json()["read"] is True


# --- Chat ---


class TestChat:
    @patch("api.v1.chat.generate_chat_response")
    @patch("api.v1.chat.create_chat_entry")
    @patch("api.v1.chat.get_recent_context")
    @patch("api.v1.chat.get_latest_briefing")
    @patch("api.v1.chat.get_interests")
    @patch("api.v1.chat.get_preferences")
    def test_send_message(
        self,
        mock_prefs,
        mock_interests,
        mock_briefing,
        mock_context,
        mock_create,
        mock_generate,
        client: TestClient,
    ):
        from chat.engine import ChatResult

        mock_prefs.return_value = {"topics": ["ai"]}
        mock_interests.return_value = []
        mock_briefing.return_value = None
        mock_context.return_value = []
        mock_generate.return_value = ChatResult(response="Here's the answer.", sources=())
        mock_create.return_value = {"id": "chat-1"}

        resp = client.post(
            "/api/v1/chat",
            json={"query": "What's the latest in AI?"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 200
        assert resp.json()["response"] == "Here's the answer."

    def test_send_empty_message(self, client: TestClient):
        resp = client.post(
            "/api/v1/chat",
            json={"query": "   "},
            headers=_auth_headers(),
        )
        assert resp.status_code == 422

    def test_send_too_long_message(self, client: TestClient):
        resp = client.post(
            "/api/v1/chat",
            json={"query": "x" * 2001},
            headers=_auth_headers(),
        )
        assert resp.status_code == 422

    @patch("api.v1.chat.get_chat_history")
    def test_get_history(self, mock_get, client: TestClient):
        mock_get.return_value = [
            {
                "id": "chat-1",
                "user_id": TEST_USER_ID,
                "query": "Hello",
                "response": "Hi there!",
                "sources": [],
                "created_at": "2026-04-04T12:00:00Z",
            },
        ]
        resp = client.get("/api/v1/chat/history", headers=_auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["messages"]) == 1
        assert data["messages"][0]["query"] == "Hello"


# --- Rate Limiting ---


class TestRateLimiting:
    def test_health_not_rate_limited(self, client: TestClient):
        """Health endpoint should not be rate limited."""
        for _ in range(65):
            resp = client.get("/health")
            assert resp.status_code == 200


# --- Error Handling ---


class TestErrorHandling:
    def test_validation_error_format(self, client: TestClient):
        """Validation errors should use consistent format."""
        resp = client.post(
            "/api/v1/chat",
            json={"query": ""},
            headers=_auth_headers(),
        )
        assert resp.status_code == 422
        data = resp.json()
        assert "error" in data
        assert "detail" in data
        assert "status" in data

    def test_401_without_token(self, client: TestClient):
        """Protected endpoints return 401 without auth."""
        endpoints = [
            ("GET", "/api/v1/user/profile"),
            ("GET", "/api/v1/preferences"),
            ("GET", "/api/v1/interests"),
            ("GET", "/api/v1/schedule"),
            ("GET", "/api/v1/briefings"),
            ("GET", "/api/v1/chat/history"),
        ]
        for method, path in endpoints:
            resp = client.request(method, path)
            assert resp.status_code in (401, 403), f"{method} {path} returned {resp.status_code}"
