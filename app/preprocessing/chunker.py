"""Structure-aware chunking for RAG preparation."""
from __future__ import annotations

from app.config import settings
from app.ingestion.models import DocumentChunk, ExtractedDocument
from app.preprocessing.cleaner import clean_text
from app.preprocessing.metadata import build_chunk_metadata


def _split_large_text(text: str, max_size: int, overlap: int) -> list[str]:
    if len(text) <= max_size:
        return [text]
    if overlap >= max_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_size, len(text))
        if end < len(text):
            boundary = max(text.rfind(". ", start, end), text.rfind("\n", start, end))
            if boundary > start + max_size // 2:
                end = boundary + 1
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def chunk_document(
    document: ExtractedDocument,
    *,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[DocumentChunk]:
    """Create chunks while retaining page/section/element provenance."""
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = settings.chunk_overlap if chunk_overlap is None else chunk_overlap
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[DocumentChunk] = []
    current_parts: list[str] = []
    current_page: int | None = None
    current_section: str | None = None
    current_type = "paragraph"
    current_confidence: float | None = None

    def flush() -> None:
        nonlocal current_parts, current_page, current_section, current_type, current_confidence
        if not current_parts:
            return
        text = "\n\n".join(current_parts).strip()
        if text:
            for piece_index, piece in enumerate(_split_large_text(text, chunk_size, chunk_overlap)):
                chunk_index = len(chunks)
                chunk_id = f"{document.document_id}_P{current_page or 0}_C{chunk_index:04d}"
                metadata = build_chunk_metadata(
                    document,
                    chunk_id=chunk_id,
                    page_number=current_page,
                    section=current_section,
                    element_type=current_type,
                    ocr_confidence=current_confidence,
                )
                metadata["split_index"] = piece_index
                chunks.append(
                    DocumentChunk(
                        text=piece,
                        document_id=document.document_id,
                        chunk_id=chunk_id,
                        filename=document.filename,
                        page_number=current_page,
                        section=current_section,
                        element_type=current_type,
                        source_type=document.file_type,
                        ocr_used=document.ocr_used,
                        ocr_confidence=current_confidence,
                        metadata=metadata,
                    )
                )
        current_parts = []
        current_page = None
        current_section = None
        current_type = "paragraph"
        current_confidence = None

    for element in document.elements:
        text = clean_text(element.text)
        if not text:
            continue

        if element.element_type == "heading":
            flush()
            current_section = text
            current_page = element.page_number
            current_type = "heading"
            current_confidence = element.confidence
            current_parts = [text]
            continue

        if current_page is None:
            current_page = element.page_number
        if element.section:
            current_section = element.section
        if element.confidence is not None:
            current_confidence = element.confidence

        proposed = "\n\n".join(current_parts + [text]).strip()
        if current_parts and len(proposed) > chunk_size:
            flush()
            current_page = element.page_number
            current_type = element.element_type
            current_confidence = element.confidence
            current_parts.append(text)
        else:
            current_type = element.element_type if not current_parts else current_type
            current_parts.append(text)

    flush()
    return chunks
