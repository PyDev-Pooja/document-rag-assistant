"""Post-generation schema/policy guardrail."""
from __future__ import annotations

from app.config import settings
from app.rag.generator import GroundedResponse


class GenerationGuard:
    def validate(self, response: GroundedResponse) -> GroundedResponse:
        response.answer = response.answer.strip()
        if len(response.answer) > settings.max_answer_chars:
            response.answer = response.answer[:settings.max_answer_chars].rstrip() + '…'
        if not response.answer:
            response.grounded = False
            response.warning = 'The model returned an empty response.'
        if response.grounded and settings.require_citations and not response.citations:
            response.grounded = False
            response.warning = 'A grounded answer must include source citations.'
        return response
