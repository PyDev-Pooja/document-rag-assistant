"""Document type and PDF text/scanned classification."""
from __future__ import annotations

from pathlib import Path

from app.config import settings


def classify_extension(path: Path) -> str:
    suffix = path.suffix.lower()
    mapping = {
        ".pdf": "pdf",
        ".docx": "docx",
        ".txt": "txt",
        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image",
    }
    if suffix not in mapping:
        raise ValueError(f"Unsupported file type: {suffix or '<none>'}")
    return mapping[suffix]


def validate_file(path: Path) -> None:
    """Validate existence, extension and size before processing."""
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Document not found: {path}")
    #if path.suffix.lower() not in settings.supported_suffixes():
    if path.suffix.lower() not in settings.supported_suffixes:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if path.stat().st_size > max_bytes:
        raise ValueError(
            f"File exceeds configured limit of {settings.max_upload_size_mb} MB"
        )


def is_pdf_scanned(path: Path) -> bool:
    """Return True when most PDF pages contain little/no native text."""
    if path.suffix.lower() != ".pdf":
        return False

    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for PDF classification") from exc

    with fitz.open(path) as pdf:
        if pdf.page_count == 0:
            return True
        low_text_pages = 0
        for page in pdf:
            text = page.get_text("text").strip()
            if len(text) < settings.pdf_text_min_chars:
                low_text_pages += 1
        return low_text_pages / pdf.page_count >= 0.5
