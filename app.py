"""Streamlit entry point for the agentic PDF summarizer."""

from __future__ import annotations

import os
import tempfile
from dataclasses import replace

import streamlit as st

from agent import build_agent, stream_agent_updates
from config import SUMMARY_STYLES, get_settings
from pdf_processor import DocumentStore
from summarizer import make_llm
from tools import build_tools
from utils import (
    build_chunk_stats_csv,
    build_summary_text,
    format_bytes,
    mask_secret,
    message_text,
)

st.set_page_config(page_title="Agentic PDF Summarizer", page_icon="📄", layout="wide")

st.title("📄 Agentic PDF Summarizer")
st.caption("Powered by LangChain, LangGraph and Google Gemini")

settings = get_settings()
try:
    settings.validate()
except ValueError as exc:
    st.error(str(exc))
    st.stop()

if "document_store" not in st.session_state:
    st.session_state.document_store = DocumentStore()
if "temp_pdf_path" not in st.session_state:
    st.session_state.temp_pdf_path = None
if "result" not in st.session_state:
    st.session_state.result = None
if "agent" not in st.session_state:
    st.session_state.agent = None


def cleanup_temp_pdf() -> None:
    path = st.session_state.get("temp_pdf_path")
    if path and os.path.exists(path):
        os.unlink(path)
    st.session_state.temp_pdf_path = None


with st.sidebar:
    st.header("Settings")
    model = st.text_input("Gemini model", value=settings.gemini_model)
    style = st.selectbox("Summary style", options=SUMMARY_STYLES)
    want_analysis = st.checkbox("Analyze document structure", value=False)
    want_quotes = st.checkbox("Extract key quotes", value=False)
    st.caption(f"API key: {mask_secret(settings.gemini_api_key)}")

    if st.button("Clear session"):
        cleanup_temp_pdf()
        st.session_state.document_store.clear()
        st.session_state.result = None
        st.session_state.agent = None
        st.session_state.upload_fingerprint = None
        st.rerun()

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is None:
    st.info("Upload a PDF to begin.")
    st.stop()

fingerprint = f"{uploaded_file.name}:{uploaded_file.size}"
if st.session_state.get("upload_fingerprint") != fingerprint:
    cleanup_temp_pdf()
    st.session_state.document_store.clear()
    st.session_state.result = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        st.session_state.temp_pdf_path = temp_file.name
    st.session_state.upload_fingerprint = fingerprint

st.success(f"Selected: {uploaded_file.name} ({format_bytes(uploaded_file.size)})")

active_settings = replace(settings, gemini_model=model.strip() or settings.gemini_model)
if (
    st.session_state.agent is None
    or st.session_state.get("agent_model") != active_settings.gemini_model
):
    llm = make_llm(active_settings)
    st.session_state.agent = build_agent(
        llm,
        build_tools(st.session_state.document_store, llm, active_settings),
    )
    st.session_state.agent_model = active_settings.gemini_model

request = (
    f"Load the PDF at {st.session_state.temp_pdf_path} and summarize it "
    f"in {style} style."
)
if want_analysis:
    request += " Also analyze the document structure."
if want_quotes:
    request += " Also extract key quotes."

if st.button("Summarize", type="primary"):
    with st.status("Agent is working...", expanded=True) as status:
        final_text = ""
        try:
            for update in stream_agent_updates(st.session_state.agent, request):
                for node, payload in update.items():
                    if node == "tools":
                        for message in payload.get("messages", []):
                            st.write(f"Called `{getattr(message, 'name', 'tool')}`")
                    elif node == "model":
                        for message in payload.get("messages", []):
                            text = message_text(getattr(message, "content", "")).strip()
                            if text:
                                st.write("Reasoning complete.")
                                final_text = text
        except Exception as exc:  # noqa: BLE001 - surface provider errors in the UI
            status.update(label="Failed", state="error")
            st.error(f"Summarization failed: {exc}")
        else:
            if not final_text:
                status.update(label="Failed", state="error")
                st.error("The agent did not return an answer.")
            else:
                st.session_state.result = {
                    "text": final_text,
                    "style": style,
                    "model": active_settings.gemini_model,
                }
                status.update(label="Done", state="complete")

result = st.session_state.result
if result:
    st.subheader("Result")
    st.write(result["text"])

    documents = st.session_state.document_store.list_documents()
    document = documents[-1] if documents else None
    name = document.name if document else uploaded_file.name

    col1, col2 = st.columns(2)
    col1.download_button(
        "Download summary (.txt)",
        data=build_summary_text(name, result["style"], result["text"]),
        file_name="summary.txt",
    )
    if document:
        col2.download_button(
            "Download chunk stats (.csv)",
            data=build_chunk_stats_csv(document.chunk_info, document.name),
            file_name="chunk_stats.csv",
            mime="text/csv",
        )

        with st.expander("Document details"):
            metric1, metric2, metric3 = st.columns(3)
            metric1.metric("Pages", document.page_count)
            metric2.metric("Chunks", len(document.chunks))
            metric3.metric("Tokens (approx.)", document.token_count)
