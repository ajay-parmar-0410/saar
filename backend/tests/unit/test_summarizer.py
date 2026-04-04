"""Tests for briefing summarizer."""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from sources.types import SourceItem
from briefing.summarizer import (
    summarize_items,
    _parse_summaries,
    _parse_top_story,
    _parse_insight,
    SummaryResult,
)


def _make_item(
    title: str,
    source: str = "newsapi",
    summary: str = "Detailed article summary.",
    impact: str = "MEDIUM",
    relevance: int = 7,
) -> SourceItem:
    return SourceItem(
        title=title,
        summary=summary,
        url="https://example.com",
        source=source,
        raw={"impact": impact, "relevance": relevance},
    )


class TestParseSummaries:
    def test_valid_json_array(self):
        response = '["Summary one.", "Summary two."]'
        result = _parse_summaries(response, 2)
        assert len(result) == 2
        assert result[0] == "Summary one."

    def test_code_block_json(self):
        response = '```json\n["Summary one.", "Summary two."]\n```'
        result = _parse_summaries(response, 2)
        assert len(result) == 2

    def test_wrong_count_returns_empty(self):
        response = '["Only one."]'
        result = _parse_summaries(response, 3)
        assert result == []

    def test_invalid_json_returns_empty(self):
        result = _parse_summaries("not json", 2)
        assert result == []


class TestParseTopStory:
    def test_valid_json(self):
        response = '{"extended_summary": "Long summary.", "why_it_matters": "Important because..."}'
        result = _parse_top_story(response)
        assert result["extended_summary"] == "Long summary."
        assert result["why_it_matters"] == "Important because..."

    def test_code_block(self):
        response = '```json\n{"extended_summary": "Test.", "why_it_matters": "Reason."}\n```'
        result = _parse_top_story(response)
        assert result["extended_summary"] == "Test."

    def test_invalid_returns_empty(self):
        result = _parse_top_story("garbage")
        assert result["extended_summary"] == ""
        assert result["why_it_matters"] == ""


class TestParseInsight:
    def test_valid_insight(self):
        response = '{"insight": "AI and markets are converging."}'
        result = _parse_insight(response)
        assert result == "AI and markets are converging."

    def test_null_insight(self):
        response = '{"insight": null}'
        result = _parse_insight(response)
        assert result is None

    def test_invalid_json(self):
        result = _parse_insight("not json")
        assert result is None


class TestSummarizeItems:
    @pytest.mark.asyncio
    async def test_empty_items(self):
        result = await summarize_items([])
        assert result.top_story is None
        assert result.items == []
        assert result.cross_domain_insight is None

    @pytest.mark.asyncio
    async def test_single_item_becomes_top_story(self):
        items = [_make_item("Major breaking news", impact="HIGH", relevance=9)]

        top_story_response = MagicMock()
        top_story_response.content = json.dumps({
            "extended_summary": "Extended details about the story.",
            "why_it_matters": "This affects millions.",
        })

        with patch("briefing.summarizer._llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock(return_value=top_story_response)
            result = await summarize_items(items, mode="detailed")

        assert result.top_story is not None
        assert result.top_story.title == "Major breaking news"
        assert "Extended details" in result.top_story.extended_summary

    @pytest.mark.asyncio
    async def test_headlines_mode(self):
        items = [
            _make_item("Top story news", impact="HIGH", relevance=9),
            _make_item("Second news item", impact="MEDIUM"),
            _make_item("Third news item", impact="LOW"),
        ]

        call_count = 0

        async def mock_ainvoke(messages):
            nonlocal call_count
            call_count += 1
            resp = MagicMock()
            if call_count == 1:
                # Top story
                resp.content = json.dumps({
                    "extended_summary": "Top story details.",
                    "why_it_matters": "Matters a lot.",
                })
            elif call_count == 2:
                # Headlines
                resp.content = json.dumps([
                    "One-line summary of second item.",
                    "One-line summary of third item.",
                ])
            else:
                # Insight
                resp.content = json.dumps({"insight": "Cross-domain connection found."})
            return resp

        with patch("briefing.summarizer._llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock(side_effect=mock_ainvoke)
            result = await summarize_items(items, mode="headlines")

        assert result.top_story is not None
        assert len(result.items) == 2
        assert result.cross_domain_insight == "Cross-domain connection found."

    @pytest.mark.asyncio
    async def test_llm_failure_fallback(self):
        items = [
            _make_item("Top story", impact="HIGH", relevance=9),
            _make_item("Second item", impact="MEDIUM", summary="Original summary."),
        ]

        with patch("briefing.summarizer._llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock(side_effect=Exception("API error"))
            result = await summarize_items(items, mode="detailed")

        # Should fallback gracefully
        assert result.top_story is not None
        assert result.top_story.extended_summary != ""
        assert len(result.items) == 1
        # Fallback uses original summary
        assert result.items[0].summary == "Original summary."

    @pytest.mark.asyncio
    async def test_top_story_picks_highest_impact(self):
        items = [
            _make_item("Low impact item", impact="LOW", relevance=5),
            _make_item("High impact item", impact="HIGH", relevance=9),
            _make_item("Medium impact item", impact="MEDIUM", relevance=7),
        ]

        top_response = MagicMock()
        top_response.content = json.dumps({
            "extended_summary": "Details.",
            "why_it_matters": "Important.",
        })
        summary_response = MagicMock()
        summary_response.content = json.dumps(["Sum 1.", "Sum 2."])
        insight_response = MagicMock()
        insight_response.content = json.dumps({"insight": None})

        responses = iter([top_response, summary_response, insight_response])

        with patch("briefing.summarizer._llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock(side_effect=lambda _: next(responses))
            result = await summarize_items(items, mode="detailed")

        assert result.top_story.title == "High impact item"
