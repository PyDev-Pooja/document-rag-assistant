"""Cross-encoder reranking."""
from __future__ import annotations

from app.config import settings
from app.schemas.retrieval import RetrievalResult


class Reranker:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(settings.reranker_model)
        return self._model

    def rerank(self, query: str, results: list[RetrievalResult], top_k: int | None = None) -> list[RetrievalResult]:
        if not results:
            return []
        target_k = top_k or settings.rerank_top_k
        if not settings.use_reranker:
            return results[:target_k]
        pairs = [[query, item.chunk.text] for item in results]
        scores = self.model.predict(pairs, show_progress_bar=False)
        for item, score in zip(results, scores):
            item.rerank_score = float(score)
            item.score = float(score)
        return sorted(results, key=lambda x: x.score, reverse=True)[:target_k]
