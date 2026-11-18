"""Small shared helpers for display and validation."""

from __future__ import annotations

import csv
from io import StringIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pdf_processor import ChunkInfo


def format_bytes(num_bytes: int) -> str:
    """Render a byte count as a compact human-readable string."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(value) < 1024 or unit == "TB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def mask_secret(value: str) -> str:
    """Return a display-safe version of a secret, revealing at most 4 characters."""
    if not value:
        return "<unset>"
    if len(value) <= 4:
        return "****"
    return f"****{value[-4:]}"


def message_text(content: object) -> str:
    """Normalize LangChain/Gemini message content into plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
            elif hasattr(block, "text"):
                parts.append(str(block.text))
        return "".join(parts)
    return str(content)


def build_summary_text(document_name: str, style: str, answer: str) -> str:
    """Create the content of the downloadable summary file."""
    return (
        f"Document: {document_name}\n"
        f"Summary style: {style}\n"
        f"{'=' * 40}\n\n"
        f"{answer}\n"
    )


def build_chunk_stats_csv(chunk_info: list[ChunkInfo], document_name: str) -> str:
    """Create a CSV report of per-chunk token and character counts."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["document", "chunk", "tokens", "characters"])
    for info in chunk_info:
        writer.writerow([document_name, info.index, info.token_count, info.char_count])
    return buffer.getvalue()
