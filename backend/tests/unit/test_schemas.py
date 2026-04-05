"""Tests for pydantic request/response schemas — input validation."""

import pytest
from pydantic import ValidationError


# --- Chat schemas ---


class TestChatRequest:
    def test_valid_query(self):
        from schemas.chat import ChatRequest

        req = ChatRequest(query="What's the latest in AI?")
        assert req.query == "What's the latest in AI?"

    def test_strips_whitespace(self):
        from schemas.chat import ChatRequest

        req = ChatRequest(query="  hello  ")
        assert req.query == "hello"

    def test_empty_query_rejected(self):
        from schemas.chat import ChatRequest

        with pytest.raises(ValidationError, match="empty"):
            ChatRequest(query="   ")

    def test_too_long_query_rejected(self):
        from schemas.chat import ChatRequest

        with pytest.raises(ValidationError, match="2000"):
            ChatRequest(query="x" * 2001)

    def test_max_length_accepted(self):
        from schemas.chat import ChatRequest

        req = ChatRequest(query="x" * 2000)
        assert len(req.query) == 2000


class TestChatResponse:
    def test_response_with_sources(self):
        from schemas.chat import ChatResponse, ChatSource

        resp = ChatResponse(
            response="Here is the answer.",
            sources=[ChatSource(title="Article", url="https://a.com", source="newsapi")],
        )
        assert resp.response == "Here is the answer."
        assert len(resp.sources) == 1

    def test_response_no_sources(self):
        from schemas.chat import ChatResponse

        resp = ChatResponse(response="No sources found.")
        assert resp.sources == []


# --- Preferences schemas ---


class TestUpdatePreferencesRequest:
    def test_valid_depth_headlines(self):
        from schemas.preferences import UpdatePreferencesRequest

        req = UpdatePreferencesRequest(briefing_depth="headlines")
        assert req.briefing_depth == "headlines"

    def test_valid_depth_detailed(self):
        from schemas.preferences import UpdatePreferencesRequest

        req = UpdatePreferencesRequest(briefing_depth="detailed")
        assert req.briefing_depth == "detailed"

    def test_invalid_depth_rejected(self):
        from schemas.preferences import UpdatePreferencesRequest

        with pytest.raises(ValidationError, match="briefing_depth"):
            UpdatePreferencesRequest(briefing_depth="ultra")

    def test_all_none_is_valid(self):
        from schemas.preferences import UpdatePreferencesRequest

        req = UpdatePreferencesRequest()
        assert req.topics is None
        assert req.sources is None
        assert req.briefing_depth is None
        assert req.location is None

    def test_partial_update(self):
        from schemas.preferences import UpdatePreferencesRequest

        req = UpdatePreferencesRequest(topics=["ai", "tech"], location="Delhi")
        assert req.topics == ["ai", "tech"]
        assert req.location == "Delhi"
        assert req.briefing_depth is None


# --- Interests schemas ---


class TestAddInterestRequest:
    def test_valid_types(self):
        from schemas.interests import AddInterestRequest, VALID_INTEREST_TYPES

        for t in VALID_INTEREST_TYPES:
            req = AddInterestRequest(type=t, value="test-value")
            assert req.type == t

    def test_invalid_type_rejected(self):
        from schemas.interests import AddInterestRequest

        with pytest.raises(ValidationError, match="Interest type"):
            AddInterestRequest(type="invalid_type", value="test")

    def test_empty_value_rejected(self):
        from schemas.interests import AddInterestRequest

        with pytest.raises(ValidationError, match="empty"):
            AddInterestRequest(type="stock", value="   ")

    def test_too_long_value_rejected(self):
        from schemas.interests import AddInterestRequest

        with pytest.raises(ValidationError, match="200"):
            AddInterestRequest(type="stock", value="x" * 201)

    def test_strips_value(self):
        from schemas.interests import AddInterestRequest

        req = AddInterestRequest(type="stock", value="  RELIANCE  ")
        assert req.value == "RELIANCE"


# --- Schedule schemas ---


class TestUpdateScheduleRequest:
    def test_valid_times(self):
        from schemas.schedule import UpdateScheduleRequest

        req = UpdateScheduleRequest(times=["07:00", "18:30"])
        assert req.times == ["07:00", "18:30"]

    def test_invalid_time_format(self):
        from schemas.schedule import UpdateScheduleRequest

        with pytest.raises(ValidationError, match="HH:MM"):
            UpdateScheduleRequest(times=["7:00"])

    def test_invalid_time_value(self):
        from schemas.schedule import UpdateScheduleRequest

        with pytest.raises(ValidationError, match="Invalid time"):
            UpdateScheduleRequest(times=["25:00"])

    def test_empty_times_rejected(self):
        from schemas.schedule import UpdateScheduleRequest

        with pytest.raises(ValidationError, match="At least one"):
            UpdateScheduleRequest(times=[])

    def test_valid_timezone(self):
        from schemas.schedule import UpdateScheduleRequest

        req = UpdateScheduleRequest(timezone="Asia/Kolkata")
        assert req.timezone == "Asia/Kolkata"

    def test_invalid_timezone(self):
        from schemas.schedule import UpdateScheduleRequest

        with pytest.raises(ValidationError, match="Invalid timezone"):
            UpdateScheduleRequest(timezone="Fake/Zone")

    def test_none_times_accepted(self):
        from schemas.schedule import UpdateScheduleRequest

        req = UpdateScheduleRequest(times=None)
        assert req.times is None

    def test_midnight(self):
        from schemas.schedule import UpdateScheduleRequest

        req = UpdateScheduleRequest(times=["00:00"])
        assert req.times == ["00:00"]

    def test_end_of_day(self):
        from schemas.schedule import UpdateScheduleRequest

        req = UpdateScheduleRequest(times=["23:59"])
        assert req.times == ["23:59"]


# --- Briefing schemas ---


class TestBriefingSchemas:
    def test_briefing_summary(self):
        from schemas.briefings import BriefingSummary

        s = BriefingSummary(id="br-1", user_id="u-1", top_story="Big news")
        assert s.read is False
        assert s.item_count == 0

    def test_briefing_detail(self):
        from schemas.briefings import BriefingDetail

        d = BriefingDetail(
            id="br-1",
            user_id="u-1",
            content="# Briefing",
            sections=[{"key": "headlines", "title": "Headlines", "items": []}],
        )
        assert d.content == "# Briefing"
        assert len(d.sections) == 1

    def test_briefing_list_response(self):
        from schemas.briefings import BriefingListResponse, BriefingSummary

        resp = BriefingListResponse(
            briefings=[BriefingSummary(id="br-1", user_id="u-1")],
            total=1,
            limit=10,
            offset=0,
        )
        assert len(resp.briefings) == 1
        assert resp.total == 1


# --- Common schemas ---


class TestCommonSchemas:
    def test_error_response(self):
        from schemas.common import ErrorResponse

        err = ErrorResponse(error="Not Found", detail="Item not found", status=404)
        assert err.status == 404

    def test_message_response(self):
        from schemas.common import MessageResponse

        msg = MessageResponse(message="Success")
        assert msg.message == "Success"


# --- User schemas ---


class TestUserSchemas:
    def test_user_profile_defaults(self):
        from schemas.user import UserProfile

        profile = UserProfile(id="u-1", email="test@test.com")
        assert profile.onboarded is False
        assert profile.name is None
        assert profile.user_type is None

    def test_user_profile_full(self):
        from schemas.user import UserProfile

        profile = UserProfile(
            id="u-1",
            email="test@test.com",
            name="Test User",
            user_type=["ai_tech"],
            onboarded=True,
            last_active_at="2026-04-04T00:00:00Z",
            created_at="2026-04-01T00:00:00Z",
        )
        assert profile.onboarded is True
        assert profile.user_type == ["ai_tech"]
