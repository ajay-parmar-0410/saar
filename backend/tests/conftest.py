"""Shared test fixtures for database tests."""

import os
import sys
import uuid

import pytest
from dotenv import load_dotenv

# Ensure backend is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


@pytest.fixture(scope="session")
def test_user_id():
    """Create a test user in Supabase Auth, yield the ID, then delete."""
    from db.client import get_supabase_client

    client = get_supabase_client()
    email = f"test-{uuid.uuid4().hex[:8]}@saar-test.local"
    password = f"TestPass!{uuid.uuid4().hex[:12]}"

    # Create user via Supabase Auth admin API
    auth_response = client.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True,
        "user_metadata": {"full_name": "Test User"},
    })
    user_id = auth_response.user.id

    yield user_id

    # Cleanup: delete auth user (cascades to all tables)
    try:
        client.auth.admin.delete_user(user_id)
    except Exception:
        pass
