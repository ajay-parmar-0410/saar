"""Tests for relevance + impact scoring filter."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from sources.types import SourceItem
from filters.relevance import (
    score_relevance_and_impact,
    _parse_scores,
    _build_scoring_prompt,
)


def _make_item(title: str, source: str = "newsapi", summary: str = "Summary text") -> SourceItem:
    return SourceItem(title=title, summary=summary, url="https://example.com", source=source)


class TestParseScores:
    def test_valid_json(self):
        response = '[{"relevance": 8, "impact": "HIGH"}, {"relevance": 3, "impact": "LOW"}]'
        result = _parse_scores(response, 2)
        assert len(result) == 2
        assert result[0]["relevance"] == 8
        assert result[0]["impact"] == "HIGH"
        assert result[1]["relevance"] == 3
        assert result[1]["impact"] == "LOW"

    def test_json_in_code_block(self):
        response = '```json\n[{"relevance": 9, "impact": "HIGH"}]\n```'
        result = _parse_scores(response, 1)
        assert result[0]["relevance"] == 9

    def test_invalid_json_returns_defaults(self):
        result = _parse_scores("not json at all", 3)
        assert len(result) == 3
        assert all(s["relevance"] == 7 for s in result)
        assert all(s["impact"] == "MEDIUM" for s in result)

    def test_wrong_count_returns_defaults(self):
        response = '[{"relevance": 8, "impact": "HIGH"}]'
        result = _parse_scores(response, 3)  # Expected 3 but got 1
        assert len(result) == 3

    def test_clamps_relevance(self):
        response = '[{"relevance": 15, "impact": "HIGH"}, {"relevance": -5, "impact": "LOW"}]'
        result = _parse_scores(response, 2)
        assert result[0]["relevance"] == 10
        assert result[1]["relevance"] == 0

    def test_invalid_impact_defaults_to_medium(self):
        response = '[{"relevance": 7, "impact": "EXTREME"}]'
        result = _parse_scores(response, 1)
        assert result[0]["impact"] == "MEDIUM"


class TestBuildScoringPrompt:
    def test_includes_topics(self):
        items = [_make_item("Test headline")]
        prompt = _build_scoring_prompt(items, ["ai", "tech"], [])
        assert "ai" in prompt
        assert "tech" in prompt

    def test_includes_interests(self):
        items = [_make_item("Test headline")]
        prompt = _build_scoring_prompt(items, [], ["RELIANCE", "TATAMOTORS"])
        assert "RELIANCE" in prompt

    def test_includes_all_items(self):
        items = [_make_item(f"Headline {i}") for i in range(5)]
        prompt = _build_scoring_prompt(items, ["tech"], [])
        for i in range(5):
            assert f"Headline {i}" in prompt


class TestScoreRelevanceAndImpact:
    @pytest.mark.asyncio
    async def test_empty_items(self):
        result = await score_relevance_and_impact([])
        assert result == []

    @pytest.mark.asyncio
    async def test_no_topics_passes_all(self):
        items = [_make_item("Some headline"), _make_item("Another headline")]
        result = await score_relevance_and_impact(items, topics=[], interests=[])
        assert len(result) == 2
        assert all(item.raw.get("relevance") == 7 for item in result)

    @pytest.mark.asyncio
    async def test_filters_low_relevance(self):
        mock_response = MagicMock()
        mock_response.content = json.dumps([
            {"relevance": 9, "impact": "HIGH"},
            {"relevance": 2, "impact": "LOW"},
        ])

        with patch("filters.relevance._llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            items = [
                _make_item("New GPT model released"),
                _make_item("Cricket match results"),
            ]
            result = await score_relevance_and_impact(items, topics=["ai"], interests=[])

        assert len(result) == 1
        assert result[0].title == "New GPT model released"
        assert result[0].raw["relevance"] == 9
        assert result[0].raw["impact"] == "HIGH"

    @pytest.mark.asyncio
    async def test_llm_failure_uses_defaults(self):
        with patch("filters.relevance._llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock(side_effect=Exception("API error"))
            items = [_make_item("Some headline")]
            result = await score_relevance_and_impact(items, topics=["tech"], interests=[])

        # Should pass through with default score of 7 (>= threshold 6)
        assert len(result) == 1
        assert result[0].raw["relevance"] == 7
