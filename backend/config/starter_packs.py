"""Starter pack definitions — default topics and sources per user type."""

from dataclasses import dataclass


@dataclass(frozen=True)
class StarterPack:
    topics: tuple[str, ...]
    sources: tuple[str, ...]


STARTER_PACKS: dict[str, StarterPack] = {
    "ai_tech": StarterPack(
        topics=(
            "artificial_intelligence",
            "machine_learning",
            "llm",
            "open_source",
            "developer_tools",
            "startups",
            "research_papers",
        ),
        sources=(
            "github",
            "hackernews",
            "reddit",
            "arxiv",
            "producthunt",
            "techcrunch",
            "huggingface",
        ),
    ),
    "general": StarterPack(
        topics=(
            "top_headlines",
            "weather",
            "trending",
            "world_news",
            "currency",
        ),
        sources=(
            "weatherapi",
            "google_news",
            "newsapi",
            "reddit_trending",
            "exchangerate",
        ),
    ),
    "trader": StarterPack(
        topics=(
            "indian_markets",
            "nifty",
            "sensex",
            "ipo",
            "earnings",
            "economy",
            "gold",
            "currency",
        ),
        sources=(
            "yahoo_finance",
            "moneycontrol",
            "economic_times",
            "exchangerate",
            "reddit_finance",
        ),
    ),
}

# All valid user types
VALID_USER_TYPES = tuple(STARTER_PACKS.keys())


def get_starter_pack(user_type: str) -> StarterPack:
    """Get the starter pack for a single user type.

    Raises KeyError if user_type is invalid.
    """
    if user_type not in STARTER_PACKS:
        raise KeyError(
            f"Unknown user type: '{user_type}'. "
            f"Valid types: {VALID_USER_TYPES}"
        )
    return STARTER_PACKS[user_type]


def get_combined_starter_pack(user_types: list[str]) -> StarterPack:
    """Combine starter packs for multiple user types, deduplicated.

    Returns a single StarterPack with merged topics and sources.
    """
    if not user_types:
        return StarterPack(topics=(), sources=())

    all_topics: list[str] = []
    all_sources: list[str] = []
    seen_topics: set[str] = set()
    seen_sources: set[str] = set()

    for user_type in user_types:
        pack = get_starter_pack(user_type)
        for topic in pack.topics:
            if topic not in seen_topics:
                all_topics.append(topic)
                seen_topics.add(topic)
        for source in pack.sources:
            if source not in seen_sources:
                all_sources.append(source)
                seen_sources.add(source)

    return StarterPack(
        topics=tuple(all_topics),
        sources=tuple(all_sources),
    )
