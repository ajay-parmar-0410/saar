"""CRUD operations for the users table."""

from datetime import datetime, timezone
from typing import Any

from db.client import get_supabase_client


def get_user(user_id: str) -> dict[str, Any] | None:
    """Fetch a user by ID."""
    client = get_supabase_client()
    result = client.table("users").select("*").eq("id", user_id).execute()
    return result.data[0] if result.data else None


def update_user(user_id: str, **fields: Any) -> dict[str, Any]:
    """Update user fields. Returns the updated user.

    Uses upsert to handle cases where the row doesn't exist yet
    (e.g., Google OAuth users where the trigger may not have fired).
    """
    client = get_supabase_client()
    fields["id"] = user_id

    result = (
        client.table("users")
        .upsert(fields, on_conflict="id")
        .execute()
    )
    return result.data[0]


def update_last_active(user_id: str) -> None:
    """Set last_active_at to now."""
    client = get_supabase_client()
    (
        client.table("users")
        .update({"last_active_at": datetime.now(timezone.utc).isoformat()})
        .eq("id", user_id)
        .execute()
    )


def delete_user(user_id: str) -> None:
    """Delete a user and all associated data (cascade), including the Supabase Auth user."""
    client = get_supabase_client()
    # Delete app data first (cascade handles related tables)
    client.table("users").delete().eq("id", user_id).execute()
    # Delete the Supabase Auth user so they can't log in again
    client.auth.admin.delete_user(user_id)
