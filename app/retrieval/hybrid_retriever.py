"""Hybrid semantic + lexical retrieval."""
from __future__ import annotations

from app.config import settings
from app.ingestion.models import DocumentChunk
from app.schemas.retrieval import RetrievalResult
from app.vectorstore.bm25_store import BM25Store
from app.vectorstore.qdrant_store import QdrantStore


class HybridRetriever:
    def __init__(self, vector_store: QdrantStore | None = None, bm25_store: BM25Store | None = None):
        self.vector_store = vector_store or QdrantStore()
        self.bm25_store = bm25_store or self._load_bm25()

    @staticmethod
    def _load_bm25() -> BM25Store:
        if settings.bm25_path.exists():
            try:
                return BM25Store.load(settings.bm25_path)
            except Exception:
                pass
        return BM25Store()

    def index_bm25(self, chunks: list[DocumentChunk], append: bool = True) -> None:
        if append:
            self.bm25_store.add(chunks)
        else:
            self.bm25_store.build(chunks)
        self.bm25_store.save(settings.bm25_path)

    def refresh_bm25(self) -> None:
        self.bm25_store = self._load_bm25()

    def retrieve(self, query: str, top_k: int | None = None, document_ids: set[str] | None = None) -> list[RetrievalResult]:
        k = top_k or settings.top_k
        semantic = self.vector_store.search(query, k, document_ids)
        keyword = self.bm25_store.search(query, k, document_ids)

        sem_scores = self._normalize({item.chunk.chunk_id: item.score for item in semantic})
        key_scores = self._normalize({chunk.chunk_id: score for chunk, score in keyword})
        by_id = {item.chunk.chunk_id: item for item in semantic}
        for chunk, _ in keyword:
            by_id.setdefault(chunk.chunk_id, RetrievalResult(chunk=chunk, score=0.0))

        merged = []
        for chunk_id, item in by_id.items():
            sem = sem_scores.get(chunk_id, 0.0)
            key = key_scores.get(chunk_id, 0.0)
            item.semantic_score = sem
            item.keyword_score = key
            item.score = settings.semantic_weight * sem + settings.keyword_weight * key
            merged.append(item)

        merged.sort(key=lambda x: x.score, reverse=True)
        return merged[:k]

    @staticmethod
    def _normalize(scores: dict[str, float]) -> dict[str, float]:
        if not scores:
            return {}
        values = list(scores.values())
        low, high = min(values), max(values)
        if high == low:
            return {key: 1.0 for key in scores}
        return {key: (value - low) / (high - low) for key, value in scores.items()}
