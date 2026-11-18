"""Streamlit entry point for the agentic PDF summarizer."""

from __future__ import annotations

import streamlit as st

from config import SUMMARY_STYLES, get_settings
from pdf_processor import DocumentStore, PDFProcessingError, process_pdf
from utils import format_bytes, mask_secret

st.set_page_config(page_title="Agentic PDF Summarizer", page_icon="📄", layout="wide")

st.title("📄 Agentic PDF Summarizer")
st.caption("Powered by LangChain, LangGraph and Google Gemini")

settings = get_settings()

with st.sidebar:
    st.header("Settings")
    st.text_input("Gemini model", value=settings.gemini_model, disabled=True)
    st.selectbox("Summary style", options=SUMMARY_STYLES, disabled=True)
    st.caption(f"API key: {mask_secret(settings.gemini_api_key)}")
    if not settings.gemini_api_key:
        st.error("Set GEMINI_API_KEY in .env to enable summarization.")

if "document_store" not in st.session_state:
    st.session_state.document_store = DocumentStore()
store = st.session_state.document_store

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        document = process_pdf(
            uploaded_file.name,
            uploaded_file.getvalue(),
            chunk_tokens=settings.chunk_tokens,
            overlap_tokens=settings.overlap_tokens,
        )
    except PDFProcessingError as exc:
        st.error(str(exc))
        st.stop()

    store.add(document)
    st.session_state.current_doc_id = document.doc_id

    st.success(f"Loaded: {document.name} ({format_bytes(uploaded_file.size)})")
    col1, col2, col3 = st.columns(3)
    col1.metric("Pages", document.page_count)
    col2.metric("Chunks", len(document.chunks))
    col3.metric("Tokens (approx.)", document.token_count)

    with st.expander("Preview first chunk"):
        st.write(document.chunks[0])

    st.info("The LangGraph agent arrives in Phase 3.")
else:
    st.info("Upload a PDF to begin.")
