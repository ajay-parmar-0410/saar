"""Standardized data types for source fetchers."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class SourceItem:
    """A single item from any data source, in standardized format."""
    title: str
    summary: str
    url: str
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    raw: dict = field(default_factory=dict)


@dataclass(frozen=True)
class SourceResult:
    """Result from a source fetcher."""
    source_name: str
    items: tuple[SourceItem, ...] = ()
    error: str | None = None
