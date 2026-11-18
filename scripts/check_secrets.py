"""Fail if tracked files look like they contain committed secrets.

Run after staging changes:
    .venv\\Scripts\\python.exe scripts\\check_secrets.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = {
    "gemini_api_key": re.compile(rb"AIza[0-9A-Za-z_\-]{20,}"),
    "quoted_api_key": re.compile(
        rb"(?i)(api[_-]?key)\s*=\s*['\"][A-Za-z0-9_\-]{24,}['\"]"
    ),
    "private_key": re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}


def tracked_files() -> list[bytes]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [item for item in output.split(b"\0") if item]


def main() -> int:
    files = tracked_files()
    findings: list[tuple[str, str]] = []

    if b".env" in files:
        findings.append((".env", "tracked env file"))

    for raw_path in files:
        path = ROOT / raw_path.decode("utf-8", errors="replace")
        if not path.is_file():
            continue
        data = path.read_bytes()
        for name, pattern in PATTERNS.items():
            if pattern.search(data):
                findings.append((raw_path.decode("utf-8", errors="replace"), name))

    if findings:
        for filename, reason in findings:
            print(f"[FAIL] {filename}: {reason}")
        return 1

    print(f"[ OK ] No secrets found in {len(files)} tracked files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
