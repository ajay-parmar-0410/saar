"""HuggingFace trending models fetcher."""

import httpx

from sources.types import SourceItem, SourceResult

HF_API = "https://huggingface.co/api/models"


async def fetch_huggingface(max_items: int = 10) -> SourceResult:
    """Fetch trending models from HuggingFace."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            HF_API,
            params={"sort": "trendingScore", "direction": "-1", "limit": max_items},
            timeout=5,
        )
        resp.raise_for_status()
        models = resp.json()

    items = tuple(
        SourceItem(
            title=model.get("modelId", ""),
            summary=f"Pipeline: {model.get('pipeline_tag', 'N/A')}. "
                    f"Downloads: {model.get('downloads', 0):,}. "
                    f"Likes: {model.get('likes', 0)}.",
            url=f"https://huggingface.co/{model.get('modelId', '')}",
            source="huggingface",
            raw={"downloads": model.get("downloads", 0), "likes": model.get("likes", 0)},
        )
        for model in models
        if model.get("modelId")
    )
    return SourceResult(source_name="huggingface", items=items)
