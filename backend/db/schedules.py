"""CRUD operations for briefing_schedules."""

from typing import Any

from db.client import get_supabase_client


def get_schedule(user_id: str) -> dict[str, Any] | None:
    """Fetch the briefing schedule for a user."""
    client = get_supabase_client()
    result = (
        client.table("briefing_schedules")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0] if result.data else None


def update_schedule(user_id: str, **fields: Any) -> dict[str, Any]:
    """Update schedule fields. Returns the updated schedule.

    Uses upsert to handle cases where the row doesn't exist yet
    (e.g., Google OAuth users where the trigger may not have fired).
    """
    client = get_supabase_client()

    # Log schedule changes
    current = get_schedule(user_id)
    if current:
        _log_schedule_changes(user_id, current, fields)

    fields["user_id"] = user_id

    result = (
        client.table("briefing_schedules")
        .upsert(fields, on_conflict="user_id")
        .execute()
    )
    return result.data[0]


def get_enabled_schedules() -> list[dict[str, Any]]:
    """Fetch all enabled schedules (for the scheduler to process)."""
    client = get_supabase_client()
    result = (
        client.table("briefing_schedules")
        .select("*, users(email, name)")
        .eq("enabled", True)
        .execute()
    )
    return result.data


def _log_schedule_changes(
    user_id: str,
    current: dict[str, Any],
    new_fields: dict[str, Any],
) -> None:
    """Log schedule changes to preference_history."""
    client = get_supabase_client()
    entries: list[dict[str, Any]] = []

    if "times" in new_fields and new_fields["times"] != current.get("times"):
        entries.append({
            "user_id": user_id,
            "action": "added",
            "field": "schedule",
            "value": f"times:{','.join(new_fields['times'])}",
        })

    if "timezone" in new_fields and new_fields["timezone"] != current.get("timezone"):
        entries.append({
            "user_id": user_id,
            "action": "added",
            "field": "schedule",
            "value": f"timezone:{new_fields['timezone']}",
        })

    if "enabled" in new_fields and new_fields["enabled"] != current.get("enabled"):
        action = "added" if new_fields["enabled"] else "removed"
        entries.append({
            "user_id": user_id,
            "action": action,
            "field": "schedule",
            "value": "enabled",
        })

    if entries:
        client.table("preference_history").insert(entries).execute()
