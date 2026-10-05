"""PDF extraction with native text first and OCR fallback."""
from __future__ import annotations

from pathlib import Path

from app.config import settings
from app.ingestion.models import ExtractedDocument, ExtractedElement
from app.ingestion.ocr import OCRService


def _extract_page_tables(page) -> list[ExtractedElement]:
    """Extract simple PDF tables when PyMuPDF table support is available."""
    elements: list[ExtractedElement] = []
    finder = getattr(page, "find_tables", None)
    if not callable(finder):
        return elements
    try:
        tables = finder()
        for table_index, table in enumerate(tables.tables):
            data = table.extract()
            rows = [" | ".join(str(cell or "").strip() for cell in row) for row in data]
            text = "\n".join(rows).strip()
            if text:
                elements.append(
                    ExtractedElement(
                        text=text,
                        page_number=page.number + 1,
                        element_type="table",
                        metadata={"table_index": table_index},
                    )
                )
    except Exception:
        return []
    return elements


def extract_pdf(path: Path, *, ocr_service: OCRService | None = None) -> ExtractedDocument:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for PDF processing") from exc

    elements: list[ExtractedElement] = []
    ocr_used = False
    extraction_method = "native"

    with fitz.open(path) as pdf:
        for page in pdf:
            page_text = page.get_text("text").strip()
            if len(page_text) >= settings.pdf_text_min_chars:
                elements.append(
                    ExtractedElement(
                        text=page_text,
                        page_number=page.number + 1,
                        element_type="paragraph",
                        source=str(path),
                    )
                )
            elif settings.ocr_enabled:
                if ocr_service is None:
                    ocr_service = OCRService(settings.ocr_provider, settings.ocr_language)
                matrix = fitz.Matrix(settings.pdf_render_dpi / 72, settings.pdf_render_dpi / 72)
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                result = ocr_service.extract(_bytes_to_image(pixmap.tobytes("png")))
                if result.text:
                    elements.append(
                        ExtractedElement(
                            text=result.text,
                            page_number=page.number + 1,
                            element_type="ocr_text",
                            source=str(path),
                            confidence=result.confidence,
                            metadata={"ocr_provider": result.provider},
                        )
                    )
                    ocr_used = True
                    extraction_method = "hybrid"

            elements.extend(_extract_page_tables(page))

    return ExtractedDocument(
        document_id=path.stem,
        filename=path.name,
        source_path=path,
        file_type="pdf",
        elements=elements,
        metadata={"page_count": len({e.page_number for e in elements if e.page_number})},
        extraction_method=extraction_method,
        ocr_used=ocr_used,
    )


def _bytes_to_image(image_bytes: bytes):
    from io import BytesIO
    from PIL import Image
    return Image.open(BytesIO(image_bytes)).convert("RGB")
