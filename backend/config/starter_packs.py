"""Starter pack definitions — default topics and sources per user type."""

from dataclasses import dataclass


@dataclass(frozen=True)
class StarterPack:
    topics: tuple[str, ...]
    sources: tuple[str, ...]


STARTER_PACKS: dict[str, StarterPack] = {
    "ai_tech": StarterPack(
        topics=(
            "ai_ml",
            "data_science",
            "cloud",
            "startups",
            "security",
        ),
        sources=(
            "github",
            "hackernews",
            "reddit",
            "arxiv",
            "producthunt",
            "google_news",
        ),
    ),
    "general": StarterPack(
        topics=(
            "world_news",
            "india",
            "science",
            "health",
        ),
        sources=(
            "weatherapi",
            "google_news",
            "newsapi",
        ),
    ),
    "trader": StarterPack(
        topics=(
            "markets",
            "economy",
            "finance",
            "startups",
        ),
        sources=(
            "yahoo_finance",
            "economic_times",
            "newsapi",
            "google_news",
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
