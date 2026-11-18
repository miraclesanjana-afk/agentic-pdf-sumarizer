"""Validate the Phase 0 prerequisites: Gemini API key and GitHub CLI login.

Run from the project root:
    .venv\\Scripts\\python.exe scripts\\validate_phase0.py

The key is read from .env and never printed. Nothing is pushed by this script.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "gemini-3.1-flash-lite"
PLACEHOLDERS = {"", "your_gemini_api_key_here", "changeme", "replace_me"}


def check_gemini() -> bool:
    load_dotenv(ROOT / ".env", override=False)
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL).strip()

    if key.lower() in PLACEHOLDERS or "your_gemini" in key.lower():
        print("[FAIL] GEMINI_API_KEY is missing or still a placeholder in .env")
        return False

    fingerprint = hashlib.sha256(key.encode()).hexdigest()[:8]
    print(f"[INFO] GEMINI_API_KEY found (sha256:{fingerprint}, length={len(key)})")
    print(f"[INFO] Testing live call with model: {model}")

    try:
        llm = ChatGoogleGenerativeAI(
            api_key=key,
            model=model,
            temperature=0,
            max_tokens=32,
            retries=1,
            request_timeout=30,
        )
        response = llm.invoke("Reply with exactly: OK")
    except Exception as exc:  # noqa: BLE001 - surface any provider/auth error
        print(f"[FAIL] Gemini call failed: {type(exc).__name__}: {exc}")
        print("       Check the key, the GEMINI_MODEL value, and network access.")
        return False

    text = str(response.content).strip()
    print(f"[ OK ] Gemini responded: {text[:120]!r}")
    return True


def check_github() -> bool:
    try:
        status = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print("[FAIL] GitHub CLI (gh) is not installed or not on PATH")
        return False

    if status.returncode != 0:
        print("[FAIL] GitHub CLI is not logged in. Run: gh auth login --web --git-protocol https")
        return False

    who = subprocess.run(
        ["gh", "api", "user", "--jq", ".login"],
        capture_output=True,
        text=True,
        check=False,
    )
    if who.returncode != 0:
        print("[FAIL] Could not read GitHub identity via `gh api user`")
        return False

    print(f"[ OK ] GitHub authenticated as: {who.stdout.strip()}")
    return True


def main() -> int:
    key_ok = check_gemini()
    github_ok = check_github()
    print("\nPhase 0:", "PASS" if key_ok and github_ok else "INCOMPLETE")
    return 0 if key_ok and github_ok else 1


if __name__ == "__main__":
    sys.exit(main())
