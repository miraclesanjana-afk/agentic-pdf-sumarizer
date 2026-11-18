from __future__ import annotations

from utils import format_bytes, mask_secret


def test_format_bytes():
    assert format_bytes(0) == "0 B"
    assert format_bytes(512) == "512 B"
    assert format_bytes(2048) == "2.0 KB"


def test_mask_secret():
    assert mask_secret("") == "<unset>"
    assert mask_secret("abc") == "****"
    assert mask_secret("supersecretkey") == "****tkey"
