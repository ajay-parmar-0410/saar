"""Product Hunt fetcher via Atom feed."""

import re
import xml.etree.ElementTree as StdET

import defusedxml.ElementTree as ET
from html import unescape

import httpx

from sources.types import SourceItem, SourceResult

PH_FEED = "https://www.producthunt.com/feed"

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


async def fetch_producthunt(max_items: int = 10) -> SourceResult:
    """Fetch latest product launches from Product Hunt feed.

    Product Hunt serves Atom XML, not RSS 2.0.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(
            PH_FEED,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Saar/1.0)"},
            timeout=10,
        )
        resp.raise_for_status()

    root = ET.fromstring(resp.text)

    # Try Atom format first (current PH format)
    entries = root.findall("atom:entry", ATOM_NS)
    if entries:
        return _parse_atom(entries, max_items)

    # Fallback: RSS 2.0 format
    channel = root.find("channel")
    if channel is not None:
        return _parse_rss(channel, max_items)

    return SourceResult(source_name="producthunt", items=())


def _parse_atom(entries: list[StdET.Element], max_items: int) -> SourceResult:
    """Parse Atom entries into SourceResult."""
    items: list[SourceItem] = []
    for entry in entries[:max_items]:
        title = entry.findtext("atom:title", "", ATOM_NS)
        link_el = entry.find("atom:link", ATOM_NS)
        link = link_el.get("href", "") if link_el is not None else ""
        raw_summary = (
            entry.findtext("atom:summary", "", ATOM_NS)
            or entry.findtext("atom:content", "", ATOM_NS)
            or ""
        )
        clean_summary = re.sub(r"<[^>]+>", "", unescape(raw_summary))[:300]
        published = (
            entry.findtext("atom:published", "", ATOM_NS)
            or entry.findtext("atom:updated", "", ATOM_NS)
            or ""
        )

        items.append(SourceItem(
            title=title,
            summary=clean_summary,
            url=link,
            source="producthunt",
            timestamp=published,
        ))

    return SourceResult(source_name="producthunt", items=tuple(items))


def _parse_rss(channel: StdET.Element, max_items: int) -> SourceResult:
    """Fallback: parse RSS 2.0 channel."""
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
