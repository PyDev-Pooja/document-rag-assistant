from __future__ import annotations

import argparse
from pathlib import Path

from app.ingestion.document_loader import load_document
from app.preprocessing.chunker import chunk_document
from app.vectorstore.qdrant_store import QdrantStore
from app.rag.chain import get_rag_chain


def main():
    parser = argparse.ArgumentParser(description='Ingest a document into Qdrant and BM25.')
    parser.add_argument('file', type=Path)
    args = parser.parse_args()
    record = load_document(args.file)
    chunks = chunk_document(record)
    indexed = QdrantStore().upsert_chunks(chunks)
    get_rag_chain().retriever.index_bm25(chunks, append=True)
    print(f'document_id={record.document_id} elements={len(record.elements)} chunks={len(chunks)} indexed={indexed}')


if __name__ == '__main__':
    main()
