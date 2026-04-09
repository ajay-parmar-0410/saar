"""NewsAPI.org fetcher."""

import os

import httpx

from sources.types import SourceItem, SourceResult

BASE_URL = "https://newsapi.org/v2"


async def fetch_news_api(
    country: str = "in",
    page_size: int = 10,
) -> SourceResult:
    """Fetch top headlines from NewsAPI.

    Falls back to /everything endpoint with India-relevant keywords
    when /top-headlines returns empty (free-tier limitation for some regions).
    """
    api_key = os.environ.get("NEWS_API_KEY", "")
    if not api_key:
        return SourceResult(source_name="newsapi", error="NEWS_API_KEY not set")

    async with httpx.AsyncClient() as client:
        # Try top-headlines first
        resp = await client.get(
            f"{BASE_URL}/top-headlines",
            params={"country": country, "pageSize": page_size, "apiKey": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        articles = data.get("articles", [])

        # Fallback: /everything with India keywords if top-headlines is empty
        if not articles:
            resp = await client.get(
                f"{BASE_URL}/everything",
                params={
                    "q": "India OR Mumbai OR Delhi OR Bengaluru",
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": page_size,
                    "apiKey": api_key,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            articles = data.get("articles", [])

    items = tuple(
        SourceItem(
            title=article.get("title", ""),
            summary=article.get("description", "") or "",
            url=article.get("url", ""),
            source="newsapi",
            timestamp=article.get("publishedAt", ""),
            raw=article,
        )
        for article in articles
        if article.get("title") and article["title"] != "[Removed]"
    )
    return SourceResult(source_name="newsapi", items=items)
