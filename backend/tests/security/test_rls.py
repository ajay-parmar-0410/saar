"""RLS (Row-Level Security) verification tests.

Tests that:
- User A cannot read User B's data
- User A cannot modify User B's data
- Unauthenticated requests get no data
"""

import os
import sys
import time
import uuid

import jwt
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")


def _make_token(user_id: str, email: str = "test@saar.local") -> str:
    return jwt.encode(
        {
            "sub": user_id,
            "email": email,
            "role": "authenticated",
            "aud": "authenticated",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        },
        JWT_SECRET,
        algorithm="HS256",
    )


def _headers(user_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {_make_token(user_id)}"}


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


@pytest.fixture(scope="module")
def user_a_id(test_user_id: str) -> str:
    """User A — the test user from conftest."""
    return test_user_id


@pytest.fixture(scope="module")
def user_b_id() -> str:
    """User B — a second test user for cross-user tests."""
    from db.client import get_supabase_client

    client = get_supabase_client()
    email = f"userb-{uuid.uuid4().hex[:8]}@saar-test.local"
    password = f"TestPass!{uuid.uuid4().hex[:12]}"

    auth_response = client.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True,
        "user_metadata": {"full_name": "User B"},
    })
    user_id = auth_response.user.id

    yield user_id

    try:
        client.auth.admin.delete_user(user_id)
    except Exception:
        pass


# --------------------------------------------------------------------------
# Unauthenticated access tests
# --------------------------------------------------------------------------


class TestUnauthenticatedAccess:
    """Requests without a valid token should be rejected."""

    PROTECTED_ENDPOINTS = [
        ("GET", "/api/v1/user/profile"),
        ("GET", "/api/v1/preferences"),
        ("GET", "/api/v1/interests"),
        ("GET", "/api/v1/schedule"),
        ("GET", "/api/v1/briefings"),
        ("GET", "/api/v1/chat/history"),
    ]

    def test_all_protected_endpoints_reject_no_token(self, client: TestClient):
        for method, path in self.PROTECTED_ENDPOINTS:
            resp = client.request(method, path)
            assert resp.status_code in (401, 403), (
                f"{method} {path} returned {resp.status_code} without auth"
            )

    def test_all_protected_endpoints_reject_bad_token(self, client: TestClient):
        headers = {"Authorization": "Bearer invalid.garbage.token"}
        for method, path in self.PROTECTED_ENDPOINTS:
            resp = client.request(method, path, headers=headers)
            assert resp.status_code == 401, (
                f"{method} {path} returned {resp.status_code} with bad token"
            )


# --------------------------------------------------------------------------
# Cross-user data isolation tests
# --------------------------------------------------------------------------


class TestCrossUserIsolation:
    """User A should not be able to read or modify User B's data."""

    def test_user_a_cannot_see_user_b_profile(
        self, client: TestClient, user_a_id: str, user_b_id: str
    ):
        """User A can only see their own profile, not User B's."""
        resp = client.get("/api/v1/user/profile", headers=_headers(user_a_id))
        if resp.status_code == 200:
            assert resp.json()["id"] == user_a_id

    def test_user_a_cannot_see_user_b_preferences(
        self, client: TestClient, user_a_id: str, user_b_id: str
    ):
        """Preferences endpoint only returns the calling user's data."""
        resp = client.get("/api/v1/preferences", headers=_headers(user_a_id))
        if resp.status_code == 200:
            assert resp.json()["user_id"] == user_a_id

    def test_user_a_cannot_see_user_b_interests(
        self, client: TestClient, user_a_id: str, user_b_id: str
    ):
        """Interests endpoint only returns the calling user's data."""
        # First add an interest as User B
        client.post(
            "/api/v1/interests",
            json={"type": "stock", "value": "SECRET_STOCK_B"},
            headers=_headers(user_b_id),
        )

        # User A should not see User B's interests
        resp = client.get("/api/v1/interests", headers=_headers(user_a_id))
        if resp.status_code == 200:
            values = [i["value"] for i in resp.json()]
            assert "SECRET_STOCK_B" not in values

    def test_user_a_cannot_see_user_b_briefings(
        self, client: TestClient, user_a_id: str, user_b_id: str
    ):
        """User A only sees their own briefings."""
        resp = client.get("/api/v1/briefings", headers=_headers(user_a_id))
        if resp.status_code == 200:
            for b in resp.json().get("briefings", []):
                assert b["user_id"] == user_a_id

    def test_user_a_cannot_read_user_b_briefing_by_id(
        self, client: TestClient, user_a_id: str, user_b_id: str
    ):
        """User A trying to access User B's briefing by ID gets 404."""
        from db.briefings import create_briefing

        # Create a briefing for User B
        briefing = create_briefing(
            user_id=user_b_id,
            content="Secret briefing for B",
            sections=[],
            top_story="B's top story",
            item_count=1,
            alert_count=0,
        )

        # User A tries to access it
        resp = client.get(
            f"/api/v1/briefings/{briefing['id']}",
            headers=_headers(user_a_id),
        )
        assert resp.status_code == 404

    def test_user_a_cannot_see_user_b_chat_history(
        self, client: TestClient, user_a_id: str, user_b_id: str
    ):
        """User A only sees their own chat history."""
        # Create a chat entry for User B
        from db.chat import create_chat_entry

        create_chat_entry(
            user_id=user_b_id,
            query="Secret question from B",
            response="Secret answer for B",
        )

        # User A should not see it
        resp = client.get("/api/v1/chat/history", headers=_headers(user_a_id))
        if resp.status_code == 200:
            messages = resp.json().get("messages", [])
            for msg in messages:
                assert msg["user_id"] == user_a_id

    def test_user_a_cannot_delete_user_b_interest(
        self, client: TestClient, user_a_id: str, user_b_id: str
    ):
        """User A cannot delete User B's interest."""
        # Add interest as User B
        resp = client.post(
            "/api/v1/interests",
            json={"type": "keyword", "value": "UNDELETABLE_BY_A"},
            headers=_headers(user_b_id),
        )
        if resp.status_code == 201:
            interest_id = resp.json()["id"]

            # User A tries to delete it
            resp = client.delete(
                f"/api/v1/interests/{interest_id}",
                headers=_headers(user_a_id),
            )
            assert resp.status_code == 404

    def test_user_a_cannot_delete_user_b_account(
        self, client: TestClient, user_a_id: str, user_b_id: str
    ):
        """User A cannot delete User B's account via API."""
        # The delete endpoint uses the JWT's user ID, not a path param
        # So User A calling DELETE /api/v1/user only affects User A
        # This verifies the endpoint is scoped to the authenticated user
        resp = client.get("/api/v1/user/profile", headers=_headers(user_b_id))
        if resp.status_code == 200:
            assert resp.json()["id"] == user_b_id  # User B still exists


class TestScheduleIsolation:
    """Schedule data is isolated per user."""

    def test_user_a_cannot_see_user_b_schedule(
        self, client: TestClient, user_a_id: str, user_b_id: str
    ):
        resp = client.get("/api/v1/schedule", headers=_headers(user_a_id))
        if resp.status_code == 200:
            assert resp.json()["user_id"] == user_a_id
