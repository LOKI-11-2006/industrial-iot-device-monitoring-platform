"""Run the deterministic local Backend Phase 1 quality gate."""

from __future__ import annotations

import subprocess
import sys


def _run(*arguments: str) -> None:
    subprocess.run([sys.executable, *arguments], check=True)  # noqa: S603


def main() -> None:
    """Run formatting, lint, strict typing, and tests in fail-fast order."""

    _run("-m", "ruff", "format", "--check", ".")
    _run("-m", "ruff", "check", ".")
    _run("-m", "mypy", "app", "scripts")
    _run("-m", "pytest")


if __name__ == "__main__":
    main()
