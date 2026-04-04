"""Relevance + Impact filter — single batched LLM call for scoring."""

import json
import logging
import os
from dataclasses import replace
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from sources.types import SourceItem

load_dotenv()

logger = logging.getLogger(__name__)

RELEVANCE_THRESHOLD = 6  # Items scoring below this are filtered out

_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
)

# Maximum items to score in a single batch (to stay within context limits)
MAX_BATCH_SIZE = 30


def _build_scoring_prompt(
    items: list[SourceItem],
    topics: list[str],
    interests: list[str],
) -> str:
    """Build a single prompt that scores all items for relevance and impact."""
    topics_str = ", ".join(topics) if topics else "general news"
    interests_str = ", ".join(interests) if interests else "none specified"

    items_block = ""
    for i, item in enumerate(items):
        items_block += f"{i + 1}. [{item.source}] {item.title}\n"
        if item.summary:
            items_block += f"   Summary: {item.summary[:150]}\n"

    return f"""You are a news relevance scorer. Score each item below based on the user's interests.

User's topics: {topics_str}
User's watchlist/interests: {interests_str}

Items to score:
{items_block}

For EACH item, provide:
- relevance: integer 0-10 (10 = perfectly relevant to user's topics/interests)
- impact: "HIGH" (affects many people/markets), "MEDIUM" (niche but significant), or "LOW" (minor news)

Respond with ONLY a JSON array, no explanation. Example:
[{{"relevance": 8, "impact": "HIGH"}}, {{"relevance": 3, "impact": "LOW"}}]

Return exactly {len(items)} objects in the same order as the items above."""


def _parse_scores(response_text: str, count: int) -> list[dict[str, Any]]:
    """Parse LLM response into score dicts, with fallback defaults."""
    default = {"relevance": 7, "impact": "MEDIUM"}

    # Try to extract JSON array from response
    text = response_text.strip()

    # Handle markdown code blocks
    if "```" in text:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start != -1 and end > start:
            text = text[start:end]

    try:
        scores = json.loads(text)
        if isinstance(scores, list) and len(scores) == count:
            return [
                {
                    "relevance": min(10, max(0, int(s.get("relevance", 7)))),
                    "impact": s.get("impact", "MEDIUM").upper()
                    if s.get("impact", "").upper() in ("HIGH", "MEDIUM", "LOW")
                    else "MEDIUM",
                }
                for s in scores
            ]
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        logger.warning("Failed to parse LLM scores: %s", e)

    # Fallback: return defaults for all items
    return [dict(default) for _ in range(count)]


async def score_relevance_and_impact(
    items: list[SourceItem],
    topics: list[str] | None = None,
    interests: list[str] | None = None,
) -> list[SourceItem]:
    """Score items for relevance and impact using a single batched LLM call.

    Items below RELEVANCE_THRESHOLD are filtered out.
    Remaining items are annotated with relevance score and impact level in raw.
    """
    if not items:
        return []

    topics = topics or []
    interests = interests or []

    # If no topics/interests specified, skip LLM and pass everything through
    if not topics and not interests:
        logger.info("Relevance: no topics/interests — passing all %d items through", len(items))
        return [
            replace(item, raw={**item.raw, "relevance": 7, "impact": "MEDIUM"})
            for item in items
        ]

    # Batch items if too many
    all_scored: list[SourceItem] = []
    for batch_start in range(0, len(items), MAX_BATCH_SIZE):
        batch = items[batch_start:batch_start + MAX_BATCH_SIZE]
        scored = await _score_batch(batch, topics, interests)
        all_scored.extend(scored)

    # Filter by relevance threshold
    passed = [item for item in all_scored if item.raw.get("relevance", 0) >= RELEVANCE_THRESHOLD]

    removed = len(items) - len(passed)
    if removed > 0:
        logger.info("Relevance: %d items → %d items (%d below threshold)", len(items), len(passed), removed)

    return passed


async def _score_batch(
    items: list[SourceItem],
    topics: list[str],
    interests: list[str],
) -> list[SourceItem]:
    """Score a single batch of items via LLM."""
    prompt = _build_scoring_prompt(items, topics, interests)

    try:
        response = await _llm.ainvoke([HumanMessage(content=prompt)])
        scores = _parse_scores(response.content, len(items))
    except Exception as e:
        logger.error("LLM scoring failed: %s — using defaults", e)
        scores = [{"relevance": 7, "impact": "MEDIUM"} for _ in items]

    scored: list[SourceItem] = []
    for item, score in zip(items, scores):
        scored.append(
            replace(
                item,
                raw={
                    **item.raw,
                    "relevance": score["relevance"],
                    "impact": score["impact"],
                },
            )
        )

    return scored
