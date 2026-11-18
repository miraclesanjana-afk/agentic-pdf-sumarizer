from __future__ import annotations

import pytest

from config import Settings


def test_from_env_reads_values(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("CHUNK_TOKENS", raising=False)
    monkeypatch.delenv("OVERLAP_TOKENS", raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text(
        "GEMINI_API_KEY=test-key\n"
        "GEMINI_MODEL=test-model\n"
        "CHUNK_TOKENS=512\n"
        "OVERLAP_TOKENS=50\n",
        encoding="utf-8",
    )

    settings = Settings.from_env(env_file)

    assert settings.gemini_api_key == "test-key"
    assert settings.gemini_model == "test-model"
    assert settings.chunk_tokens == 512
    assert settings.overlap_tokens == 50
    settings.validate()


def test_validate_rejects_missing_key(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("", encoding="utf-8")

    settings = Settings.from_env(env_file)

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        settings.validate()
