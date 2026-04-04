"""Reddit API fetcher."""

import httpx

from sources.types import SourceItem, SourceResult

DEFAULT_SUBREDDITS = {
    "ai_tech": ["MachineLearning", "LocalLLaMA", "technology", "programming"],
    "general": ["worldnews", "popular", "todayilearned"],
    "trader": ["IndianStreetBets", "IndianStockMarket", "stocks"],
}


async def fetch_reddit(
    subreddits: list[str] | None = None,
    user_type: str = "general",
    min_upvotes: int = 50,
    max_items: int = 10,
) -> SourceResult:
    """Fetch top posts from specified subreddits."""
    subs = subreddits or DEFAULT_SUBREDDITS.get(user_type, DEFAULT_SUBREDDITS["general"])

    all_items: list[SourceItem] = []

    async with httpx.AsyncClient() as client:
        for sub in subs:
            try:
                resp = await client.get(
                    f"https://www.reddit.com/r/{sub}/hot.json",
                    params={"limit": 15, "t": "day"},
                    headers={"User-Agent": "Saar/1.0"},
                    timeout=5,
                )
                resp.raise_for_status()
                data = resp.json()

                for post in data.get("data", {}).get("children", []):
                    pd = post.get("data", {})
                    ups = pd.get("ups", 0)
                    if ups < min_upvotes:
                        continue
                    if pd.get("stickied"):
                        continue

                    all_items.append(SourceItem(
                        title=pd.get("title", ""),
                        summary=pd.get("selftext", "")[:300] or pd.get("title", ""),
                        url=f"https://reddit.com{pd.get('permalink', '')}",
                        source="reddit",
                        timestamp=str(pd.get("created_utc", "")),
                        raw={"subreddit": sub, "ups": ups, "num_comments": pd.get("num_comments", 0)},
                    ))
            except Exception:
                continue

    # Sort by upvotes, take top N
    all_items.sort(key=lambda x: x.raw.get("ups", 0), reverse=True)
    return SourceResult(source_name="reddit", items=tuple(all_items[:max_items]))
