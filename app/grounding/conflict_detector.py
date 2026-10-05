"""Conservative detection of conflicting numeric facts in retrieved evidence."""
from __future__ import annotations

import re
from dataclasses import dataclass

NUMBER = re.compile(r'(?<!\w)(?:₹|\$|€|£)?\s*\d+(?:[.,]\d+)*(?:\s*%|\s*(?:days?|weeks?|months?|years?))?', re.I)


@dataclass
class Conflict:
    key: str
    values: dict[str, list[str]]


class ConflictDetector:
    def detect(self, evidence) -> list[Conflict]:
        buckets: dict[str, dict[str, list[str]]] = {}
        for item in evidence:
            text = item.chunk.text
            for match in NUMBER.finditer(text):
                key = self._context_key(text, match.start(), match.end())
                buckets.setdefault(key, {}).setdefault(match.group().strip(), []).append(item.chunk.chunk_id)
        return [Conflict(key, values) for key, values in buckets.items() if len(values) > 1]

    @staticmethod
    def _context_key(text: str, start: int, end: int) -> str:
        context = text[max(0, start-80):min(len(text), end+80)].lower()
        context = re.sub(r'\d[\d.,]*', '<num>', context)
        return re.sub(r'\s+', ' ', context).strip()
