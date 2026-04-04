"""Tests for deduplication filter."""

import pytest
from sources.types import SourceItem
from filters.dedup import deduplicate


def _make_item(title: str, source: str = "newsapi", summary: str = "Some summary", url: str = "https://example.com") -> SourceItem:
    return SourceItem(title=title, summary=summary, url=url, source=source)


class TestDeduplicate:
    def test_empty_list(self):
        assert deduplicate([]) == []

    def test_single_item(self):
        items = [_make_item("Apple launches iPhone 16")]
        result = deduplicate(items)
        assert len(result) == 1
        assert result[0].title == "Apple launches iPhone 16"

    def test_no_duplicates(self):
        items = [
            _make_item("Apple launches iPhone 16"),
            _make_item("Google launches Pixel 9"),
        ]
        result = deduplicate(items)
        assert len(result) == 2

    def test_merges_near_duplicates(self):
        items = [
            _make_item("Apple launches iPhone 16", source="newsapi"),
            _make_item("Apple unveils new iPhone 16", source="google_news"),
        ]
        result = deduplicate(items)
        assert len(result) == 1
        assert result[0].raw.get("source_count", 1) == 2

    def test_keeps_longer_summary(self):
        items = [
            _make_item("Apple launches iPhone 16", summary="Short."),
            _make_item("Apple unveils the new iPhone 16", summary="A much longer and more detailed summary of the event."),
        ]
        result = deduplicate(items)
        assert len(result) == 1
        assert "detailed" in result[0].summary

    def test_multiple_duplicates_merged(self):
        items = [
            _make_item("OpenAI releases GPT-5 model today", source="moneycontrol"),
            _make_item("OpenAI has released the GPT-5 model", source="economic_times"),
            _make_item("OpenAI releases new GPT-5 model", source="newsapi"),
            _make_item("OpenAI launches GPT-5 model today", source="google_news"),
            _make_item("OpenAI officially releases GPT-5", source="reddit"),
        ]
        result = deduplicate(items)
        assert len(result) == 1
        assert result[0].raw.get("source_count", 1) == 5

    def test_merged_sources_tracked(self):
        items = [
            _make_item("New GPT model released", source="hackernews", url="https://hn.com/1"),
            _make_item("New GPT model is released", source="reddit", url="https://reddit.com/1"),
        ]
        result = deduplicate(items)
        assert len(result) == 1
        merged = result[0].raw.get("merged_sources", [])
        assert len(merged) == 2
        sources = {m["source"] for m in merged}
        assert sources == {"hackernews", "reddit"}

    def test_case_insensitive(self):
        items = [
            _make_item("APPLE LAUNCHES IPHONE 16"),
            _make_item("apple launches iphone 16"),
        ]
        result = deduplicate(items)
        assert len(result) == 1

    def test_different_topics_not_merged(self):
        items = [
            _make_item("Apple launches iPhone 16"),
            _make_item("Google launches Pixel 9"),
            _make_item("Samsung launches Galaxy S25"),
        ]
        result = deduplicate(items)
        assert len(result) == 3
