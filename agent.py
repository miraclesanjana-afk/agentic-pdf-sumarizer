"""LangGraph agent construction and invocation helpers."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from prompts import AGENT_SYSTEM_PROMPT
from utils import message_text

Agent = Any


def build_agent(llm: BaseChatModel, tools: list[BaseTool]) -> Agent:
    """Create a LangGraph-backed tool-calling agent."""
    return create_agent(model=llm, tools=tools, system_prompt=AGENT_SYSTEM_PROMPT)


def agent_final_text(result: dict[str, Any]) -> str:
    """Return the last non-empty AI message from an agent result."""
    for message in reversed(result.get("messages", [])):
        if getattr(message, "type", None) == "ai":
            text = message_text(getattr(message, "content", "")).strip()
            if text:
                return text
    return ""


def run_agent(agent: Agent, request: str) -> str:
    """Invoke the agent with a user request and return its final answer."""
    result = agent.invoke({"messages": [{"role": "user", "content": request}]})
    return agent_final_text(result)


def stream_agent_updates(agent: Agent, request: str) -> Iterator[dict[str, Any]]:
    """Yield LangGraph node updates so a UI can show progress."""
    yield from agent.stream(
        {"messages": [{"role": "user", "content": request}]},
        stream_mode="updates",
    )
