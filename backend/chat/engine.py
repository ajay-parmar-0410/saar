"""Chat engine — query-aware source search + LLM response with citations."""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from sources.types import SourceItem

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChatSource:
    """A cited source in a chat response."""

    title: str
    url: str
    source: str


@dataclass(frozen=True)
class ChatResult:
    """Result from the chat engine."""

    response: str
    sources: tuple[ChatSource, ...] = ()


# ---------------------------------------------------------------------------
# Source search helpers
# ---------------------------------------------------------------------------

async def _search_google_news(query: str, max_items: int = 5) -> list[SourceItem]:
    """Search Google News RSS for items matching the query."""
    from sources.news_google import fetch_google_news

    try:
        result = await fetch_google_news(topic=query, max_items=max_items)
        return list(result.items)
    except Exception as e:
        logger.warning("Google News search failed: %s", e)
        return []


async def _search_hackernews(query: str, max_items: int = 5) -> list[SourceItem]:
    """Search Hacker News Algolia for items matching the query."""
    import httpx
    from sources.types import SourceItem as SI

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://hn.algolia.com/api/v1/search",
                params={"query": query, "hitsPerPage": max_items},
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()

        items: list[SI] = []
        for hit in data.get("hits", []):
            title = hit.get("title", "")
            if not title:
                continue
            items.append(SI(
                title=title,
                summary=title,
                url=hit.get("url", "")
                or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                source="hackernews",
                timestamp=hit.get("created_at", ""),
                raw={"points": hit.get("points", 0)},
            ))
        return items
    except Exception as e:
        logger.warning("HN search failed: %s", e)
        return []


async def _search_newsapi(query: str, max_items: int = 5) -> list[SourceItem]:
    """Search NewsAPI for items matching the query."""
    import os
    import httpx

    api_key = os.environ.get("NEWS_API_KEY", "")
    if not api_key:
        return []

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "pageSize": max_items,
                    "sortBy": "relevancy",
                    "apiKey": api_key,
                },
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()

        return [
            SourceItem(
                title=a.get("title", ""),
                summary=a.get("description", "") or "",
                url=a.get("url", ""),
                source="newsapi",
                timestamp=a.get("publishedAt", ""),
            )
            for a in data.get("articles", [])
            if a.get("title") and a["title"] != "[Removed]"
        ]
    except Exception as e:
        logger.warning("NewsAPI search failed: %s", e)
        return []


async def search_sources_for_query(query: str) -> list[SourceItem]:
    """Search multiple sources in parallel for items related to the query.

    Returns a deduplicated, combined list of source items.
    """
    results = await asyncio.gather(
        _search_google_news(query),
        _search_hackernews(query),
        _search_newsapi(query),
        return_exceptions=True,
    )

    combined: list[SourceItem] = []
    seen_urls: set[str] = set()

    for result in results:
        if isinstance(result, Exception):
            logger.warning("Source search raised: %s", result)
            continue
        for item in result:
            if item.url and item.url not in seen_urls:
                seen_urls.add(item.url)
                combined.append(item)

    return combined[:10]  # Cap at 10 items


# ---------------------------------------------------------------------------
# Context builders
# ---------------------------------------------------------------------------

def _build_briefing_context(latest_briefing: dict[str, Any] | None) -> str:
    """Extract useful context from today's briefing."""
    if not latest_briefing:
        return ""

    parts: list[str] = []

    top_story = latest_briefing.get("top_story", "")
    if top_story:
        parts.append(f"Today's top story: {top_story}")

    sections = latest_briefing.get("sections", [])
    if sections:
        headlines: list[str] = []
        for section in sections[:5]:
            section_title = section.get("title", "")
            items = section.get("items", [])
            for item in items[:3]:
                title = item.get("title", "") if isinstance(item, dict) else str(item)
                if title:
                    headlines.append(f"  - [{section_title}] {title}")
        if headlines:
            parts.append("Today's briefing headlines:\n" + "\n".join(headlines))

    return "\n\n".join(parts)


def _build_user_context(
    preferences: dict[str, Any] | None,
    interests: list[dict[str, Any]] | None,
) -> str:
    """Build context string from user preferences and interests."""
    parts: list[str] = []

    if preferences:
        topics = preferences.get("topics", [])
        if topics:
            parts.append(f"User's topics of interest: {', '.join(topics)}")
        sources = preferences.get("sources", [])
        if sources:
            parts.append(f"User's preferred sources: {', '.join(sources)}")

    if interests:
        watchlist = [f"{i.get('type', '')}:{i.get('value', '')}" for i in interests]
        if watchlist:
            parts.append(f"User's watchlist: {', '.join(watchlist)}")

    return "\n".join(parts)


def _build_conversation_context(recent_context: list[dict[str, Any]]) -> str:
    """Build conversation history string for follow-up support."""
    if not recent_context:
        return ""

    lines: list[str] = []
    for entry in recent_context[-5:]:
        lines.append(f"User: {entry['query']}")
        # Truncate long responses to save context window
        resp = entry.get("response", "")
        lines.append(f"Assistant: {resp[:300]}")

    return "Recent conversation:\n" + "\n".join(lines)


def _build_source_context(items: list[SourceItem]) -> str:
    """Format searched source items as context for the LLM."""
    if not items:
        return ""

    lines: list[str] = []
    for i, item in enumerate(items, 1):
        lines.append(
            f"[{i}] ({item.source}) {item.title}\n"
            f"    {item.summary[:200]}\n"
            f"    URL: {item.url}"
        )

    return "Relevant sources found:\n" + "\n".join(lines)


# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are Saar, a helpful personalized daily briefing assistant.
Your job is to answer the user's question accurately and concisely using the provided context and sources.

Rules:
- If relevant sources are provided, cite them by mentioning the source name in your answer.
- If the user asks about today's briefing, use the briefing context provided.
- If the user is following up on a previous question, use the conversation context.
- If you cannot find relevant information, say so honestly — do not make up facts.
- Keep responses concise but informative (2-4 paragraphs max).
- When citing sources, mention them naturally (e.g., "According to HackerNews..." or "A report from NewsAPI...")."""


async def generate_chat_response(
    query: str,
    user_id: str,
    preferences: dict[str, Any] | None = None,
    interests: list[dict[str, Any]] | None = None,
    latest_briefing: dict[str, Any] | None = None,
    recent_context: list[dict[str, Any]] | None = None,
) -> ChatResult:
    """Generate a chat response with source citations.

    1. Search sources in parallel for query-relevant content.
    2. Build full context (user prefs, briefing, conversation, sources).
    3. Call LLM with context + query.
    4. Return response + source citations.
    """
    # Step 1: Search sources
    searched_items = await search_sources_for_query(query)

    # Step 2: Build context blocks
    context_blocks: list[str] = []

    user_ctx = _build_user_context(preferences, interests)
    if user_ctx:
        context_blocks.append(user_ctx)

    briefing_ctx = _build_briefing_context(latest_briefing)
    if briefing_ctx:
        context_blocks.append(briefing_ctx)

    conv_ctx = _build_conversation_context(recent_context or [])
    if conv_ctx:
        context_blocks.append(conv_ctx)

    source_ctx = _build_source_context(searched_items)
    if source_ctx:
        context_blocks.append(source_ctx)

    full_context = "\n\n---\n\n".join(context_blocks)

    # Step 3: Call LLM
    user_message = f"""Context:
{full_context}

User question: {query}"""

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3)

    try:
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ])
        response_text = str(response.content)
    except Exception as e:
        logger.error("Chat LLM call failed: %s", e)
        return ChatResult(
            response="I'm sorry, I couldn't process your request right now. Please try again.",
        )

    # Step 4: Build source citations from searched items
    sources = tuple(
        ChatSource(title=item.title, url=item.url, source=item.source)
        for item in searched_items
        if item.url
    )

    return ChatResult(response=response_text, sources=sources)
