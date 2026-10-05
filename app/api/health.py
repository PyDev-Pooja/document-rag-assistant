"""Health endpoint."""
from __future__ import annotations

from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=['health'])


@router.get('/health')
def health():
    qdrant = 'unknown'
    try:
        from app.vectorstore.qdrant_store import QdrantStore
        QdrantStore().client.get_collections()
        qdrant = 'ok'
    except Exception as exc:
        qdrant = f'unavailable:{type(exc).__name__}'
    return {'status': 'ok', 'environment': settings.environment, 'qdrant': qdrant}
