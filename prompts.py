"""Prompt templates used by the agent's tools."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

STYLES = {
    "brief": "Write a concise 2-3 sentence overview of the document.",
    "detailed": "Extract the key points, arguments and conclusions in a structured way.",
    "bullet_points": "Produce a scannable bullet-point summary of the most important ideas.",
    "executive": "Write a business-focused summary with insights and recommendations.",
}

AGENT_SYSTEM_PROMPT = """You are a careful document analyst with access to PDF tools.

Workflow:
1. If given a PDF file path, call `load_pdf` first and remember the returned doc_id.
2. Use `summarize_document` for the requested summary style.
3. Call `analyze_document_structure` or `extract_key_quotes` only when the user asks,
   or when they would clearly improve the answer.
4. Do not invent document contents. If a tool reports an error, explain it plainly.

Prefer tool results over your own guesses, and keep the final answer focused.
"""

_SYSTEM_MESSAGE = (
    "You are a precise assistant analyzing an uploaded PDF. "
    "Use only the supplied text. Do not invent facts."
)


def _template(human: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [("system", _SYSTEM_MESSAGE), ("human", human)]
    )


CHUNK_SUMMARY = _template(
    "Summarize this PDF excerpt using the requested style.\n\n"
    "Style: {style}\n\n"
    "Excerpt:\n{text}\n\n"
    "Summary:"
)

COMBINE = _template(
    "Combine the following chunk summaries into one coherent final summary.\n\n"
    "Style: {style}\n\n"
    "Chunk summaries:\n{summaries}\n\n"
    "Final summary:"
)

ANALYSIS = _template(
    "Analyze the structure of the document. Identify sections, main themes and "
    "how the argument is organized.\n\nDocument text:\n{text}\n\nAnalysis:"
)

QUOTES = _template(
    "Extract the most important verbatim quotes from the document. "
    "Return each quote on its own line.\n\nDocument text:\n{text}\n\nQuotes:"
)
