"""Google News RSS fetcher."""

import xml.etree.ElementTree as ET
from html import unescape

import httpx

from sources.types import SourceItem, SourceResult

GOOGLE_NEWS_RSS = "https://news.google.com/rss"


async def fetch_google_news(
    topic: str = "",
    country: str = "IN",
    lang: str = "en",
    max_items: int = 10,
) -> SourceResult:
    """Fetch headlines from Google News RSS."""
    params = {"hl": f"{lang}-{country}", "gl": country, "ceid": f"{country}:{lang}"}

    url = f"{GOOGLE_NEWS_RSS}/search?q={topic}" if topic else GOOGLE_NEWS_RSS
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=5)
        resp.raise_for_status()

    root = ET.fromstring(resp.text)
    channel = root.find("channel")
    if channel is None:
        return SourceResult(source_name="google_news", items=())

    items: list[SourceItem] = []
    for item_el in channel.findall("item")[:max_items]:
        title = item_el.findtext("title", "")
        link = item_el.findtext("link", "")
        pub_date = item_el.findtext("pubDate", "")
        description = unescape(item_el.findtext("description", "") or "")

        items.append(SourceItem(
            title=title,
            summary=description[:300],
            url=link,
            source="google_news",
            timestamp=pub_date,
        ))

    return SourceResult(source_name="google_news", items=tuple(items))
