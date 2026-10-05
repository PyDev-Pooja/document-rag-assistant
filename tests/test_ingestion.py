from pathlib import Path
import pytest
from app.config import settings
from app.ingestion.document_loader import load_document


def test_txt_ingestion(tmp_path: Path):
    path = tmp_path / 'sample.txt'
    path.write_text('Annual leave is 25 days.', encoding='utf-8')
    record = load_document(path)
    assert record.file_type == 'txt'
    assert record.elements[0].text == 'Annual leave is 25 days.'


def test_unsupported_extension(tmp_path: Path):
    path = tmp_path / 'sample.exe'
    path.write_bytes(b'data')
    with pytest.raises(ValueError):
        load_document(path)
