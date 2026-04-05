"""Arxiv API fetcher for AI/ML papers."""

import defusedxml.ElementTree as ET

import httpx

from sources.types import SourceItem, SourceResult

ARXIV_API = "https://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom"}


async def fetch_arxiv(
    query: str = "cat:cs.AI OR cat:cs.LG OR cat:cs.CL",
    max_items: int = 10,
) -> SourceResult:
    """Fetch recent papers from Arxiv."""
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(
            ARXIV_API,
            params={
                "search_query": query,
                "start": 0,
                "max_results": max_items,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            },
            timeout=10,
        )
        resp.raise_for_status()

    root = ET.fromstring(resp.text)
    entries = root.findall("atom:entry", NS)

    items = tuple(
        SourceItem(
            title=entry.findtext("atom:title", "", NS).strip().replace("\n", " "),
            summary=entry.findtext("atom:summary", "", NS).strip()[:300].replace("\n", " "),
            url=entry.findtext("atom:id", "", NS),
            source="arxiv",
            timestamp=entry.findtext("atom:published", "", NS),
            raw={"authors": [a.findtext("atom:name", "", NS) for a in entry.findall("atom:author", NS)]},
        )
        for entry in entries
    )
    return SourceResult(source_name="arxiv", items=items)
