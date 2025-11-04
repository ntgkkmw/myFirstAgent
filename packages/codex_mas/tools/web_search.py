"""Web search tool stub."""
from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel


class SearchHit(BaseModel):
    title: str
    url: str
    snippet: str
    indexed_at: datetime | None = None


DEFAULT_HITS = [
    SearchHit(title="Stub Result 1", url="https://example.com/1", snippet="Placeholder search hit."),
    SearchHit(title="Stub Result 2", url="https://example.com/2", snippet="Placeholder search hit."),
]


def web_search(query: str, *, k: int = 8) -> List[SearchHit]:
    """Return mocked search results (placeholder implementation)."""

    if not query.strip():
        raise ValueError("query must be non-empty")
    return DEFAULT_HITS[:k]


__all__ = ["SearchHit", "web_search"]

