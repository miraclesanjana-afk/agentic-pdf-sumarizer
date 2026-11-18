from __future__ import annotations

from prompts import ANALYSIS, CHUNK_SUMMARY, COMBINE, QUOTES, STYLES


def test_styles_cover_expected_options():
    assert set(STYLES) == {"brief", "detailed", "bullet_points", "executive"}


def test_chunk_prompt_includes_style_and_text():
    messages = CHUNK_SUMMARY.format_messages(style="brief", text="Some excerpt")

    assert "brief" in messages[1].content
    assert "Some excerpt" in messages[1].content
    assert messages[0].type == "system"


def test_other_prompts_format():
    assert "Final" in COMBINE.format_messages(style="detailed", summaries="1. x")[1].content
    assert "structure" in ANALYSIS.format_messages(text="abc")[1].content.lower()
    assert "quotes" in QUOTES.format_messages(text="abc")[1].content.lower()
