"""Hacker News fetcher via Algolia API."""

import httpx

from sources.types import SourceItem, SourceResult

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"


async def fetch_hackernews(
    max_items: int = 10,
) -> SourceResult:
    """Fetch top stories from Hacker News."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            HN_SEARCH_URL,
            params={
                "tags": "front_page",
                "hitsPerPage": max_items,
            },
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()

    items = tuple(
        SourceItem(
            title=hit.get("title", ""),
            summary=hit.get("title", ""),
            url=hit.get("url", "") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
            source="hackernews",
            timestamp=hit.get("created_at", ""),
            raw={"points": hit.get("points", 0), "num_comments": hit.get("num_comments", 0)},
        )
        for hit in data.get("hits", [])
        if hit.get("title")
    )
    return SourceResult(source_name="hackernews", items=items)
