"""Shared data models for document ingestion and preprocessing."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ExtractedElement:
    """A single piece of extracted document content."""

    text: str
    page_number: int | None = None
    section: str | None = None
    element_type: str = "paragraph"
    source: str | None = None
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExtractedDocument:
    """Normalized output produced by all document loaders."""

    document_id: str
    filename: str
    source_path: Path
    file_type: str
    elements: list[ExtractedElement] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    extraction_method: str = "native"
    ocr_used: bool = False


@dataclass(slots=True)
class DocumentChunk:
    """RAG-ready chunk with provenance metadata."""

    text: str
    document_id: str
    chunk_id: str
    filename: str
    page_number: int | None
    section: str | None
    element_type: str = "paragraph"
    source_type: str = "unknown"
    ocr_used: bool = False
    ocr_confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
