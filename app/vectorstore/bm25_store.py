"""Persistent lexical BM25 index."""
from __future__ import annotations

import pickle
import re
from pathlib import Path

from app.ingestion.models import DocumentChunk

TOKEN_PATTERN = re.compile(r'[A-Za-z0-9_./:%-]+')

def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


class BM25Store:
    def __init__(self):
        self.chunks: list[DocumentChunk] = []
        self._index = None

    def build(self, chunks: list[DocumentChunk]) -> None:
        from rank_bm25 import BM25Okapi
        self.chunks = list(chunks)
        self._index = BM25Okapi([tokenize(c.text) for c in self.chunks])

    def add(self, chunks: list[DocumentChunk]) -> None:
        existing_ids = {c.chunk_id for c in self.chunks}
        merged = self.chunks + [c for c in chunks if c.chunk_id not in existing_ids]
        self.build(merged)

    def search(self, query: str, top_k: int = 20, document_ids: set[str] | None = None):
        if self._index is None or not self.chunks:
            return []
        scores = self._index.get_scores(tokenize(query))
        indices = sorted(range(len(scores)), key=lambda i: float(scores[i]), reverse=True)
        results = []
        for idx in indices:
            chunk = self.chunks[idx]
            if document_ids and chunk.document_id not in document_ids:
                continue
            results.append((chunk, float(scores[idx])))
            if len(results) >= top_k:
                break
        return results

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('wb') as handle:
            pickle.dump(self, handle)

    @classmethod
    def load(cls, path: str | Path) -> 'BM25Store':
        with Path(path).open('rb') as handle:
            return pickle.load(handle)
