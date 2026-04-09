"""LLM summarizer — batched summarization for briefing items."""

import json
import logging
from dataclasses import dataclass, field

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from sources.types import SourceItem

load_dotenv()

logger = logging.getLogger(__name__)

_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
)


@dataclass(frozen=True)
class SummarizedItem:
    """A source item with its LLM-generated summary."""
    title: str
    summary: str
    url: str
    source: str
    impact: str
    relevance: int
    raw: dict = field(default_factory=dict)


@dataclass(frozen=True)
class TopStory:
    """The highest-impact item with an extended summary."""
    title: str
    extended_summary: str
    url: str
    source: str
    why_it_matters: str


@dataclass(frozen=True)
class SummaryResult:
    """Complete summarization output."""
    top_story: TopStory | None
    items: list[SummarizedItem]
    cross_domain_insight: str | None


def _build_headlines_prompt(items: list[SourceItem]) -> str:
    """Build prompt for headlines mode (1-line summaries)."""
    items_block = ""
    for i, item in enumerate(items):
        items_block += f"{i + 1}. [{item.source}] {item.title}\n"
        if item.summary:
            items_block += f"   Context: {item.summary[:200]}\n"

    return f"""Summarize each news item below in exactly ONE concise sentence.

Items:
{items_block}

Respond with ONLY a JSON array of strings, one summary per item, in the same order.
Example: ["Summary of item 1.", "Summary of item 2."]

Return exactly {len(items)} summaries."""


def _build_detailed_prompt(items: list[SourceItem]) -> str:
    """Build prompt for detailed mode (2-3 sentence summaries)."""
    items_block = ""
    for i, item in enumerate(items):
        items_block += f"{i + 1}. [{item.source}] {item.title}\n"
        if item.summary:
            items_block += f"   Context: {item.summary[:300]}\n"

    return f"""Summarize each news item below in 2-3 informative sentences. Include key facts and context.

Items:
{items_block}

Respond with ONLY a JSON array of strings, one summary per item, in the same order.
Example: ["Two to three sentence summary of item 1.", "Two to three sentence summary of item 2."]

Return exactly {len(items)} summaries."""


def _build_top_story_prompt(item: SourceItem) -> str:
    """Build prompt for extended top story summary."""
    return f"""You are writing the "Top Story" section of a daily news briefing.

Story: {item.title}
Source: {item.source}
Details: {item.summary}

Write a JSON object with:
- "extended_summary": A 4-5 sentence detailed summary of this story
- "why_it_matters": A 1-2 sentence explanation of why this matters to the reader

Respond with ONLY the JSON object, no explanation.
Example: {{"extended_summary": "...", "why_it_matters": "..."}}"""


def _build_insight_prompt(items: list[SourceItem]) -> str:
    """Build prompt for cross-domain insight."""
    titles = [f"- {item.title} ({item.source})" for item in items[:10]]
    titles_block = "\n".join(titles)

    return f"""Look at these news items from different domains and identify ONE cross-domain insight or connection between them. If no meaningful connection exists, respond with null.

Items:
{titles_block}

Respond with ONLY a JSON object: {{"insight": "Your one-sentence insight"}} or {{"insight": null}}"""


def _parse_summaries(response_text: str, count: int) -> list[str]:
    """Parse LLM summary response into list of strings."""
    text = response_text.strip()
    if "```" in text:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start != -1 and end > start:
            text = text[start:end]

    try:
        summaries = json.loads(text)
        if isinstance(summaries, list) and len(summaries) == count:
            return [str(s) for s in summaries]
    except (json.JSONDecodeError, TypeError):
        logger.warning("Failed to parse summaries response")

    return []


def _parse_top_story(response_text: str) -> dict[str, str]:
    """Parse top story response."""
    text = response_text.strip()
    if "```" in text:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return {
                "extended_summary": str(data.get("extended_summary", "")),
                "why_it_matters": str(data.get("why_it_matters", "")),
            }
    except (json.JSONDecodeError, TypeError):
        logger.warning("Failed to parse top story response")

    return {"extended_summary": "", "why_it_matters": ""}


def _parse_insight(response_text: str) -> str | None:
    """Parse cross-domain insight response."""
    text = response_text.strip()
    if "```" in text:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            insight = data.get("insight")
            return str(insight) if insight else None
    except (json.JSONDecodeError, TypeError):
        pass

    return None


async def summarize_items(
    items: list[SourceItem],
    mode: str = "detailed",
) -> SummaryResult:
    """Summarize items using batched LLM calls.

    Args:
        items: Filtered and scored source items.
        mode: "headlines" (1-line each) or "detailed" (2-3 sentences each).

    Returns:
        SummaryResult with top story, summarized items, and optional insight.
    """
    if not items:
        return SummaryResult(top_story=None, items=[], cross_domain_insight=None)

    # Find top story (highest impact + relevance)
    top_item = max(
        items,
        key=lambda x: (
            0 if x.raw.get("impact") == "HIGH" else (1 if x.raw.get("impact") == "MEDIUM" else 2),
            -x.raw.get("relevance", 0),
        ),
    )
    # Note: sort key is (impact_order, -relevance), so min gives highest impact + relevance
    top_item = min(
        items,
        key=lambda x: (
            0 if x.raw.get("impact") == "HIGH" else (1 if x.raw.get("impact") == "MEDIUM" else 2),
            -x.raw.get("relevance", 0),
        ),
    )

    remaining = [item for item in items if item is not top_item]

    # Build all prompts
    if mode == "headlines":
        summary_prompt = _build_headlines_prompt(remaining) if remaining else None
    else:
        summary_prompt = _build_detailed_prompt(remaining) if remaining else None

    top_story_prompt = _build_top_story_prompt(top_item)
    insight_prompt = _build_insight_prompt(items) if len(items) >= 3 else None

    # Execute LLM calls — top story + summaries + insight
    top_story_data = {"extended_summary": "", "why_it_matters": ""}
    summaries: list[str] = []
    insight: str | None = None

    # Top story call
    try:
        response = await _llm.ainvoke([HumanMessage(content=top_story_prompt)])
        top_story_data = _parse_top_story(response.content)
    except Exception as e:
        logger.error("Top story summarization failed: %s", e)
        top_story_data = {
            "extended_summary": top_item.summary,
            "why_it_matters": "This is today's most impactful story.",
        }

    top_story = TopStory(
        title=top_item.title,
        extended_summary=top_story_data["extended_summary"] or top_item.summary,
        url=top_item.url,
        source=top_item.source,
        why_it_matters=top_story_data["why_it_matters"],
    )

    # Summaries call
    if summary_prompt and remaining:
        try:
            response = await _llm.ainvoke([HumanMessage(content=summary_prompt)])
            summaries = _parse_summaries(response.content, len(remaining))
        except Exception as e:
            logger.error("Batch summarization failed: %s", e)

    # Fallback: use raw titles/summaries if LLM failed
    if not summaries and remaining:
        summaries = [
            item.summary if item.summary else item.title
            for item in remaining
        ]

    summarized_items = [
        SummarizedItem(
            title=item.title,
            summary=summaries[i] if i < len(summaries) else item.summary,
            url=item.url,
            source=item.source,
            impact=item.raw.get("impact", "MEDIUM"),
            relevance=item.raw.get("relevance", 0),
            raw=item.raw,
        )
        for i, item in enumerate(remaining)
    ]

    # Insight call (only if enough diverse items)
    if insight_prompt:
        try:
            response = await _llm.ainvoke([HumanMessage(content=insight_prompt)])
            insight = _parse_insight(response.content)
        except Exception as e:
            logger.error("Insight generation failed: %s", e)

    return SummaryResult(
        top_story=top_story,
        items=summarized_items,
        cross_domain_insight=insight,
    )
