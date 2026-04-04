"""CRUD operations for the chat_history table."""

from typing import Any

from db.client import get_supabase_client


def create_chat_entry(
    user_id: str,
    query: str,
    response: str,
    sources: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Save a chat exchange. Returns the created entry."""
    client = get_supabase_client()
    result = (
        client.table("chat_history")
        .insert({
            "user_id": user_id,
            "query": query,
            "response": response,
            "sources": sources or [],
        })
        .execute()
    )
    return result.data[0]


def get_chat_history(
    user_id: str, limit: int = 50
) -> list[dict[str, Any]]:
    """Fetch recent chat history for a user, oldest first."""
    client = get_supabase_client()
    result = (
        client.table("chat_history")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    # Reverse so oldest is first (conversation order)
    return list(reversed(result.data))


def get_recent_context(
    user_id: str, limit: int = 5
) -> list[dict[str, Any]]:
    """Fetch last N chat entries for LLM context window."""
    client = get_supabase_client()
    result = (
        client.table("chat_history")
        .select("query, response")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return list(reversed(result.data))
