"""Tests for briefing scheduler."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from briefing.scheduler import (
    validate_timezone,
    _make_job_id,
    _parse_time,
    schedule_user_briefing,
    remove_user_jobs,
)


class TestValidateTimezone:
    def test_valid_timezone(self):
        assert validate_timezone("Asia/Kolkata") is True

    def test_valid_utc(self):
        assert validate_timezone("UTC") is True

    def test_valid_us_timezone(self):
        assert validate_timezone("America/New_York") is True

    def test_invalid_timezone(self):
        assert validate_timezone("Invalid/Timezone") is False

    def test_empty_string(self):
        assert validate_timezone("") is False


class TestParseTime:
    def test_morning(self):
        assert _parse_time("08:00") == (8, 0)

    def test_evening(self):
        assert _parse_time("18:30") == (18, 30)

    def test_midnight(self):
        assert _parse_time("00:00") == (0, 0)


class TestMakeJobId:
    def test_format(self):
        job_id = _make_job_id("user-123", "08:00")
        assert job_id == "briefing_user-123_08:00"


class TestScheduleUserBriefing:
    def test_disabled_schedule_returns_empty(self):
        scheduler = AsyncIOScheduler()
        result = schedule_user_briefing(
            scheduler=scheduler,
            user_id="user-1",
            schedule={"enabled": False, "times": ["08:00"], "timezone": "UTC"},
            preferences={"topics": [], "sources": [], "user_types": ["general"]},
            interest_values=[],
        )
        assert result == []

    def test_invalid_timezone_returns_empty(self):
        scheduler = AsyncIOScheduler()
        result = schedule_user_briefing(
            scheduler=scheduler,
            user_id="user-1",
            schedule={"enabled": True, "times": ["08:00"], "timezone": "Invalid/TZ"},
            preferences={"topics": [], "sources": [], "user_types": ["general"]},
            interest_values=[],
        )
        assert result == []

    def test_no_times_returns_empty(self):
        scheduler = AsyncIOScheduler()
        result = schedule_user_briefing(
            scheduler=scheduler,
            user_id="user-1",
            schedule={"enabled": True, "times": [], "timezone": "UTC"},
            preferences={"topics": [], "sources": [], "user_types": ["general"]},
            interest_values=[],
        )
        assert result == []

    def test_adds_job_for_each_time(self):
        scheduler = AsyncIOScheduler()
        result = schedule_user_briefing(
            scheduler=scheduler,
            user_id="user-1",
            schedule={"enabled": True, "times": ["08:00", "18:00"], "timezone": "Asia/Kolkata"},
            preferences={
                "topics": ["tech"],
                "sources": ["newsapi"],
                "user_types": ["general"],
                "location": "Mumbai",
                "briefing_depth": "detailed",
            },
            interest_values=["RELIANCE"],
        )
        assert len(result) == 2
        assert "briefing_user-1_08:00" in result
        assert "briefing_user-1_18:00" in result

        # Verify jobs exist in scheduler
        jobs = scheduler.get_jobs()
        assert len(jobs) == 2

    def test_replaces_existing_job(self):
        scheduler = AsyncIOScheduler()
        schedule = {"enabled": True, "times": ["08:00"], "timezone": "UTC"}
        prefs = {"topics": [], "sources": [], "user_types": ["general"]}

        # Schedule twice
        schedule_user_briefing(scheduler, "user-1", schedule, prefs, [])
        schedule_user_briefing(scheduler, "user-1", schedule, prefs, [])

        # Should still have only 1 job
        jobs = scheduler.get_jobs()
        assert len(jobs) == 1


class TestRemoveUserJobs:
    def test_removes_all_user_jobs(self):
        scheduler = AsyncIOScheduler()
        schedule = {"enabled": True, "times": ["08:00", "18:00"], "timezone": "UTC"}
        prefs = {"topics": [], "sources": [], "user_types": ["general"]}

        schedule_user_briefing(scheduler, "user-1", schedule, prefs, [])
        assert len(scheduler.get_jobs()) == 2

        removed = remove_user_jobs(scheduler, "user-1")
        assert removed == 2
        assert len(scheduler.get_jobs()) == 0

    def test_does_not_remove_other_user_jobs(self):
        scheduler = AsyncIOScheduler()
        schedule = {"enabled": True, "times": ["08:00"], "timezone": "UTC"}
        prefs = {"topics": [], "sources": [], "user_types": ["general"]}

        schedule_user_briefing(scheduler, "user-1", schedule, prefs, [])
        schedule_user_briefing(scheduler, "user-2", schedule, prefs, [])

        remove_user_jobs(scheduler, "user-1")
        jobs = scheduler.get_jobs()
        assert len(jobs) == 1
        assert jobs[0].id.startswith("briefing_user-2_")

    def test_no_jobs_returns_zero(self):
        scheduler = AsyncIOScheduler()
        assert remove_user_jobs(scheduler, "user-1") == 0
