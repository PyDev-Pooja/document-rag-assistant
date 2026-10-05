[33mcommit 2fcfbd26ba59ad7c5cd0f1b78138fbf813db9c6a[m
Author: PyDev-Pooja <poojapydev173@gmail.com>
Date:   Mon Oct 5 10:34:39 2026 +0530

    Initial commit

 .env.example                                       |  49 [32m+++[m
 .env.txt                                           |  49 [32m+++[m
 .gitignore                                         |  20 [32m++[m
 .vs/PythonSettings.json                            |   3 [32m+[m
 .vs/VSWorkspaceState.json                          |   9 [32m+[m
 .../6e74d701-bb9e-46b1-bea4-d9e8aeb74c4b.vsidx     | Bin [31m0[m -> [32m107675[m bytes
 .../b9d4cd3a-d354-48ae-81b9-b1cd22f209dc.vsidx     | Bin [31m0[m -> [32m3526[m bytes
 .../c881ade3-b836-4dd2-9f51-b991414777b6.vsidx     | Bin [31m0[m -> [32m107[m bytes
 .../ee0e3e95-6b56-4762-849b-30c3a24c489b.vsidx     | Bin [31m0[m -> [32m3039[m bytes
 .../f5a3e084-a888-4637-a7ee-6f004a581a61.vsidx     | Bin [31m0[m -> [32m7377[m bytes
 .../sessions/af92c024-ef9f-4397-99ea-5bd504dd7e94  | Bin [31m0[m -> [32m3969[m bytes
 .../sessions/d75f3e7c-855b-4b2c-a491-60c4dfd3b7e9  | Bin [31m0[m -> [32m3969[m bytes
 .vs/document-rag-assistant.slnx/v18/.wsuo          | Bin [31m0[m -> [32m85504[m bytes
 .../v18/DocumentLayout.backup.json                 | 288 [32m+++++++++++++++++[m
 .../v18/DocumentLayout.json                        | 341 [32m+++++++++++++++++++++[m
 .../18.10.1201.59691/SemanticSymbols.db            | Bin [31m0[m -> [32m77824[m bytes
 .vs/slnx.sqlite                                    | Bin [31m0[m -> [32m90112[m bytes
 Dockerfile                                         |  14 [32m+[m
 README.md                                          |  56 [32m++++[m
 app/api/chat.py                                    |  24 [32m++[m
 app/api/health.py                                  |  19 [32m++[m
 app/api/upload.py                                  |  63 [32m++++[m
 app/config.py                                      |  92 [32m++++++[m
 app/embeddings/embedding_model.py                  |  50 [32m+++[m
 app/evaluation/grounding_eval.py                   |  24 [32m++[m
 app/evaluation/ragas_eval.py                       |  14 [32m+[m
 app/evaluation/test_questions.py                   |  18 [32m++[m
 app/grounding/citation_validator.py                |  33 [32m++[m
 app/grounding/claim_extractor.py                   |  11 [32m+[m
 app/grounding/conflict_detector.py                 |  30 [32m++[m
 app/grounding/evidence_checker.py                  |  83 [32m+++++[m
 app/guardrails/generation_guard.py                 |  19 [32m++[m
 app/guardrails/input_guard.py                      |  36 [32m+++[m
 app/guardrails/output_guard.py                     |  47 [32m+++[m
 app/guardrails/retrieval_guard.py                  |  35 [32m+++[m
 app/ingestion/__init__.py                          |   5 [32m+[m
 app/ingestion/document_classifier.py               |  56 [32m++++[m
 app/ingestion/document_loader.py                   |  61 [32m++++[m
 app/ingestion/docx_loader.py                       |  69 [32m+++++[m
 app/ingestion/models.py                            |  50 [32m+++[m
 app/ingestion/ocr.py                               | 135 [32m++++++++[m
 app/ingestion/pdf_loader.py                        |  96 [32m++++++[m
 app/ingestion/table_extractor.py                   |  25 [32m++[m
 app/main.py                                        |  25 [32m++[m
 app/preprocessing/__init__.py                      |   5 [32m+[m
 app/preprocessing/chunker.py                       | 124 [32m++++++++[m
 app/preprocessing/cleaner.py                       |  27 [32m++[m
 app/preprocessing/metadata.py                      |  51 [32m+++[m
 app/rag/chain.py                                   |  55 [32m++++[m
 app/rag/generator.py                               |  80 [32m+++++[m
 app/rag/prompts.py                                 |  37 [32m+++[m
 app/retrieval/hybrid_retriever.py                  |  66 [32m++++[m
 app/retrieval/query_rewriter.py                    |  15 [32m+[m
 app/retrieval/reranker.py                          |  30 [32m++[m
 app/rules/rule_engine.py                           |  30 [32m++[m
 app/schemas/retrieval.py                           |  23 [32m++[m
 app/vectorstore/bm25_store.py                      |  55 [32m++++[m
 app/vectorstore/qdrant_store.py                    | 142 [32m+++++++++[m
 config/.gitkeep                                    |   0
 data/evaluation/.gitkeep                           |   0
 data/processed/.gitkeep                            |   0
 data/uploads/.gitkeep                              |   0
 docker-compose.yml                                 |  38 [32m+++[m
 frontend/streamlit_app.py                          |  77 [32m+++++[m
 requirements-core.txt                              |  32 [32m++[m
 requirements.txt                                   |  33 [32m++[m
 scripts/ingest.py                                  |  24 [32m++[m
 tests/test_grounding.py                            |  19 [32m++[m
 tests/test_guardrails.py                           |  11 [32m+[m
 tests/test_ingestion.py                            |  19 [32m++[m
 tests/test_retrieval.py                            |   7 [32m+[m
 71 files changed, 2949 insertions(+)
