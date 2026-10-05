"""Metadata and provenance generation."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib

from app.ingestion.models import ExtractedDocument


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_document_metadata(document: ExtractedDocument) -> dict[str, Any]:
    full_text = "\n".join(element.text for element in document.elements)
    pages = sorted({element.page_number for element in document.elements if element.page_number})
    return {
        "document_id": document.document_id,
        "filename": document.filename,
        "source_path": str(document.source_path),
        "file_type": document.file_type,
        "extraction_method": document.extraction_method,
        "ocr_used": document.ocr_used,
        "page_numbers": pages,
        "content_hash": content_hash(full_text),
        **document.metadata,
    }


def build_chunk_metadata(
    document: ExtractedDocument,
    *,
    chunk_id: str,
    page_number: int | None,
    section: str | None,
    element_type: str,
    ocr_confidence: float | None,
) -> dict[str, Any]:
    return {
        "document_id": document.document_id,
        "filename": document.filename,
        "file_type": document.file_type,
        "source_path": str(Path(document.source_path)),
        "chunk_id": chunk_id,
        "page": page_number,
        "section": section,
        "element_type": element_type,
        "ocr_used": document.ocr_used,
        "ocr_confidence": ocr_confidence,
    }
