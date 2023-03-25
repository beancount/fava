"""Account name helpers."""
from __future__ import annotations


def parent(acc: str) -> str | None:
    """Get the name of the parent of the given account."""
    parts = acc.rsplit(":", maxsplit=1)
    return parts[0] if len(parts) == 2 else None


def root(acc: str) -> str:
    """Get root account of the given account."""
    parts = acc.split(":", maxsplit=1)
    return parts[0]
