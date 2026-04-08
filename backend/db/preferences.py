"""CRUD operations for user_preferences + preference_history logging."""

from datetime import datetime, timezone
from typing import Any

from db.client import get_supabase_client


def get_preferences(user_id: str) -> dict[str, Any] | None:
    """Fetch preferences for a user."""
    client = get_supabase_client()
    result = (
        client.table("user_preferences")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0] if result.data else None


def update_preferences(
    user_id: str, **fields: Any
) -> dict[str, Any]:
    """Update preferences and log changes to preference_history.

    Uses upsert to handle cases where the row doesn't exist yet
    (e.g., Google OAuth users where the trigger may not have fired).
    Returns the updated preferences.
    """
    client = get_supabase_client()

    current = get_preferences(user_id)

    # Log changes to preference_history
    if current:
        _log_preference_changes(user_id, current, fields)

    fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    fields["user_id"] = user_id

    result = (
        client.table("user_preferences")
        .upsert(fields, on_conflict="user_id")
        .execute()
    )
    return result.data[0]


def _log_preference_changes(
    user_id: str,
    current: dict[str, Any],
    new_fields: dict[str, Any],
) -> None:
    """Compare old and new preferences, log additions and removals."""
    client = get_supabase_client()
    history_entries: list[dict[str, Any]] = []

    for field_name in ("topics", "sources"):
        if field_name not in new_fields:
            continue

        old_values = set(current.get(field_name, []) or [])
        new_values = set(new_fields[field_name] or [])

        for added in new_values - old_values:
            history_entries.append({
                "user_id": user_id,
                "action": "added",
                "field": field_name.rstrip("s"),  # "topics" -> "topic"
                "value": added,
            })

        for removed in old_values - new_values:
            history_entries.append({
                "user_id": user_id,
                "action": "removed",
                "field": field_name.rstrip("s"),
                "value": removed,
            })

    # Log scalar field changes
    for field_name in ("briefing_depth", "location"):
        if field_name not in new_fields:
            continue
        old_val = current.get(field_name)
        new_val = new_fields[field_name]
        if old_val != new_val:
            history_entries.append({
                "user_id": user_id,
                "action": "added",
                "field": field_name,
                "value": str(new_val),
            })

    if history_entries:
        client.table("preference_history").insert(history_entries).execute()


def get_preference_history(
    user_id: str, limit: int = 50
) -> list[dict[str, Any]]:
    """Fetch preference change history for a user."""
    client = get_supabase_client()
    result = (
        client.table("preference_history")
        .select("*")
        .eq("user_id", user_id)
        .order("changed_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data
