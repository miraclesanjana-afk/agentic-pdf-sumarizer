"""Shared test fixtures."""

from __future__ import annotations

from io import BytesIO

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject


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
