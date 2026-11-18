from __future__ import annotations

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessage

from agent import agent_final_text, build_agent, run_agent, stream_agent_updates
from config import Settings
from pdf_processor import DocumentStore
from tests.fakes import FakeToolModel
from tests.helpers import make_pdf
from tools import build_tools


def build_fake_agent(tmp_path):
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(make_pdf("Agent test document"))
    settings = Settings(gemini_api_key="test", chunk_tokens=200, overlap_tokens=10)
    store = DocumentStore()
    model = FakeToolModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {"name": "load_pdf", "args": {"file_path": str(pdf_path)}, "id": "call-1"}
                ],
            ),
            AIMessage(content="PDF loaded successfully."),
        ]
    )
    tools = build_tools(store, FakeListChatModel(responses=["summary"]), settings)
    return build_agent(model, tools), store


def test_agent_invokes_tool_and_returns_final_text(tmp_path):
    agent, store = build_fake_agent(tmp_path)

    result = agent.invoke({"messages": [{"role": "user", "content": "Load the PDF"}]})

    types = [message.type for message in result["messages"]]
    assert "tool" in types
    assert agent_final_text(result) == "PDF loaded successfully."
    assert len(store.list_documents()) == 1


def test_run_agent_helper(tmp_path):
    agent, _ = build_fake_agent(tmp_path)

    assert run_agent(agent, "Load the PDF") == "PDF loaded successfully."


def test_stream_agent_updates_yields_nodes(tmp_path):
    agent, _ = build_fake_agent(tmp_path)

    nodes = [next(iter(update)) for update in stream_agent_updates(agent, "Load the PDF")]

    assert nodes == ["model", "tools", "model"]
