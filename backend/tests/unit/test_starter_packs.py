"""Tests for starter pack configuration."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from config.starter_packs import (
    VALID_USER_TYPES,
    get_combined_starter_pack,
    get_starter_pack,
)


class TestGetStarterPack:
    def test_ai_tech_pack(self):
        pack = get_starter_pack("ai_tech")
        assert "github" in pack.sources
        assert "arxiv" in pack.sources
        assert "artificial_intelligence" in pack.topics

    def test_general_pack(self):
        pack = get_starter_pack("general")
        assert "weatherapi" in pack.sources
        assert "newsapi" in pack.sources
        assert "weather" in pack.topics

    def test_trader_pack(self):
        pack = get_starter_pack("trader")
        assert "yahoo_finance" in pack.sources
        assert "indian_markets" in pack.topics

    def test_invalid_type_raises(self):
        with pytest.raises(KeyError, match="Unknown user type"):
            get_starter_pack("invalid_type")


class TestGetCombinedStarterPack:
    def test_single_type(self):
        pack = get_combined_starter_pack(["ai_tech"])
        single = get_starter_pack("ai_tech")
        assert set(pack.topics) == set(single.topics)
        assert set(pack.sources) == set(single.sources)

    def test_multiple_types_combined(self):
        pack = get_combined_starter_pack(["ai_tech", "trader"])
        assert "github" in pack.sources
        assert "yahoo_finance" in pack.sources
        assert "artificial_intelligence" in pack.topics
        assert "indian_markets" in pack.topics

    def test_no_duplicates(self):
        pack = get_combined_starter_pack(["general", "trader"])
        # "currency" appears in both topic lists
        assert pack.topics.count("currency") == 1
        # "exchangerate" appears in both source lists
        assert pack.sources.count("exchangerate") == 1

    def test_empty_types(self):
        pack = get_combined_starter_pack([])
        assert pack.topics == ()
        assert pack.sources == ()

    def test_all_types_combined(self):
        pack = get_combined_starter_pack(list(VALID_USER_TYPES))
        assert len(pack.topics) > 0
        assert len(pack.sources) > 0
        # No duplicates
        assert len(pack.topics) == len(set(pack.topics))
        assert len(pack.sources) == len(set(pack.sources))
