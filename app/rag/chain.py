"""End-to-end guarded RAG orchestration."""
from __future__ import annotations

from app.config import settings
from app.guardrails.input_guard import InputGuard
from app.guardrails.retrieval_guard import RetrievalGuard
from app.guardrails.output_guard import OutputGuard
from app.schemas.retrieval import RetrievalResult
from app.rag.generator import GroundedResponse, LLMGenerator
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.query_rewriter import QueryRewriter
from app.retrieval.reranker import Reranker


class RAGChain:
    def __init__(self):
        self.retriever = HybridRetriever()
        self.reranker = Reranker()
        self.generator = LLMGenerator()
        self.query_rewriter = QueryRewriter()
        self.input_guard = InputGuard()
        self.retrieval_guard = RetrievalGuard()
        self.output_guard = OutputGuard()

    def answer(self, question: str, history=None, document_ids: set[str] | None = None) -> GroundedResponse:
        input_result = self.input_guard.validate(question)
        if not input_result.allowed:
            return GroundedResponse(answer=input_result.message, grounded=False, warning=input_result.reason)

        rewritten = self.query_rewriter.rewrite(question, history)
        self.retriever.refresh_bm25()
        retrieved = self.retriever.retrieve(rewritten, settings.top_k, document_ids)

        retrieval_result = self.retrieval_guard.validate(retrieved)
        if not retrieval_result.allowed:
            return GroundedResponse(
                answer=retrieval_result.message,
                grounded=False,
                confidence=retrieval_result.score,
                warning=retrieval_result.reason,
            )

        reranked = self.reranker.rerank(rewritten, retrieved, settings.rerank_top_k)
        response = self.generator.generate(rewritten, reranked)
        return self.output_guard.validate(response, reranked)


_singleton: RAGChain | None = None


def get_rag_chain() -> RAGChain:
    global _singleton
    if _singleton is None:
        _singleton = RAGChain()
    return _singleton
