"""Reddit API fetcher — uses OAuth app-only token to avoid cloud IP blocks."""

import logging
import os

import httpx

from sources.types import SourceItem, SourceResult

logger = logging.getLogger(__name__)

DEFAULT_SUBREDDITS = {
    "ai_tech": ["MachineLearning", "LocalLLaMA", "technology", "programming"],
    "general": ["worldnews", "popular", "todayilearned"],
    "trader": ["IndianStreetBets", "IndianStockMarket", "stocks"],
}

OAUTH_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
OAUTH_API_BASE = "https://oauth.reddit.com"
PUBLIC_API_BASE = "https://www.reddit.com"

USER_AGENT = "Saar:v1.0 (by /u/saar-app)"


async def _get_oauth_token(client: httpx.AsyncClient) -> str | None:
    """Get app-only OAuth token using client credentials.

    Requires REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET env vars.
    Returns None if credentials are missing or auth fails.
    """
    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return None

    try:
        resp = await client.post(
            OAUTH_TOKEN_URL,
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get("access_token")
    except Exception as e:
        logger.warning("Reddit OAuth failed: %s", e)
        return None


async def fetch_reddit(
    subreddits: list[str] | None = None,
    user_type: str = "general",
    min_upvotes: int = 50,
    max_items: int = 10,
) -> SourceResult:
    """Fetch top posts from specified subreddits.

    Uses OAuth API if credentials are available (works from cloud IPs),
    falls back to public JSON API otherwise.
    """
    subs = subreddits or DEFAULT_SUBREDDITS.get(user_type, DEFAULT_SUBREDDITS["general"])

    all_items: list[SourceItem] = []

    async with httpx.AsyncClient() as client:
        # Try OAuth first (required for cloud/server environments)
        token = await _get_oauth_token(client)
        if token:
            base_url = OAUTH_API_BASE
            headers = {"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT}
        else:
            base_url = PUBLIC_API_BASE
            headers = {"User-Agent": USER_AGENT}

        for sub in subs:
            try:
                resp = await client.get(
                    f"{base_url}/r/{sub}/hot.json",
                    params={"limit": 15, "t": "day"},
                    headers=headers,
                    timeout=10,
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
