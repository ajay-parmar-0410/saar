"""Source registry — maps source names to fetcher functions."""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from functools import partial
from typing import Any

from sources.retry import with_retry
from sources.types import SourceResult

from sources.weather import fetch_weather
from sources.news_api import fetch_news_api
from sources.news_google import fetch_google_news
from sources.reddit import fetch_reddit
from sources.github_trending import fetch_github_trending
from sources.hackernews import fetch_hackernews
from sources.arxiv import fetch_arxiv
from sources.producthunt import fetch_producthunt
from sources.huggingface import fetch_huggingface
from sources.yahoo_finance import fetch_yahoo_finance
from sources.rss_feed import fetch_rss
from sources.currency import fetch_currency

logger = logging.getLogger(__name__)

# Type alias for fetcher functions
Fetcher = Callable[..., Coroutine[Any, Any, SourceResult]]

# Registry: source name → (fetcher function, default kwargs)
SOURCE_REGISTRY: dict[str, tuple[Fetcher, dict[str, Any]]] = {
    "weatherapi": (fetch_weather, {}),
    "newsapi": (fetch_news_api, {}),
    "google_news": (fetch_google_news, {}),
    "reddit": (fetch_reddit, {}),
    "reddit_trending": (fetch_reddit, {"subreddits": ["popular", "worldnews"]}),
    "reddit_finance": (fetch_reddit, {"subreddits": ["IndianStreetBets", "IndianStockMarket", "stocks"]}),
    "github": (fetch_github_trending, {}),
    "hackernews": (fetch_hackernews, {}),
    "arxiv": (fetch_arxiv, {}),
    "producthunt": (fetch_producthunt, {}),
    "huggingface": (fetch_huggingface, {}),
    "yahoo_finance": (fetch_yahoo_finance, {}),
    "moneycontrol": (fetch_rss, {"feed_name": "moneycontrol"}),
    "economic_times": (fetch_rss, {"feed_name": "economic_times"}),
    "techcrunch": (fetch_rss, {"feed_name": "techcrunch"}),
    "exchangerate": (fetch_currency, {}),
}


def get_fetchers_for_sources(source_names: list[str]) -> list[tuple[str, Fetcher, dict[str, Any]]]:
    """Return fetcher functions for the given source names.

    Unknown source names are skipped with a warning.
    """
    fetchers: list[tuple[str, Fetcher, dict[str, Any]]] = []
    for name in source_names:
        if name in SOURCE_REGISTRY:
            fn, kwargs = SOURCE_REGISTRY[name]
            fetchers.append((name, fn, kwargs))
        else:
            logger.warning("Unknown source '%s' — skipping", name)
    return fetchers


async def fetch_all_sources(
    source_names: list[str],
    location: str = "Mumbai",
    user_type: str = "general",
    watchlist_symbols: list[str] | None = None,
) -> list[SourceResult]:
    """Fetch data from all specified sources in parallel.

    Returns a list of SourceResult, one per source.
    Failed sources return SourceResult with error field set.
    """
    fetchers = get_fetchers_for_sources(source_names)

    async def _run_fetcher(
        name: str, fn: Fetcher, kwargs: dict[str, Any]
    ) -> SourceResult:
        # Inject context-specific params
        if name == "weatherapi":
            kwargs = {**kwargs, "location": location}
        elif name in ("reddit", "reddit_trending", "reddit_finance"):
            kwargs = {**kwargs, "user_type": user_type}
        elif name == "yahoo_finance" and watchlist_symbols:
            kwargs = {**kwargs, "symbols": watchlist_symbols}

        return await with_retry(
            partial(fn, **kwargs),
            source_name=name,
        )

    tasks = [_run_fetcher(name, fn, kwargs) for name, fn, kwargs in fetchers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    final: list[SourceResult] = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            name = fetchers[i][0]
            logger.error("Source '%s' raised exception: %s", name, result)
            final.append(SourceResult(source_name=name, error=str(result)))
        else:
            final.append(result)

    return final
