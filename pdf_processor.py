"""PDF text extraction, cleaning, token counting and chunking."""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

import tiktoken
from pypdf import PdfReader

_ENCODING_NAME = "cl100k_base"
_encoding = tiktoken.get_encoding(_ENCODING_NAME)


class PDFProcessingError(Exception):
    """Raised when a PDF cannot be read or contains no usable text."""


@dataclass(frozen=True)
class ChunkInfo:
    """Statistics for one chunk, used by exports and the UI."""

    index: int
    token_count: int
    char_count: int


@dataclass
class Document:
    """A cleaned PDF and its token-limited chunks."""

    doc_id: str
    name: str
    text: str
    chunks: list[str]
    page_count: int
    chunk_info: list[ChunkInfo]

    @property
    def token_count(self) -> int:
        return sum(info.token_count for info in self.chunk_info)


def clean_text(text: str) -> str:
    """Normalize whitespace and repair hyphenated line breaks."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")
    text = text.replace("\xa0", " ")
    text = re.sub(r"(\w)-\n(?=\w)", r"\1", text)
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text(source: bytes | BinaryIO | str | Path) -> tuple[str, int]:
    """Return (raw_text, page_count) for a PDF given as bytes, file object or path."""
    try:
        if isinstance(source, bytes):
            reader = PdfReader(BytesIO(source))
        elif isinstance(source, (str, Path)):
            reader = PdfReader(str(source))
        else:
            reader = PdfReader(source)

        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages), len(pages)
    except PDFProcessingError:
        raise
    except Exception as exc:  # noqa: BLE001 - pypdf raises varied parse errors
        raise PDFProcessingError(f"Could not read PDF: {exc}") from exc


def count_tokens(text: str) -> int:
    """Count tokens using tiktoken's cl100k_base encoding (an approximation for Gemini)."""
    return len(_encoding.encode(text))


def chunk_text(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    """Split text into overlapping, token-limited chunks."""
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
    if overlap_tokens < 0 or overlap_tokens >= max_tokens:
        raise ValueError("overlap_tokens must be >= 0 and smaller than max_tokens")

    token_ids = _encoding.encode(text)
    if not token_ids:
        return []

    chunks: list[str] = []
    step = max_tokens - overlap_tokens
    start = 0
    while start < len(token_ids):
        end = min(start + max_tokens, len(token_ids))
        chunk = _encoding.decode(token_ids[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == len(token_ids):
            break
        start += step
    return chunks


def process_pdf(
    file_name: str,
    data: bytes,
    *,
    chunk_tokens: int,
    overlap_tokens: int,
) -> Document:
    """Extract, clean and chunk a PDF into a Document ready for the agent."""
    raw_text, page_count = extract_text(data)
    text = clean_text(raw_text)
    if not text:
        raise PDFProcessingError(
            "No extractable text found. The PDF may be a scanned image; run OCR first."
        )

    chunks = chunk_text(text, chunk_tokens, overlap_tokens)
    if not chunks:
        raise PDFProcessingError("Text extraction produced no usable chunks.")

    chunk_info = [
        ChunkInfo(index=i, token_count=count_tokens(chunk), char_count=len(chunk))
        for i, chunk in enumerate(chunks, start=1)
    ]
    return Document(
        doc_id=uuid4().hex[:8],
        name=file_name,
        text=text,
        chunks=chunks,
        page_count=page_count,
        chunk_info=chunk_info,
    )


class DocumentStore:
    """Small in-memory registry of processed documents for agent tools."""

    def __init__(self) -> None:
        self._documents: dict[str, Document] = {}
        self._lock = threading.Lock()

    def add(self, document: Document) -> str:
        with self._lock:
            self._documents[document.doc_id] = document
        return document.doc_id

    def get(self, doc_id: str) -> Document:
        with self._lock:
            try:
                return self._documents[doc_id]
            except KeyError as exc:
                raise KeyError(f"Unknown document id: {doc_id}") from exc

    def list_documents(self) -> list[Document]:
        with self._lock:
            return list(self._documents.values())

    def clear(self) -> None:
        with self._lock:
            self._documents.clear()
