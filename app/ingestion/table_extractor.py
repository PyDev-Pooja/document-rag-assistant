"""Table normalization utilities used by the ingestion layer."""
from __future__ import annotations

from typing import Iterable


def rows_to_markdown(rows: Iterable[Iterable[object]]) -> str:
    rows = [[str(cell or "").strip() for cell in row] for row in rows]
    rows = [row for row in rows if any(cell for cell in row)]
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    header = normalized[0]
    separator = ["---"] * width
    body = normalized[1:]
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(separator) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def table_to_rag_text(markdown: str) -> str:
    """Add a semantic prefix so tables remain understandable when embedded."""
    cleaned = markdown.strip()
    return f"TABLE:\n{cleaned}" if cleaned else ""
