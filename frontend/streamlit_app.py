"""Streamlit UI for document upload and grounded chat."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings
from app.ingestion.document_loader import load_document
from app.preprocessing.chunker import chunk_document
from app.vectorstore.qdrant_store import QdrantStore
from app.rag.chain import get_rag_chain

st.set_page_config(page_title='Grounded RAG Assistant', page_icon='📚', layout='wide')
st.title('📚 Document Intelligence & Grounded RAG Assistant')
st.caption('Answers are restricted to indexed evidence and are validated before display.')

if 'history' not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header('Document Ingestion')
    uploads = st.file_uploader(
        'Upload documents',
        type=sorted(ext.lstrip('.') for ext in settings.supported_suffixes),
        accept_multiple_files=True,
    )
    if st.button('Process Documents', use_container_width=True):
        if not uploads:
            st.warning('Please upload at least one document.')
        else:
            all_chunks = []
            for uploaded in uploads:
                target = settings.upload_dir / Path(uploaded.name).name
                target.write_bytes(uploaded.getbuffer())
                record = load_document(target)
                chunks = chunk_document(record)
                QdrantStore().upsert_chunks(chunks)
                all_chunks.extend(chunks)
                st.success(f'{record.filename}: {len(record.elements)} elements → {len(chunks)} chunks')

            if all_chunks:
                get_rag_chain().retriever.index_bm25(all_chunks, append=True)
                st.success(f'Indexed {len(all_chunks)} chunks.')

st.divider()
for message in st.session_state.history:
    with st.chat_message(message['role']):
        st.write(message['content'])

question = st.chat_input('Ask a question about the uploaded documents...')
if question:
    st.session_state.history.append({'role': 'user', 'content': question})
    with st.chat_message('user'):
        st.write(question)

    with st.chat_message('assistant'):
        with st.spinner('Retrieving, reranking and validating evidence...'):
            response = get_rag_chain().answer(question, history=st.session_state.history[:-1])
        st.write(response.answer)
        if response.grounded:
            st.success(f'Grounding confidence: {response.confidence:.0%}')
        else:
            st.warning(response.warning or 'Grounding validation failed.')
        if response.citations:
            st.markdown('#### Sources')
            for citation in response.citations:
                location = f'Page {citation.page_start}' if citation.page_start else 'Page unavailable'
                section = f' — {citation.section}' if citation.section else ''
                st.write(f'📄 **{citation.filename}** · {location}{section} · `{citation.chunk_id}`')

    st.session_state.history.append({'role': 'assistant', 'content': response.answer})
