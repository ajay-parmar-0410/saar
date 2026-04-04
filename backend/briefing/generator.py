"""Briefing generator — organizes filtered items into sections and stores briefing."""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sources.types import SourceItem
from briefing.summarizer import SummaryResult, SummarizedItem, TopStory

logger = logging.getLogger(__name__)

# Section definitions per user type
SECTION_CONFIG: dict[str, list[dict[str, Any]]] = {
    "ai_tech": [
        {"key": "ai_tech", "title": "AI & Tech", "sources": {"github", "hackernews", "techcrunch", "producthunt", "huggingface"}, "topics": {"artificial_intelligence", "machine_learning", "llm", "developer_tools", "startups"}},
        {"key": "research", "title": "Research", "sources": {"arxiv"}, "topics": {"research_papers"}},
        {"key": "community", "title": "Community Buzz", "sources": {"reddit"}, "topics": {"open_source"}},
    ],
    "trader": [
        {"key": "markets", "title": "Markets", "sources": {"yahoo_finance", "moneycontrol"}, "topics": {"indian_markets", "nifty", "sensex"}},
        {"key": "watchlist", "title": "Watchlist", "sources": set(), "topics": {"ipo", "earnings"}},
        {"key": "economy", "title": "Economic News", "sources": {"economic_times", "exchangerate"}, "topics": {"economy", "gold", "currency"}},
    ],
    "general": [
        {"key": "headlines", "title": "Headlines", "sources": {"newsapi", "google_news"}, "topics": {"top_headlines", "world_news"}},
        {"key": "weather", "title": "Weather", "sources": {"weatherapi"}, "topics": {"weather"}},
        {"key": "trending", "title": "Trending", "sources": {"reddit_trending"}, "topics": {"trending"}},
    ],
}


@dataclass(frozen=True)
class BriefingSection:
    """A named section in the briefing."""
    key: str
    title: str
    items: list[SummarizedItem]


@dataclass(frozen=True)
class Briefing:
    """Complete generated briefing."""
    user_id: str
    date: str
    top_story: TopStory | None
    sections: list[BriefingSection]
    cross_domain_insight: str | None
    item_count: int
    alert_count: int
    markdown: str
    sections_json: list[dict[str, Any]]


def _classify_item(
    item: SummarizedItem,
    section_configs: list[dict[str, Any]],
) -> str | None:
    """Determine which section an item belongs to based on source and topic matching."""
    for config in section_configs:
        if item.source in config["sources"]:
            return config["key"]
    # Fallback: check if item could fit any section by topic
    return None


def _organize_into_sections(
    items: list[SummarizedItem],
    user_types: list[str],
) -> list[BriefingSection]:
    """Group items into named sections based on user type configuration."""
    # Merge section configs for all user types
    all_configs: list[dict[str, Any]] = []
    seen_keys: set[str] = set()

    for user_type in user_types:
        configs = SECTION_CONFIG.get(user_type, SECTION_CONFIG["general"])
        for config in configs:
            if config["key"] not in seen_keys:
                all_configs.append(config)
                seen_keys.add(config["key"])

    # Classify items into sections
    section_items: dict[str, list[SummarizedItem]] = {
        config["key"]: [] for config in all_configs
    }
    uncategorized: list[SummarizedItem] = []

    for item in items:
        section_key = _classify_item(item, all_configs)
        if section_key and section_key in section_items:
            section_items[section_key].append(item)
        else:
            uncategorized.append(item)

    # Distribute uncategorized items to first section
    if uncategorized and all_configs:
        first_key = all_configs[0]["key"]
        section_items[first_key].extend(uncategorized)

    # Build sections (skip empty ones)
    sections: list[BriefingSection] = []
    for config in all_configs:
        items_in_section = section_items[config["key"]]
        if items_in_section:
            sections.append(BriefingSection(
                key=config["key"],
                title=config["title"],
                items=items_in_section,
            ))

    return sections


def _count_alerts(items: list[SummarizedItem]) -> int:
    """Count HIGH impact items as alerts."""
    return sum(1 for item in items if item.impact == "HIGH")


def _render_markdown(
    date: str,
    top_story: TopStory | None,
    sections: list[BriefingSection],
    insight: str | None,
) -> str:
    """Render the briefing as markdown."""
    md = f"# Daily Briefing — {date}\n\n"

    # Top Story
    if top_story:
        md += "## Top Story\n"
        md += f"**{top_story.title}**\n\n"
        md += f"{top_story.extended_summary}\n\n"
        if top_story.why_it_matters:
            md += f"*Why it matters:* {top_story.why_it_matters}\n\n"
        md += f"Source: [{top_story.source}]({top_story.url})\n\n"
        md += "---\n\n"

    # Sections
    for section in sections:
        md += f"## {section.title}\n\n"
        for item in section.items:
            impact_badge = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "⚪"}.get(item.impact, "⚪")
            md += f"- {impact_badge} **{item.title}**\n"
            md += f"  {item.summary}\n"
            md += f"  [{item.source}]({item.url})\n\n"

    # Cross-domain insight
    if insight:
        md += "---\n\n"
        md += "## Insight\n"
        md += f"💡 {insight}\n\n"

    return md


def _sections_to_json(
    sections: list[BriefingSection],
) -> list[dict[str, Any]]:
    """Convert sections to JSON-serializable dicts for DB storage."""
    return [
        {
            "key": section.key,
            "title": section.title,
            "items": [
                {
                    "title": item.title,
                    "summary": item.summary,
                    "url": item.url,
                    "source": item.source,
                    "impact": item.impact,
                    "relevance": item.relevance,
                }
                for item in section.items
            ],
        }
        for section in sections
    ]


def generate_briefing(
    user_id: str,
    summary_result: SummaryResult,
    user_types: list[str] | None = None,
) -> Briefing:
    """Generate a complete briefing from summarized items.

    Args:
        user_id: The user this briefing is for.
        summary_result: Output from the summarizer.
        user_types: User type(s) for section organization.

    Returns:
        A complete Briefing ready to be stored.
    """
    user_types = user_types or ["general"]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    sections = _organize_into_sections(summary_result.items, user_types)
    sections_json = _sections_to_json(sections)

    all_items = summary_result.items
    alert_count = _count_alerts(all_items)

    markdown = _render_markdown(
        date=today,
        top_story=summary_result.top_story,
        sections=sections,
        insight=summary_result.cross_domain_insight,
    )

    return Briefing(
        user_id=user_id,
        date=today,
        top_story=summary_result.top_story,
        sections=sections,
        cross_domain_insight=summary_result.cross_domain_insight,
        item_count=len(all_items) + (1 if summary_result.top_story else 0),
        alert_count=alert_count,
        markdown=markdown,
        sections_json=sections_json,
    )


def store_briefing(briefing: Briefing) -> dict[str, Any]:
    """Store briefing in the database. Returns the created DB record."""
    from db.briefings import create_briefing

    top_story_str = ""
    if briefing.top_story:
        top_story_str = f"{briefing.top_story.title}: {briefing.top_story.extended_summary}"

    return create_briefing(
        user_id=briefing.user_id,
        content=briefing.markdown,
        sections=briefing.sections_json,
        top_story=top_story_str,
        item_count=briefing.item_count,
        alert_count=briefing.alert_count,
    )
