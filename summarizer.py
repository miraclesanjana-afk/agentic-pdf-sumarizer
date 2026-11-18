"""Gemini-backed summarization operations used by the agent tools."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from config import SUMMARY_STYLES, Settings
from prompts import ANALYSIS, CHUNK_SUMMARY, COMBINE, QUOTES, STYLES
from utils import message_text

MAX_ANALYSIS_CHARS = 12_000


def make_llm(settings: Settings) -> BaseChatModel:
    """Create the Gemini chat model used by every tool."""
    return ChatGoogleGenerativeAI(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        temperature=0,
        retries=6,
        request_timeout=120,
    )


def _invoke(prompt: object, llm: BaseChatModel, **values: object) -> str:
    return message_text((prompt | llm).invoke(values).content).strip()


def _check_style(style: str) -> str:
    normalized = style.strip().lower()
    if normalized not in STYLES or normalized not in SUMMARY_STYLES:
        raise ValueError(f"Unknown summary style: {style}. Choose from {', '.join(STYLES)}")
    return normalized


def summarize_document(llm: BaseChatModel, chunks: list[str], style: str) -> str:
    """Map each chunk to a summary, then reduce them into a final summary."""
    chosen_style = _check_style(style)
    if not chunks:
        raise ValueError("No chunks available to summarize")

    chunk_summaries = [
        _invoke(CHUNK_SUMMARY, llm, style=chosen_style, text=chunk) for chunk in chunks
    ]
    numbered = "\n\n".join(f"{i}. {text}" for i, text in enumerate(chunk_summaries, start=1))
    return _invoke(COMBINE, llm, style=chosen_style, summaries=numbered)


def analyze_structure(llm: BaseChatModel, text: str) -> str:
    """Describe the document's sections and themes."""
    if not text.strip():
        raise ValueError("No text available to analyze")
    return _invoke(ANALYSIS, llm, text=text[:MAX_ANALYSIS_CHARS])


def extract_quotes(llm: BaseChatModel, text: str) -> str:
    """Extract key verbatim quotes from the document."""
    if not text.strip():
        raise ValueError("No text available for quote extraction")
    return _invoke(QUOTES, llm, text=text[:MAX_ANALYSIS_CHARS])
