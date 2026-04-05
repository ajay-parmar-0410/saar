"""Tests for error handler middleware."""

import os
import sys
import time

import jwt
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

os.environ.setdefault("SUPABASE_JWT_SECRET", "test-secret-for-error-handler")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
os.environ.setdefault("SUPABASE_ANON_KEY", "test-key")
os.environ.setdefault("GROQ_API_KEY", "test-key")

JWT_SECRET = os.environ["SUPABASE_JWT_SECRET"]


def _make_token() -> str:
    return jwt.encode(
        {
            "sub": "test-user-id",
            "email": "test@saar.local",
            "role": "authenticated",
            "aud": "authenticated",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        },
        JWT_SECRET,
        algorithm="HS256",
    )


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


class TestValidationErrorFormat:
    """Validation errors return consistent JSON envelope."""

    def test_missing_required_field(self, client: TestClient):
        resp = client.post(
            "/api/v1/chat",
            json={},
            headers={"Authorization": f"Bearer {_make_token()}"},
        )
        assert resp.status_code == 422
        data = resp.json()
        assert "error" in data
        assert "detail" in data
        assert "status" in data
        assert data["status"] == 422

    def test_invalid_field_value(self, client: TestClient):
        resp = client.put(
            "/api/v1/schedule",
            json={"times": ["99:99"]},
            headers={"Authorization": f"Bearer {_make_token()}"},
        )
        assert resp.status_code == 422
        data = resp.json()
        assert data["error"] == "Validation Error"


class TestAuthErrors:
    """Auth errors return proper status codes."""

    def test_no_token_returns_401_or_403(self, client: TestClient):
        resp = client.get("/api/v1/user/profile")
        assert resp.status_code in (401, 403)

    def test_invalid_token_returns_401(self, client: TestClient):
        resp = client.get(
            "/api/v1/user/profile",
            headers={"Authorization": "Bearer invalid.token"},
        )
        assert resp.status_code == 401

    def test_expired_token_returns_401(self, client: TestClient):
        token = jwt.encode(
            {
                "sub": "test-user-id",
                "email": "test@test.com",
                "role": "authenticated",
                "aud": "authenticated",
                "iat": int(time.time()) - 7200,
                "exp": int(time.time()) - 3600,
            },
            JWT_SECRET,
            algorithm="HS256",
        )
        resp = client.get(
            "/api/v1/user/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401
        assert "expired" in resp.json()["detail"].lower()


class TestServerErrors:
    """Internal errors return safe 500 without leaking details."""

    @patch("api.v1.user.get_user", side_effect=RuntimeError("DB connection lost"))
    def test_unhandled_exception_returns_500(self, mock_get, client: TestClient):
        resp = client.get(
            "/api/v1/user/profile",
            headers={"Authorization": f"Bearer {_make_token()}"},
        )
        assert resp.status_code == 500
        data = resp.json()
        assert data["error"] == "Internal Server Error"
        assert "DB connection" not in data["detail"]  # No leak
        assert data["status"] == 500
