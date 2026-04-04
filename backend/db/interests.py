"""CRUD operations for user_interests (watchlist)."""

from typing import Any

from db.client import get_supabase_client


def get_interests(user_id: str) -> list[dict[str, Any]]:
    """Fetch all watchlist items for a user."""
    client = get_supabase_client()
    result = (
        client.table("user_interests")
        .select("*")
        .eq("user_id", user_id)
        .order("added_at", desc=True)
        .execute()
    )
    return result.data


def get_interests_by_type(
    user_id: str, interest_type: str
) -> list[dict[str, Any]]:
    """Fetch watchlist items filtered by type."""
    client = get_supabase_client()
    result = (
        client.table("user_interests")
        .select("*")
        .eq("user_id", user_id)
        .eq("type", interest_type)
        .order("added_at", desc=True)
        .execute()
    )
    return result.data


def add_interest(
    user_id: str, interest_type: str, value: str
) -> dict[str, Any]:
    """Add a watchlist item. Returns the created item."""
    client = get_supabase_client()
    result = (
        client.table("user_interests")
        .insert({
            "user_id": user_id,
            "type": interest_type,
            "value": value,
        })
        .execute()
    )

    # Log to preference history
    client.table("preference_history").insert({
        "user_id": user_id,
        "action": "added",
        "field": "interest",
        "value": f"{interest_type}:{value}",
    }).execute()

    return result.data[0]


def remove_interest(user_id: str, interest_id: str) -> None:
    """Remove a watchlist item by ID."""
    client = get_supabase_client()

    # Fetch before delete for history logging
    existing = (
        client.table("user_interests")
        .select("type, value")
        .eq("id", interest_id)
        .eq("user_id", user_id)
        .execute()
    )

    client.table("user_interests").delete().eq("id", interest_id).eq(
        "user_id", user_id
    ).execute()

    if existing.data:
        item = existing.data[0]
        client.table("preference_history").insert({
            "user_id": user_id,
            "action": "removed",
            "field": "interest",
            "value": f"{item['type']}:{item['value']}",
        }).execute()
