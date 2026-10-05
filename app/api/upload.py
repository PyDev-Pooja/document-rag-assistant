"""Document upload and ingestion endpoint."""
from __future__ import annotations

import shutil
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.ingestion.document_loader import load_document
from app.preprocessing.chunker import chunk_document
from app.vectorstore.qdrant_store import QdrantStore
from app.rag.chain import get_rag_chain


router = APIRouter(prefix='/documents', tags=['documents'])


@router.post('/upload')
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or 'upload').name
    extension = Path(filename).suffix.lower()
   
    if extension not in settings.supported_suffixes:
        raise HTTPException(status_code=400, detail=f'Unsupported file type: {extension}')

    destination = settings.upload_dir / filename
    if destination.exists() and not settings.allow_duplicate_documents:
        # Add a safe numeric suffix rather than overwriting an existing file.
        stem, suffix = destination.stem, destination.suffix
        
        counter = 1
        while destination.exists():
            destination = settings.upload_dir / f'{stem}_{counter}{suffix}'
            counter += 1

    try:
        with destination.open('wb') as output:
            shutil.copyfileobj(file.file, output)

        if destination.stat().st_size > settings.max_upload_size_mb * 1024 * 1024:
            destination.unlink(missing_ok=True)
            raise HTTPException(status_code=413, detail='Uploaded file exceeds the configured size limit.')

        record = load_document(destination)
        chunks = chunk_document(record)
        indexed = QdrantStore().upsert_chunks(chunks)
        get_rag_chain().retriever.index_bm25(chunks, append=True)
       # print(f'Uploaded and processed document: {record.document_id} ({len(chunks)} chunks, {indexed} vectors indexed)')

        return {
            'document_id': record.document_id,
            'filename': record.filename,
            'file_type': record.file_type,
            'elements': len(record.elements),
            'chunks': len(chunks),
            'indexed_vectors': indexed,
            'ocr_used': record.ocr_used,
            'extraction_method': record.extraction_method,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
