"""Briefing scheduler — APScheduler cron jobs per user."""

import logging
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from sources.registry import fetch_all_sources
from sources.types import SourceItem
from filters.pipeline import run_filter_pipeline, PipelineConfig
from briefing.summarizer import summarize_items
from briefing.generator import generate_briefing, store_briefing

logger = logging.getLogger(__name__)

# Module-level scheduler instance
_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


def _make_job_id(user_id: str, time_str: str) -> str:
    """Create a unique job ID for a user + time combination."""
    return f"briefing_{user_id}_{time_str}"


async def generate_user_briefing(
    user_id: str,
    user_types: list[str],
    topics: list[str],
    sources: list[str],
    interests: list[str],
    location: str,
    briefing_depth: str,
    watchlist_symbols: list[str] | None = None,
) -> dict[str, Any] | None:
    """Full pipeline: fetch → filter → summarize → generate → store.

    Returns the stored briefing DB record, or None on failure.
    """
    logger.warning("Generating briefing for user %s | sources=%s | topics=%s", user_id, sources, topics)

    try:
        # Stage 1: Fetch from all configured sources
        source_results = await fetch_all_sources(
            source_names=sources,
            location=location,
            user_type=user_types[0] if user_types else "general",
            watchlist_symbols=watchlist_symbols,
        )

        # Flatten all items from all sources
        all_items: list[SourceItem] = []
        for result in source_results:
            if result.error:
                logger.warning("Source '%s' failed: %s", result.source_name, result.error)
            all_items.extend(result.items)

        logger.warning("Fetched %d items from %d sources", len(all_items), len(source_results))

        if not all_items:
            logger.warning("No items fetched for user %s — skipping briefing", user_id)
            return None

        # Stage 2: Filter pipeline
        mode = "headlines" if briefing_depth == "headlines" else "detailed"
        pipeline_config = PipelineConfig(
            topics=topics,
            interests=interests,
            mode=mode,
        )
        pipeline_result = await run_filter_pipeline(all_items, pipeline_config)

        logger.info(
            "Pipeline: %d → %d items for user %s",
            len(all_items),
            len(pipeline_result.items),
            user_id,
        )

        if not pipeline_result.items:
            logger.warning("All items filtered out for user %s", user_id)
            return None

        # Stage 3: Summarize
        summary_result = await summarize_items(
            pipeline_result.items,
            mode=mode,
        )

        # Stage 4: Generate briefing
        briefing = generate_briefing(
            user_id=user_id,
            summary_result=summary_result,
            user_types=user_types,
        )

        # Stage 5: Store in database
        db_record = store_briefing(briefing)
        logger.info("Briefing stored for user %s (id=%s)", user_id, db_record.get("id"))

        return db_record

    except Exception as e:
        logger.error("Briefing generation failed for user %s: %s", user_id, e, exc_info=True)
        return None


def _parse_time(time_str: str) -> tuple[int, int]:
    """Parse a time string like '08:00' into (hour, minute)."""
    parts = time_str.split(":")
    return int(parts[0]), int(parts[1])


def validate_timezone(tz_name: str) -> bool:
    """Check if a timezone name is valid."""
    if not tz_name:
        return False
    try:
        ZoneInfo(tz_name)
        return True
    except (ZoneInfoNotFoundError, KeyError, ValueError):
        return False


def schedule_user_briefing(
    scheduler: AsyncIOScheduler,
    user_id: str,
    schedule: dict[str, Any],
    preferences: dict[str, Any],
    interest_values: list[str],
) -> list[str]:
    """Add cron jobs for a user's briefing schedule.

    Args:
        scheduler: The APScheduler instance.
        user_id: The user ID.
        schedule: Schedule dict with keys: times, timezone, enabled.
        preferences: User preferences dict with keys: user_types, topics, sources, location, briefing_depth.
        interest_values: List of watchlist interest values.

    Returns:
        List of job IDs that were added.
    """
    if not schedule.get("enabled", False):
        logger.debug("Schedule disabled for user %s — skipping", user_id)
        return []

    tz_name = schedule.get("timezone", "Asia/Kolkata")
    if not validate_timezone(tz_name):
        logger.error("Invalid timezone '%s' for user %s", tz_name, user_id)
        return []

    times = schedule.get("times", [])
    if not times:
        logger.debug("No scheduled times for user %s", user_id)
        return []

    job_ids: list[str] = []

    for time_str in times:
        hour, minute = _parse_time(time_str)
        job_id = _make_job_id(user_id, time_str)

        # Remove existing job if present
        existing = scheduler.get_job(job_id)
        if existing:
            scheduler.remove_job(job_id)

        user_types = preferences.get("user_types", ["general"])
        topics = preferences.get("topics", [])
        sources = preferences.get("sources", [])
        location = preferences.get("location", "Mumbai")
        briefing_depth = preferences.get("briefing_depth", "detailed")

        # Extract stock symbols from interests for watchlist
        watchlist_symbols = [v for v in interest_values if ":" not in v] if interest_values else None

        scheduler.add_job(
            generate_user_briefing,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=tz_name),
            id=job_id,
            args=[
                user_id,
                user_types,
                topics,
                sources,
                interest_values,
                location,
                briefing_depth,
                watchlist_symbols,
            ],
            replace_existing=True,
            name=f"Briefing for {user_id} at {time_str}",
        )

        job_ids.append(job_id)
        logger.info("Scheduled briefing for user %s at %s %s", user_id, time_str, tz_name)

    return job_ids


def remove_user_jobs(scheduler: AsyncIOScheduler, user_id: str) -> int:
    """Remove all briefing jobs for a user. Returns count of removed jobs."""
    removed = 0
    for job in scheduler.get_jobs():
        if job.id.startswith(f"briefing_{user_id}_"):
            scheduler.remove_job(job.id)
            removed += 1
    if removed:
        logger.info("Removed %d jobs for user %s", removed, user_id)
    return removed


async def load_all_schedules(scheduler: AsyncIOScheduler) -> int:
    """Load all enabled schedules from DB and create jobs.

    Called on app startup. Returns count of jobs created.
    """
    from db.schedules import get_enabled_schedules
    from db.preferences import get_preferences
    from db.interests import get_interests

    schedules = get_enabled_schedules()
    total_jobs = 0

    for schedule in schedules:
        user_id = schedule["user_id"]

        preferences = get_preferences(user_id)
        if not preferences:
            logger.warning("No preferences found for user %s — skipping schedule", user_id)
            continue

        interests = get_interests(user_id)
        interest_values = [i["value"] for i in interests]

        job_ids = schedule_user_briefing(
            scheduler=scheduler,
            user_id=user_id,
            schedule=schedule,
            preferences=preferences,
            interest_values=interest_values,
        )
        total_jobs += len(job_ids)

    logger.info("Loaded %d briefing jobs from %d schedules", total_jobs, len(schedules))
    return total_jobs
