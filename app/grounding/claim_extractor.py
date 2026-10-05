"""Simple deterministic claim segmentation."""
from __future__ import annotations

import re


def extract_claims(answer: str) -> list[str]:
    if not answer:
        return []
    parts = re.split(r'(?<=[.!?])\s+|;\s+', re.sub(r'\s+', ' ', answer).strip())
    return [part.strip(' -•') for part in parts if len(part.strip()) >= 10]
