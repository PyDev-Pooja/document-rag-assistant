"""Grounded chat endpoint."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.rag.chain import get_rag_chain

router = APIRouter(prefix='/chat', tags=['chat'])


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    document_ids: list[str] = Field(default_factory=list)
    history: list[dict[str, str]] = Field(default_factory=list)

@router.post('')
def chat(request: ChatRequest):
    response = get_rag_chain().answer(
        request.question,
        history=request.history,
        document_ids=set(request.document_ids) or None,
    )
    return response.model_dump()
