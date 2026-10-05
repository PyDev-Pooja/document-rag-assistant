"""Text normalization without destroying provenance-sensitive content."""
from __future__ import annotations

import re


_WHITESPACE_RE = re.compile(r"[\t\f\r ]+")
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    """Normalize OCR/native text while retaining line and paragraph structure."""
    if not text:
        return ""
    text = text.replace("\x00", " ").replace("\u00a0", " ")
    lines = []
    for line in text.splitlines():
        line = _WHITESPACE_RE.sub(" ", line).strip()
        if line:
            lines.append(line)
    cleaned = "\n".join(lines)
    return _MULTI_NEWLINE_RE.sub("\n\n", cleaned).strip()


def normalize_for_hash(text: str) -> str:
    """Normalize text for duplicate/content comparisons."""
    return " ".join(clean_text(text).lower().split())
