"""CRUD operations for the briefings table."""

from datetime import datetime, timezone
from typing import Any

from db.client import get_supabase_client


def create_briefing(
    user_id: str,
    content: str,
    sections: list[dict[str, Any]],
    top_story: str,
    item_count: int,
    alert_count: int,
) -> dict[str, Any]:
    """Create a new briefing. Returns the created briefing."""
    client = get_supabase_client()
    result = (
        client.table("briefings")
        .insert({
            "user_id": user_id,
            "content": content,
            "sections": sections,
            "top_story": top_story,
            "item_count": item_count,
            "alert_count": alert_count,
        })
        .execute()
    )
    return result.data[0]


def get_briefing(briefing_id: str) -> dict[str, Any] | None:
    """Fetch a single briefing by ID."""
    client = get_supabase_client()
    result = (
        client.table("briefings")
        .select("*")
        .eq("id", briefing_id)
        .execute()
    )
    return result.data[0] if result.data else None


def get_user_briefings(
    user_id: str, limit: int = 20, offset: int = 0
) -> list[dict[str, Any]]:
    """Fetch briefings for a user, most recent first."""
    client = get_supabase_client()
    result = (
        client.table("briefings")
        .select("*")
        .eq("user_id", user_id)
        .order("generated_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return result.data


def get_latest_briefing(user_id: str) -> dict[str, Any] | None:
    """Fetch the most recent briefing for a user."""
    client = get_supabase_client()
    result = (
        client.table("briefings")
        .select("*")
        .eq("user_id", user_id)
        .order("generated_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def mark_as_read(briefing_id: str) -> dict[str, Any]:
    """Mark a briefing as read."""
    client = get_supabase_client()
    result = (
        client.table("briefings")
        .update({
            "read": True,
            "read_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", briefing_id)
        .execute()
    )
    return result.data[0]
