"""Tests for authentication middleware and routes."""

import os
import time

import jwt
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Create a FastAPI test client."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

    from main import app
    return TestClient(app)


@pytest.fixture(scope="module")
def jwt_secret():
    """Get the JWT secret from env."""
    secret = os.environ.get("SUPABASE_JWT_SECRET", "")
    if not secret:
        pytest.skip("SUPABASE_JWT_SECRET not set")
    return secret


def _make_token(secret: str, payload_overrides: dict | None = None) -> str:
    """Helper to create a test JWT."""
    payload = {
        "sub": "00000000-0000-0000-0000-000000000001",
        "email": "test@saar.local",
        "role": "authenticated",
        "aud": "authenticated",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    if payload_overrides:
        payload.update(payload_overrides)
    return jwt.encode(payload, secret, algorithm="HS256")


class TestHealthEndpoint:
    """Health endpoint should be accessible without auth."""

    def test_health_no_auth(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestProtectedEndpoints:
    """Protected endpoints require valid JWT."""

    def test_me_without_token_returns_401(self, client: TestClient):
        response = client.get("/me")
        assert response.status_code in (401, 403)

    def test_me_with_invalid_token_returns_401(self, client: TestClient):
        response = client.get(
            "/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_me_with_valid_token(
        self, client: TestClient, jwt_secret: str
    ):
        token = _make_token(jwt_secret)
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "00000000-0000-0000-0000-000000000001"
        assert data["email"] == "test@saar.local"

    def test_me_with_expired_token_returns_401(
        self, client: TestClient, jwt_secret: str
    ):
        token = _make_token(jwt_secret, {"exp": int(time.time()) - 100})
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_me_with_wrong_secret_returns_401(self, client: TestClient):
        token = _make_token("wrong-secret-key")
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401


class TestAuthRoutes:
    """Auth routes should be accessible without JWT."""

    def test_magic_link_endpoint_exists(self, client: TestClient):
        response = client.post(
            "/auth/magic-link",
            json={"email": "test@example.com"},
        )
        # Should not be 404 (route exists) or 403 (no auth needed)
        assert response.status_code != 404
        assert response.status_code != 403

    def test_magic_link_invalid_email(self, client: TestClient):
        response = client.post(
            "/auth/magic-link",
            json={"email": "not-an-email"},
        )
        assert response.status_code == 422  # Validation error

    def test_logout_endpoint(self, client: TestClient):
        response = client.post("/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

    def test_refresh_endpoint_exists(self, client: TestClient):
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "fake-token"},
        )
        # Should not be 404 (route exists)
        assert response.status_code != 404
