"""Qdrant vector database adapter."""
from __future__ import annotations

import uuid
from pathlib import Path

from app.config import settings
from app.embeddings.embedding_model import EmbeddingModel
from app.ingestion.models import DocumentChunk
from app.schemas.retrieval import RetrievalResult


class QdrantStore:
    def __init__(self, embedding_model: EmbeddingModel | None = None):
        self.embedding_model = embedding_model or EmbeddingModel()
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from qdrant_client import QdrantClient
            self._client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
            )
        return self._client

    def ensure_collection(self, vector_size: int | None = None) -> None:
        from qdrant_client import models
        exists = self.client.collection_exists(settings.qdrant_collection)
        if exists:
            return
        size = vector_size or len(self.embedding_model.embed_query('vector dimension probe'))
        self.client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(size=size, distance=models.Distance.COSINE),
        )

    def upsert_chunks(self, chunks: list[DocumentChunk], batch_size: int = 64) -> int:
        if not chunks:
            return 0
        from qdrant_client import models
        self.ensure_collection()
        count = 0
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            vectors = self.embedding_model.embed_documents([c.text for c in batch])
            points = []
            for chunk, vector in zip(batch, vectors):
                point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, chunk.chunk_id))
                points.append(
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            'text': chunk.text,
                            'document_id': chunk.document_id,
                            'chunk_id': chunk.chunk_id,
                            'filename': chunk.filename,
                            'page_number': chunk.page_number,
                            'section': chunk.section,
                            'element_type': chunk.element_type,
                            'source_type': chunk.source_type,
                            'ocr_used': chunk.ocr_used,
                            'ocr_confidence': chunk.ocr_confidence,
                            'metadata': chunk.metadata,
                        },
                    )
                )
            self.client.upsert(
                collection_name=settings.qdrant_collection,
                points=points,
                wait=True,
            )
            count += len(points)
        return count

    def search(self, query: str, top_k: int | None = None, document_ids: set[str] | None = None) -> list[RetrievalResult]:
        from qdrant_client import models
        self.ensure_collection()
        vector = self.embedding_model.embed_query(query)
        query_filter = None
        if document_ids:
            query_filter = models.Filter(
                should=[
                    models.FieldCondition(
                        key='document_id',
                        match=models.MatchValue(value=doc_id),
                    )
                    for doc_id in document_ids
                ]
            )
        response = self.client.query_points(
            collection_name=settings.qdrant_collection,
            query=vector,
            query_filter=query_filter,
            limit=top_k or settings.top_k,
            with_payload=True,
        )
        results: list[RetrievalResult] = []
        for point in response.points:
            payload = dict(point.payload or {})
            chunk = DocumentChunk(
                text=str(payload.get('text', '')),
                document_id=str(payload.get('document_id', '')),
                chunk_id=str(payload.get('chunk_id', '')),
                filename=str(payload.get('filename', '')),
                page_number=payload.get('page_number'),
                section=payload.get('section'),
                element_type=str(payload.get('element_type', 'paragraph')),
                source_type=str(payload.get('source_type', 'unknown')),
                ocr_used=bool(payload.get('ocr_used', False)),
                ocr_confidence=payload.get('ocr_confidence'),
                metadata=payload.get('metadata') or {},
            )
            score = float(point.score or 0.0)
            results.append(RetrievalResult(chunk=chunk, score=score, semantic_score=score))
        return results

    def delete_document(self, document_id: str) -> None:
        from qdrant_client import models
        self.client.delete(
            collection_name=settings.qdrant_collection,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key='document_id',
                            match=models.MatchValue(value=document_id),
                        )
                    ]
                )
            ),
            wait=True,
        )

    def count(self) -> int:
        try:
            info = self.client.get_collection(settings.qdrant_collection)
            return int(getattr(info, 'points_count', 0) or 0)
        except Exception:
            return 0
