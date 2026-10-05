"""SentenceTransformers embedding adapter."""
from __future__ import annotations

from typing import Sequence

from app.config import settings


class EmbeddingModel: 
    """Lazy-loading normalized sentence embedding model."""

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(
                settings.embedding_model,
                device=settings.embedding_device,
            )
        return self._model

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self.model.encode(
            list(texts),
            batch_size=settings.embedding_batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    def as_langchain_embeddings(self):
        from langchain_core.embeddings import Embeddings
        parent = self

        class SentenceTransformerEmbeddings(Embeddings):
            def embed_documents(self, texts: list[str]) -> list[list[float]]:
                return parent.embed_documents(texts)

            def embed_query(self, text: str) -> list[float]:
                return parent.embed_query(text)

        return SentenceTransformerEmbeddings()
