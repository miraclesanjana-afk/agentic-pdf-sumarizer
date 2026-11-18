from __future__ import annotations

from pdf_processor import ChunkInfo
from utils import build_chunk_stats_csv, build_summary_text, format_bytes, mask_secret


def test_format_bytes():
    assert format_bytes(0) == "0 B"
    assert format_bytes(512) == "512 B"
    assert format_bytes(2048) == "2.0 KB"


def test_mask_secret():
    assert mask_secret("") == "<unset>"
    assert mask_secret("abc") == "****"
    assert mask_secret("supersecretkey") == "****tkey"


def test_build_summary_text():
    text = build_summary_text("doc.pdf", "brief", "A summary.")

    assert "doc.pdf" in text
    assert "brief" in text
    assert "A summary." in text


def test_build_chunk_stats_csv():
    info = [ChunkInfo(index=1, token_count=12, char_count=40)]

    csv_text = build_chunk_stats_csv(info, "doc.pdf")

    assert "document,chunk,tokens,characters" in csv_text
    assert "doc.pdf,1,12,40" in csv_text
