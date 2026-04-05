"""Integration tests for the briefing generation pipeline.

Tests the full flow: fetch sources → filter pipeline → summarize → generate briefing.
Uses mocked LLM but real filter logic.
"""

import os
import sys
import json

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sources.types import SourceItem, SourceResult
from filters.pipeline import run_filter_pipeline, PipelineConfig
from briefing.summarizer import summarize_items
from briefing.generator import generate_briefing


def _make_items(count: int = 10) -> list[SourceItem]:
    """Create a batch of realistic test items."""
    headlines = [
        ("OpenAI releases GPT-5 with reasoning improvements", "newsapi"),
        ("RBI cuts repo rate by 25 basis points", "economic_times"),
        ("GitHub Copilot now supports multi-file editing", "github"),
        ("Nifty 50 hits all-time high above 25000", "yahoo_finance"),
        ("New transformer architecture halves training cost", "arxiv"),
        ("Redis 8.0 released with major performance gains", "hackernews"),
        ("Indian Rupee strengthens to 82.5 per USD", "exchangerate"),
        ("Hugging Face launches open model hub 2.0", "huggingface"),
        ("r/MachineLearning trending: diffusion vs autoregressive", "reddit"),
        ("Next.js 16 introduces Turbopack by default", "producthunt"),
    ]
    return [
        SourceItem(
            title=title,
            summary=f"Detailed coverage of: {title}. Multiple sources confirm the development.",
            url=f"https://example.com/{i}",
            source=source,
        )
        for i, (title, source) in enumerate(headlines[:count])
    ]


class TestFullPipeline:
    """End-to-end pipeline: items → filter → summarize → briefing."""

    @pytest.mark.asyncio
    async def test_filter_pipeline_processes_items(self):
        items = _make_items(10)
        config = PipelineConfig(topics=[], interests=[], max_items=8)
        result = await run_filter_pipeline(items, config)

        assert len(result.items) <= 8
        assert result.stats["input"] == 10
        assert result.stats["output"] == len(result.items)

    @pytest.mark.asyncio
    async def test_summarize_filtered_items(self):
        items = _make_items(5)

        # Mock LLM for summarization
        call_count = 0

        async def mock_ainvoke(messages):
            nonlocal call_count
            call_count += 1
            resp = MagicMock()
            if call_count == 1:
                resp.content = json.dumps({
                    "extended_summary": "Comprehensive details about the top story.",
                    "why_it_matters": "This affects the entire tech industry.",
                })
            elif call_count == 2:
                resp.content = json.dumps([
                    f"Summary of item {i+1}." for i in range(4)
                ])
            else:
                resp.content = json.dumps({"insight": "AI and finance are converging."})
            return resp

        with patch("briefing.summarizer._llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock(side_effect=mock_ainvoke)
            result = await summarize_items(items, mode="detailed")

        assert result.top_story is not None
        assert len(result.items) >= 1

    @pytest.mark.asyncio
    async def test_generate_briefing_from_summary(self):
        items = _make_items(5)

        # Mock summarization
        call_count = 0

        async def mock_ainvoke(messages):
            nonlocal call_count
            call_count += 1
            resp = MagicMock()
            if call_count == 1:
                resp.content = json.dumps({
                    "extended_summary": "GPT-5 represents a major leap in AI reasoning.",
                    "why_it_matters": "Sets new benchmarks across multiple domains.",
                })
            elif call_count == 2:
                resp.content = json.dumps([
                    f"Brief summary {i}." for i in range(4)
                ])
            else:
                resp.content = json.dumps({"insight": "AI and markets moving in tandem."})
            return resp

        with patch("briefing.summarizer._llm") as mock_llm:
            mock_llm.ainvoke = AsyncMock(side_effect=mock_ainvoke)
            summary_result = await summarize_items(items, mode="detailed")

        briefing = generate_briefing(
            user_id="pipeline-test-user",
            summary_result=summary_result,
            user_types=["ai_tech", "trader"],
        )

        assert briefing.user_id == "pipeline-test-user"
        assert briefing.item_count > 0
        assert "Daily Briefing" in briefing.markdown
        assert len(briefing.sections_json) > 0

    @pytest.mark.asyncio
    async def test_pipeline_with_duplicate_items(self):
        """Pipeline correctly deduplicates near-identical items."""
        items = [
            SourceItem(
                title="OpenAI releases GPT-5 model today",
                summary="OpenAI has released GPT-5 today with major improvements.",
                url="https://example.com/1",
                source="newsapi",
            ),
            SourceItem(
                title="OpenAI releases new GPT-5 model today",
                summary="OpenAI officially released the GPT-5 model today.",
                url="https://example.com/2",
                source="google_news",
            ),
            SourceItem(
                title="GitHub Copilot gets major update with new features",
                summary="GitHub Copilot receives major update with new features.",
                url="https://example.com/3",
                source="github",
            ),
        ]

        config = PipelineConfig(topics=[], interests=[])
        result = await run_filter_pipeline(items, config)

        assert result.stats["dedup_removed"] >= 1
        assert len(result.items) == 2

    @pytest.mark.asyncio
    async def test_pipeline_filters_clickbait(self):
        """Pipeline removes clickbait titles."""
        items = [
            SourceItem(
                title="You won't believe what happened at Google",
                summary="Clickbait article about Google.",
                url="https://example.com/bait",
                source="newsapi",
            ),
            SourceItem(
                title="Google announces new AI framework",
                summary="Google officially announces a new AI framework for developers.",
                url="https://example.com/real",
                source="newsapi",
            ),
        ]

        config = PipelineConfig(topics=[], interests=[])
        result = await run_filter_pipeline(items, config)

        assert result.stats["quality_removed"] >= 1
        titles = [item.title for item in result.items]
        assert "You won't believe what happened at Google" not in titles
