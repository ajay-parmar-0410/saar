"""Quality filter — rule-based filtering for low-quality content."""

import logging
import re

from sources.types import SourceItem

logger = logging.getLogger(__name__)

# Minimum content length (title + summary combined)
MIN_CONTENT_LENGTH = 30

# Reddit upvote thresholds by source type
REDDIT_MIN_UPVOTES = 50

# Clickbait heuristic patterns (case-insensitive)
CLICKBAIT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"you won'?t believe", re.IGNORECASE),
    re.compile(r"this (?:one )?(?:simple |weird )?trick", re.IGNORECASE),
    re.compile(r"doctors (?:are )?(?:shocked|hate)", re.IGNORECASE),
    re.compile(r"what happens next (?:will |might )?shock", re.IGNORECASE),
    re.compile(r"(?:top|best) \d+ (?:reasons|ways|things)", re.IGNORECASE),
    re.compile(r"is (?:finally )?dead", re.IGNORECASE),
    re.compile(r"you need to (?:see|know|read) this", re.IGNORECASE),
    re.compile(r"(?:jaw[- ]?dropping|mind[- ]?blowing|insane)", re.IGNORECASE),
    re.compile(r"🚨|💥|🤯|😱", re.IGNORECASE),
)

# Sources considered reputable (skip reputation check for these)
REPUTABLE_SOURCES = frozenset({
    "newsapi", "google_news", "arxiv", "github", "hackernews",
    "yahoo_finance", "moneycontrol", "economic_times", "techcrunch",
    "producthunt", "huggingface", "weatherapi", "exchangerate",
})


def _is_clickbait(title: str) -> bool:
    """Check if a title matches clickbait heuristic patterns."""
    return any(pattern.search(title) for pattern in CLICKBAIT_PATTERNS)


def _has_enough_content(item: SourceItem) -> bool:
    """Check if the item has minimum content length."""
    combined = f"{item.title} {item.summary}".strip()
    return len(combined) >= MIN_CONTENT_LENGTH


def _passes_reddit_quality(item: SourceItem) -> bool:
    """Check if a Reddit item meets upvote threshold."""
    if item.source != "reddit":
        return True

    upvotes = item.raw.get("score", 0)
    return upvotes >= REDDIT_MIN_UPVOTES


def _is_reputable_source(item: SourceItem) -> bool:
    """Check if the item comes from a reputable source."""
    return item.source in REPUTABLE_SOURCES


def filter_quality(items: list[SourceItem]) -> list[SourceItem]:
    """Apply rule-based quality filters.

    Filters applied in order:
    1. Minimum content length
    2. Reddit upvote threshold
    3. Clickbait title detection
    """
    if not items:
        return []

    filtered: list[SourceItem] = []

    for item in items:
        # Check content length
        if not _has_enough_content(item):
            logger.debug("Quality: filtered (too short): '%s'", item.title[:60])
            continue

        # Check Reddit quality
        if not _passes_reddit_quality(item):
            logger.debug("Quality: filtered (low upvotes): '%s'", item.title[:60])
            continue

        # Check clickbait
        if _is_clickbait(item.title):
            logger.debug("Quality: filtered (clickbait): '%s'", item.title[:60])
            continue

        filtered.append(item)

    removed = len(items) - len(filtered)
    if removed > 0:
        logger.info("Quality: %d items → %d items (%d removed)", len(items), len(filtered), removed)

    return filtered
