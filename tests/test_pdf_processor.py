from __future__ import annotations

from io import BytesIO

import pytest
import tiktoken
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from pdf_processor import (
    DocumentStore,
    PDFProcessingError,
    chunk_text,
    clean_text,
    count_tokens,
    extract_text,
    process_pdf,
)


def make_pdf(text: str = "Hello PDF world") -> bytes:
    """Build a minimal one-page PDF containing `text`."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)

    stream = DecodedStreamObject()
    stream.set_data(f"BT /F1 12 Tf 72 700 Td ({text}) Tj ET".encode())
    page[NameObject("/Contents")] = writer._add_object(stream)

    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})}
    )

    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_extract_text_from_bytes():
    text, pages = extract_text(make_pdf("Hello PDF world"))

    assert pages == 1
    assert "Hello PDF world" in text


def test_clean_text():
    messy = "Line  one \xa0 here\r\ninter-\nnational\r\r\rDone"

    assert clean_text(messy) == "Line one here\ninternational\n\nDone"


def test_chunk_text_respects_limits_and_overlap():
    text = " ".join(f"word{i}" for i in range(60))

    chunks = chunk_text(text, max_tokens=12, overlap_tokens=3)

    assert len(chunks) > 1
    assert all(0 < count_tokens(chunk) <= 12 for chunk in chunks)
    encoding = tiktoken.get_encoding("cl100k_base")
    first, second = encoding.encode(chunks[0]), encoding.encode(chunks[1])
    assert first[-3:] == second[:3]


def test_chunk_text_rejects_invalid_overlap():
    with pytest.raises(ValueError, match="overlap_tokens"):
        chunk_text("some text", max_tokens=10, overlap_tokens=10)


def test_process_pdf_builds_document():
    data = make_pdf("A short document for testing")

    doc = process_pdf("sample.pdf", data, chunk_tokens=50, overlap_tokens=5)

    assert doc.name == "sample.pdf"
    assert doc.page_count == 1
    assert len(doc.chunks) == len(doc.chunk_info) >= 1
    assert doc.token_count == sum(info.token_count for info in doc.chunk_info)


def test_process_pdf_rejects_empty_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buffer = BytesIO()
    writer.write(buffer)

    with pytest.raises(PDFProcessingError, match="No extractable text"):
        process_pdf("blank.pdf", buffer.getvalue(), chunk_tokens=50, overlap_tokens=5)


def test_document_store_roundtrip():
    doc = process_pdf(
        "sample.pdf", make_pdf("Stored document"), chunk_tokens=50, overlap_tokens=5
    )
    store = DocumentStore()

    doc_id = store.add(doc)

    assert store.get(doc_id) is doc
    with pytest.raises(KeyError, match="Unknown document id"):
        store.get("missing")
