"""Schemas used by the retrieval and RAG layers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.ingestion.models import DocumentChunk

@dataclass(slots=True)
class RetrievalResult:
    """A single retrieved chunk with retrieval scores."""

    chunk: DocumentChunk
    score: float
    retrieval_method: str = "unknown"

    semantic_score: float | None = None
    bm25_score: float | None = None
    keyword_score: float | None = None
    rerank_score: float | None = None

    metadata: dict[str, Any] = field(default_factory=dict)