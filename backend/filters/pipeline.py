"""Filter pipeline orchestrator — chains all filters in sequence."""

import logging
from collections import defaultdict
from dataclasses import dataclass

from sources.types import SourceItem
from filters.dedup import deduplicate
from filters.quality import filter_quality
from filters.relevance import score_relevance_and_impact

logger = logging.getLogger(__name__)

# Impact level ordering for sorting
IMPACT_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

# Default item limits
DETAILED_LIMIT = 25
HEADLINES_LIMIT = 10

# Source-to-category mapping for diversity guarantees
SOURCE_CATEGORY: dict[str, str] = {
    "github": "tech",
    "hackernews": "tech",
    "producthunt": "tech",
    "techcrunch": "tech",
    "huggingface": "tech",
    "arxiv": "research",
    "newsapi": "news",
    "google_news": "news",
    "reddit": "trending",
    "reddit_trending": "trending",
    "reddit_finance": "markets",
    "yahoo_finance": "markets",
    "moneycontrol": "markets",
    "economic_times": "economy",
    "exchangerate": "economy",
    "weatherapi": "weather",
}

# Fill priority after guaranteed slots (higher = filled first)
CATEGORY_PRIORITY: dict[str, int] = {
    "news": 7,
    "tech": 6,
    "markets": 5,
    "research": 4,
    "economy": 3,
    "trending": 2,
    "weather": 1,
}


@dataclass(frozen=True)
class PipelineConfig:
    """Configuration for the filter pipeline."""
    topics: list[str] | None = None
    interests: list[str] | None = None
    mode: str = "detailed"  # "detailed" or "headlines"
    max_items: int | None = None  # Override default limits

    @property
    def item_limit(self) -> int:
        if self.max_items is not None:
            return self.max_items
        return HEADLINES_LIMIT if self.mode == "headlines" else DETAILED_LIMIT


@dataclass(frozen=True)
class PipelineResult:
    """Result from the filter pipeline."""
    items: list[SourceItem]
    stats: dict[str, int]


def _sort_by_impact(items: list[SourceItem]) -> list[SourceItem]:
    """Sort items by impact level: HIGH first, then MEDIUM, then LOW."""
    return sorted(
        items,
        key=lambda item: (
            IMPACT_ORDER.get(item.raw.get("impact", "MEDIUM"), 1),
            -item.raw.get("relevance", 0),
        ),
    )


def _diverse_limit(items: list[SourceItem], limit: int) -> list[SourceItem]:
    """Limit items while guaranteeing at least 1 top item per active source category.

    Strategy:
    1. Group items by category, pick the best item from each (guaranteed slots).
    2. Fill remaining slots by category priority order (news > tech > markets > ...).
    """
    if len(items) <= limit:
        return items

    # Group by category
    by_category: dict[str, list[SourceItem]] = defaultdict(list)
    for item in items:
        cat = SOURCE_CATEGORY.get(item.source, "news")
        by_category[cat].append(item)

    # Phase 1: guarantee 1 best item per active category
    reserved: list[SourceItem] = []
    remaining_by_cat: dict[str, list[SourceItem]] = {}
    for cat, cat_items in by_category.items():
        reserved.append(cat_items[0])  # already sorted by impact+relevance
        remaining_by_cat[cat] = cat_items[1:]

    # If guaranteed slots already exceed limit, trim lowest-priority categories
    if len(reserved) > limit:
        reserved.sort(
            key=lambda item: (
                -CATEGORY_PRIORITY.get(SOURCE_CATEGORY.get(item.source, "news"), 0),
                IMPACT_ORDER.get(item.raw.get("impact", "MEDIUM"), 1),
            ),
        )
        return reserved[:limit]

    # Phase 2: fill remaining slots from leftover items, ordered by category priority
    slots_left = limit - len(reserved)
    reserved_set = set(id(item) for item in reserved)

    # Build priority-ordered pool of remaining items
    fill_pool: list[SourceItem] = []
    cats_by_priority = sorted(
        remaining_by_cat.keys(),
        key=lambda c: -CATEGORY_PRIORITY.get(c, 0),
    )
    for cat in cats_by_priority:
        fill_pool.extend(remaining_by_cat[cat])

    fill = fill_pool[:slots_left]
    return reserved + fill


async def run_filter_pipeline(
    items: list[SourceItem],
    config: PipelineConfig | None = None,
) -> PipelineResult:
    """Run the full noise filtering pipeline.

    Pipeline stages:
    1. Deduplication (fuzzy title matching)
    2. Quality filtering (rule-based)
    3. Relevance + Impact scoring (single batched LLM call)
    4. Sort by impact and relevance
    5. Limit to configured max items
    """
    config = config or PipelineConfig()
    initial_count = len(items)

    if not items:
        return PipelineResult(items=[], stats={"input": 0, "output": 0})

    logger.info("Pipeline: starting with %d items", initial_count)

    # Stage 1: Deduplication
    deduped = deduplicate(items)
    after_dedup = len(deduped)

    # Stage 2: Quality filter
    quality_passed = filter_quality(deduped)
    after_quality = len(quality_passed)

    # Stage 3: Relevance + Impact scoring (single LLM call)
    scored = await score_relevance_and_impact(
        quality_passed,
        topics=config.topics,
        interests=config.interests,
    )
    after_relevance = len(scored)

    # Stage 4: Sort by impact then relevance
    sorted_items = _sort_by_impact(scored)

    # Stage 5: Diversity-aware limit (guarantees 1 item per source category)
    limited = _diverse_limit(sorted_items, config.item_limit)

    stats = {
        "input": initial_count,
        "after_dedup": after_dedup,
        "dedup_removed": initial_count - after_dedup,
        "after_quality": after_quality,
        "quality_removed": after_dedup - after_quality,
        "after_relevance": after_relevance,
        "relevance_removed": after_quality - after_relevance,
        "output": len(limited),
        "limit_trimmed": len(sorted_items) - len(limited),
    }

    logger.info(
        "Pipeline: %d → %d items (dedup: -%d, quality: -%d, relevance: -%d, limit: -%d)",
        initial_count,
        len(limited),
        stats["dedup_removed"],
        stats["quality_removed"],
        stats["relevance_removed"],
        stats["limit_trimmed"],
    )

    return PipelineResult(items=limited, stats=stats)
