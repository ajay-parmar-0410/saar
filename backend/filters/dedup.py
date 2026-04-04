"""Deduplication filter — merges near-duplicate items using fuzzy title matching."""

import logging
from dataclasses import replace
from rapidfuzz import fuzz

from sources.types import SourceItem

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 75  # 0-100 scale in rapidfuzz


def _pick_best_summary(a: SourceItem, b: SourceItem) -> str:
    """Return the longer (more detailed) summary."""
    return a.summary if len(a.summary) >= len(b.summary) else b.summary


def _normalize_title(title: str) -> str:
    """Lowercase and strip extra whitespace for comparison."""
    return " ".join(title.lower().split())


def deduplicate(items: list[SourceItem]) -> list[SourceItem]:
    """Remove near-duplicate items based on fuzzy title matching.

    When duplicates are found:
    - Keep the item with the longer summary
    - Track all source URLs and source names in raw["merged_sources"]
    - Count how many sources reported the same story
    """
    if len(items) <= 1:
        return list(items)

    # Track which items have been merged into another
    merged_into: dict[int, int] = {}  # index → canonical index
    results: dict[int, SourceItem] = {}  # canonical index → merged item
    source_tracker: dict[int, list[dict[str, str]]] = {}  # canonical → list of sources

    for i, item in enumerate(items):
        if i in merged_into:
            continue

        # Initialize this item as canonical
        if i not in results:
            results[i] = item
            source_tracker[i] = [{"source": item.source, "url": item.url}]

        norm_i = _normalize_title(item.title)

        for j in range(i + 1, len(items)):
            if j in merged_into:
                continue

            norm_j = _normalize_title(items[j].title)
            score = fuzz.token_set_ratio(norm_i, norm_j)

            if score >= SIMILARITY_THRESHOLD:
                merged_into[j] = i
                source_tracker[i].append({
                    "source": items[j].source,
                    "url": items[j].url,
                })

                # Keep the better summary
                best_summary = _pick_best_summary(results[i], items[j])
                current = results[i]
                merged_raw = {
                    **current.raw,
                    "merged_sources": source_tracker[i],
                    "source_count": len(source_tracker[i]),
                }
                results[i] = replace(
                    current,
                    summary=best_summary,
                    raw=merged_raw,
                )

                logger.debug(
                    "Merged duplicate: '%s' ↔ '%s' (score=%.1f)",
                    items[i].title,
                    items[j].title,
                    score,
                )

    deduped = list(results.values())
    removed = len(items) - len(deduped)
    if removed > 0:
        logger.info("Dedup: %d items → %d items (%d duplicates removed)", len(items), len(deduped), removed)

    return deduped
