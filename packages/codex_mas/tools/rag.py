"""RAG retrieval tool stub."""
from __future__ import annotations

from typing import List

from pydantic import BaseModel


class DocChunk(BaseModel):
    doc_id: str
    text: str
    score: float


DEFAULT_CHUNKS = [
    DocChunk(doc_id="doc-1", text="Example document chunk for testing.", score=0.8),
    DocChunk(doc_id="doc-2", text="Secondary chunk.", score=0.6),
]


def rag_retrieve(query: str, *, k: int = 8) -> List[dict[str, str | float]]:
    if not query.strip():
        raise ValueError("query must be non-empty")
    return [chunk.model_dump() for chunk in DEFAULT_CHUNKS[:k]]


__all__ = ["DocChunk", "rag_retrieve"]

