"""Integration tests for source fetchers — calls real APIs."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


@pytest.mark.asyncio
async def test_weather_fetcher():
    from sources.weather import fetch_weather
    result = await fetch_weather("Mumbai")
    assert result.source_name == "weatherapi"
    assert result.error is None
    assert len(result.items) == 1
    assert "°C" in result.items[0].summary


@pytest.mark.asyncio
async def test_news_api_fetcher():
    from sources.news_api import fetch_news_api
    result = await fetch_news_api(page_size=3)
    assert result.source_name == "newsapi"
    assert result.error is None
    # NewsAPI free tier may return empty results depending on region/rate limits
    if result.items:
        assert all(item.url for item in result.items)


@pytest.mark.asyncio
async def test_hackernews_fetcher():
    from sources.hackernews import fetch_hackernews
    result = await fetch_hackernews(max_items=5)
    assert result.source_name == "hackernews"
    assert result.error is None
    assert len(result.items) > 0


@pytest.mark.asyncio
async def test_currency_fetcher():
    from sources.currency import fetch_currency
    result = await fetch_currency("USD")
    assert result.source_name == "exchangerate"
    assert result.error is None
    assert len(result.items) == 1
    assert "INR" in result.items[0].summary


@pytest.mark.asyncio
async def test_huggingface_fetcher():
    from sources.huggingface import fetch_huggingface
    result = await fetch_huggingface(max_items=3)
    assert result.source_name == "huggingface"
    assert result.error is None
    assert len(result.items) > 0


@pytest.mark.asyncio
async def test_arxiv_fetcher():
    from sources.arxiv import fetch_arxiv
    result = await fetch_arxiv(max_items=3)
    assert result.source_name == "arxiv"
    assert result.error is None
    assert len(result.items) > 0


@pytest.mark.asyncio
async def test_google_news_fetcher():
    from sources.news_google import fetch_google_news
    result = await fetch_google_news(max_items=3)
    assert result.source_name == "google_news"
    assert result.error is None
    assert len(result.items) > 0


@pytest.mark.asyncio
async def test_source_returns_standardized_format():
    """All sources should return items with required fields."""
    from sources.hackernews import fetch_hackernews
    result = await fetch_hackernews(max_items=2)
    for item in result.items:
        assert item.title
        assert item.source
        assert isinstance(item.summary, str)
        assert isinstance(item.url, str)


@pytest.mark.asyncio
async def test_fetcher_handles_error_gracefully():
    """A source with bad config should return error, not crash."""
    from sources.weather import fetch_weather
    # Temporarily clear the API key
    original = os.environ.get("WEATHER_API_KEY", "")
    os.environ["WEATHER_API_KEY"] = ""
    result = await fetch_weather()
    os.environ["WEATHER_API_KEY"] = original
    assert result.error is not None
