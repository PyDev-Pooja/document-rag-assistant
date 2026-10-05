"""Deterministic conversational query rewriting."""
from __future__ import annotations

import re


class QueryRewriter:
    REFERENCE_WORDS = re.compile(r'\b(it|this|that|these|those|they|them|he|she|previous|above|earlier)\b', re.I)

    def rewrite(self, question: str, history: list[dict[str, str]] | None = None) -> str:
        q = ' '.join((question or '').split()).strip()
        if not q or not history or not self.REFERENCE_WORDS.search(q):
            return q
        recent = [m.get('content', '').strip() for m in history[-6:] if m.get('role') == 'user']
        return f'{q}\nPrevious user context: {recent[-1]}' if recent else q
