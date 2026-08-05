"""Defensive redaction helpers for structured log context."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

_REDACTED = "[REDACTED]"
_SENSITIVE_KEYS = frozenset(
    {
        "authorization",
        "cookie",
        "password",
        "privatekey",
        "refreshtoken",
        "resetlink",
        "resettoken",
        "secret",
        "setcookie",
        "token",
    }
)


def _normalized_key(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def redact(value: Any) -> Any:
    """Recursively redact values associated with known sensitive key names."""

    if isinstance(value, Mapping):
        return {
            str(key): _REDACTED if _normalized_key(str(key)) in _SENSITIVE_KEYS else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [redact(item) for item in value]
    return value
