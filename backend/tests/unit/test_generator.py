"""Tests for briefing generator."""

import pytest
from unittest.mock import patch, MagicMock

from briefing.summarizer import SummaryResult, SummarizedItem, TopStory
from briefing.generator import (
    generate_briefing,
    _organize_into_sections,
    _count_alerts,
    _render_markdown,
    Briefing,
    BriefingSection,
)


def _make_summarized_item(
    title: str = "Test headline",
    source: str = "newsapi",
    summary: str = "Test summary.",
    impact: str = "MEDIUM",
    relevance: int = 7,
) -> SummarizedItem:
    return SummarizedItem(
        title=title,
        summary=summary,
        url="https://example.com",
        source=source,
        impact=impact,
        relevance=relevance,
    )


def _make_top_story(title: str = "Breaking news") -> TopStory:
    return TopStory(
        title=title,
        extended_summary="Extended details about the story.",
        url="https://example.com",
        source="newsapi",
        why_it_matters="This affects millions.",
    )


class TestOrganizeIntoSections:
    def test_tech_sources(self):
        items = [
            _make_summarized_item("GitHub update", source="github"),
            _make_summarized_item("New paper on arxiv", source="arxiv"),
            _make_summarized_item("Reddit discussion", source="reddit"),
        ]
        sections = _organize_into_sections(items, ["ai_tech"])
        keys = [s.key for s in sections]
        assert "tech" in keys
        assert "research" in keys
        assert "trending" in keys

    def test_trader_user(self):
        items = [
            _make_summarized_item("Nifty rises", source="yahoo_finance"),
            _make_summarized_item("Rupee falls", source="economic_times"),
        ]
        sections = _organize_into_sections(items, ["trader"])
        keys = [s.key for s in sections]
        assert "markets" in keys

    def test_general_user(self):
        items = [
            _make_summarized_item("World news", source="google_news"),
            _make_summarized_item("Weather update", source="weatherapi"),
        ]
        sections = _organize_into_sections(items, ["general"])
        keys = [s.key for s in sections]
        assert "headlines" in keys
        assert "weather" in keys

    def test_combined_user_types(self):
        items = [
            _make_summarized_item("GitHub update", source="github"),
            _make_summarized_item("Nifty rises", source="yahoo_finance"),
        ]
        sections = _organize_into_sections(items, ["ai_tech", "trader"])
        keys = [s.key for s in sections]
        assert "tech" in keys
        assert "markets" in keys

    def test_empty_sections_skipped(self):
        items = [_make_summarized_item("GitHub update", source="github")]
        sections = _organize_into_sections(items, ["ai_tech"])
        # Only the section with items should appear
        assert all(len(s.items) > 0 for s in sections)

    def test_uncategorized_goes_to_headlines(self):
        items = [_make_summarized_item("Random item", source="unknown_source")]
        sections = _organize_into_sections(items, ["general"])
        # Should land in headlines section
        assert len(sections) == 1
        assert sections[0].key == "headlines"
        assert len(sections[0].items) == 1


class TestCountAlerts:
    def test_counts_high_impact(self):
        items = [
            _make_summarized_item(impact="HIGH"),
            _make_summarized_item(impact="MEDIUM"),
            _make_summarized_item(impact="HIGH"),
            _make_summarized_item(impact="LOW"),
        ]
        assert _count_alerts(items) == 2

    def test_no_alerts(self):
        items = [
            _make_summarized_item(impact="MEDIUM"),
            _make_summarized_item(impact="LOW"),
        ]
        assert _count_alerts(items) == 0

    def test_empty_items(self):
        assert _count_alerts([]) == 0


class TestRenderMarkdown:
    def test_includes_top_story(self):
        top = _make_top_story("Big Breaking News")
        md = _render_markdown("2026-04-04", top, [], None)
        assert "Big Breaking News" in md
        assert "Top Story" in md
        assert "Why it matters" in md

    def test_includes_sections(self):
        sections = [
            BriefingSection(
                key="headlines",
                title="Headlines",
                items=[_make_summarized_item("Test item")],
            )
        ]
        md = _render_markdown("2026-04-04", None, sections, None)
        assert "## Headlines" in md
        assert "Test item" in md

    def test_includes_insight(self):
        md = _render_markdown("2026-04-04", None, [], "AI and markets converge.")
        assert "AI and markets converge." in md

    def test_impact_badges(self):
        sections = [
            BriefingSection(
                key="test",
                title="Test",
                items=[
                    _make_summarized_item(impact="HIGH"),
                    _make_summarized_item(impact="MEDIUM"),
                    _make_summarized_item(impact="LOW"),
                ],
            )
        ]
        md = _render_markdown("2026-04-04", None, sections, None)
        assert "🔴" in md
        assert "🟡" in md
        assert "⚪" in md


class TestGenerateBriefing:
    def test_generates_complete_briefing(self):
        summary_result = SummaryResult(
            top_story=_make_top_story(),
            items=[
                _make_summarized_item("Item 1", source="github", impact="HIGH"),
                _make_summarized_item("Item 2", source="newsapi", impact="MEDIUM"),
            ],
            cross_domain_insight="Interesting connection.",
        )

        briefing = generate_briefing(
            user_id="test-user-123",
            summary_result=summary_result,
            user_types=["ai_tech"],
        )

        assert briefing.user_id == "test-user-123"
        assert briefing.top_story is not None
        assert briefing.item_count == 3  # 2 items + top story
        assert briefing.alert_count == 1  # 1 HIGH impact
        assert briefing.cross_domain_insight == "Interesting connection."
        assert "Daily Briefing" in briefing.markdown
        assert len(briefing.sections_json) > 0

    def test_default_general_user(self):
        summary_result = SummaryResult(
            top_story=None,
            items=[_make_summarized_item("News", source="google_news")],
            cross_domain_insight=None,
        )

        briefing = generate_briefing(
            user_id="test-user",
            summary_result=summary_result,
        )

        # Should use general sections
        assert briefing.item_count == 1

    def test_sections_json_structure(self):
        summary_result = SummaryResult(
            top_story=None,
            items=[_make_summarized_item("GH Item", source="github")],
            cross_domain_insight=None,
        )

        briefing = generate_briefing(
            user_id="test-user",
            summary_result=summary_result,
            user_types=["ai_tech"],
        )

        assert len(briefing.sections_json) >= 1
        section = briefing.sections_json[0]
        assert "key" in section
        assert "title" in section
        assert "items" in section
        assert len(section["items"]) >= 1
        item = section["items"][0]
        assert "title" in item
        assert "summary" in item
        assert "url" in item
        assert "source" in item
        assert "impact" in item
