"""Retrieval quality gate."""
from __future__ import annotations

from dataclasses import dataclass
from app.config import settings
#from app.ingestion.models import RetrievalResult
from app.schemas.retrieval import RetrievalResult


@dataclass
class RetrievalGuardResult:
    allowed: bool
    message: str = ''
    reason: str | None = None
    score: float = 0.0


class RetrievalGuard:
    def validate(self, results: list[RetrievalResult]) -> RetrievalGuardResult:
        if not results:
            return RetrievalGuardResult(
                False,
                'I could not find sufficient information in the uploaded documents.',
                'no_retrieval_results',
                0.0,
            )
        best = max(item.score for item in results)
        if best < settings.min_retrieval_score:
            return RetrievalGuardResult(
                False,
                'I could not find sufficient information in the uploaded documents.',
                'retrieval_score_below_threshold',
                best,
            )
        return RetrievalGuardResult(True, score=best)
