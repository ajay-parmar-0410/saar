"""Generic RSS feed fetcher for MoneyControl, Economic Times, TechCrunch."""

import xml.etree.ElementTree as ET
from html import unescape

import defusedxml.ElementTree as SafeET

import httpx

from sources.types import SourceItem, SourceResult

# Predefined RSS feeds
RSS_FEEDS: dict[str, str] = {
    "moneycontrol": "https://www.livemint.com/rss/news",
    "economic_times": "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
    "techcrunch": "https://techcrunch.com/feed/",
}


async def fetch_rss(
    feed_name: str = "moneycontrol",
    feed_url: str | None = None,
    max_items: int = 10,
) -> SourceResult:
    """Fetch items from an RSS feed."""
    url = feed_url or RSS_FEEDS.get(feed_name, "")
    if not url:
        return SourceResult(source_name=feed_name, error=f"Unknown RSS feed: {feed_name}")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            url,
            timeout=10,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Saar/1.0)"},
        )
        resp.raise_for_status()

    # Some feeds use non-UTF-8 encoding (e.g. ISO-8859-1); decode safely
    content = resp.text
    root = SafeET.fromstring(content)

    # Handle both RSS 2.0 and Atom feeds
    channel = root.find("channel")
    if channel is not None:
        return _parse_rss(channel, feed_name, max_items)

    # Try Atom format
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)
    if entries:
        return _parse_atom(entries, feed_name, max_items)

    return SourceResult(source_name=feed_name, items=())


def _parse_rss(channel: ET.Element, feed_name: str, max_items: int) -> SourceResult:
    items: list[SourceItem] = []
    for item_el in channel.findall("item")[:max_items]:
        title = item_el.findtext("title", "")
        link = item_el.findtext("link", "")
        description = unescape(item_el.findtext("description", "") or "")
        pub_date = item_el.findtext("pubDate", "")

        # Strip HTML tags from description
        import re
        clean_desc = re.sub(r"<[^>]+>", "", description)[:300]

        items.append(SourceItem(
            title=title,
            summary=clean_desc,
            url=link,
            source=feed_name,
            timestamp=pub_date,
        ))
    return SourceResult(source_name=feed_name, items=tuple(items))


def _parse_atom(entries: list[ET.Element], feed_name: str, max_items: int) -> SourceResult:
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items: list[SourceItem] = []
    for entry in entries[:max_items]:
        title = entry.findtext("atom:title", "", ns)
        link_el = entry.find("atom:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        summary = entry.findtext("atom:summary", "", ns) or entry.findtext("atom:content", "", ns) or ""
        published = entry.findtext("atom:published", "", ns) or entry.findtext("atom:updated", "", ns) or ""

        import re
        clean = re.sub(r"<[^>]+>", "", unescape(summary))[:300]

        items.append(SourceItem(
            title=title,
            summary=clean,
            url=link,
            source=feed_name,
            timestamp=published,
        ))
    return SourceResult(source_name=feed_name, items=tuple(items))
