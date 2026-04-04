"""Tests for the source registry."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sources.registry import SOURCE_REGISTRY, get_fetchers_for_sources


class TestGetFetchersForSources:
    def test_known_sources(self):
        fetchers = get_fetchers_for_sources(["github", "hackernews", "newsapi"])
        assert len(fetchers) == 3
        names = [f[0] for f in fetchers]
        assert "github" in names
        assert "hackernews" in names
        assert "newsapi" in names

    def test_unknown_source_skipped(self):
        fetchers = get_fetchers_for_sources(["github", "nonexistent"])
        assert len(fetchers) == 1
        assert fetchers[0][0] == "github"

    def test_empty_list(self):
        fetchers = get_fetchers_for_sources([])
        assert len(fetchers) == 0

    def test_ai_tech_sources(self):
        """AI/Tech user should get all 7 expected sources."""
        ai_sources = ["github", "hackernews", "reddit", "arxiv", "producthunt", "techcrunch", "huggingface"]
        fetchers = get_fetchers_for_sources(ai_sources)
        assert len(fetchers) == 7

    def test_general_sources(self):
        """General user should get all 5 expected sources."""
        general_sources = ["weatherapi", "google_news", "newsapi", "reddit_trending", "exchangerate"]
        fetchers = get_fetchers_for_sources(general_sources)
        assert len(fetchers) == 5

    def test_trader_sources(self):
        """Trader user should get all 5 expected sources."""
        trader_sources = ["yahoo_finance", "moneycontrol", "economic_times", "exchangerate", "reddit_finance"]
        fetchers = get_fetchers_for_sources(trader_sources)
        assert len(fetchers) == 5

    def test_all_registry_entries_have_callables(self):
        """Every entry in the registry should have a callable fetcher."""
        for name, (fn, kwargs) in SOURCE_REGISTRY.items():
            assert callable(fn), f"{name} fetcher is not callable"
            assert isinstance(kwargs, dict), f"{name} kwargs is not a dict"
