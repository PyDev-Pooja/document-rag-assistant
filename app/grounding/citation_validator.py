"""Citation provenance validator."""
from __future__ import annotations

from dataclasses import dataclass
from app.config import settings


@dataclass
class CitationValidation:
    allowed: bool
    message: str = ''
    valid_citations: list = None


class CitationValidator:
    def validate(self, citations, evidence) -> CitationValidation:
        from app.rag.generator import Citation
        valid_by_id = {item.chunk.chunk_id: item.chunk for item in evidence}
        valid: list[Citation] = []
        for citation in citations or []:
            chunk = valid_by_id.get(citation.chunk_id)
            if not chunk:
                continue
            if citation.document_id != chunk.document_id:
                continue
            if citation.filename != chunk.filename:
                continue
            if citation.page_start is not None and chunk.page_number is not None and citation.page_start != chunk.page_number:
                continue
            valid.append(citation)
        if settings.require_citations and not valid:
            return CitationValidation(False, 'The response did not contain a valid citation to retrieved evidence.', [])
        return CitationValidation(True, valid_citations=valid)
