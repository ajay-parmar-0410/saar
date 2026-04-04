"""Tests for all database CRUD operations."""

import pytest


class TestUsers:
    """Tests for db.users module."""

    def test_get_user_returns_auto_created_profile(self, test_user_id: str):
        from db.users import get_user

        user = get_user(test_user_id)
        assert user is not None
        assert user["id"] == test_user_id
        assert user["name"] == "Test User"

    def test_update_user(self, test_user_id: str):
        from db.users import get_user, update_user

        updated = update_user(test_user_id, name="Updated Name")
        assert updated["name"] == "Updated Name"

        fetched = get_user(test_user_id)
        assert fetched["name"] == "Updated Name"

        # Restore
        update_user(test_user_id, name="Test User")

    def test_update_user_type(self, test_user_id: str):
        from db.users import get_user, update_user

        updated = update_user(
            test_user_id, user_type=["ai_tech", "trader"]
        )
        assert set(updated["user_type"]) == {"ai_tech", "trader"}

        fetched = get_user(test_user_id)
        assert set(fetched["user_type"]) == {"ai_tech", "trader"}

    def test_update_last_active(self, test_user_id: str):
        from db.users import get_user, update_last_active

        before = get_user(test_user_id)
        update_last_active(test_user_id)
        after = get_user(test_user_id)
        assert after["last_active_at"] >= before["last_active_at"]

    def test_get_nonexistent_user_returns_none(self):
        from db.users import get_user

        result = get_user("00000000-0000-0000-0000-000000000000")
        assert result is None


class TestPreferences:
    """Tests for db.preferences module."""

    def test_auto_created_preferences(self, test_user_id: str):
        from db.preferences import get_preferences

        prefs = get_preferences(test_user_id)
        assert prefs is not None
        assert prefs["user_id"] == test_user_id
        assert prefs["briefing_depth"] == "detailed"
        assert prefs["location"] == "Mumbai"

    def test_update_topics_and_sources(self, test_user_id: str):
        from db.preferences import get_preferences, update_preferences

        updated = update_preferences(
            test_user_id,
            topics=["ai", "markets", "weather"],
            sources=["github", "reddit"],
        )
        assert set(updated["topics"]) == {"ai", "markets", "weather"}
        assert set(updated["sources"]) == {"github", "reddit"}

    def test_update_logs_to_preference_history(self, test_user_id: str):
        from db.preferences import (
            get_preference_history,
            update_preferences,
        )

        update_preferences(
            test_user_id,
            topics=["ai", "markets", "weather", "crypto"],
        )

        history = get_preference_history(test_user_id)
        topic_entries = [h for h in history if h["field"] == "topic"]
        assert len(topic_entries) > 0
        values = {h["value"] for h in topic_entries}
        assert "crypto" in values

    def test_update_briefing_depth(self, test_user_id: str):
        from db.preferences import get_preferences, update_preferences

        update_preferences(test_user_id, briefing_depth="headlines")
        prefs = get_preferences(test_user_id)
        assert prefs["briefing_depth"] == "headlines"

        # Restore
        update_preferences(test_user_id, briefing_depth="detailed")

    def test_update_location(self, test_user_id: str):
        from db.preferences import get_preferences, update_preferences

        update_preferences(test_user_id, location="Delhi")
        prefs = get_preferences(test_user_id)
        assert prefs["location"] == "Delhi"

        # Restore
        update_preferences(test_user_id, location="Mumbai")


class TestInterests:
    """Tests for db.interests module (watchlist)."""

    def test_add_and_get_interest(self, test_user_id: str):
        from db.interests import add_interest, get_interests

        item = add_interest(test_user_id, "stock", "RELIANCE")
        assert item["type"] == "stock"
        assert item["value"] == "RELIANCE"
        assert item["user_id"] == test_user_id

        all_items = get_interests(test_user_id)
        values = {i["value"] for i in all_items}
        assert "RELIANCE" in values

    def test_get_interests_by_type(self, test_user_id: str):
        from db.interests import add_interest, get_interests_by_type

        add_interest(test_user_id, "repo", "langchain-ai/langchain")
        add_interest(test_user_id, "subreddit", "r/LocalLLaMA")

        repos = get_interests_by_type(test_user_id, "repo")
        assert any(i["value"] == "langchain-ai/langchain" for i in repos)

        subs = get_interests_by_type(test_user_id, "subreddit")
        assert any(i["value"] == "r/LocalLLaMA" for i in subs)

    def test_remove_interest(self, test_user_id: str):
        from db.interests import (
            add_interest,
            get_interests,
            remove_interest,
        )

        item = add_interest(test_user_id, "keyword", "LLM")
        item_id = item["id"]

        remove_interest(test_user_id, item_id)

        all_items = get_interests(test_user_id)
        ids = {i["id"] for i in all_items}
        assert item_id not in ids

    def test_remove_logs_to_preference_history(self, test_user_id: str):
        from db.interests import add_interest, remove_interest
        from db.preferences import get_preference_history

        item = add_interest(test_user_id, "stock", "TCS")
        remove_interest(test_user_id, item["id"])

        history = get_preference_history(test_user_id)
        removed = [
            h for h in history
            if h["action"] == "removed"
            and h["field"] == "interest"
            and "TCS" in h["value"]
        ]
        assert len(removed) > 0


class TestSchedules:
    """Tests for db.schedules module."""

    def test_auto_created_schedule(self, test_user_id: str):
        from db.schedules import get_schedule

        schedule = get_schedule(test_user_id)
        assert schedule is not None
        assert schedule["user_id"] == test_user_id
        assert schedule["timezone"] == "Asia/Kolkata"
        assert schedule["enabled"] is True

    def test_update_schedule_times(self, test_user_id: str):
        from db.schedules import get_schedule, update_schedule

        updated = update_schedule(
            test_user_id, times=["07:00", "18:00"]
        )
        assert set(updated["times"]) == {"07:00", "18:00"}

        fetched = get_schedule(test_user_id)
        assert set(fetched["times"]) == {"07:00", "18:00"}

    def test_disable_schedule(self, test_user_id: str):
        from db.schedules import get_schedule, update_schedule

        update_schedule(test_user_id, enabled=False)
        schedule = get_schedule(test_user_id)
        assert schedule["enabled"] is False

        # Restore
        update_schedule(test_user_id, enabled=True)

    def test_get_enabled_schedules(self, test_user_id: str):
        from db.schedules import get_enabled_schedules, update_schedule

        update_schedule(test_user_id, enabled=True)
        schedules = get_enabled_schedules()
        assert any(s["user_id"] == test_user_id for s in schedules)


class TestBriefings:
    """Tests for db.briefings module."""

    def test_create_and_get_briefing(self, test_user_id: str):
        from db.briefings import create_briefing, get_briefing

        briefing = create_briefing(
            user_id=test_user_id,
            content="# Today's Briefing\nMarket up 2%",
            sections=[{"title": "Markets", "items": []}],
            top_story="Nifty hits all-time high",
            item_count=5,
            alert_count=1,
        )
        assert briefing["user_id"] == test_user_id
        assert briefing["top_story"] == "Nifty hits all-time high"
        assert briefing["read"] is False

        fetched = get_briefing(briefing["id"])
        assert fetched is not None
        assert fetched["content"] == "# Today's Briefing\nMarket up 2%"

    def test_get_user_briefings_ordered(self, test_user_id: str):
        from db.briefings import create_briefing, get_user_briefings

        create_briefing(
            user_id=test_user_id,
            content="Briefing 2",
            sections=[],
            top_story="Story 2",
            item_count=3,
            alert_count=0,
        )

        briefings = get_user_briefings(test_user_id)
        assert len(briefings) >= 2
        # Most recent first
        assert briefings[0]["generated_at"] >= briefings[1]["generated_at"]

    def test_get_latest_briefing(self, test_user_id: str):
        from db.briefings import get_latest_briefing

        latest = get_latest_briefing(test_user_id)
        assert latest is not None
        assert latest["user_id"] == test_user_id

    def test_mark_as_read(self, test_user_id: str):
        from db.briefings import get_latest_briefing, mark_as_read

        latest = get_latest_briefing(test_user_id)
        updated = mark_as_read(latest["id"])
        assert updated["read"] is True
        assert updated["read_at"] is not None


class TestChat:
    """Tests for db.chat module."""

    def test_create_and_get_chat(self, test_user_id: str):
        from db.chat import create_chat_entry, get_chat_history

        entry = create_chat_entry(
            user_id=test_user_id,
            query="What happened with Nifty today?",
            response="Nifty rose 1.5% driven by banking stocks.",
            sources=[
                {"title": "ET Markets", "url": "https://example.com"}
            ],
        )
        assert entry["query"] == "What happened with Nifty today?"
        assert len(entry["sources"]) == 1

        history = get_chat_history(test_user_id)
        assert any(h["id"] == entry["id"] for h in history)

    def test_chat_history_order(self, test_user_id: str):
        from db.chat import create_chat_entry, get_chat_history

        create_chat_entry(
            user_id=test_user_id,
            query="Follow up question",
            response="Follow up answer",
        )

        history = get_chat_history(test_user_id)
        assert len(history) >= 2
        # Oldest first (conversation order)
        assert history[0]["created_at"] <= history[-1]["created_at"]

    def test_get_recent_context(self, test_user_id: str):
        from db.chat import get_recent_context

        context = get_recent_context(test_user_id, limit=2)
        assert len(context) <= 2
        assert all("query" in c and "response" in c for c in context)
        # Should not include full fields like sources
        assert all("sources" not in c for c in context)
