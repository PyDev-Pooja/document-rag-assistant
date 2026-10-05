"""Top-level document ingestion orchestrator."""
from __future__ import annotations

from pathlib import Path
import hashlib
from app.ingestion.document_classifier import classify_extension, validate_file
from app.config import settings
from app.ingestion.docx_loader import extract_docx, extract_txt
#from app.ingestion.document_classifier
from app.ingestion.document_classifier import validate_file
#import classify_extension, validate_file
from app.ingestion.models import ExtractedDocument
from app.ingestion.ocr import OCRService
from app.ingestion.pdf_loader import extract_pdf


def build_document_id(path: Path) -> str:
    """Create a stable ID from filename, size and modification time."""
    stat = path.stat()
    raw = f"{path.name}:{stat.st_size}:{stat.st_mtime_ns}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]


def load_document(path: str | Path) -> ExtractedDocument:
    path = Path(path)
    validate_file(path)
    kind = classify_extension(path)
    print(kind)
    if kind == "pdf":
        document = extract_pdf(path, ocr_service=OCRService())
    elif kind == "docx":
        document = extract_docx(path)
    elif kind == "txt":
        document = extract_txt(path)
    elif kind == "image":
        ocr = OCRService()
        result = ocr.extract(path)
        from app.ingestion.models import ExtractedElement
        document = ExtractedDocument(
            document_id=path.stem,
            filename=path.name,
            source_path=path,
            file_type="image",
            elements=[
                ExtractedElement(
                    text=result.text,
                    element_type="ocr_text",
                    source=str(path),
                    confidence=result.confidence,
                    metadata={"ocr_provider": result.provider},
                )
            ] if result.text else [],
            extraction_method="ocr",
            ocr_used=True,
        )
    else:
        raise ValueError(f"No loader configured for document kind: {kind}")

    # Replace a simple stem ID with a stable content/file fingerprint.
    document.document_id = build_document_id(path)
    return document
