"""Tests for quality filter."""

import pytest
from sources.types import SourceItem
from filters.quality import filter_quality


def _make_item(
    title: str = "Legitimate headline about technology",
    summary: str = "A proper summary with enough content.",
    source: str = "newsapi",
    raw: dict | None = None,
) -> SourceItem:
    return SourceItem(
        title=title,
        summary=summary,
        url="https://example.com",
        source=source,
        raw=raw or {},
    )


class TestQualityFilter:
    def test_empty_list(self):
        assert filter_quality([]) == []

    def test_passes_legitimate_items(self):
        items = [
            _make_item("New breakthrough in quantum computing"),
            _make_item("RBI announces monetary policy changes"),
        ]
        result = filter_quality(items)
        assert len(result) == 2

    def test_filters_too_short_content(self):
        items = [_make_item(title="Hi", summary="")]
        result = filter_quality(items)
        assert len(result) == 0

    def test_filters_clickbait_trick(self):
        items = [_make_item(title="This one simple trick will change your life")]
        result = filter_quality(items)
        assert len(result) == 0

    def test_filters_clickbait_wont_believe(self):
        items = [_make_item(title="You won't believe what happened next")]
        result = filter_quality(items)
        assert len(result) == 0

    def test_filters_clickbait_doctors_hate(self):
        items = [_make_item(title="Doctors hate this new weight loss method")]
        result = filter_quality(items)
        assert len(result) == 0

    def test_filters_clickbait_jaw_dropping(self):
        items = [_make_item(title="Jaw-dropping results from the new AI model")]
        result = filter_quality(items)
        assert len(result) == 0

    def test_passes_legitimate_headline(self):
        items = [_make_item(title="OpenAI releases GPT-5 with improved reasoning capabilities")]
        result = filter_quality(items)
        assert len(result) == 1

    def test_filters_low_upvote_reddit(self):
        items = [_make_item(source="reddit", raw={"score": 5})]
        result = filter_quality(items)
        assert len(result) == 0

    def test_passes_high_upvote_reddit(self):
        items = [_make_item(source="reddit", raw={"score": 500})]
        result = filter_quality(items)
        assert len(result) == 1

    def test_non_reddit_skips_upvote_check(self):
        items = [_make_item(source="hackernews", raw={"score": 2})]
        result = filter_quality(items)
        assert len(result) == 1

    def test_mixed_items(self):
        items = [
            _make_item(title="Legitimate news about markets"),
            _make_item(title="You won't believe this stock tip"),
            _make_item(source="reddit", raw={"score": 3}),
            _make_item(title="RBI changes interest rate by 50bps"),
        ]
        result = filter_quality(items)
        assert len(result) == 2
