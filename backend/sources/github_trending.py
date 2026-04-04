"""GitHub trending repos fetcher via API search."""

import os
from datetime import datetime, timedelta, timezone

import httpx

from sources.types import SourceItem, SourceResult


async def fetch_github_trending(
    language: str = "",
    max_items: int = 10,
) -> SourceResult:
    """Fetch trending repositories from the last 7 days."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    query = f"created:>{since} stars:>10"
    if language:
        query += f" language:{language}"

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.github.com/search/repositories",
            params={"q": query, "sort": "stars", "order": "desc", "per_page": max_items},
            headers=headers,
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()

    items = tuple(
        SourceItem(
            title=f"{repo['full_name']} ({repo.get('stargazers_count', 0)} stars)",
            summary=repo.get("description", "") or "No description",
            url=repo.get("html_url", ""),
            source="github",
            timestamp=repo.get("created_at", ""),
            raw={"stars": repo.get("stargazers_count", 0), "language": repo.get("language", "")},
        )
        for repo in data.get("items", [])
    )
    return SourceResult(source_name="github", items=items)
