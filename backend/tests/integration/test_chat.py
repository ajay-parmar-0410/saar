"""Integration tests for the chat engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chat.engine import (
    ChatResult,
    ChatSource,
    generate_chat_response,
    search_sources_for_query,
    _build_briefing_context,
    _build_user_context,
    _build_conversation_context,
    _build_source_context,
)
from sources.types import SourceItem


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_source_item(
    title: str = "Test Article",
    url: str = "https://example.com/article",
    source: str = "newsapi",
    summary: str = "Article summary.",
) -> SourceItem:
    return SourceItem(
        title=title,
        summary=summary,
        url=url,
        source=source,
    )


def _mock_llm_response(content: str) -> MagicMock:
    resp = MagicMock()
    resp.content = content
    return resp


# ---------------------------------------------------------------------------
# Context builder tests
# ---------------------------------------------------------------------------

class TestBuildBriefingContext:
    def test_none_briefing(self):
        assert _build_briefing_context(None) == ""

    def test_with_top_story(self):
        briefing = {"top_story": "AI models break new benchmark"}
        ctx = _build_briefing_context(briefing)
        assert "AI models break new benchmark" in ctx

    def test_with_sections(self):
        briefing = {
            "top_story": "",
            "sections": [
                {
                    "title": "Tech",
                    "items": [
                        {"title": "New GPU released"},
                        {"title": "Python 4.0 announced"},
                    ],
                },
            ],
        }
        ctx = _build_briefing_context(briefing)
        assert "New GPU released" in ctx
        assert "[Tech]" in ctx

    def test_empty_briefing(self):
        assert _build_briefing_context({}) == ""


class TestBuildUserContext:
    def test_none_preferences(self):
        assert _build_user_context(None, None) == ""

    def test_with_topics(self):
        prefs = {"topics": ["ai", "markets"]}
        ctx = _build_user_context(prefs, None)
        assert "ai" in ctx
        assert "markets" in ctx

    def test_with_interests(self):
        interests = [
            {"type": "stock", "value": "AAPL"},
            {"type": "repo", "value": "langchain-ai/langchain"},
        ]
        ctx = _build_user_context(None, interests)
        assert "AAPL" in ctx
        assert "langchain" in ctx


class TestBuildConversationContext:
    def test_empty_context(self):
        assert _build_conversation_context([]) == ""

    def test_with_entries(self):
        entries = [
            {"query": "What's happening with AI?", "response": "Several new models..."},
            {"query": "Tell me more", "response": "Specifically, Llama 4..."},
        ]
        ctx = _build_conversation_context(entries)
        assert "What's happening with AI?" in ctx
        assert "Tell me more" in ctx
        assert "Llama 4" in ctx

    def test_truncates_long_responses(self):
        entries = [{"query": "Q", "response": "x" * 500}]
        ctx = _build_conversation_context(entries)
        # Response truncated to 300 chars
        assert len(ctx) < 500


class TestBuildSourceContext:
    def test_empty_items(self):
        assert _build_source_context([]) == ""

    def test_formats_items(self):
        items = [
            _make_source_item(title="Article One", source="newsapi", url="https://a.com"),
            _make_source_item(title="Article Two", source="hackernews", url="https://b.com"),
        ]
        ctx = _build_source_context(items)
        assert "[1]" in ctx
        assert "[2]" in ctx
        assert "Article One" in ctx
        assert "newsapi" in ctx


# ---------------------------------------------------------------------------
# Source search tests
# ---------------------------------------------------------------------------

class TestSearchSources:
    @pytest.mark.asyncio
    async def test_returns_deduplicated_items(self):
        items = [
            _make_source_item(title="Same Article", url="https://same.com"),
        ]
        with (
            patch("chat.engine._search_google_news", new_callable=AsyncMock, return_value=items),
            patch("chat.engine._search_hackernews", new_callable=AsyncMock, return_value=items),
            patch("chat.engine._search_newsapi", new_callable=AsyncMock, return_value=[]),
        ):
            result = await search_sources_for_query("test query")
            # Same URL should be deduplicated
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_handles_search_failures(self):
        with (
            patch("chat.engine._search_google_news", new_callable=AsyncMock, side_effect=Exception("fail")),
            patch("chat.engine._search_hackernews", new_callable=AsyncMock, return_value=[]),
            patch("chat.engine._search_newsapi", new_callable=AsyncMock, return_value=[]),
        ):
            result = await search_sources_for_query("test")
            assert result == []

    @pytest.mark.asyncio
    async def test_caps_at_10_items(self):
        items = [
            _make_source_item(title=f"Article {i}", url=f"https://example.com/{i}")
            for i in range(8)
        ]
        with (
            patch("chat.engine._search_google_news", new_callable=AsyncMock, return_value=items),
            patch("chat.engine._search_hackernews", new_callable=AsyncMock, return_value=items),
            patch("chat.engine._search_newsapi", new_callable=AsyncMock, return_value=[]),
        ):
            result = await search_sources_for_query("test")
            assert len(result) <= 10


# ---------------------------------------------------------------------------
# Full engine tests
# ---------------------------------------------------------------------------

class TestGenerateChatResponse:
    @pytest.mark.asyncio
    async def test_returns_response_with_sources(self):
        """Query about a topic returns response + source links."""
        searched = [
            _make_source_item(title="Llama 4 Release", source="hackernews", url="https://hn.com/1"),
            _make_source_item(title="Llama 4 Review", source="newsapi", url="https://news.com/2"),
        ]

        with (
            patch("chat.engine.search_sources_for_query", new_callable=AsyncMock, return_value=searched),
            patch("chat.engine.ChatGroq") as MockLLM,
        ):
            mock_instance = MockLLM.return_value
            mock_instance.ainvoke = AsyncMock(
                return_value=_mock_llm_response(
                    "Llama 4 was recently released by Meta. According to HackerNews, it shows significant improvements."
                )
            )

            result = await generate_chat_response(
                query="What's happening with Llama 4?",
                user_id="user-123",
                preferences={"topics": ["ai"]},
            )

        assert isinstance(result, ChatResult)
        assert "Llama 4" in result.response
        assert len(result.sources) == 2
        assert result.sources[0].title == "Llama 4 Release"

    @pytest.mark.asyncio
    async def test_gibberish_query_returns_polite_response(self):
        """Random gibberish gets a polite 'no info' response."""
        with (
            patch("chat.engine.search_sources_for_query", new_callable=AsyncMock, return_value=[]),
            patch("chat.engine.ChatGroq") as MockLLM,
        ):
            mock_instance = MockLLM.return_value
            mock_instance.ainvoke = AsyncMock(
                return_value=_mock_llm_response(
                    "I couldn't find relevant information on that topic. Could you rephrase your question?"
                )
            )

            result = await generate_chat_response(
                query="aslkdjf aslkdjf lkasjdf",
                user_id="user-123",
            )

        assert isinstance(result, ChatResult)
        assert len(result.response) > 0
        assert len(result.sources) == 0

    @pytest.mark.asyncio
    async def test_llm_failure_returns_fallback(self):
        """LLM error returns a graceful fallback message."""
        with (
            patch("chat.engine.search_sources_for_query", new_callable=AsyncMock, return_value=[]),
            patch("chat.engine.ChatGroq") as MockLLM,
        ):
            mock_instance = MockLLM.return_value
            mock_instance.ainvoke = AsyncMock(side_effect=Exception("API timeout"))

            result = await generate_chat_response(
                query="Tell me about markets",
                user_id="user-123",
            )

        assert "sorry" in result.response.lower()
        assert len(result.sources) == 0

    @pytest.mark.asyncio
    async def test_briefing_context_used(self):
        """Chat references today's briefing when available."""
        briefing = {
            "top_story": "RBI cuts interest rate by 25bps",
            "sections": [],
        }

        with (
            patch("chat.engine.search_sources_for_query", new_callable=AsyncMock, return_value=[]),
            patch("chat.engine.ChatGroq") as MockLLM,
        ):
            mock_instance = MockLLM.return_value

            # Capture the prompt to verify briefing context is included
            captured_messages = []

            async def capture_invoke(messages):
                captured_messages.extend(messages)
                return _mock_llm_response("The RBI cut rates by 25bps today.")

            mock_instance.ainvoke = AsyncMock(side_effect=capture_invoke)

            result = await generate_chat_response(
                query="Tell me about today's top story",
                user_id="user-123",
                latest_briefing=briefing,
            )

        # Verify briefing context was passed to LLM
        user_msg = str(captured_messages[-1].content)
        assert "RBI cuts interest rate" in user_msg

    @pytest.mark.asyncio
    async def test_conversation_followup(self):
        """Follow-up questions use recent conversation context."""
        recent = [
            {"query": "What's new in AI?", "response": "Several new LLM models were released."},
        ]

        with (
            patch("chat.engine.search_sources_for_query", new_callable=AsyncMock, return_value=[]),
            patch("chat.engine.ChatGroq") as MockLLM,
        ):
            mock_instance = MockLLM.return_value

            captured_messages = []

            async def capture_invoke(messages):
                captured_messages.extend(messages)
                return _mock_llm_response("Specifically, Llama 4 and GPT-5 were the highlights.")

            mock_instance.ainvoke = AsyncMock(side_effect=capture_invoke)

            result = await generate_chat_response(
                query="Tell me more",
                user_id="user-123",
                recent_context=recent,
            )

        # Verify conversation context was passed
        user_msg = str(captured_messages[-1].content)
        assert "What's new in AI?" in user_msg
        assert "Tell me more" in user_msg

    @pytest.mark.asyncio
    async def test_user_preferences_in_context(self):
        """User preferences and interests are included in LLM context."""
        with (
            patch("chat.engine.search_sources_for_query", new_callable=AsyncMock, return_value=[]),
            patch("chat.engine.ChatGroq") as MockLLM,
        ):
            mock_instance = MockLLM.return_value

            captured_messages = []

            async def capture_invoke(messages):
                captured_messages.extend(messages)
                return _mock_llm_response("Here's the latest on AAPL.")

            mock_instance.ainvoke = AsyncMock(side_effect=capture_invoke)

            await generate_chat_response(
                query="How is my watchlist doing?",
                user_id="user-123",
                preferences={"topics": ["markets", "tech"], "sources": ["yahoo_finance"]},
                interests=[{"type": "stock", "value": "AAPL"}],
            )

        user_msg = str(captured_messages[-1].content)
        assert "markets" in user_msg
        assert "AAPL" in user_msg
