"""NewsAPI.org fetcher."""

import os

import httpx

from sources.types import SourceItem, SourceResult


async def fetch_news_api(
    country: str = "in",
    page_size: int = 10,
) -> SourceResult:
    """Fetch top headlines from NewsAPI."""
    api_key = os.environ.get("NEWS_API_KEY", "")
    if not api_key:
        return SourceResult(source_name="newsapi", error="NEWS_API_KEY not set")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://newsapi.org/v2/top-headlines",
            params={"country": country, "pageSize": page_size, "apiKey": api_key},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()

    items = tuple(
        SourceItem(
            title=article.get("title", ""),
            summary=article.get("description", "") or "",
            url=article.get("url", ""),
            source="newsapi",
            timestamp=article.get("publishedAt", ""),
            raw=article,
        )
        for article in data.get("articles", [])
        if article.get("title") and article["title"] != "[Removed]"
    )
    return SourceResult(source_name="newsapi", items=items)
