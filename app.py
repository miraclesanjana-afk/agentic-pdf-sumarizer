"""Streamlit entry point for the agentic PDF summarizer."""

from __future__ import annotations

import streamlit as st

from config import SUMMARY_STYLES, get_settings
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

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    st.success(f"Selected: {uploaded_file.name} ({format_bytes(uploaded_file.size)})")
    st.info("PDF ingestion is implemented in Phase 2; the agent arrives in Phase 3.")
else:
    st.info("Upload a PDF to begin.")
