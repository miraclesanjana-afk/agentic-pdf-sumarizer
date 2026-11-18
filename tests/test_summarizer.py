from __future__ import annotations

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from config import Settings
from summarizer import analyze_structure, extract_quotes, make_llm, summarize_document
from utils import message_text


def test_make_llm_uses_configured_model():
    llm = make_llm(Settings(gemini_api_key="test-key", gemini_model="test-model"))

    assert llm.model == "test-model"


def test_summarize_document_maps_chunks_then_combines():
    llm = FakeListChatModel(responses=["chunk one", "chunk two", "final summary"])

    result = summarize_document(llm, ["text one", "text two"], "brief")

    assert result == "final summary"


def test_analyze_and_quotes():
    llm = FakeListChatModel(responses=["structure result", "quotes result"])

    assert analyze_structure(llm, "Document text") == "structure result"
    assert extract_quotes(llm, "Document text") == "quotes result"


def test_unknown_style_raises():
    llm = FakeListChatModel(responses=[])

    try:
        summarize_document(llm, ["text"], "unknown")
    except ValueError as exc:
        assert "Unknown summary style" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_message_text_normalizes_gemini_content_blocks():
    content = [{"type": "text", "text": "hello"}, {"type": "text", "text": " world"}]

    assert message_text(content) == "hello world"
