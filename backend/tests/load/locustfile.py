"""Load tests for the Saar API.

Run:
  locust -f tests/load/locustfile.py --headless -u 100 -r 10 -t 60s --host http://localhost:8000

Or with web UI:
  locust -f tests/load/locustfile.py --host http://localhost:8000
"""

import os
import time

import jwt
from locust import HttpUser, between, task, tag

JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")


def _make_token(user_id: str = "load-test-user") -> str:
    """Create a valid JWT for load testing."""
    return jwt.encode(
        {
            "sub": user_id,
            "email": "loadtest@saar.local",
            "role": "authenticated",
            "aud": "authenticated",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        },
        JWT_SECRET,
        algorithm="HS256",
    )


class HealthCheckUser(HttpUser):
    """Simulates lightweight health check traffic."""

    wait_time = between(0.1, 0.5)
    weight = 3

    @task
    @tag("health")
    def health(self):
        self.client.get("/health")


class BriefingUser(HttpUser):
    """Simulates a user checking their briefings."""

    wait_time = between(1, 3)
    weight = 5

    def on_start(self):
        self.token = _make_token(f"briefing-user-{self.environment.runner.user_count}")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    @tag("briefings")
    def list_briefings(self):
        self.client.get(
            "/api/v1/briefings",
            headers=self.headers,
            name="/api/v1/briefings",
        )

    @task(2)
    @tag("preferences")
    def get_preferences(self):
        self.client.get(
            "/api/v1/preferences",
            headers=self.headers,
            name="/api/v1/preferences",
        )

    @task(1)
    @tag("schedule")
    def get_schedule(self):
        self.client.get(
            "/api/v1/schedule",
            headers=self.headers,
            name="/api/v1/schedule",
        )

    @task(1)
    @tag("interests")
    def list_interests(self):
        self.client.get(
            "/api/v1/interests",
            headers=self.headers,
            name="/api/v1/interests",
        )

    @task(1)
    @tag("profile")
    def get_profile(self):
        self.client.get(
            "/api/v1/user/profile",
            headers=self.headers,
            name="/api/v1/user/profile",
        )


class ChatUser(HttpUser):
    """Simulates a user using the chat feature."""

    wait_time = between(2, 5)
    weight = 2

    def on_start(self):
        self.token = _make_token(f"chat-user-{self.environment.runner.user_count}")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    @task(2)
    @tag("chat")
    def get_chat_history(self):
        self.client.get(
            "/api/v1/chat/history",
            headers=self.headers,
            name="/api/v1/chat/history",
        )

    @task(1)
    @tag("chat", "write")
    def send_message(self):
        self.client.post(
            "/api/v1/chat",
            json={"query": "What's the latest in AI?"},
            headers=self.headers,
            name="/api/v1/chat",
        )
