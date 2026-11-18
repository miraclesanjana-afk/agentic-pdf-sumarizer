"""Central configuration for the agentic PDF summarizer."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = "gemini-3.1-flash-lite"
DEFAULT_CHUNK_TOKENS = 1000
DEFAULT_OVERLAP_TOKENS = 100
SUMMARY_STYLES = ("brief", "detailed", "bullet_points", "executive")


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables / .env."""

    gemini_api_key: str
    gemini_model: str = DEFAULT_MODEL
    chunk_tokens: int = DEFAULT_CHUNK_TOKENS
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS

    @classmethod
    def from_env(cls, env_path: Path | None = None) -> Settings:
        """Load settings, optionally from a specific .env file."""
        load_dotenv(env_path or (ROOT_DIR / ".env"), override=False)
        return cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
            gemini_model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL,
            chunk_tokens=int(os.getenv("CHUNK_TOKENS", DEFAULT_CHUNK_TOKENS)),
            overlap_tokens=int(os.getenv("OVERLAP_TOKENS", DEFAULT_OVERLAP_TOKENS)),
        )

    def validate(self) -> None:
        """Raise ValueError if settings are unusable."""
        if not self.gemini_api_key or "your_gemini" in self.gemini_api_key.lower():
            raise ValueError("GEMINI_API_KEY is missing or still a placeholder in .env")
        if not self.gemini_model:
            raise ValueError("GEMINI_MODEL must not be empty")
        if self.chunk_tokens <= 0:
            raise ValueError("CHUNK_TOKENS must be positive")
        if self.overlap_tokens < 0 or self.overlap_tokens >= self.chunk_tokens:
            raise ValueError("OVERLAP_TOKENS must be >= 0 and smaller than CHUNK_TOKENS")


def get_settings(env_path: Path | None = None) -> Settings:
    """Convenience loader used by the app and tests."""
    return Settings.from_env(env_path)
