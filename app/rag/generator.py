"""LangChain LLM generation with structured grounded output."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from app.config import settings
from app.schemas.retrieval import RetrievalResult
from app.rag.prompts import SYSTEM_PROMPT, HUMAN_PROMPT


class Citation(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page_start: int | None = None
    page_end: int | None = None
    section: str | None = None


class GroundedResponse(BaseModel):
    answer: str
    grounded: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    claims: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    warning: str | None = None


class LLMGenerator:
    def __init__(self):
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            kwargs: dict[str, Any] = {
                'model': settings.llm_model,
                'temperature': settings.llm_temperature,
                'max_tokens': settings.llm_max_tokens,
                'api_key': settings.llm_api_key,
            }
            if settings.llm_base_url:
                kwargs['base_url'] = settings.llm_base_url
            self._llm = ChatOpenAI(**kwargs)
        return self._llm

    def generate(self, question: str, evidence: list[RetrievalResult]) -> GroundedResponse:
        from langchain_core.prompts import ChatPromptTemplate

        context = self._format_evidence(evidence)
        prompt = ChatPromptTemplate.from_messages([
            ('system', SYSTEM_PROMPT),
            ('human', HUMAN_PROMPT),
        ])
        messages = prompt.format_messages(question=question, context=context)

        structured = self.llm.with_structured_output(GroundedResponse)
        result = structured.invoke(messages)
        return result if isinstance(result, GroundedResponse) else GroundedResponse.model_validate(result)

    @staticmethod
    def _format_evidence(evidence: list[RetrievalResult]) -> str:
        blocks = []
        for item in evidence:
            chunk = item.chunk
            blocks.append(
                '\n'.join([
                    '<evidence>',
                    f'CHUNK_ID: {chunk.chunk_id}',
                    f'DOCUMENT_ID: {chunk.document_id}',
                    f'FILENAME: {chunk.filename}',
                    f'PAGE: {chunk.page_number if chunk.page_number is not None else "N/A"}',
                    f'SECTION: {chunk.section or "N/A"}',
                    f'CONTENT: {chunk.text}',
                    '</evidence>',
                ])
            )
        return '\n\n---\n\n'.join(blocks)
