"""Single source of truth for deterministic RAG thresholds and decisions."""
from __future__ import annotations

from dataclasses import dataclass
from app.config import settings


@dataclass
class RuleDecision:
    allowed: bool
    reason: str
    score: float = 0.0


class RuleEngine:
    def retrieval_rule(self, score: float) -> RuleDecision:
        allowed = score >= settings.min_retrieval_score
        return RuleDecision(allowed, 'retrieval_score_ok' if allowed else 'retrieval_score_too_low', score)

    def grounding_rule(self, score: float) -> RuleDecision:
        allowed = score >= settings.min_grounding_score
        return RuleDecision(allowed, 'grounding_score_ok' if allowed else 'grounding_score_too_low', score)

    def citation_rule(self, count: int) -> RuleDecision:
        allowed = count > 0 if settings.require_citations else True
        return RuleDecision(allowed, 'citations_ok' if allowed else 'citations_missing', 1.0 if allowed else 0.0)

    @staticmethod
    def external_knowledge_allowed() -> bool:
        return settings.allow_external_knowledge
