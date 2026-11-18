"""Small shared helpers for display and validation."""

from __future__ import annotations


def format_bytes(num_bytes: int) -> str:
    """Render a byte count as a compact human-readable string."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(value) < 1024 or unit == "TB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def mask_secret(value: str) -> str:
    """Return a display-safe version of a secret, revealing at most 4 characters."""
    if not value:
        return "<unset>"
    if len(value) <= 4:
        return "****"
    return f"****{value[-4:]}"
