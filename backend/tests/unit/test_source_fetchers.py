"""Unit tests for source fetchers — mocked HTTP calls."""

import os
import sys

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sources.types import SourceItem, SourceResult


# ---------------------------------------------------------------------------
# Weather
# ---------------------------------------------------------------------------


class TestWeatherFetcher:
    @pytest.mark.asyncio
    async def test_returns_weather_item(self):
        mock_data = {
            "location": {"name": "Mumbai", "country": "India"},
            "current": {
                "temp_c": 32,
                "condition": {"text": "Partly Cloudy"},
                "humidity": 75,
                "wind_kph": 12,
            },
            "forecast": {
                "forecastday": [{
                    "day": {
                        "maxtemp_c": 35,
                        "mintemp_c": 27,
                        "daily_chance_of_rain": 20,
                    }
                }]
            },
        }

        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_data
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("sources.weather.httpx.AsyncClient", return_value=mock_client), \
             patch.dict(os.environ, {"WEATHER_API_KEY": "test-key"}):
            from sources.weather import fetch_weather
            result = await fetch_weather("Mumbai")

        assert result.source_name == "weatherapi"
        assert result.error is None
        assert len(result.items) == 1
        assert "32" in result.items[0].summary
        assert "Mumbai" in result.items[0].title

    @pytest.mark.asyncio
    async def test_missing_api_key_returns_error(self):
        with patch.dict(os.environ, {"WEATHER_API_KEY": ""}):
            from sources.weather import fetch_weather
            result = await fetch_weather()

        assert result.error is not None
        assert "WEATHER_API_KEY" in result.error


# ---------------------------------------------------------------------------
# Hacker News
# ---------------------------------------------------------------------------


class TestHackerNewsFetcher:
    @pytest.mark.asyncio
    async def test_returns_items(self):
        mock_data = {
            "hits": [
                {
                    "title": "Show HN: Cool Project",
                    "url": "https://example.com",
                    "objectID": "123",
                    "created_at": "2026-04-04T12:00:00Z",
                    "points": 150,
                    "num_comments": 42,
                },
                {
                    "title": "Rust is fast",
                    "url": "https://rust.com",
                    "objectID": "456",
                    "created_at": "2026-04-04T11:00:00Z",
                    "points": 200,
                    "num_comments": 80,
                },
            ]
        }

        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_data
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("sources.hackernews.httpx.AsyncClient", return_value=mock_client):
            from sources.hackernews import fetch_hackernews
            result = await fetch_hackernews(max_items=5)

        assert result.source_name == "hackernews"
        assert result.error is None
        assert len(result.items) == 2
        assert result.items[0].title == "Show HN: Cool Project"
        assert result.items[0].raw["points"] == 150

    @pytest.mark.asyncio
    async def test_skips_items_without_title(self):
        mock_data = {
            "hits": [
                {"title": "Valid", "url": "https://a.com", "objectID": "1"},
                {"title": "", "url": "https://b.com", "objectID": "2"},
                {"url": "https://c.com", "objectID": "3"},
            ]
        }

        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_data
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("sources.hackernews.httpx.AsyncClient", return_value=mock_client):
            from sources.hackernews import fetch_hackernews
            result = await fetch_hackernews()

        assert len(result.items) == 1
        assert result.items[0].title == "Valid"


# ---------------------------------------------------------------------------
# Currency
# ---------------------------------------------------------------------------


class TestCurrencyFetcher:
    @pytest.mark.asyncio
    async def test_returns_exchange_rate(self):
        mock_data = {
            "rates": {
                "INR": 83.5,
                "EUR": 0.92,
                "GBP": 0.79,
                "JPY": 150.2,
                "AED": 3.67,
            }
        }

        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_data
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("sources.currency.httpx.AsyncClient", return_value=mock_client):
            from sources.currency import fetch_currency
            result = await fetch_currency("USD")

        assert result.source_name == "exchangerate"
        assert result.error is None
        assert len(result.items) == 1
        assert "INR" in result.items[0].summary


# ---------------------------------------------------------------------------
# Source types
# ---------------------------------------------------------------------------


class TestSourceTypes:
    def test_source_item_frozen(self):
        item = SourceItem(title="Test", summary="Sum", url="https://a.com", source="test")
        with pytest.raises(AttributeError):
            item.title = "Modified"

    def test_source_result_frozen(self):
        result = SourceResult(source_name="test")
        with pytest.raises(AttributeError):
            result.source_name = "other"

    def test_source_item_defaults(self):
        item = SourceItem(title="T", summary="S", url="https://a.com", source="s")
        assert item.raw == {}
        assert item.timestamp is not None

    def test_source_result_defaults(self):
        result = SourceResult(source_name="test")
        assert result.items == ()
        assert result.error is None
