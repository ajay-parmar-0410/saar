"""Product Hunt fetcher via RSS."""

import defusedxml.ElementTree as ET
from html import unescape

import httpx

from sources.types import SourceItem, SourceResult

PH_RSS = "https://www.producthunt.com/feed"


async def fetch_producthunt(max_items: int = 10) -> SourceResult:
    """Fetch latest product launches from Product Hunt RSS."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(PH_RSS, timeout=5)
        resp.raise_for_status()

    root = ET.fromstring(resp.text)
    channel = root.find("channel")
    if channel is None:
        return SourceResult(source_name="producthunt", items=())

    items: list[SourceItem] = []
    for item_el in channel.findall("item")[:max_items]:
        title = item_el.findtext("title", "")
        link = item_el.findtext("link", "")
        description = unescape(item_el.findtext("description", "") or "")
        pub_date = item_el.findtext("pubDate", "")

        items.append(SourceItem(
            title=title,
            summary=description[:300],
            url=link,
            source="producthunt",
            timestamp=pub_date,
        ))

    return SourceResult(source_name="producthunt", items=tuple(items))
