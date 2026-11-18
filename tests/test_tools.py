from __future__ import annotations

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from config import Settings
from pdf_processor import DocumentStore
from tests.helpers import make_pdf
from tools import build_tools


def make_toolset(tmp_path, responses=None):
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(make_pdf("Document body"))
    llm = FakeListChatModel(responses=responses or ["chunk summary", "final summary"])
    settings = Settings(gemini_api_key="test", chunk_tokens=200, overlap_tokens=10)
    tools = {tool.name: tool for tool in build_tools(DocumentStore(), llm, settings)}
    return pdf_path, tools


def test_load_pdf_and_summarize(tmp_path):
    pdf_path, tools = make_toolset(tmp_path)

    load_result = tools["load_pdf"].invoke({"file_path": str(pdf_path)})

    assert "doc_id=" in load_result
    doc_id = load_result.split("doc_id=")[1].split()[0]
    summary = tools["summarize_document"].invoke({"doc_id": doc_id, "style": "brief"})
    assert summary == "final summary"


def test_unknown_document_returns_error(tmp_path):
    _, tools = make_toolset(tmp_path)

    result = tools["summarize_document"].invoke({"doc_id": "missing", "style": "brief"})

    assert result.startswith("Error summarizing")


def test_list_loaded_documents(tmp_path):
    pdf_path, tools = make_toolset(tmp_path)
    tools["load_pdf"].invoke({"file_path": str(pdf_path)})

    listing = tools["list_loaded_documents"].invoke({})

    assert "doc.pdf" in listing
