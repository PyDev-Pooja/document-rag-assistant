# Document Intelligence & Grounded RAG Assistant

A modular document-grounded RAG platform for PDF, DOCX, TXT and image inputs.

## Pipeline

1. File validation and ingestion
2. Native text/table extraction
3. OCR fallback for scanned content
4. Cleaning and structure-aware chunking
5. SentenceTransformers embeddings
6. Qdrant vector indexing
7. BM25 lexical indexing
8. Hybrid semantic + keyword retrieval
9. Cross-encoder reranking
10. LangChain structured generation
11. Four-layer guardrails
12. Claim-level evidence validation
13. Citation provenance validation
14. Conflict detection
15. FastAPI + Streamlit interfaces
16. Evaluation and unit tests

## Grounding policy

The generator is instructed to use only supplied evidence, while a second validation layer independently checks claims against retrieved chunks and validates citations. The default system is configured to refuse when retrieval or grounding thresholds are not met.

No implementation can honestly guarantee perfect grounding on arbitrary inputs. This project makes grounding explicit, measurable and auditable through thresholds, source provenance, claim checks and tests.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS

docker compose up qdrant
uvicorn app.main:app --reload
```

Streamlit:

```bash
streamlit run frontend/streamlit_app.py
```

API documentation:

`http://localhost:8000/docs`

## LLM configuration

The project uses an OpenAI-compatible LangChain chat model interface. Set `LLM_MODEL`, `LLM_API_KEY`, and optionally `LLM_BASE_URL`. This allows a hosted provider or compatible local inference server to be used.
