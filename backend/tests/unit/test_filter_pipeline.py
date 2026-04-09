"""Tests for filter pipeline orchestrator."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from sources.types import SourceItem
from filters.pipeline import run_filter_pipeline, PipelineConfig, PipelineResult


def _make_item(
    title: str,
    source: str = "newsapi",
    summary: str = "A proper news summary with enough content.",
    raw: dict | None = None,
) -> SourceItem:
    return SourceItem(
        title=title,
        summary=summary,
        url="https://example.com",
        source=source,
        raw=raw or {},
    )


def _mock_llm_scores(items_count: int, relevance: int = 8, impact: str = "HIGH") -> MagicMock:
    """Create a mock LLM response with uniform scores."""
    mock_response = MagicMock()
    mock_response.content = json.dumps([
        {"relevance": relevance, "impact": impact}
        for _ in range(items_count)
    ])
    return mock_response


class TestPipelineConfig:
    def test_default_detailed_limit(self):
        config = PipelineConfig()
        assert config.item_limit == 25

    def test_headlines_limit(self):
        config = PipelineConfig(mode="headlines")
        assert config.item_limit == 10

    def test_custom_limit(self):
        config = PipelineConfig(max_items=5)
        assert config.item_limit == 5


class TestPipelineResult:
    def test_frozen(self):
        result = PipelineResult(items=[], stats={"input": 0, "output": 0})
        with pytest.raises(AttributeError):
            result.items = []


class TestRunFilterPipeline:
    @pytest.mark.asyncio
    async def test_empty_input(self):
        result = await run_filter_pipeline([])
        assert result.items == []
        assert result.stats["input"] == 0
        assert result.stats["output"] == 0

    @pytest.mark.asyncio
    async def test_removes_duplicates(self):
        items = [
            _make_item("Apple launches iPhone 16", source="newsapi"),
            _make_item("Apple unveils new iPhone 16", source="google_news"),
            _make_item("Google releases Pixel 9", source="newsapi"),
        ]

        # No topics = skip LLM scoring
        config = PipelineConfig(topics=[], interests=[])
        result = await run_filter_pipeline(items, config)

        assert result.stats["dedup_removed"] >= 1
        assert len(result.items) == 2

    @pytest.mark.asyncio
    async def test_removes_low_quality(self):
        items = [
            _make_item("Legitimate news headline"),
            _make_item("You won't believe this trick!", source="reddit", raw={"score": 5}),
        ]
        config = PipelineConfig(topics=[], interests=[])
        result = await run_filter_pipeline(items, config)

        assert result.stats["quality_removed"] >= 1

    @pytest.mark.asyncio
    async def test_full_pipeline_with_scoring(self):
        items = [
            _make_item(f"News headline {i}") for i in range(10)
        ]

        mock_response = _mock_llm_scores(10, relevance=8, impact="HIGH")

        with patch("filters.relevance._llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            config = PipelineConfig(topics=["tech"], interests=["AAPL"])
            result = await run_filter_pipeline(items, config)

        assert len(result.items) <= config.item_limit
        assert result.stats["input"] == 10

    @pytest.mark.asyncio
    async def test_sorts_by_impact(self):
        items = [
            _make_item("New VS Code extension released for Python developers"),
            _make_item("RBI changes monetary policy interest rate by 50 basis points"),
            _make_item("Samsung announces Galaxy S26 with improved camera system"),
        ]

        mock_response = MagicMock()
        mock_response.content = json.dumps([
            {"relevance": 8, "impact": "LOW"},
            {"relevance": 9, "impact": "HIGH"},
            {"relevance": 7, "impact": "MEDIUM"},
        ])

        with patch("filters.relevance._llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            config = PipelineConfig(topics=["general"], interests=[])
            result = await run_filter_pipeline(items, config)

        assert len(result.items) == 3
        assert result.items[0].raw["impact"] == "HIGH"
        assert result.items[1].raw["impact"] == "MEDIUM"
        assert result.items[2].raw["impact"] == "LOW"

    @pytest.mark.asyncio
    async def test_respects_item_limit(self):
        items = [_make_item(f"Headline {i}") for i in range(50)]
        config = PipelineConfig(topics=[], interests=[], max_items=5)
        result = await run_filter_pipeline(items, config)

        assert len(result.items) <= 5

    @pytest.mark.asyncio
    async def test_pipeline_handles_all_filtered_out(self):
        items = [
            _make_item("Hi", summary=""),  # Too short
        ]
        config = PipelineConfig(topics=[], interests=[])
        result = await run_filter_pipeline(items, config)

        assert len(result.items) == 0
        assert result.stats["quality_removed"] >= 1

    @pytest.mark.asyncio
    async def test_stats_are_accurate(self):
        items = [
            _make_item("Apple launches iPhone 16", source="newsapi"),
            _make_item("Apple unveils new iPhone 16", source="google_news"),
            _make_item("Valid unique headline"),
        ]
        config = PipelineConfig(topics=[], interests=[])
        result = await run_filter_pipeline(items, config)

        stats = result.stats
        assert stats["input"] == 3
        assert stats["dedup_removed"] + stats["quality_removed"] + stats["relevance_removed"] + stats["limit_trimmed"] == stats["input"] - stats["output"]
