"""Filter pipeline orchestrator — chains all filters in sequence."""

import logging
from dataclasses import dataclass

from sources.types import SourceItem
from filters.dedup import deduplicate
from filters.quality import filter_quality
from filters.relevance import score_relevance_and_impact

logger = logging.getLogger(__name__)

# Impact level ordering for sorting
IMPACT_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

# Default item limits
DETAILED_LIMIT = 18
HEADLINES_LIMIT = 10


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

    # Stage 5: Limit
    limited = sorted_items[:config.item_limit]

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
