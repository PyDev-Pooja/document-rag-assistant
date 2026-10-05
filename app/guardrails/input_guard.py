"""Input safety and scope guardrail."""
from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class GuardResult:
    allowed: bool
    message: str = ''
    reason: str | None = None
    score: float = 0.0


class InputGuard:
    PATTERNS = [
        r'ignore\s+(all|any|the)?\s*(previous|prior|above)\s+instructions',
        r'reveal\s+(your|the)\s+(system|developer)\s+prompt',
        r'show\s+(me\s+)?(your|the)\s+hidden\s+instructions',
        r'override\s+(your|the)\s+rules',
    ]

    def validate(self, question: str) -> GuardResult:
        q = ' '.join((question or '').split())
        if not q:
            return GuardResult(False, 'Please enter a question.', 'empty_question')
        if len(q) > 2000:
            return GuardResult(False, 'The question is too long. Please shorten it.', 'question_too_long')
        if any(re.search(pattern, q, flags=re.I) for pattern in self.PATTERNS):
            return GuardResult(
                False,
                'I can answer questions about the uploaded documents, but I cannot reveal or override internal instructions.',
                'prompt_injection_detected',
            )
        return GuardResult(True, score=1.0)
