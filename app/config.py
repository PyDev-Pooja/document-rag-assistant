"""Centralized application configuration."""
from __future__ import annotations

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings for ingestion, retrieval, RAG and guardrails."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False,
    )

    app_name: str = 'Document Intelligence & Grounded RAG Assistant'
    environment: str = 'development'
    host: str = '0.0.0.0'
    port: int = 8000
    log_level: str = 'INFO'

    upload_dir: Path = Path('data/uploads')
    processed_dir: Path = Path('data/processed')
    evaluation_dir: Path = Path('data/evaluation')

    max_upload_size_mb: int = Field(default=50, ge=1, le=2048)
    allow_duplicate_documents: bool = False
    supported_extensions: str = '.pdf,.docx,.txt,.png,.jpg,.jpeg'

    ocr_enabled: bool = True
    ocr_provider: str = 'paddle'
    ocr_language: str = 'en'
    ocr_confidence_threshold: float = Field(default=0.80, ge=0.0, le=1.0)
    pdf_text_min_chars: int = Field(default=40, ge=0)
    pdf_render_dpi: int = Field(default=180, ge=72, le=600)

    chunk_size: int = Field(default=1000, ge=100)
    chunk_overlap: int = Field(default=150, ge=0)
    min_chunk_chars: int = Field(default=80, ge=0)

    embedding_model: str = 'BAAI/bge-m3'
    embedding_device: str = 'cpu'
    embedding_batch_size: int = 16

    qdrant_url: str = 'http://localhost:6333'
    qdrant_api_key: str | None = None
    qdrant_collection: str = 'document_chunks'

    top_k: int = Field(default=20, ge=1, le=100)
    rerank_top_k: int = Field(default=5, ge=1, le=50)
    semantic_weight: float = Field(default=0.70, ge=0.0, le=1.0)
    keyword_weight: float = Field(default=0.30, ge=0.0, le=1.0)
    min_retrieval_score: float = Field(default=0.65, ge=0.0, le=1.0)

    reranker_model: str = 'BAAI/bge-reranker-v2-m3'
    use_reranker: bool = True

    llm_provider: str = 'openai_compatible'
    llm_model: str = 'gpt-4.1-mini'
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    llm_max_tokens: int = 900

    allow_external_knowledge: bool = False
    require_citations: bool = True
    min_grounding_score: float = Field(default=0.80, ge=0.0, le=1.0)
    max_regeneration_attempts: int = Field(default=1, ge=0, le=3)
    max_answer_chars: int = Field(default=4000, ge=200)

    @property
    def supported_suffixes(self) -> set[str]:
        return {
            value.strip().lower()
            for value in self.supported_extensions.split(',')
            if value.strip()
        }

    @property
    def bm25_path(self) -> Path:
        return self.processed_dir / 'bm25_store.pkl'

    def prepare_directories(self) -> None:
        for directory in (self.upload_dir, self.processed_dir, self.evaluation_dir):
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.prepare_directories()
